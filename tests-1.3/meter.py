import logging

from oftest import config
import oftest.base_tests as base_tests
import ofp
from loxi.pp import pp

from oftest.testutils import *
from oftest.parse import parse_ipv6
import FuncUtils
import time


@group("standard")
class MeterFeatureStatsRequst(base_tests.SimpleDataPlane):
    """
    """

    def runTest(self):
        delete_all_flows(self.controller)
        # config
        in_port, out_port = openflow_ports(2)
        request = ofp.message.meter_features_stats_request()
        response, _ = self.controller.transact(request)

        print(response.show())


@group("standard")
class MeterStatsRequest(base_tests.SimpleDataPlane):
    """
    """

    def runTest(self):
        pass

@group("standard")
class MeterBand(base_tests.SimpleDataPlane):
    """
    """

    def runTest(self):
        pass

