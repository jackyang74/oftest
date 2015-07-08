"""
Test suite 90 checks async OpenFlow protocol messages and their correct implementation. In
contrast to the basic checks, return values are checked for correctness, and configurations for
functional implementation.
"""

import logging

from oftest import config
import oftest.base_tests as base_tests
import ofp
import time
import FuncUtils
from oftest.testutils import *


class OFPR_NO_MATCH_reason(base_tests.SimpleDataPlane):
    """
    Verify packet_in specifies the right reason (no match or send to controller)

    Derived from Testsuite 90.10 Test case 90.10: OFPR_NO_MATCH uint8_t reason
    """

    def runTest(self):
        delete_all_flows(self.controller)

        # config
        in_port, out_port = openflow_ports(2)
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     instructions=[ofp.instruction.apply_actions(
                                         [ofp.action.output(
                                             port=ofp.OFPP_CONTROLLER,
                                             max_len=ofp.OFPCML_NO_BUFFER
                                         )])])
        # test
        pkt = str(simple_tcp_packet())
        self.dataplane.send(in_port, pkt)
        response, _ = self.controller.poll(ofp.message.packet_in)
        self.assertTrue(response is not None, "No packetin received")
        self.assertEqual(response.reason, ofp.OFPR_NO_MATCH,
                         "Packetin reason field is not NO_MATCH")


class OFPR_NO_MATCH_buffer(base_tests.SimpleDataPlane):
    """
    Verify packet_in OFPR_NO _MATCH implements buffer handling correct

    Derived from Test case 90.20: OFPR_NO_MATCH unit8_t data[0] buffered
    """

    def runTest(self):
        delete_all_flows(self.controller)

        # config
        in_port, out_port = openflow_ports(2)
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     instructions=[ofp.instruction.apply_actions(
                                         [ofp.action.output(
                                             port=ofp.OFPP_CONTROLLER,
                                             max_len=1000
                                         )])])
        # test
        request = ofp.message.get_config_request()
        response, _ = self.controller.transact(request)
        logging.info(response.show() + "num=" + str(response.miss_send_len))

        pkt = str(simple_tcp_packet(pktlen=70, ip_ttl=1))
        self.dataplane.send(in_port, pkt)
        response, _ = self.controller.poll(ofp.message.packet_in)
        self.assertTrue(response is not None, "No packetin received")
        logging.info(response.show())
        logging.info(len(response.data))

        self.assertEqual(response.reason, ofp.OFPR_NO_MATCH,
                         "Packetin reason field is not NO_MATCH")
        # TODO


class OFPR_NO_MATCH_nobuffer(base_tests.SimpleDataPlane):
    """
    Verify packet_in OFPR_NO _MATCH implements buffer handling correct

    Derived from Test case 90.20: OFPR_NO_MATCH unit8_t data[0] buffered
    """

    def runTest(self):
        delete_all_flows(self.controller)

        # config
        in_port, out_port = openflow_ports(2)
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     instructions=[ofp.instruction.apply_actions(
                                         [ofp.action.output(
                                             port=ofp.OFPP_CONTROLLER,
                                             max_len=1000
                                         )])])
        # test
        request = ofp.message.set_config(miss_send_len=0)
        self.controller.message_send(request)

        pkt = str(simple_tcp_packet(pktlen=70))
        self.dataplane.send(in_port, pkt)
        response, _ = self.controller.poll(ofp.message.packet_in)
        self.assertTrue(response is not None, "No packetin received")

        self.assertEqual(response.reason, ofp.OFPR_NO_MATCH,
                         "Packetin reason field is not NO_MATCH")
        # TODO


class OFPR_NO_MATCH_inport_totalen(base_tests.SimpleDataPlane):
    """
    Verify packet_in OFPR_NO _MATCH reports correct inport

    Derived from Test case 90.40: OFPR_NO_MATCH uint16_t in_port
    and Test case 90.50: OFPR_NO_MATCH int16_t total_len
    """

    def runTest(self):
        delete_all_flows(self.controller)

        # config
        in_port, out_port = openflow_ports(2)
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     instructions=[ofp.instruction.apply_actions(
                                         [ofp.action.output(
                                             port=ofp.OFPP_CONTROLLER,
                                             max_len=ofp.OFPCML_NO_BUFFER
                                         )])])
        # test
        pkt = str(simple_tcp_packet(pktlen=70))
        self.dataplane.send(in_port, pkt)
        verify_packet_in(self, pkt, in_port, ofp.OFPR_NO_MATCH)


