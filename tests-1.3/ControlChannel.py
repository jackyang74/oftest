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


@group('standard')
class StartupBahavior(base_tests.SimpleDataPlane):
    """
    Verify the startup mode, verify no packets are forwarded

    Derived from Test case 10.10: Startup behavior with established control channel
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

    Derived from Test case 10.20: Configure and establish control channel
    """

    def runTest(self):
        pass


@group('standard')
class HelloVersionAnnouncement(base_tests.SimpleProtocol):
    """
    Check the Switch reports the correct version to the controller

    Derived from Test case 10.30 Supported version announcement
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

    Derived from Test case 10.40: Supported version negotiation
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

    Derived from Test case 10.50: No common version negotiated
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


