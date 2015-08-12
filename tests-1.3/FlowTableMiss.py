import logging

from oftest import config
import oftest.base_tests as base_tests
import ofp
import FuncUtils
from oftest.testutils import *


@group('standard')
class DefaultDrop(base_tests.SimpleDataPlane):
    """
    Verify that the switch drops unmatched packets if no table miss flow entry exists.
    """

    def runTest(self):
        in_port, out_port = openflow_ports(2)
        delete_all_flows(self.controller)

        pkt = str(simple_tcp_packet())
        self.dataplane.send(in_port, pkt)
        verify_no_packet_in(self, pkt, None)
        verify_packets(self, pkt, [in_port, out_port])


@group('standard')
class PacketIn(base_tests.SimpleDataPlane):
    """
    Test packet in function for a table-miss flow. Send a packet to each dataplane port and verify that a packet in message is received from the controller for each
    """

    def runTest(self):
        delete_all_flows(self.controller)

        parsed_pkt = simple_tcp_packet()
        pkt = str(parsed_pkt)

        FuncUtils.flow_entry_install(
            self.controller,
            "flow_add",
            instructions=[
                ofp.instruction.apply_actions(
                    actions=[
                        ofp.action.output(
                            port=ofp.OFPP_CONTROLLER,
                            max_len=ofp.OFPCML_NO_BUFFER)])],
            prio=0)

        for of_port in config["port_map"].keys():
            logging.info("PacketInMiss test, port %d", of_port)
            self.dataplane.send(of_port, pkt)
            verify_packet_in(self, pkt, of_port, ofp.OFPR_NO_MATCH)
            # verify_packets(self, pkt, []) ensures no packets are received from other ports
            verify_packets(self, pkt, [])


@group('standard')
class IdleTimeout(base_tests.SimpleDataPlane):
    """
    Verify flow removed message for timeout is implemented

    Derived from Test case 40.210: Timeout with flow removed message
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        # flow add
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])],
                                     idle_timeout=1,
                                     flags=ofp.OFPFF_SEND_FLOW_REM
                                     )
        # send packet to in_port and verify
        start_time = time.time()
        dura_time = 6
        while True:
            if time.time() - start_time > dura_time:
                break
            pkt = str(simple_tcp_packet())
            self.dataplane.send(in_port, pkt)
        time.sleep(5)

        msg, _ = self.controller.poll(ofp.message.flow_removed)
        self.assertTrue(msg is not None, "Error message was not received")
        self.assertEqual(msg.duration_sec, dura_time + 1, "Time is not correct")


@group('standard')
class HardTimeout(base_tests.SimpleDataPlane):
    """
    Verify flow removed message for timeout is implemented

    Derived from Test case 40.210: Timeout with flow removed message
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        # flow add
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])],
                                     hard_timeout=1,
                                     flags=ofp.OFPFF_SEND_FLOW_REM
                                     )
        # send packet to in_port and verify
        start_time = time.time()
        dura_time = 6
        while True:
            if time.time() - start_time > dura_time:
                break
            pkt = str(simple_tcp_packet())
            self.dataplane.send(in_port, pkt)
        time.sleep(5)

        msg, _ = self.controller.poll(ofp.message.flow_removed)
        self.assertTrue(msg is not None, "Error message was not received")
        self.assertEqual(msg.duration_sec,  1, "Time is not correct")