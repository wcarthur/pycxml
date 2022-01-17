import unittest
from numpy import array, arange, pi
import NumpyTestCase
from pycxml.converter import convert


class TestConvert(NumpyTestCase.NumpyTestCase):
    lat = array(arange(0, -21, -1, 'd'))

    f = array([0.00000000e+00,  -2.53834962e-06,  -5.07592604e-06,
               -7.61195628e-06,  -1.01456678e-05,  -1.26762889e-05,
               -1.52030487e-05,  -1.77251775e-05,  -2.02419070e-05,
               -2.27524707e-05,  -2.52561037e-05,  -2.77520434e-05,
               -3.02395297e-05,  -3.27178046e-05,  -3.51861134e-05,
               -3.76437042e-05,  -4.00898283e-05,  -4.25237407e-05,
               -4.49447000e-05,  -4.73519686e-05,  -4.97448134e-05])

    def test_mps2kmphr(self):
        """Convert from m/s to km/h"""
        self.assertEqual(convert(0, "mps", "kph"), 0.)
        self.assertEqual(convert(1, "mps", "kph"), 3.6)
        self.assertEqual(convert(5, "mps", "kph"), 18.)
        self.assertEqual(convert(15, "mps", "kph"), 54.)
        self.assertEqual(convert(100, "mps", "kph"), 360.)
        self.assertEqual(convert(0, "m/s", "kmh"), 0.)
        self.assertEqual(convert(1, "m/s", "kmh"), 3.6)
        self.assertEqual(convert(5, "m/s", "km/h"), 18.)
        self.assertEqual(convert(15, "m s-1", "km/h"), 54.)
        self.assertEqual(convert(100, "m s-1", "km/h"), 360.)

    def test_kmh2mps(self):
        """Convert from km/h to m/s"""
        self.assertAlmostEqual(convert(3.6, "kph", "m/s"), 1.0, 3)
        self.assertAlmostEqual(convert(36., "km/h", 'm/s'), 10., 3)
        self.assertAlmostEqual(convert(36., "kmh", 'm/s'), 10., 3)
        self.assertAlmostEqual(convert(36., "kmh", 'mps'), 10., 3)
        self.assertAlmostEqual(convert(36., "kmh", 'm s-1'), 10., 3)

    def test_knots2kmh(self):
        """Convert from knots to km/h"""
        self.assertAlmostEqual(convert(1, "kts", "km/h"), 1.852, 5)
        self.assertAlmostEqual(convert(1, "kn", "km/h"), 1.852, 5)
        self.assertAlmostEqual(convert(1, "kt", "km/h"), 1.852, 5)

    def test_kmh2knots(self):
        """Convert from kmh to knots"""
        self.assertAlmostEqual(convert(1.852, "kmh", "kts"), 1., 5)
        self.assertAlmostEqual(convert(18.52, "km/h", "kt"), 10., 5)
        self.assertAlmostEqual(convert(18.52, "km/h", "kn"), 10., 5)

    def test_km2deg(self):
        """Convert distance in km to distance in degrees"""
        self.assertEqual(convert(0, "km", "deg"), 0)
        self.assertAlmostEqual(convert(1, "km", "deg"), 360/(2*pi*6367), 3)
        self.assertAlmostEqual(convert(2, "km", "deg"), 720/(2*pi*6367), 3)
        self.assertAlmostEqual(convert(10, "km", "deg"), 3600/(2*pi*6367), 3)

    def test_deg2km(self):
        """Convert distance in degrees to distance in km"""
        self.assertEqual(convert(0, "deg", "km"), 0)
        self.assertAlmostEqual(convert(1, "deg", "km"),
                               (1/(360/(2*pi*6367))), 3)
        self.assertAlmostEqual(convert(2, "deg", "km"),
                               (2/(360/(2*pi*6367))), 3)
        self.assertAlmostEqual(convert(10, "deg", "km"),
                               (10/(360/(2*pi*6367))), 3)

    def test_km2m(self):
        """Convert distance in km to distance in m"""
        self.assertEqual(convert(0, "km", "m"), 0)
        self.assertAlmostEqual(convert(1, "km", "m"), 1000)

    def test_m2km(self):
        """Convert distance in m to distance in km"""
        self.assertEqual(convert(0, "m", "km"), 0)
        self.assertAlmostEqual(convert(1000., "m", "km"), 1.)
        self.assertAlmostEqual(convert(10000., "m", "km"), 10.)

    def test_m2nm(self):
        self.assertEqual(convert(0, "m", "nm"), 0)
        self.assertAlmostEqual(convert(1000., "m", "nm"), 0.539957)

    def test_hPa2Pa(self):
        """Convert pressure from hPa to Pa"""
        self.assertEqual(convert(0, "hPa", "Pa"), 0.0)
        self.assertEqual(convert(1, "hPa", "Pa"), 100.0)
        self.assertEqual(convert(10, "hPa", "Pa"), 1000.0)
        self.assertEqual(convert(15, "hPa", "Pa"), 1500.0)
        self.assertEqual(convert(600, "hPa", "Pa"), 60000.0)

    def test_kgmetre2hPa(self):
        """Convert from Pa to hPa"""
        self.assertEqual(convert(0, "Pa", "hPa"), 0.0)
        self.assertEqual(convert(1, "Pa", "hPa"), 0.01)
        self.assertEqual(convert(100, "Pa", "hPa"), 1.0)
        self.assertEqual(convert(200, "Pa", "hPa"), 2.0)
        self.assertEqual(convert(600, "Pa", "hPa"), 6.0)

    def test_celcius2F(self):
        """Convert temperatures in Celcius to Farenheit"""
        self.assertEqual(convert(0, "C", "F"), 32.0)
        self.assertAlmostEqual(convert(37.78, "C", "F"), 100, 2)
        self.assertAlmostEqual(convert(-40, "C", "F"), -40, 2)

    def test_farenheit2C(self):
        """Convert temperatures in Farenheit to Celcius"""
        self.assertEqual(convert(32, "F", "C"), 0.0)
        self.assertAlmostEqual(convert(100, "F", "C"), 37.78, 2)
        self.assertAlmostEqual(convert(-40, "F", "C"), -40, 2)


if __name__ == "__main__":
    unittest.main()
