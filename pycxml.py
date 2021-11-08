"""
pycxml - A python translator for Cyclone XML (cxml)


"""

import os
import sys
from itertools import product
from datetime import datetime

import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET

import logging as log

from validator import Validator, CXML_SCHEMA
from converter import convert


DATEFMT = "%Y-%m-%dT%H:%M:%SZ"
FORECAST_COLUMNS = ["disturbance", "validtime", "latitude",
                    "longitude", "pcentre", "windspeed", "rmax", "poci"]
ENSEMBLE_COLUMNS = ["disturbance", "member", "validtime", "latitude",
                    "longitude", "pcentre", "windspeed", "rmax", "poci"]

RADII_COLUMNS = ['R34NEQ', 'R34SEQ', 'R34SWQ', 'R34NWQ',
                 'R48NEQ', 'R48SEQ', 'R48SWQ', 'R48NWQ',
                 'R64NEQ', 'R64SEQ', 'R64SWQ', 'R64NWQ']


def validate(xmlfile):
    """
    Validate an xml file with a given xsd schema definition

    :param str xmlfile: The XML file to validate

    :returns: True if `xmlfile` is a valid xml file based on the
              default CXML XSD definition

    """
    validator = Validator(CXML_SCHEMA)
    validator.validate(xmlfile)
    return


def parsePosition(lonelem, latelem):
    """
    Parse the positional elements to ensure correct geographical coordinates
    The CXML schema allows for various units of N/S and E/W, so need to use
    caution to ensure they are correctly parsed.

    :param lonelem: :class:`xml.etree.ElementTree.Element` containing
    longitudinal position information

    :param latelem: :class:`xml.etree.ElementTree.Element` containing
    latitudinal position information

    :returns: :tuple: (lon, lat) in geographical coordinates.
    (longitude (0, 360], latitude (-90, 90))

    :note: No checking of the units attribute is performed here. We assume any
    invalid values are captured by validating against the schema definition.
    """

    latvalue = float(latelem.text)
    latunits = latelem.attrib['units']
    latvalue = -latvalue if latunits == 'deg S' else latvalue

    lonvalue = float(lonelem.text)
    lonunits = lonelem.attrib['units']
    lonvalue = -lonvalue if lonunits == 'deg W' else lonvalue
    lonvalue = np.mod(lonvalue, 360)

    return (lonvalue, latvalue)


def getMSLP(fix, units='hPa'):
    """
    From a `fix` element, extract the minimum pressure and return the value,
    converted to hPa. We make the assumption that the `units` attribute exists
    in the file (it is a required attribute of the `pressure` element in the
    XSD).

    :param fix: :class:`xml.etree.ElementTree.element` containing details of a
    disturbance fix
    :param str units: output units (default "hPa")
    :returns: Minimum pressure, in specified units, if it exists. None
    otherwise.
    """
    mslpelem = fix.find('./cycloneData/minimumPressure/pressure')
    if mslpelem is not None:
        mslp = float(mslpelem.text)
        inunits = mslpelem.attrib['units']
        return convert(mslp, inunits, units)
    else:
        # log.warning("No minimum pressure data in this fix")
        return None


def getWindSpeed(fix, units='km/h'):
    """
    From a `fix` element, extract the maximum wind speed and return the value,
    converted to the given units.

    :param fix:  :class:`xml.etree.ElementTree.element` containing details of a
    disturbance fix
    :param str units: Units to convert maximum wind speed value to.

    :returns: maximum wind speed, in given units, if it exists. None otherwise.
    """
    windelem = fix.find('./cycloneData/maximumWind/speed')
    if windelem is not None:
        wind = float(windelem.text)
        inunits = windelem.attrib['units']
        return convert(wind, inunits, units)
    else:
        log.warning("No maximum wind speed data in this fix")
        return None


def getPoci(fix):
    """
    From a `fix` element, extract the pressure of the outermost closed isobar,
    if it exists, and return the value, converted to hPa.

    :param fix: :class:`xml.etree.ElementTree.element` containing details of a
    disturbance fix

    :returns: Pressure of outermost closed isobar, in hPa, if it exists. None
    otherwise.
    """
    pocielem = fix.find('./cycloneData/lastClosedIsobar/pressure')
    if pocielem is not None:
        poci = float(pocielem.text)
        units = pocielem.attrib['units']
        return convert(poci, units, 'hPa')
    else:
        # log.warning("No pressure of outer isobar data in this fix")
        return None


