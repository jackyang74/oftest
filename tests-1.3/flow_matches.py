"""These tests fall under Conformance Test-Suite (OF-SWITCH-1.0.1 TestCases).
    Refer Documentation -- Detailed testing methodology 
    <Some of test-cases are directly taken from oftest>
"""

"Test Suite 50 --> Flow Matching"


import logging

import unittest
import random

from oftest import config
import oftest.controller as controller
import ofp
import oftest.dataplane as dataplane
import oftest.parse as parse
import oftest.base_tests as base_tests
import time

import oftest.testutils as testutils
import time
import FuncUtils



class AllWildcardMatch(base_tests.SimpleDataPlane):

    """
        Test Numbber 50.10
        Verify for an all wildcarded flow all the injected packets would match that flow
    """

    def runTest(self):
        logging.info("50.10 --> Running All Wildcard Match test")

        of_ports = config["port_map"].keys()
        of_ports.sort()
        self.assertTrue(len(of_ports) > 1, "Not enough ports for test")

        #Clear Switch State
        testutils.delete_all_flows(self.controller)

        logging.info("Inserting an all wildcarded flow and sending packets with various match fields")
        logging.info("Expecting all sent packets to match")

        in_port = of_ports[0]
        egress_port = of_ports[1]

        #Insert an All Wildcarded flow.
        FuncUtils.wildcard_all(self,of_ports)

        #check for different  match fields and verify packet implements the action specified in the flow
        pkt1 = str(testutils.simple_tcp_packet(eth_src="00:01:01:01:01:01"))
        self.dataplane.send(in_port, pkt1)
        testutils.verify_packets(self, pkt1, [egress_port])

        # pkt2 = str(testutils.simple_tcp_packet(eth_dst="00:01:01:01:01:01"))
        # self.dataplane.send(in_port, pkt2)
        # verify_packets(self, pkt2, [egress_port])
        #
        # pkt3 = str(testutils.simple_tcp_packet(ip_src="192.168.2.1"))
        # self.dataplane.send(in_port, pkt3)
        # verify_packets(self, pkt3, [egress_port])
        #
        # pkt4 = str(testutils.simple_tcp_packet(ip_dst="192.168.2.2"))
        # self.dataplane.send(in_port, pkt4)
        # verify_packets(self, pkt4, [egress_port])
        #
        # pkt5 = str(testutils.simple_tcp_packet(ip_tos=2))
        # self.dataplane.send(in_port, pkt5)
        # verify_packets(self, pkt5, [egress_port])
        #
        # pkt6 = str(testutils.simple_tcp_packet(tcp_sport=8080))
        # self.dataplane.send(in_port, pkt6)
        # verify_packets(self, pkt6, [egress_port])
        #
        # pkt7 = str(testutils.simple_tcp_packet(tcp_dport=8081))
        # self.dataplane.send(in_port, pkt7)
        # verify_packets(self, pkt7, [egress_port])
