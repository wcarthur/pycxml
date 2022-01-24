import os
import unittest
import pycxml
import xml.etree.ElementTree as ET


class TestValidation(unittest.TestCase):
    def setUp(self):
        # The basic example CXML file from BoM is actually invalid!
        self.xml_file = "./tests/test_data/CXML_example.xml"
        self.missing_file = "CXML_example.xml"

    def test_validate(self):
        self.assertFalse(pycxml.validate(self.xml_file))

    def test_missingfile(self):
        self.assertRaises(IOError, pycxml.validate, self.missing_file)


if __name__ == "__main__":
    unittest.main()
