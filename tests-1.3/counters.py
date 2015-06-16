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

from oftest.testutils import *
from oftest.parse import parse_ipv6
import FuncUtils
import time

@group('TestSuite60')
class FlowReceivedPackets(base_tests.SimpleDataPlane):
    """
    TestCase 60.10: Flow Received Packets

    Verify that the packet_count counter in the Flow-stats reply increments
    in accordance with packets received.
    """
    def runTest(self):
        logging.info("TestCase 60.10: Flow Received Packets")
        in_port, out_port = openflow_ports(2)
        #Clear Switch State
        delete_all_flows(self.controller)

        #add flow
        request, match, _ = FuncUtils.dpctl_cmd_to_msg("flow-mod cmd='add',table=0,prio=15 in_port={} "
                                                       "apply:output={}".format(in_port,out_port))
        self.controller.message_send(request)

        pkg_num = 10
        pkt = str(simple_tcp_packet())
        for i in range(10):
            self.dataplane.send(in_port, pkt)

        verify_flow_stats(self, match, table_id=0, pkts= pkg_num)


@group('TestSuite60')
class FlowReceivedBytes(base_tests.SimpleDataPlane):
    """
    TestCase 60.10: Flow Received Packets

    Verify that the packet_count counter in the Flow-stats reply increments
    in accordance with packets received.
    """
    def runTest(self):
        logging.info("TestCase 60.20: Flow Received Packets")
        in_port, out_port = openflow_ports(2)
        #Clear Switch State
        delete_all_flows(self.controller)

        #add flow
        request, match, _ = FuncUtils.dpctl_cmd_to_msg("flow-mod cmd='add',table=0,prio=15 in_port={} "
                                                       "apply:output={}".format(in_port,out_port))
        self.controller.message_send(request)

        pkg_num = 10
        pkt = str(simple_tcp_packet())
        for i in range(10):
            self.dataplane.send(in_port, pkt)

        verify_flow_stats(self, match, table_id=0, bytes= pkg_num*len(pkt))

@group('TestSuite60')
class DurationSecs(base_tests.SimpleDataPlane):
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

        for i in range(1,10):
            time.sleep(2)
            stats = get_flow_stats(self, match, table_id=0)
            self.assertEqual(len(stats),1, "The num of matched flow entry error")
            self.assertTrue(stats[0].duration_sec<= i*2+1 and stats[0].duration_sec >= i*2-1,
                            "Duration time error")


@group('TestSuite60')
class DurationNSecs(base_tests.SimpleDataPlane):
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

        for i in range(1,10):
            time.sleep(1)
            stats = get_flow_stats(self, match, table_id=0)
            # print(stats[0].duration_nsec)
            self.assertEqual(len(stats),1, "The num of matched flow entry error")
            self.assertTrue(stats[0].duration_nsec<= 10000000, "Duration time error")


@group('TestSuite60')
class DurationNSecs(base_tests.SimpleDataPlane):
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

        for i in range(1,10):
            time.sleep(1)
            stats = get_flow_stats(self, match, table_id=0)
            # print(stats[0].duration_nsec)
            self.assertEqual(len(stats),1, "The num of matched flow entry error")
            self.assertTrue(stats[0].duration_nsec<= 10000000, "Duration time error")