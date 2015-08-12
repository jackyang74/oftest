# Distributed under the OpenFlow Software License (see LICENSE)
# Copyright (c) 2010 The Board of Trustees of The Leland Stanford Junior University
# Copyright (c) 2012, 2013 Big Switch Networks, Inc.
# Copyright (c) 2012, 2013 CPqD
# Copyright (c) 2012, 2013 Ericsson
"""
Basic test cases

Test cases in other modules depend on this functionality.
"""

import logging

from oftest import config
import oftest.base_tests as base_tests
import ofp
import time
import copy
from oftest.testutils import *
import FuncUtils


@group('standard')
class StartupBahavior(base_tests.SimpleDataPlane):
    """
    Verify the startup mode, verify no packets are forwarded
    """

    def runTest(self):
        ports = openflow_ports(4)
        pkt = str(simple_tcp_packet())

        for in_port in ports:
            self.dataplane.send(in_port, pkt)
            for out_port in ports:
                verify_no_packet(self, pkt, out_port)


@group('standard')
class TCPDefaultPort(base_tests.SimpleDataPlane):
    """
    Test all methods of control channel establishment
    """

    def runTest(self):
        pass


@group('standard')
class HelloVersionAnnouncement(base_tests.SimpleProtocol):
    """
    Check the Switch reports the correct version to the controller
    """

    def runTest(self):
        response, _ = self.controller.poll(ofp.OFPT_HELLO)
        self.assertTrue(response is not None,
                        "No Hello message was received")
        self.assertEqual(response.version, ofp.OFP_VERSION,
                         "Incorrect version 0x{0:x} from HELLO message sent from switch".format(response.version))


@group('standard')
class HelloVersionNegotiation(base_tests.SimpleProtocol):
    """
    Check the Switch negotiates the correct version with the controller
    """

    def runTest(self):
        response, _ = self.controller.poll(ofp.message.hello_failed_error_msg)
        self.assertFalse((response is not None) and (response.code == ofp.OFPHFC_INCOMPATIBLE),
                         "Hello Error was received for the reason Version INCOMPATIBLE")


@group('standard')
class HelloVersionIncompatible(base_tests.SimpleProtocol):
    """
    Verify the switch reports the correct error message and terminates the
    connection when no common version can be negotiated with the controller.
    """

    def runTest(self):
        request = ofp.message.hello()
        # change hello message version to incorrect number
        request.version = 0
        self.controller.message_send(request)

        response, _ = self.controller.poll(ofp.message.hello_failed_error_msg)
        self.assertTrue(response is not None,
                        "No Error message was received")
        self.assertTrue(response.code == ofp.OFPHFC_INCOMPATIBLE,
                        "Hello Error with reason Version INCOMPATIBLE was not received")


class ExistingFlowEntriesStayActive(base_tests.SimpleDataPlane):
    """
    Verify that flows stay active and timeout as configured after control channel re-establishment.
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port1, out_port2 = openflow_ports(3)

        # flow add
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port1)])],
                                     hard_timeout=1,
                                     )
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port2)])],
                                     hard_timeout=100
                                     )
        # tests
        time.sleep(5)
        stats = get_flow_stats(self, ofp.match())
        self.assertEqual(len(stats), 1, "Expected empty flow stats reply")
