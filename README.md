# pycxml - A Python interface to Cyclone XML

CycloneXML ("CXML") is an XML data model used to exchange tropical cyclone
related analysis and forecast information. Currently the Australian Bureau of
Meteorology is responsible for maintenance and improvements to CXML. 

This package is a python interface to the data model, to validate, read, and
write CXML data. Currently based on CXML version 1.3.

For more information:

Cyclone XML page: http://www.bom.gov.au/cyclone/cxmlinfo/index.shtml

CXML Specification document:
http://www.bom.gov.au/cyclone/cxmlinfo/CXMLspecification1.3.pdf

CXML XML Schema Definition: http://www.bom.gov.au/cyclone/cxmlinfo/cxml.1.3.xsd

## Installation

Clone the repo, `cd` into the top directory and run:

    pip install .

To check that the installation has worked correctly run the tests:

    pytest tests

## Dependencies

This package requires:

- `numpy`
- `pandas
- `lxml`

The tests additionally require `pycodestyle`. All of these will 
be automatically downloaded and installed in the installation step.

## Usage

CXML supports three data types: `forecast`, `ensembleForecast` and `analysis`.

Ensemble forecasts (`ensembleForecast`) are an extension of the `forecast`
datatype, in that there are multiple members for each forecast.

### Reading a CXML file

To read a CXML file, use the `pycxml.loadfile` function. Data are returned as a
`pandas.DataFrame`

>>> import pycxml
>>> pycxml.loadfile('./test_data/CXML_example.xml')



## Examples of CXML data

The Cyclone XML site contains some basic examples of CXML data. Additional
(operational) data can be accessed via the UCAR Research Data Archive, dataset
[ds330.3](https://rda.ucar.edu/datasets/ds330.3/index.html). 

## Contact information

Author: Craig Arthur
Email: craig.arthur@ga.gov.au

Last updated: 2021-11-09