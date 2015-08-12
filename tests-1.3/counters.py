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


@group('optional')
class FlowReceivedPackets(base_tests.SimpleDataPlane):
    """
    Verify that the packet_count counter in the Flow-stats reply increments
    in accordance with packets received.
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        # add flow
        request = FuncUtils.flow_entry_install(self.controller,
                                               "flow_add",
                                               match=ofp.match([ofp.oxm.in_port(in_port)]),
                                               instructions=[
                                                   ofp.instruction.apply_actions([ofp.action.output(out_port)])],
                                               )
        # test
        pkt_num = 10
        pkt = str(simple_tcp_packet())
        for i in range(10):
            self.dataplane.send(in_port, pkt)

        verify_flow_stats(self, request.match, table_id=0, pkts=pkt_num)


@group('optional')
class FlowReceivedBytes(base_tests.SimpleDataPlane):
    """ 
    Verify that the byte_count counter in the Flow-stats reply increments in
    accordance with packets received.
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        # add flow
        request = FuncUtils.flow_entry_install(self.controller,
                                               "flow_add",
                                               match=ofp.match([ofp.oxm.in_port(in_port)]),
                                               instructions=[
                                                   ofp.instruction.apply_actions([ofp.action.output(out_port)])],
                                               )
        # test
        pkt_num = 10
        pkt = str(simple_tcp_packet())
        for i in range(10):
            self.dataplane.send(in_port, pkt)

        verify_flow_stats(self, request.match, table_id=0, bytes=pkt_num * len(pkt))


@group('standard')
class FlowDurationSecs(base_tests.SimpleDataPlane):
    """
    Verify that the duration_sec counter in the Flow_stats reply increments
    in accordance with the time the flow has been alive
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)
        # add flow
        request = FuncUtils.flow_entry_install(self.controller,
                                               "flow_add",
                                               match=ofp.match([ofp.oxm.in_port(in_port)]),
                                               instructions=[
                                                   ofp.instruction.apply_actions([ofp.action.output(out_port)])])
        # test
        for i in range(1, 10):
            time.sleep(2)
            stats = get_flow_stats(self, request.match, table_id=0)
            self.assertEqual(len(stats), 1, "The num of matched flow entry error")
            self.assertTrue(stats[0].duration_sec <= i * 2 + 1 and stats[0].duration_sec >= i * 2 - 1,
                            "Duration time error")


@group('optional')
class FlowDurationNSecs(base_tests.SimpleDataPlane):
    """
    Verify that the duration_nsec counter in the Flow_stats reply increments
    in accordance with the time the flow has been alive
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)
        # add flow
        request = FuncUtils.flow_entry_install(self.controller,
                                               "flow_add",
                                               match=ofp.match([ofp.oxm.in_port(in_port)]),
                                               instructions=[
                                                   ofp.instruction.apply_actions([ofp.action.output(out_port)])])
        # test
        for i in range(1, 10):
            time.sleep(1)
            stats = get_flow_stats(self, request.match, table_id=0)
            self.assertEqual(len(stats), 1, "The num of matched flow entry error")
            # Deviation is less than 0.1 sec
            self.assertLess(abs(1000000000 * i - stats[0].duration_nsec - stats[0].duration_sec * 1000000000),
                            100000000, "Duration time error")


@group('standard')
class PortReceivedPackets(base_tests.SimpleDataPlane):
    """
    Verify that the rx_packets counter in the Port_Stats reply increments in
    accordance with the packets received
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)
        # add flow
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])]
                                     )
        # test
        pkt_num = 10
        pkt = str(simple_tcp_packet())
        for i in range(10):
            self.dataplane.send(in_port, pkt)

        verify_port_stats(self, in_port, rx_pkts=pkt_num)


@group('standard')
class PortTransmittedPackets(base_tests.SimpleDataPlane):
    """
    Verify that the tx_packets counter in the Port_Stats reply increments in
    accordance with the packets transmitted
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)
        # add flow
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])]
                                     )
        # test
        pkt_num = 10
        pkt = str(simple_tcp_packet())
        for i in range(10):
            self.dataplane.send(in_port, pkt)

        verify_port_stats(self, out_port, tx_pkts=pkt_num)


