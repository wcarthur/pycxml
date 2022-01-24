import numpy as np
import unittest
from datetime import datetime, timedelta
import pycxml
import pandas as pd
from pandas.testing import assert_series_equal
import xml.etree.ElementTree as ET

"""
With most of these tests, we do *not* test malformed XML elements, as they
should be captured by the validation steps.
"""


class TestIsEnsemble(unittest.TestCase):
    def setUp(self):
        self.ensembleMember = ET.fromstring(
            """<?xml version="1.0"?>
            <header>
                <generatingApplication>
                    <ensemble>
                        <numMembers>1000</numMembers>
                        <perturbationMethod>DeMaria Method</perturbationMethod>
                    </ensemble>
                </generatingApplication>
                <baseTime>2007-07-25T12:00:00Z</baseTime>
                <creationTime>2007-07-25T15:42:00</creationTime>
            </header>"""
        )

        self.ensembleElem = ET.fromstring(
            """<?xml version="1.0"?>
            <ensemble>
                <numMembers>1000</numMembers>
                <perturbationMethod>DeMaria Method</perturbationMethod>
            </ensemble>"""
        )

        self.nonEnsemble = ET.fromstring(
            """
            <header>
                <product>Cyclone Analysis</product>
                <generatingApplication>
                    <applicationType>Radar hurricane analysis</applicationType>
                </generatingApplication>
                <productionCenter>
                    NWS
                    <subCenter>National Hurricane Center</subCenter>
                </productionCenter>
                <baseTime>2007-07-25T12:00:00Z</baseTime>
                <creationTime>2007-07-25T15:42:00</creationTime>
            </header>"""
        )

    def testIsEnsemble(self):
        self.assertTrue(pycxml.pycxml.isEnsemble(self.ensembleMember))
        self.assertFalse(pycxml.pycxml.isEnsemble(self.nonEnsemble))

    def testGetEnsembleMemberCount(self):
        self.assertEqual(pycxml.pycxml.ensembleCount(self.ensembleElem), 1000)


class TestGetWindData(unittest.TestCase):
    def setUp(self):
        self.testVals = [100, 100, 50]
        self.testUnits = ["kt", "km/h", "m/s"]
        self.testwindelems = [
            ET.fromstring(
                f"""<?xml version="1.0"?>
            <fix>
                <cycloneData>
                    <maximumWind>
                        <speed precision="0.01" units="{u}">{v}</speed>
                    </maximumWind>
                </cycloneData>
            </fix>"""
            )
            for u, v in zip(self.testUnits, self.testVals)
        ]
        self.results = [185.2, 100, 180]

        self.missingElem = ET.fromstring(
            """<?xml version="1.0"?>
            <fix>
                <cycloneData>
                    <minimumPressure>
                        <pressure precision="0.01" units="{u}">{v}</pressure>
                    </minimumPressure>
                </cycloneData>
            </fix>"""
        )

    def testValidWind(self):
        for inelem, out in zip(self.testwindelems, self.results):
            self.assertAlmostEqual(pycxml.pycxml.getWindSpeed(inelem), out)

    def testMissingElem(self):
        self.assertIsNone(pycxml.pycxml.getWindSpeed(self.missingElem))


class TestGetMSLPData(unittest.TestCase):
    def setUp(self):
        self.testVals = [990, 1005, 99000]
        self.testUnits = ["mb", "hPa", "Pa"]
        self.testmslpelems = [
            ET.fromstring(
                f"""<?xml version="1.0"?>
            <fix>
                <cycloneData>
                    <minimumPressure>
                        <pressure precision="0.01" units="{u}">{v}</pressure>
                    </minimumPressure>
                </cycloneData>
            </fix>"""
            )
            for u, v in zip(self.testUnits, self.testVals)
        ]
        self.results = [990, 1005, 990]
        self.missingElem = ET.fromstring(
            """<?xml version="1.0"?>
            <fix>
                <cycloneData>
                    <maximumWind>
                        <speed precision="0.01" units="{u}">{v}</speed>
                    </maximumWind>
                </cycloneData>
            </fix>"""
        )

    def testValidMslp(self):
        for inelem, out in zip(self.testmslpelems, self.results):
            self.assertAlmostEqual(pycxml.pycxml.getMSLP(inelem), out)

    def testMissingElem(self):
        self.assertIsNone(pycxml.pycxml.getMSLP(self.missingElem))


