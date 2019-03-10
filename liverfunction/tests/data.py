"""
Definition of data and files for the tests.
The files are located in the data directory.
"""
import os
from os.path import join as pjoin

test_dir = os.path.dirname(os.path.abspath(__file__))  # directory of test files
data_dir = pjoin(test_dir, 'data')  # directory of data for tests


################################################################
# acetaminophen
################################################################
# ExternalModelDefinitions
APAP_SBML = pjoin(data_dir, 'apap_body_3_flat.xml')