@group('optional')
class PortReceivedBytes(base_tests.SimpleDataPlane):
    """
    Verify that the rx_bytes counter in the Port_Stats reply increments in
    accordance with the bytes received
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)
        # add flow
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])]
                                     )
        # test
        pkt_num = 10
        pkt = str(simple_tcp_packet())
        for i in range(pkt_num):
            self.dataplane.send(in_port, pkt)

        verify_port_stats(self, in_port, rx_bytes=pkt_num * len(pkt))


@group('optional')
class PortTransmittedBytes(base_tests.SimpleDataPlane):
    """
    Verify that the tx_bytes counter in the Port_Stats reply increments in
    accordance with the packets transmitted
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)
        # add flow
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])]
                                     )
        # test
        pkt_num = 10
        pkt = str(simple_tcp_packet())
        for i in range(pkt_num):
            self.dataplane.send(in_port, pkt)

        verify_port_stats(self, out_port, tx_bytes=pkt_num * len(pkt))


@group('optional')
class PortReceiveDrops(base_tests.SimpleDataPlane):
    """
    Verify that the rx_dropped counter in the Port_Stats reply increments in
    accordance with the packets dropped
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        # add flow
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])]
                                     )
        stat = get_port_stats(self, in_port)[0]
        self.assertTrue(stat.rx_dropped is not None, "No rx_dropped field")

        # TODO:OSNT to trigger dropped action


@group('optional')
class PortTransmitDrops(base_tests.SimpleDataPlane):
    """
    Verify that the tx_dropped counter in the Port_Stats reply increments in
    accordance with the packets dropped
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        # add flow
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])]
                                     )
        stat = get_port_stats(self, in_port)[0]
        self.assertTrue(stat.rx_dropped is not None, "No rx_dropped field")

        # TODO:OSNT to trigger dropped action


@group('standard')
class QueueTransmitPackets(base_tests.SimpleDataPlane):
    """
    Verify that the tx_packets counter in the Queue_Stats reply increments
    in accordance with packets transmitted from the queue.
    """

    # TODO:OSNT to trigger dropped action
    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        # add flow
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])]
                                     )
        stat = get_port_stats(self, in_port)[0]
        self.assertTrue(stat.rx_dropped is not None, "No rx_dropped field")


@group('standard')
class ActiveEntries(base_tests.SimpleDataPlane):
    """

    """

    def runTest(self):
        logging.info("")
        flow_stats = get_flow_stats(self, ofp.match())
        in_port, out_port = openflow_ports(2)
        # Clear Switch State
        delete_all_flows(self.controller)

        flow_entry_num = 10
        table_num = 5
        for i in range(table_num):
            for j in range(flow_entry_num):
                FuncUtils.flow_entry_install(self.controller,
                                             "flow_add",
                                             table_id=i,
                                             match=ofp.match([ofp.oxm.in_port(in_port)]),
                                             instructions=[
                                                 ofp.instruction.apply_actions([ofp.action.output(out_port)])],
                                             prio=j
                                             )
        # test
        request = ofp.message.table_stats_request()
        (reply, pkt) = self.controller.transact(request)

        active_entry = 0
        for obj in reply.entries:
            active_entry += obj.active_count
        self.assertEqual(flow_entry_num * table_num, active_entry, "Active entry error")


@group('standard')
class MeterDurationSecs(base_tests.SimpleDataPlane):
    """
    Verify that the duration_sec counter in the Flow_stats reply increments
    in accordance with the time the flow has been alive
    """
    # TODO you need to complete

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)
        # add flow
        request = FuncUtils.flow_entry_install(self.controller,
                                               "flow_add",
                                               match=ofp.match([ofp.oxm.in_port(in_port)]),
                                               instructions=[
                                                   ofp.instruction.apply_actions([ofp.action.output(out_port)])])
        # test
        for i in range(1, 10):
            time.sleep(2)
            stats = get_flow_stats(self, request.match, table_id=0)
            self.assertEqual(len(stats), 1, "The num of matched flow entry error")
            self.assertTrue(stats[0].duration_sec <= i * 2 + 1 and stats[0].duration_sec >= i * 2 - 1,
                            "Duration time error")
