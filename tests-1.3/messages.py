"""
Test suite 80 checks OpenFlow protocol messages and their correct implementation. In
contrast to the basic checks, return values are checked for correctness, and configurations for
functional implementation
"""

import logging

from oftest import config
import oftest.base_tests as base_tests
import ofp

from oftest.testutils import *


@group('standard')
class HelloWithoutBody(base_tests.SimpleProtocol):
    """
    Verify OFPT_HELLO without body is accepted by the device

    Test case 80.10: OFPT_HELLO without body
    """

    def runTest(self):
        request = ofp.message.hello()
        self.controller.message_send(request)

        response, _ = self.controller.poll(ofp.message.hello_failed_error_msg)
        self.assertTrue(response is None,
                        "Hello Error message was received")


@group('standard')
class HelloWithBody(base_tests.SimpleProtocol):
    """
    Verify OFPT_HELLO with body is accepted by the device

    Test case 80.20: OFPT_HELLO with body
    """

    def runTest(self):
        msg = ofp.message.echo_request()
        msg.xid = 213
        request = ofp.message.hello(elements=[msg])
        self.controller.message_send(request)

        response, _ = self.controller.poll(ofp.message.hello_failed_error_msg)
        self.assertTrue(response is None,
                        "Hello Error message was received")


@group('standard')
class ErrorMessage(base_tests.SimpleProtocol):
    """
    Verify basic error message type is implemented

    Test case 80.30: OFPT_ERROR
    """

    def runTest(self):
        request = ofp.message.hello()
        # change hello message version to incorrect number
        request.version = ofp.OFP_VERSION - 1
        self.controller.message_send(request)

        response, _ = self.controller.poll(ofp.message.hello_failed_error_msg)
        self.assertTrue(response is not None,
                        "No Error message was received")
        self.assertTrue(response.code == ofp.OFPHFC_INCOMPATIBLE,
                        "Hello Error with reason Version INCOMPATIBLE was not received")


@group('standard')
class EchoWithoutBody(base_tests.SimpleProtocol):
    """
    Test echo response with no data

    Test case 80.40: Verify Echo Reply messages are implemented
    """

    def runTest(self):
        request = ofp.message.echo_request()
        response, pkt = self.controller.transact(request)
        self.assertTrue(response is not None,
                        "Did not get echo reply")
        self.assertEqual(response.type, ofp.OFPT_ECHO_REPLY,
                         'response is not echo_reply')
        self.assertEqual(request.xid, response.xid,
                         'response xid != request xid')
        self.assertEqual(len(response.data), 0, 'response data non-empty')


@group('standard')
class EchoWithBody(base_tests.SimpleProtocol):
    """
    Test echo response with short string data
    """

    def runTest(self):
        data = 'OpenFlow Will Rule The World'
        request = ofp.message.echo_request(data=data)
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        "Did not get echo reply")
        self.assertEqual(response.type, ofp.OFPT_ECHO_REPLY,
                         'response is not echo_reply')
        self.assertEqual(request.xid, response.xid,
                         'response xid != request xid')
        self.assertEqual(request.data, response.data,
                         'response data != request data')


@group('standard')
class FeaturesRequestReply(base_tests.SimpleProtocol):
    """
    Verify OFPT_FEATURES_REQUEST / Reply dialogue

    Derived from Test case 80.60: Features Request-Reply
    """

    def runTest(self):
        request = ofp.message.features_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        'Did not get features reply')
        self.assertEqual(request.xid, response.xid,
                         'response xid != request xid')


@group('standard')
class FeaturesReply(base_tests.SimpleProtocol):
    """
    Verify OFPT_FEATURES_REPLY contains complete feature information

    Derived from Test case 80.70: Features Reply
    """

    def runTest(self):
        request = ofp.message.features_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        'Did not get features reply')
        self.assertEqual(request.xid, response.xid,
                         'response xid != request xid')
        self.assertTrue(response.capabilities is not None,
                        "No features are supported")



@group('standard')
class OFPC_FLOW_STATS(base_tests.SimpleProtocol):
    """
    Verify OFPT_FEATURES_REPLY for Flow statistics support
    """

    def runTest(self):
        request = ofp.message.features_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        'Did not get features reply')
        self.assertEqual(request.xid, response.xid,
                         'response xid != request xid')
        self.assertNotEqual(response.capabilities & ofp.OFPC_FLOW_STATS, 0,
                            "OFPC_FLOW_STATS is not supported")


