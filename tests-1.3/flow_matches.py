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


@testutils.group('TestSuite50')
class AllWildcardMatch(base_tests.SimpleDataPlane):

    """
        Test Numbber 50.10
        Verify for an all wildcarded flow all the injected packets would match that flow
    """

    def runTest(self):
        logging.info("Test case 50.10: All Wildcards")
        in_port, out_port1, out_port2 = testutils.openflow_ports(3)

        #Clear Switch State
        testutils.delete_all_flows(self.controller)

        # flow add
        request, _, _ = FuncUtils.dpctl_cmd_to_msg("flow-mod cmd='add',table=0,prio=15} "
                                                   "apply:output={}".format(out_port1))

        self.controller.message_send(request)
        testutils.do_barrier(self.controller)

        #check for different  match fields and verify packet implements the action specified in the flow
        pkt1 = str(testutils.simple_tcp_packet(eth_src="00:01:01:01:01:01"))
        self.dataplane.send(in_port, pkt1)
        testutils.verify_packets(self, pkt1, [out_port1])
        testutils.verify_no_packet(self, pkt1, out_port2)


@testutils.group('TestSuite50')
class InPort(base_tests.SimpleDataPlane):
    """
    Match on ingress port
    """
    def runTest(self):
        logging.info("Test case 50.20: Ingress Port")

        testutils.delete_all_flows(self.controller)
        in_port, out_port, bad_port = testutils.openflow_ports(3)

        # flow add
        request, _, _ = FuncUtils.dpctl_cmd_to_msg("flow-mod cmd='add',table=0,prio=15 in_port={}} "
                                                   "apply:output={}".format(in_port,out_port))
        self.controller.message_send(request)

        #flow add to controller
        logging.info("Inserting match-all flow sending packets to controller")
        request = ofp.message.flow_add(
            table_id=0,
            instructions=[
                ofp.instruction.apply_actions(
                    actions=[
                        ofp.action.output(
                            port=ofp.OFPP_CONTROLLER,
                            max_len=ofp.OFPCML_NO_BUFFER)])],
            buffer_id=ofp.OFP_NO_BUFFER,
            priority=1)
        self.controller.message_send(request)
        testutils.do_barrier(self.controller)

        pkt = testutils.simple_tcp_packet()
        pktstr = str(pkt)
        logging.info("Sending packet on matching ingress port, expecting output to port %d", out_port)
        self.dataplane.send(in_port, pktstr)
        testutils.verify_packets(self, pktstr, [out_port])

        logging.info("Sending packet on non-matching ingress port, expecting packet-in")
        self.dataplane.send(bad_port, pktstr)
        testutils.verify_packet_in(self, pktstr, bad_port, ofp.OFPR_ACTION)