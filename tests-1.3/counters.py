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

        pkt_num  = 10
        pkt = str(simple_tcp_packet())
        for i in range(10):
            self.dataplane.send(in_port, pkt)

        verify_flow_stats(self, match, table_id=0, pkts= pkt_num )


@group('TestSuite60')
class FlowReceivedBytes(base_tests.SimpleDataPlane):
    """ 
    TestCase 60.10: Flow Received Bytes

    """
    def runTest(self):
        logging.info("TestCase 60.20: Flow Received Bytes")
        in_port, out_port = openflow_ports(2)
        #Clear Switch State
        delete_all_flows(self.controller)

        #add flow
        request, match, _ = FuncUtils.dpctl_cmd_to_msg("flow-mod cmd='add',table=0,prio=15 in_port={} "
                                                       "apply:output={}".format(in_port,out_port))
        self.controller.message_send(request)

        pkt_num  = 10
        pkt = str(simple_tcp_packet())
        for i in range(10):
            self.dataplane.send(in_port, pkt)

        verify_flow_stats(self, match, table_id=0, bytes= pkt_num *len(pkt))

@group('TestSuite60')
class FlowDurationSecs(base_tests.SimpleDataPlane):
    """
    Test case 60.30: Duration (secs)

    """
    def runTest(self):
        logging.info("TestCase 60.30: Flow Duration (secs)")
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
    Test case 60.30: Duration (secs)

    """
    def runTest(self):
        logging.info("TestCase 60.30: Flow Duration (nsecs)")
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
class PortReceivedPackets(base_tests.SimpleDataPlane):
    """
    TestCase 60.50: Received Packets

    """
    def runTest(self):
        logging.info("TestCase 60.50: Port Received Packets")
        in_port, out_port = openflow_ports(2)
        #Clear Switch State
        delete_all_flows(self.controller)

        #add flow
        request, match, _ = FuncUtils.dpctl_cmd_to_msg("flow-mod cmd='add',table=0,prio=15 in_port={} "
                                                       "apply:output={}".format(in_port,out_port))
        self.controller.message_send(request)

        pkt_num  = 10
        pkt = str(simple_tcp_packet())
        for i in range(10):
            self.dataplane.send(in_port, pkt)

        verify_port_stats(self, in_port, rx_pkts = pkt_num )


@group('TestSuite60')
class PortTransmittedPackets(base_tests.SimpleDataPlane):
    """
    Test case 60.60: Transmitted Packets

    """
    def runTest(self):
        logging.info("Test case 60.60: Transmitted Packets")
        in_port, out_port = openflow_ports(2)
        #Clear Switch State
        delete_all_flows(self.controller)

        #add flow
        request, match, _ = FuncUtils.dpctl_cmd_to_msg("flow-mod cmd='add',table=0,prio=15 in_port={} "
                                                       "apply:output={}".format(in_port,out_port))
        self.controller.message_send(request)

        pkt_num  = 10
        pkt = str(simple_tcp_packet())
        for i in range(10):
            self.dataplane.send(in_port, pkt)

        verify_port_stats(self, out_port, tx_pkts = pkt_num )


@group('TestSuite60')
class PortReceivedBytes(base_tests.SimpleDataPlane):
    """
    TestCase 60.70: Port Received bytes

    """
    def runTest(self):
        logging.info("TestCase 60.70: Port Received bytes")
        in_port, out_port = openflow_ports(2)
        #Clear Switch State
        delete_all_flows(self.controller)

        #add flow
        request, match, _ = FuncUtils.dpctl_cmd_to_msg("flow-mod cmd='add',table=0,prio=15 in_port={} "
                                                       "apply:output={}".format(in_port,out_port))
        self.controller.message_send(request)

        pkt_num = 10
        pkt = str(simple_tcp_packet())
        for i in range(pkt_num):
            self.dataplane.send(in_port, pkt)

        verify_port_stats(self, in_port, rx_bytes = pkt_num *len(pkt))


@group('TestSuite60')
class PortReceivedBytes(base_tests.SimpleDataPlane):
    """
    TestCase 60.80: Port Transmitted bytes

    """
    def runTest(self):
        logging.info("TestCase 60.80: Port Transmitted bytes")
        in_port, out_port = openflow_ports(2)
        #Clear Switch State
        delete_all_flows(self.controller)

        #add flow
        request, match, _ = FuncUtils.dpctl_cmd_to_msg("flow-mod cmd='add',table=0,prio=15 in_port={} "
                                                       "apply:output={}".format(in_port,out_port))
        self.controller.message_send(request)

        pkt_num = 10
        pkt = str(simple_tcp_packet())
        for i in range(pkt_num):
            self.dataplane.send(in_port, pkt)

        verify_port_stats(self, out_port, tx_bytes = pkt_num *len(pkt))


@group('TestSuite60')
class PortTransmitDrops(base_tests.SimpleDataPlane):
    """
    TestCase 60.90: Port Transmitted drops

    """
    def runTest(self):
        logging.info("Test case 60.100: Port Receive drops")
        in_port, out_port = openflow_ports(2)
        #Clear Switch State
        delete_all_flows(self.controller)

        #add flow
        request, match, _ = FuncUtils.dpctl_cmd_to_msg("flow-mod cmd='add',table=0,prio=15 in_port={} "
                                                       "apply:output={}".format(in_port,out_port))
        self.controller.message_send(request)


        # TODO:OSNT
        # verify_port_stats(self, out_port, tx_bytes = pkt_num *len(pkt))


@group('TestSuite60')
class CRCErrors(base_tests.SimpleDataPlane):
    """
    TestCase 60.150: CRCErrors

    """
    def runTest(self):
        logging.info("Test case 60.100: Port Receive drops")
        in_port, out_port = openflow_ports(2)

        #Clear Switch State
        delete_all_flows(self.controller)

        # TODO: send CRC error packets


@group('TestSuite60')
class ActiveEntries(base_tests.SimpleDataPlane):
    """
    TestCase 60.200 Active Entries

    """
    def runTest(self):
        logging.info("")
        flow_stats = get_flow_stats(self, ofp.match())
        in_port, out_port = openflow_ports(2)
        #Clear Switch State
        delete_all_flows(self.controller)

        flow_entry_num = 10
        table_num = 5
        for i in range(table_num):
            for j in range(flow_entry_num):
                request,_,_ = FuncUtils.dpctl_cmd_to_msg("flow-mod cmd='add',table={},prio={} "
                                                     "in_port={} apply:output={}".format(i, j, in_port, out_port))
                self.controller.message_send(request)

        request = ofp.message.table_stats_request()
        (reply , pkt) = self.controller.transact(request)

        active_entry = 0
        print(len(reply.entries))
        for obj in reply.entries:
            active_entry += obj.active_count
        self.seertEqual(flow_entry_num*table_num, active_entry, "Active entry error")