class TestGetPoci(unittest.TestCase):
    def setUp(self):
        testVals = [1000, 1001, 1005, 100500]
        testUnits = ["hPa", "hPa", "mb", "Pa"]

        self.testxmlpocielems = [
            ET.fromstring(
                f"""<?xml version="1.0"?>
            <fix>
                <cycloneData>
                    <lastClosedIsobar>
                        <pressure units="{u}">{v}</pressure>"
                    </lastClosedIsobar>
                </cycloneData>
            </fix>"""
            )
            for v, u in zip(testVals, testUnits)
        ]
        self.results = [1000, 1001, 1005, 1005]

        self.missingpocielem = ET.fromstring(
            f"""<?xml version="1.0"?>
        <fix><cycloneData><maximumWind><rmw units="km">100</rmw>
            </maximumWind></cycloneData></fix>"""
        )

    def testGetPOCI(self):
        for inelem, out in zip(self.testxmlpocielems, self.results):
            self.assertAlmostEqual(pycxml.pycxml.getPoci(inelem), out)

    def testMissingData(self):
        assert 1013.25 == pycxml.pycxml.getPoci(self.missingpocielem)


class TestGetRadiusMaxWind(unittest.TestCase):
    def setUp(self):
        testVals = [15, 25, 40, 100]
        testUnits = ["km", "nm", "km", "mi"]

        self.testxmlradelems = [
            ET.fromstring(
                f"""<?xml version="1.0"?>
            <fix>
                <cycloneData>
                    <maximumWind>
                        <radius units="{u}">{v}</radius>
                    </maximumWind>
                </cycloneData>
            </fix>"""
            )
            for v, u in zip(testVals, testUnits)
        ]
        self.results = [15, 46.3, 40, 160.934]

        self.missingradelem = ET.fromstring(
            f"""<?xml version="1.0"?>
        <fix><cycloneData><maximumWind><speed units="km/h">100</speed>
            </maximumWind></cycloneData></fix>"""
        )

    def testGetRadiusMaxWind(self):
        for inelem, out in zip(self.testxmlradelems, self.results):
            self.assertAlmostEqual(pycxml.pycxml.getRmax(inelem), out)

    def testMissingData(self):
        self.assertIsNone(pycxml.pycxml.getRmax(self.missingradelem))


class TestWindContours(unittest.TestCase):
    def setUp(self):
        self.testxmlwindcontour = ET.fromstring(
            f"""<?xml version="1.0"?>
            <fix>
            <cycloneData>
            <windContours>
                <windSpeed units="kt">
                    34.0
                    <radius units="nm" sector="NEQ">70.0</radius>
                    <radius units="nm" sector="SEQ">70.0</radius>
                    <radius units="nm" sector="SWQ">60.0</radius>
                    <radius units="nm" sector="NWQ">50.0</radius>
                </windSpeed>
                <windSpeed units="kt">
                    48.0
                    <radius units="nm" sector="NEQ">20.0</radius>
                    <radius units="nm" sector="SEQ">20.0</radius>
                </windSpeed>
            </windContours>
            </cycloneData>
            </fix>"""
        )
        windradii = {
            "R34avg": 62.5,
            "R34NEQ": 70.0,
            "R34SEQ": 70.0,
            "R34SWQ": 60.0,
            "R34NWQ": 50.0,
            "R48NEQ": 20.0,
            "R48SEQ": 20,
        }
        self.windradii = pd.Series(
            windradii, index=pycxml.pycxml.RADII_COLUMNS, dtype=object
        )

    def testwindcontours(self):
        assert_series_equal(
            pycxml.pycxml.getWindContours(
                self.testxmlwindcontour), self.windradii
        )


