import logging

from lxml import etree
from pathlib import Path

LOGGER = logging.getLogger(__name__)

CXML_SCHEMA = str(Path(__file__).parent / 'cxml.1.3.xsd')


class Validator:
    """
    XML file validator using XSD schema
    """

    def __init__(self, xsd_file: str):
        """
        :param str xsd_file: Name of the CXML XSD file
        """
        self.schema = etree.XMLSchema(
            etree.parse(xsd_file)
        )

    def validate(self, xml_filename: str):
        """
        Validate XML file against XSD schema
        :param xml_filename: name of xml file to validate
        :raises AssertionError: on schema validation error
        """

        LOGGER.debug('Validating XML file')

        return self.schema.assert_(
            etree.parse(xml_filename)
        )
