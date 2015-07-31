"""
    OSNT was integrated into OFTest. We use OSNT to get bandwidth and delay data.
"""
import logging

from oftest import config
import oftest.base_tests as base_tests
import osnt
from osnt.osnt_tester import *
import ofp

from oftest.testutils import *


@group('optional')
class PPSTest(base_tests.SimpleDataPlane):
    """
    """

    def runTest(self):
        tester = OSNT_Tester()
        pass


@group('optional')
class BPSTest(base_tests.SimpleDataPlane):
    """
    """

    def runTest(self):
        pass


@group('optional')
class DelayTest(base_tests.SimpleDataPlane):
    """
    """

    def runTest(self):
        pass
