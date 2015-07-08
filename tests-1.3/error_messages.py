import logging

from oftest import config
import oftest.base_tests as base_tests
import ofp
import time
import FuncUtils
from oftest.testutils import *


class OFPHFC_INCOMPATIBLE(base_tests.SimpleProtocol):
    """
    Verify DUT is able to respond correctly to error condition

    Derived from Test case 100.10: OFPHFC_INCOMPATIBLE
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


class OFPBRC_BAD_VERSION(base_tests.SimpleProtocol):
    # TODO
    """
    Verify DUT is able to respond correctly to error condition

    Derived from Test case 100.10: OFPHFC_INCOMPATIBLE
    """

    def runTest(self):
        request = ofp.message.stats_request()
        # change version to 0
        request.version = 0
        self.controller.message_send(request)

        # time.sleep(10000)
        response, _ = self.controller.poll(ofp.message.bad_request_error_msg)
        self.assertTrue(response is not None,
                        "No Error message was received")
        self.assertEqual(response.code, ofp.OFPBRC_BAD_VERSION,
                         "Error message error code is not OFPBRC_BAD_VERSION")


class OFPBRC_BAD_TYPE(base_tests.SimpleProtocol):
    """
    Verify DUT is able to respond correctly to error condition

    Derived from Test case 100.10: OFPHFC_INCOMPATIBLE
    """

    def runTest(self):
        request = ofp.message.stats_request()
        # change version to 0
        request.type = ofp.OFPT_FEATURES_REPLY
        self.controller.message_send(request)

        response, _ = self.controller.poll(ofp.message.bad_request_error_msg)
        self.assertTrue(response is not None,
                        "No Error message was received")
        self.assertEqual(response.code, ofp.OFPBRC_BAD_TYPE,
                         "Error message error code is not OFPBRC_BAD_TYPE")


class OFPBRC_BAD_LEN(base_tests.SimpleDataPlane):
    # TODO library doesn't support the modification of packet length
    """
    Verify DUT is able to respond correctly to error condition

    Derived from Test case 100.10: OFPHFC_INCOMPATIBLE
    """

    def runTest(self):
        request = ofp.message.features_request()
        request.xid = 123123
        msg = request.pack()

        response, _ = self.controller.poll(ofp.message.bad_request_error_msg)
        self.assertTrue(response is not None,
                        "No Error message was received")
        self.assertEqual(response.code, ofp.OFPBRC_BAD_LEN,
                         "Error message error code is not OFPBRC_BAD_LEN")


class OFPBRC_BUFFER_EMPTY(base_tests.SimpleDataPlane):
    # TODO
    """
    Verify Controller is able to use the OFPT_PACKET_OUT message
    to send a packet out of one of the DUT ports

    Derived from Test case 90.150: OFPT_PACKET_OUT
    """

    def runTest(self):
        in_port = openflow_ports(1)[0]
        pkt = str(simple_tcp_packet())

        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     instructions=[ofp.instruction.apply_actions(
                                         [ofp.action.output(
                                             port=ofp.OFPP_CONTROLLER,
                                             max_len=2000
                                         )])])

        pkt = str(simple_tcp_packet())
        self.dataplane.send(in_port, pkt)
        response, _ = self.controller.poll(ofp.message.packet_in)
        # for i in range(1):
        msg = ofp.message.packet_out(
            in_port=ofp.OFPP_CONTROLLER,
            actions=[ofp.action.output(port=in_port)],
            buffer_id=response.buffer_id,
            data=pkt)
        self.controller.message_send(msg)

        response, _ = self.controller.poll(ofp.message.bad_request_error_msg)
        self.assertEqual(response.code, ofp.OFPBRC_BUFFER_EMPTY,
                         "Error message error code is not OFPBRC_BUFFER_EMPTY")


class OFPBAC_BAD_TYPE(base_tests.SimpleProtocol):
    """
    Verify DUT is able to respond correctly to error condition

    Derived from Test case 100.10: OFPHFC_INCOMPATIBLE
    """

    def runTest(self):
        action = ofp.action.output(
            port=ofp.OFPP_CONTROLLER,
            max_len=ofp.OFPCML_NO_BUFFER
        )
        action.type = 100
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     instructions=[ofp.instruction.apply_actions(
                                         [action])])
        response, _ = self.controller.poll(ofp.message.bad_action_error_msg)
        self.assertTrue(response is not None,
                        "No Error message was received")
        self.assertEqual(response.code, ofp.OFPBAC_BAD_TYPE,
                         "Error message error code is not OFPBRC_BAD_TYPE")


class OFPBAC_BAD_ARGUMENT(base_tests.SimpleProtocol):
    """
    Verify DUT is able to respond correctly to error condition

    Derived from Test case 100.10: OFPHFC_INCOMPATIBLE
    """

    def runTest(self):
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     instructions=[ofp.instruction.apply_actions(
                                         [ofp.action.push_vlan(ethertype=0x0081)])])
        response, _ = self.controller.poll(ofp.message.bad_action_error_msg)
        self.assertTrue(response is not None,
                        "No Error message was received")
        self.assertEqual(response.code, ofp.OFPBAC_BAD_ARGUMENT,
                         "Error message error code is not OFPBAC_BAD_ARGUMENT")


class OFPFMFC_OVERLAP(base_tests.SimpleProtocol):
    """

    """

    def runTest(self):
        delete_all_flows(self.controller)

        logging.info("Inserting flow: flow-mod cmd=add,table=0,prio=15 in_port=1 apply:output=2")
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(2)]),
                                     instructions=[
                                         ofp.instruction.apply_actions([ofp.action.output(1)]),
                                     ])

        logging.info("Inserting flow:  flow-mod cmd=add,table=0,prio=15,flags=0x2 apply:output=1")
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(2)]),
                                     instructions=[
                                         ofp.instruction.apply_actions([ofp.action.output(1)]),
                                     ],
                                     flags=ofp.OFPFF_CHECK_OVERLAP, )

        # Verify the correct error message is returned
        response, _ = self.controller.poll(exp_msg=ofp.message.flow_mod_failed_error_msg)
        self.assertTrue(response is not None,
                        "No Flow Mod Failed Error message was received")
        self.assertEqual(response.code, ofp.OFPFMFC_OVERLAP,
                         "Error message error code is not OFPFMFC_OVERLAP")


class OFPFMFC_BAD_COMMAND(base_tests.SimpleProtocol):
    """
    Verify Controller is able to respond correctly to error condition -- OFPFMFC_BAD_COMMAND

    Derived from Test case 100.240: OFPFMFC_BAD_COMMAND
    """

    def runTest(self):
        request = ofp.message.flow_add()
        request._command = 250
        self.controller.message_send(request)

        response, _ = self.controller.poll(ofp.message.flow_mod_failed_error_msg)
        self.assertTrue(response is not None,
                        "No Error message was received")
        self.assertEqual(response.code, ofp.OFPFMFC_BAD_COMMAND,
                         "Error message error code is not OFPFMFC_BAD_COMMAND")