class OFPR_Action_reason(base_tests.SimpleDataPlane):
    """
    Verify packet_in specifies the correct reason for Action explicitly output to controller

    Derived from Test case 90.60: OFPR_Action uint8_t reason
    """

    def runTest(self):
        delete_all_flows(self.controller)

        # config
        in_port, out_port = openflow_ports(2)
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions(
                                         [ofp.action.output(
                                             port=ofp.OFPP_CONTROLLER,
                                             max_len=ofp.OFPCML_NO_BUFFER
                                         )])])
        # test
        pkt = str(simple_tcp_packet(pktlen=70))
        self.dataplane.send(in_port, pkt)
        verify_packet_in(self, pkt, in_port, ofp.OFPR_ACTION)


class OFPR_Action_buffered(base_tests.SimpleDataPlane):
    """
    Verify packet_in OFPR_ACTION implements buffer handling correct

    Derived from Test case 90.60: OFPR_Action uint8_t reason
    """

    def runTest(self):
        delete_all_flows(self.controller)

        # config
        in_port, out_port = openflow_ports(2)
        max_len = 100
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions(
                                         [ofp.action.output(
                                             port=ofp.OFPP_CONTROLLER,
                                             max_len=max_len
                                         )])])
        # test
        pkt = str(simple_tcp_packet(pktlen=700))
        self.dataplane.send(in_port, pkt)

        response, _ = self.controller.poll(ofp.message.packet_in)
        self.assertTrue(response is not None, "No packetin received")
        self.assertEqual(response.reason, ofp.OFPR_ACTION, "Reason of packetin is incorrect")
        self.assertEqual(len(response.data), max_len, "Length of packetin is incorrect")


class OFPR_Action_unbuffered(base_tests.SimpleDataPlane):
    """
    Verify packet_in OFPR_ACTION implements buffer handling correct

    Derived from Test case 90.60: OFPR_Action uint8_t reason
    """

    def runTest(self):
        delete_all_flows(self.controller)

        # config
        in_port, out_port = openflow_ports(2)
        max_len = 100
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions(
                                         [ofp.action.output(
                                             port=ofp.OFPP_CONTROLLER,
                                             max_len=ofp.OFPCML_NO_BUFFER
                                         )])])
        # test
        pkt = str(simple_tcp_packet(pktlen=0))
        self.dataplane.send(in_port, pkt)

        response, _ = self.controller.poll(ofp.message.packet_in)
        logging.info(response.show())
        self.assertTrue(response is not None, "No packetin received")
        # self.assertEqual(len(response.data), max_len, "Length of packetin is incorrect")


class OFPR_ACTION_inport_totalen(base_tests.SimpleDataPlane):
    """
    Verify packet_in OFPR_ACTION reports correct inport and total lengeth

    Derived from Test case 90.90: OFPR_ACTION uint16_t in_port
    and OFPR_ACTION int16_t total_len
    """

    def runTest(self):
        delete_all_flows(self.controller)

        # config
        in_port, out_port = openflow_ports(2)
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions(
                                         [ofp.action.output(
                                             port=ofp.OFPP_CONTROLLER,
                                             max_len=ofp.OFPCML_NO_BUFFER
                                         )])])
        # test
        pkt = str(simple_tcp_packet(pktlen=70))
        self.dataplane.send(in_port, pkt)
        verify_packet_in(self, pkt, in_port, ofp.OFPR_ACTION)


class OFPT_PORT_STATUS(base_tests.SimpleDataPlane):
    """
    Verify packet_in OFPR_ACTION implements buffer handling correct

    Derived from Test case 90.60: OFPR_Action uint8_t reason
    """
    # TODO
    def runTest(self):
        delete_all_flows(self.controller)

        # config
        in_port, out_port = openflow_ports(2)
        rv = port_config_set(self.controller, in_port,
                             ofp.OFPPC_PORT_DOWN,
                             ofp.OFPPC_PORT_DOWN | ofp.OFPPC_NO_RECV |
                             ofp.OFPPC_NO_FWD | ofp.OFPPC_NO_PACKET_IN)
        # test
        response, _ = self.controller.poll(ofp.message.port_status, 100)
        logging.info(response.show())
        # self.assertTrue(response is not None, "No packetin received")
        # self.assertEqual(len(response.data), max_len, "Length of packetin is incorrect")