@group('standard')
class OFPC_TABLE_STATS(base_tests.SimpleProtocol):
    """
    Verify OFPT_FEATURES_REPLY for Table statistics support
    """

    def runTest(self):
        request = ofp.message.features_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        'Did not get features reply')
        self.assertEqual(request.xid, response.xid,
                         'response xid != request xid')
        self.assertNotEqual(response.capabilities & ofp.OFPC_TABLE_STATS, 0,
                            "OFPC_TABLE_STATS is not supported")


@group('standard')
class OFPC_PORT_STATS(base_tests.SimpleProtocol):
    """
    Verify OFPT_FEATURES_REPLY for Port statistics support
    """

    def runTest(self):
        request = ofp.message.features_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        'Did not get features reply')
        self.assertEqual(request.xid, response.xid,
                         'response xid != request xid')
        self.assertNotEqual(response.capabilities & ofp.OFPC_PORT_STATS, 0,
                            "OFPC_PORT_STATS is not supported")


@group('standard')
class OFPC_IP_REASM(base_tests.SimpleProtocol):
    """
    Verify OFPT_FEATURES_REPLY for IP packet reassembly
    """

    def runTest(self):
        request = ofp.message.features_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        'Did not get features reply')
        self.assertEqual(request.xid, response.xid,
                         'response xid != request xid')
        if response.capabilities & 0x20:
            logging.info("OFPC_IP_REASM is supported")
        else:
            logging.info("OFPC_IP_REASM is not supported")


@group('standard')
class ConfigGet(base_tests.SimpleProtocol):
    """
    Verify that a basic Get Config Request does not generate an error.
    """

    def runTest(self):
        request = ofp.message.get_config_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        "No response to get config request")
        self.assertTrue(response.flags is not None,
                        "Config reply has flags")


@group('standard')
class ConfigGetMissSendLen(base_tests.SimpleProtocol):
    """
    Check OFPT_GET_CONFIG_REPLY value for No special handling for fragments
    """

    def runTest(self):
        request = ofp.message.get_config_request()
        response, _ = self.controller.transact(request)
        logging.info(response.show())
        self.assertTrue(response is not None,
                        "No response to get config request")


@group('standard')
class ConfigSetMissSendLen(base_tests.SimpleProtocol):
    """
    Verify implementation of OFPT_SET_CONFIG - miss_send_len
    """

    def setUp(self):
        base_tests.SimpleProtocol.setUp(self)
        request = ofp.message.get_config_request()
        response, _ = self.controller.transact(request)
        self.miss_send_len = response.miss_send_len

    def runTest(self):
        request = ofp.message.set_config(miss_send_len=111)
        self.controller.message_send(request)

        request = ofp.message.get_config_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        "No response to get config request")
        self.assertEqual(response.miss_send_len, 111,
                         "Can't set the field miss_send_len")

    def tearDown(self):
        request = ofp.message.set_config(miss_send_len=self.miss_send_len)
        self.controller.message_send(request)
        base_tests.SimpleProtocol.tearDown(self)

class OFPT_PACKET_OUT(base_tests.SimpleDataPlane):
    """
    Verify Controller is able to use the OFPT_PACKET_OUT message
    to send a packet out of one of the DUT ports
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


@group('standard')
class BarrierRequest(base_tests.SimpleProtocol):
    """
    Verify that a basic barrier request does not generate an error.
    """

    def runTest(self):
        request = ofp.message.barrier_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        "No response to Barrier Request")


@group('standard')
class AsyncConfigGet(base_tests.SimpleProtocol):
    """
    Verify initial async config

    Other tests rely on connections starting with these values.
    """

    def runTest(self):
        logging.info("Sending get async config request")
        response, _ = self.controller.transact(ofp.message.async_get_request())
        self.assertTrue(response != None, "No response to get async config request")
        logging.info(response.show())
        self.assertEquals(response.packet_in_mask_equal_master & 0x07, 0x07)
        self.assertEquals(response.port_status_mask_equal_master & 0x07, 0x07)
        self.assertEquals(response.flow_removed_mask_equal_master & 0x0f, 0x0f)
