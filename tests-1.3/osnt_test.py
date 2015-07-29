"""
    OSNT was integrated into OFTest. We use OSNT to get bandwidth and delay data.
"""
import logging

from oftest import config
import oftest.base_tests as base_tests
import ofp

from oftest.testutils import *



@group('optional')
class BandWidthTest(base_tests.SimpleDataPlane):
    """
    """

    def runTest(self):
        pass

@group('optional')
class DelayTest(base_tests.SimpleDataPlane):
    """
    """

    def runTest(self):
        pas
        s