class OFPT_PORT_MOD_No_Forward(base_tests.SimpleDataPlane):
    """
    Verify Controller is able to use the OFPT_PORT_MOD -OFPPFL_NO_FWD message to change port state on the DUT

    Derived from Test case 90.130: OFPT_PORT_MOD - No_Forward
    """

    def runTest(self):
        delete_all_flows(self.controller)

        # config
        in_port, out_port = openflow_ports(2)
        rv = port_config_set(self.controller, in_port,
                             ofp.OFPPC_NO_FWD,
                             ofp.OFPPC_PORT_DOWN | ofp.OFPPC_NO_RECV |
                             ofp.OFPPC_NO_FWD | ofp.OFPPC_NO_PACKET_IN)
        # test
        response, _ = self.controller.poll(ofp.message.port_status)
        self.assertNotEqual(response.desc.config & ofp.OFPPC_NO_FWD, 0, "Config is incorrect")

        rv = port_config_set(self.controller, in_port,
                             0,
                             ofp.OFPPC_PORT_DOWN | ofp.OFPPC_NO_RECV |
                             ofp.OFPPC_NO_FWD | ofp.OFPPC_NO_PACKET_IN)
        # test
        response, _ = self.controller.poll(ofp.message.port_status)
        self.assertEqual(response.desc.config & ofp.OFPPC_NO_FWD, 0, "Config is incorrect")


class OFPT_PORT_MOD_No_PacketIn(base_tests.SimpleDataPlane):
    """
    Verify Controller is able to use the OFPT_PORT_MOD-NO_PACKET_IN
    message to change port state on the DUT

    Derived from Test case 90.140: OFPT_PORT_MOD - No_Packet_in
    """

    def runTest(self):
        delete_all_flows(self.controller)

        # config
        in_port, out_port = openflow_ports(2)
        rv = port_config_set(self.controller, in_port,
                             ofp.OFPPC_NO_PACKET_IN,
                             ofp.OFPPC_PORT_DOWN | ofp.OFPPC_NO_RECV |
                             ofp.OFPPC_NO_FWD | ofp.OFPPC_NO_PACKET_IN)
        # test
        response, _ = self.controller.poll(ofp.message.port_status)
        self.assertNotEqual(response.desc.config & ofp.OFPPC_NO_PACKET_IN, 0, "Config is incorrect")

        rv = port_config_set(self.controller, in_port,
                             0,
                             ofp.OFPPC_PORT_DOWN | ofp.OFPPC_NO_RECV |
                             ofp.OFPPC_NO_FWD | ofp.OFPPC_NO_PACKET_IN)
        # test
        response, _ = self.controller.poll(ofp.message.port_status)
        self.assertEqual(response.desc.config & ofp.OFPPC_NO_PACKET_IN, 0, "Config is incorrect")


class OFPT_PACKET_OUT(base_tests.SimpleDataPlane):
    """
    Verify Controller is able to use the OFPT_PACKET_OUT message
    to send a packet out of one of the DUT ports

    Derived from Test case 90.150: OFPT_PACKET_OUT
    """

    def runTest(self):
        pkt = str(simple_tcp_packet())

        for of_port in config["port_map"].keys():
            msg = ofp.message.packet_out(
                in_port=ofp.OFPP_CONTROLLER,
                actions=[ofp.action.output(port=of_port)],
                buffer_id=ofp.OFP_NO_BUFFER,
                data=pkt)

            logging.info("PacketOut test, port %d", of_port)
            self.controller.message_send(msg)
            verify_packets(self, pkt, [of_port])


class OFPT_QUEUE_GET_CONFIG_REPLY(base_tests.SimpleDataPlane):
    """

    Derived from Test case 90.140: OFPT_PORT_MOD - No_Packet_in
    """

    def runTest(self):
        # config
        for port in openflow_ports(4):
            request = ofp.message.queue_get_config_request(port=port)
            response, _ = self.controller.transact(request)

            self.assertTrue(response is not None, "No queue_get_config_reply was received")
            logging.info(response.show())