def getRmax(fix):
    """
    From a `fix` element, determine radius to maximum winds and return value
    converted to km

    :param fix: :class:`xml.etree.ElementTree.element` containing details of a
    disturbance fix

    :returns: Radius to maximum winds, in km
    """

    rmwelem = fix.find('./cycloneData/maximumWind/radius')
    if rmwelem is not None:
        rmw = float(rmwelem.text)
        units = rmwelem.attrib['units']
        return convert(rmw, units, 'km')
    else:
        log.warning("No rmw data in this fix")
        return None


def parseFix(fix):
    """
    `fix` is a single CXML fix element that describes the position of a
    disturbance at a particular time.

    :param fix: :class:`xml.etree.ElementTree.element` containing details of a
    disturbance fix.

    :returns: :class:`dict`
    """

    # This is strictly not a mandatory atttribute
    # hour = int(fix.attrib['hour'])

    # These are the only two mandatory elements of a fix.
    # Every other element is optional
    fixdata = {}
    fixdata['validtime'] = getHeaderTime(fix, 'validTime')
    fixdata['longitude'], fixdata['latitude'] = parsePosition(
        fix.find('longitude'), fix.find('latitude'))

    # Other elements, may not be present:
    fixdata['pcentre'] = getMSLP(fix)
    fixdata['windspeed'] = getWindSpeed(fix)
    fixdata['rmax'] = getRmax(fix)
    fixdata['poci'] = getPoci(fix)
    series = pd.Series(fixdata, index=FORECAST_COLUMNS)
    if fix.find('./cycloneData/windContours'):
        windradii = getWindContours(fix)
        fixdata = pd.concat([series, windradii])
        series = pd.Series(fixdata, index=FORECAST_COLUMNS+RADII_COLUMNS)

    return series


def getWindContours(fix):
    """
    :param fix: :class:`xml.etree.ElementTree.element` containing
    details of the wind contours element of a disturbance fix.
    """
    data = {}
    for elem in fix.findall('cycloneData/windContours/windSpeed'):
        mag = int(float(elem.text))
        for r in elem.findall('radius'):
            quadrant = r.attrib['sector']
            distance = float(r.text)
            data[f"R{mag:d}{quadrant}"] = distance
    return pd.Series(data, index=RADII_COLUMNS)


def getHeaderTime(header, field="baseTime"):
    """
    Determine the base time of the forecast from the header information.
    There are two times that can be included in the header - the `creationTime`
    and the `baseTime`. `creationTime` is mandatory, `baseTime` is optional.

    `creationTime` is the date/time the data was created.
    `baseTime` is the reference time for an analysis or forecast - i.e. when
    the forecast was initialised, or the analysis was valid.

    :param header: :class:`xml.etree.ElementTree.Element` containing header
    information for the CXML file being processed.

    :returns: :class:`datetime` object for the requested field. If `baseTime`
    was requested and does not exist, returns None.

    """
    try:
        dtstr = header.find(field).text
    except AttributeError:
        log.warning(f"Header information does not contain {field} element")
        return None

    try:
        dt = datetime.strptime(dtstr, DATEFMT)
    except ValueError:
        raise ValueError("Date format does not match required format")
    else:
        return dt


def getHeaderCenter(header):
    """
    Retrieve the production centre from the header information. The production
    centre, if included, optionally includes a `subCenter` element. In the
    Australian case, this is used to specify which TC Warning Centre issued the
    bulletin (i.e. Perth, Brisbane, Darwin TCWC).

    :param header: :class:`xml.etree.ElementTree.Element` containing header
    information for the CXML file being processed.
    """
    centre = header.find("productionCenter").text
    if header.find('productionCenter/subCenter') is not None:
        subCentre = header.find('productionCenter/subCenter').text
        centre = f"{centre} - {subCentre}"

    return centre


def parseHeader(header):
    """
    Process header information from a CXML file

    :param header: :class:`xml.etree.ElementTree.Element` containing header
    information for the CXML file being processed.

    """
    basetime = getHeaderTime(header, "baseTime")
    creationtime = getHeaderTime(header, "creationTime")
    centre = getHeaderCenter(header)

    return basetime, creationtime, centre


