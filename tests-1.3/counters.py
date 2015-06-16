"""
Flow match test cases

These tests check the behavior of each match field. The only action used is a
single output.
"""

import logging

from oftest import config
import oftest.base_tests as base_tests
import ofp
import oftest.packet as scapy

import oftest.testutils as testutils
from oftest.parse import parse_ipv6
import FuncUtils


@group('TestSuite60')
class ReceivedPackets(base_tests.SimpleDataPlane):
    """
    TestCase 60.10: Received Packets

    Verify that the packet_count counter in the Flow-stats reply increments
    in accordance with packets received.
    """
    def runTest(self):
        logging.info("TestCase 60.10: Received Packets")
        in_port, out_port = openflow_ports(2)
        #Clear Switch State
        delete_all_flows(self.controller)

        #add flow
        request, match, _ = FuncUtils.dpctl_cmd_to_msg("flow-mod cmd='add',table=0,prio=15 in_port={} "
                                                   "apply:output={}".format(in_port,out_port))
        self.controller.message_send(request)

        stats = get_flow_stats(self, match, table_id=0)
        print(stats.show())


