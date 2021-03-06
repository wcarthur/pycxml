"""
pycxml - A python translator for Cyclone XML (cxml)


"""

import os
import sys
from datetime import datetime

import numpy as np
import xml.etree.ElementTree as ET

import logging as log

import xmlschema
from converter import convert

CXMLXSD = xmlschema.XMLSchema("cxml.1.3.xsd")
DATEFMT = "%Y-%m-%dT%H:%M:%SZ"


def validate(xmlfile):
    """
    Validate an xml file with a given xsd schema definition

    :param str xmlfile: The XML file to validate

    :returns: True if `xmlfile` is a valid xml file based on the
              default CXML XSD definition

    """
    return CXMLXSD.is_valid(xmlfile)


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
    latvalue = latvalue if latunits == 'deg N' else -latvalue

    lonvalue = float(lonelem.text)
    lonunits = lonelem.attrib['units']
    lonvalue = lonvalue if lonunits == 'deg E' else -lonvalue
    lonvalue = np.mod(lonvalue, 360)

    return (lonvalue, latvalue)


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

    hour = int(fix.attrib['hour'])
    validTime = getHeaderTime(fix, 'validTime')
    lon, lat = parsePosition(fix.find('longitude'), fix.find('latitude'))
    mslpelem = fix.find('./cycloneData/minimumPressure/pressure')
    mslp = float(mslpelem.text)
    mslpunits = mslpelem.attrib['units']

    windspeedelem = fix.find('./cycloneData/maximumWind/speed')
    wind = float(windspeedelem.text)
    windunits = windspeedelem.attrib['units']
    windavgper = fix.find('./cycloneData/maximumWind/averagingPeriod').text
    rmax = getRmax(fix)

    print(f"+{hour:02d}: {validTime}, {lat}, {lon}, {mslp}, {wind}, {rmax}")


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
        log.warning(f"Header information does not contain {field}")
        return

    try:
        dt = datetime.strptime(dtstr, DATEFMT)
    except ValueError:
        raise ValueError("Date format does not match required format")
    else:
        return dt


def getHeaderCenter(header):
    """
    Retrieve the production centre from the header information

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

    :returns: xml.etree root

    """

    if not os.path.isfile(xmlfile):
        log.exception(f"{xmlfile} is not a file")
        raise IOError

    log.info(f"Parsing {xmlfile}")

    if validate(xmlfile):
        log.info(f"{xmlfile} is a valid CXML file")
    else:
        log.error(f"{xmlfile} is not a valid CXML file")
        log.error("Check the file contents")
        return None

    tree = ET.parse(xmlfile)
    xroot = tree.getroot()
    data = xroot.findall("./data[@type='forecast']/disturbance")
    log.debug(f"There are {len(data)} disturbances reported in this CXML file")
    for d in data:
        distId, tcId, tcName = parseDisturbance(d)
        log.info(f"Disturbance: {distId} - {tcName} - {tcId}")
        fixes = d.findall("./fix")

        log.debug(f"Disturbance {distId}: number of fixes: {len(fixes)}")
        for f in fixes:
            parseFix(f)