def isEnsemble(header):
    """
    Determine if a file represents an ensemble forecast product.
    These have an <ensemble> element in the header, which contains
    information on the number of members and the perturbation method.

    :param header: :class:`xml.etree.ElementTree.Element` containing header
    information for the CXML file being processed.

    :returns: `True` if this represents an ensemble forecast, False otherwise.
    """
    if header.find('generatingApplication/ensemble') is not None:
        return True
    else:
        return False


def ensembleCount(ensembleElem):
    """
    Get the number of ensemble members from the header
    :param header: :class:`xml.etree.ElementTree.Element` containing header
    information for the CXML file being processed.

    :returns: Number of ensemble members
    """

    nmembers = ensembleElem.find('numMembers')
    return int(nmembers.text)


def parseEnsemble(data: list) -> list:
    """

    :param list data: List of data elements
    :returns: a list of `pd.DataFrames` that each contain an ensemble member
    """
    forecasts = []
    for d in data:
        log.debug(f"Ensemble member: {d.attrib['member']}")
        member = d.attrib['member']
        disturbance = d.find('disturbance')
        distId, tcId, tcName = parseDisturbance(disturbance)
        df = pd.DataFrame(columns=ENSEMBLE_COLUMNS+RADII_COLUMNS)
        fixes = disturbance.findall("./fix")
        log.debug(f"Disturbance {distId}: number of fixes: {len(fixes)}")
        for f in fixes:
            fixdata = parseFix(f)
            df.loc[len(df), :] = fixdata
        forecasts.append(df)
    return forecasts


def parseForecast(data) -> pd.DataFrame:
    """
    Parse a data element to extract forecast information into a DataFrame.

    :param data: :class:`xml.etree.ElementTree.Element` containing forecas
    data.

    :returns: `pd.DataFrame` of the forecast data.
    """
    disturbance = data.find('disturbance')
    distId, tcId, tcName = parseDisturbance(disturbance)
    df = pd.DataFrame(columns=FORECAST_COLUMNS+RADII_COLUMNS)
    fixes = disturbance.findall("./fix")
    log.debug(f"Disturbance {distId}: number of fixes: {len(fixes)}")

    for f in fixes:
        fixdata = parseFix(f)
        df.loc[len(df), :] = fixdata
    df['disturbance'] = disturbance
    return df


def parseAnalysis(data):
    pass


def parseDisturbance(dist):
    """
    Process a disturbance feature (i.e. a TC event)

    :param dist: :class:`xml.etree.ElementTree.Element` containing details of
    a disturbance

    :returns: :class:`pandas.DataFrame` containing analysis and forecast data
    for a disturbance
    """
    distId = dist.attrib['ID']

    if dist.find('localId') is not None:
        tcId = dist.find('localId').text
    else:
        log.debug("No localId attribute given")
        tcId = ""

    if dist.find('cycloneName') is not None:
        tcName = dist.find('cycloneName').text
    else:
        log.debug("No cycloneName attribute given")
        tcName = ""

    return distId, tcId, tcName


def loadfile(xmlfile):
    """
    Load a CXML file and validate it

    :param str xmlfile: Path to the CXML file to load

    :returns: :class:`pandas.DataFrame` containing the data in all disturbances
    included in the file.

    """

    if not os.path.isfile(xmlfile):
        log.exception(f"{xmlfile} is not a file")
        raise IOError

    log.info(f"Parsing {xmlfile}")

    # try:
    #     validate(xmlfile)
    # except AssertionError as e:
    #    log.error(f"{xmlfile} is not a valid CXML file: {e}")
    #     raise

    tree = ET.parse(xmlfile)
    xroot = tree.getroot()
    header = xroot.find('header')

    if isEnsemble(header):
        ensembleElem = header.find('generatingApplication/ensemble')
        nmembers = ensembleCount(ensembleElem)
        log.info(f"This is an ensemble forecast with {nmembers} members")
        data = xroot.findall("./data")
        forecasts = parseEnsemble(data)
        return forecasts
    else:
        data = xroot.findall("./data")
        for d in data:
            if d.attrib['type'] == 'forecast':
                forecast = parseForecast(d)
                return forecast
            elif d.attrib['type'] == 'analysis':
                analysis = parseAnalysis(d)
                return analysis