class TestGetHeadertime(unittest.TestCase):
    def setUp(self):
        self.testxmlheadertime = ET.fromstring(
            """<?xml version="1.0"?>
        <header>
            <baseTime>2021-01-01T00:00:00Z</baseTime>
            <creationTime>2021-01-03T19:13:16Z</creationTime>
        </header>"""
        )

        self.testxmlheadertimefmt = ET.fromstring(
            """<?xml version="1.0"?>
        <header>
            <baseTime>2021-01-01 00:00:00</baseTime>
            <creationTime>2021-01-01 00:00:00</creationTime>
        </header>"""
        )

        self.testxmlheadernobase = ET.fromstring(
            """<?xml version="1.0"?>
        <header>
            <creationTime>2021-01-03T19:13:16Z</creationTime>
        </header>"""
        )

    def testGetBaseTime(self):
        testbt = pycxml.pycxml.getHeaderTime(
            self.testxmlheadertime, "baseTime")
        resultbt = datetime(2021, 1, 1, 0, 0)

        self.assertAlmostEqual(testbt, resultbt, delta=timedelta(seconds=1))

    def testNoBaseTimeElement(self):
        rc = pycxml.pycxml.getHeaderTime(self.testxmlheadernobase, "baseTime")
        self.assertEqual(None, rc)

    def testBaseTimeFormat(self):
        self.assertRaises(
            ValueError,
            pycxml.pycxml.getHeaderTime,
            self.testxmlheadertimefmt,
            "baseTime",
        )

    def testGetCreationTime(self):
        testct = pycxml.pycxml.getHeaderTime(
            self.testxmlheadertime, "creationTime")
        resultct = datetime(2021, 1, 3, 19, 13, 16)

        self.assertAlmostEqual(testct, resultct, delta=timedelta(seconds=1))

    def testCreationTimeFormat(self):
        self.assertRaises(
            ValueError,
            pycxml.pycxml.getHeaderTime,
            self.testxmlheadertimefmt,
            "creationTime",
        )

    def testMissingElem(self):
        self.assertIsNone(
            pycxml.pycxml.getHeaderTime(self.testxmlheadertime, "createTime")
        )


class TestParsePosition(unittest.TestCase):
    def setUp(self):
        testLats = [15.5, 20.5, -17, 17]
        testLatUnits = ["deg N", "deg S", "deg N", "deg N"]
        testLons = [175.6, 180, 185, 185]
        testLonUnits = ["deg W", "deg E", "deg E", "deg W"]

        self.testxmllatelems = [
            ET.fromstring(
                f"""<?xml version="1.0"?>
        <latitude units="{latu}">{latv}</latitude>
        """
            )
            for (latv, latu) in zip(testLats, testLatUnits)
        ]

        self.testxmllonelems = [
            ET.fromstring(
                f"""<?xml version="1.0"?>
        <longitude units="{lonu}">{lonv}</longitude>
        """
            )
            for (lonv, lonu) in zip(testLons, testLonUnits)
        ]

    def test_parsePositionTranslateDegW(self):
        self.assertEqual(
            pycxml.pycxml.parsePosition(
                self.testxmllonelems[0], self.testxmllatelems[0]
            ),
            (184.4, 15.5),
        )

    def test_parsePositionTranslateDegS(self):
        self.assertEqual(
            pycxml.pycxml.parsePosition(
                self.testxmllonelems[1], self.testxmllatelems[1]
            ),
            (180, -20.5),
        )

    def test_parsePosition(self):
        self.assertEqual(
            pycxml.pycxml.parsePosition(
                self.testxmllonelems[2], self.testxmllatelems[2]
            ),
            (185, -17),
        )

    def test_parsePositionTranslateDegNW(self):
        self.assertEqual(
            pycxml.pycxml.parsePosition(
                self.testxmllonelems[3], self.testxmllatelems[3]
            ),
            (175, 17),
        )


class TestLoadfile(unittest.TestCase):
    def setUp(self):
        pass

    def test_missingfile(self):
        self.assertRaises(IOError, pycxml.pycxml.loadfile, "badxml.xml")


class TestGetHeaderCenter(unittest.TestCase):
    def setUp(self):
        self.testxmlheadercentre = ET.fromstring(
            """<?xml version="1.0"?>
        <header>
            <productionCenter>TEST CENTER</productionCenter>
        </header>"""
        )

        self.testxmlheadersubcentre = ET.fromstring(
            """<?xml version="1.0"?>
        <header>
            <productionCenter>TEST CENTER<subCenter>TCWC</subCenter>
            </productionCenter>
        </header>"""
        )

    def testGetCentre(self):
        result = pycxml.pycxml.getHeaderCenter(self.testxmlheadercentre)
        self.assertEqual(result, "TEST CENTER")

    def testSubCenter(self):
        result = pycxml.pycxml.getHeaderCenter(self.testxmlheadersubcentre)
        self.assertEqual(result, "TEST CENTER - TCWC")


class TestEstimateMslp(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame()
        self.df["windspeed"] = np.array([72, 121])
        self.df["latitude"] = np.array([-10, -20])
        self.df["translation_speed"] = np.array([5, 20])
        self.df["R34avg"] = np.array([25, 40])
        self.df["poci"] = np.array([1013, 1013])

    def test_mslp(self):
        mslp = pycxml.pycxml.estimate_mslp(self.df)
        assert np.allclose(np.array([1004.35429, 983.4766]), mslp)


if __name__ == "__main__":
    unittest.main()
