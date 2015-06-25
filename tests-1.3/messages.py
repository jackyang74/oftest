
"""
Test suite 80 checks OpenFlow protocol messages and their correct implementation. In
contrast to the basic checks, return values are checked for correctness, and configurations for
functional implementation
"""

import logging

from oftest import config
import oftest.base_tests as base_tests
import ofp
import time

from oftest.testutils import *


@group('standard')
class HelloWithoutBody(base_tests.SimpleProtocol):
    """
    Test case 80.10: OFPT_HELLO without body

    """

    def runTest(self):
        logging.info("Test case 20.100: Verify basic Hello messages are implemented")
        request = ofp.message.hello()
        self.controller.message_send(request)

        response, _ = self.controller.poll(ofp.message.hello_failed_error_msg)
        self.assertTrue(response is None,
                        "Hello Error message was received")


@group('standard')
class HelloWithBody(base_tests.SimpleProtocol):
    """
    Test case 80.20: OFPT_HELLO with body

    """

    def runTest(self):
        logging.info("Test case 20.100: Verify basic Hello messages are implemented")
        request = ofp.message.hello(elements=["Test Heloo"])
        self.controller.message_send(request)

        response, _ = self.controller.poll(ofp.message.hello_failed_error_msg)
        self.assertTrue(response is None,
                        "Hello Error message was received")


@group('TestSuite10')
class ErrorMessage(base_tests.SimpleProtocol):
    """
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

@group('TestSuite20')
class EchoWithoutBody(base_tests.SimpleProtocol):
    """
    Test case 20.110: Verify Echo Reply messages are implemented
    Test echo response with no data
    """

    def runTest(self):
        logging.info("Test case 20.110: Verify Echo Reply messages are implemented")
        request = ofp.message.echo_request()
        response, pkt = self.controller.transact(request)
        self.assertTrue(response is not None,
                        "Did not get echo reply")
        self.assertEqual(response.type, ofp.OFPT_ECHO_REPLY,
                         'response is not echo_reply')
        self.assertEqual(request.xid, response.xid,
                         'response xid != request xid')
        self.assertEqual(len(response.data), 0, 'response data non-empty')


@group('OFTest')
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


class FeaturesRequestReply(base_tests.SimpleProtocol):
    """

    """

    def runTest(self):
        request = ofp.message.features_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        'Did not get features reply')
        self.assertEqual(request.xid, response.xid,
                         'response xid != request xid')


class FeaturesReply(base_tests.SimpleProtocol):
    """

    """

    def runTest(self):
        request = ofp.message.features_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        'Did not get features reply')
        self.assertEqual(request.xid, response.xid,
                         'response xid != request xid')
        self.assertTrue(response.capabilities  is not None,
                            "No features are supported")


class DatapathID(base_tests.SimpleProtocol):
    """

    """

    def runTest(self):
        request = ofp.message.features_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        'Did not get features reply')
        self.assertEqual(request.xid, response.xid,
                         'response xid != request xid')
        self.assertTrue(response.datapath_id is not None,
                            "No features are supported")


class Feature_n_buffer(base_tests.SimpleProtocol):
    """

    """

    def runTest(self):
        request = ofp.message.features_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        'Did not get features reply')
        self.assertEqual(request.xid, response.xid,
                         'response xid != request xid')
        self.assertTrue(response.n_buffers is not None,
                            "No features are supported")


class Feature_n_tables(base_tests.SimpleProtocol):
    """

    """

    def runTest(self):
        request = ofp.message.features_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        'Did not get features reply')
        self.assertEqual(request.xid, response.xid,
                         'response xid != request xid')
        self.assertTrue(response.n_tables is not None,
                            "No features are supported")

class OFPC_FLOW_STATS(base_tests.SimpleProtocol):
    """

    """

    def runTest(self):
        request = ofp.message.features_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        'Did not get features reply')
        self.assertEqual(request.xid, response.xid,
                         'response xid != request xid')
        self.assertEqual(response.capabilities & 0x1 , 1,
                            "OFPC_FLOW_STATS is not supported")


class OFPC_TABLE_STATS(base_tests.SimpleProtocol):
    """

    """

    def runTest(self):
        request = ofp.message.features_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        'Did not get features reply')
        self.assertEqual(request.xid, response.xid,
                         'response xid != request xid')
        self.assertEqual(response.capabilities & 0x2 , 1,
                            "OFPC_TABLE_STATS is not supported")



class OFPC_PORT_STATS(base_tests.SimpleProtocol):
    """

    """

    def runTest(self):
        request = ofp.message.features_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        'Did not get features reply')
        self.assertEqual(request.xid, response.xid,
                         'response xid != request xid')
        self.assertEqual(response.capabilities & 0x4 , 1,
                            "OFPC_TABLE_STATS is not supported")

class OFPC_IP_REASM(base_tests.SimpleProtocol):
    """

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


class ConfigGet(base_tests.SimpleProtocol):
    """
    Test case 20.20: Verify basic Config Request is implemented

    Verify that a basic Get Config Request does not generate an error.    """

    def runTest(self):
        logging.info("Test case 20.20: Verify basic Config Request is implemented")
        request = ofp.message.get_config_request()
        response, _ = self.controller.transact(request)
        logging.info(response.show())
        self.assertTrue(response is not None,
                        "No response to get config request")
        self.assertTrue(response.flags is not None,
                        "Config reply has flags")


class ConfigGetMissSendLen(base_tests.SimpleProtocol):
    """
    Test case 20.20: Verify basic Config Request is implemented

    Verify that a basic Get Config Request does not generate an error.    """

    def runTest(self):
        request = ofp.message.get_config_request()
        response, _ = self.controller.transact(request)
        logging.info(response.show())
        self.assertTrue(response is not None,
                        "No response to get config request")
        # TODO verify the len in the packet_in message is correct

class ConfigSetMissSendLen(base_tests.SimpleProtocol):
    """

    Verify that a basic Get Config Request does not generate an error.    """

    def runTest(self):
        request = ofp.message.set_config(miss_send_len = 111)
        response, _ = self.controller.transact(request)

        request = ofp.message.get_config_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        "No response to get config request")
        self.assertEqual(response.miss_send_len, 111,
                         "Can't set the field miss_send_len")


class ConfigSet_FRAG_NORMAL(base_tests.SimpleProtocol):
    """

    Verify that a basic Get Config Request does not generate an error.    """

    def runTest(self):
        request = ofp.message.set_config(flags=ofp.OFPC_FRAG_NORMAL)
        response, _ = self.controller.transact(request)

        request = ofp.message.get_config_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        "No response to get config request")
        self.assertEqual(response.flags, ofp.OFPC_FRAG_NORMAL,
                         "Can't set the field miss_send_len")


class ConfigSet_FRAG_DROP(base_tests.SimpleProtocol):
    """

    Verify that a basic Get Config Request does not generate an error.    """

    def runTest(self):
        request = ofp.message.set_config(flags=ofp.OFPC_FRAG_DROP)
        response, _ = self.controller.transact(request)

        request = ofp.message.get_config_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        "No response to get config request")
        self.assertEqual(response.flags, ofp.OFPC_FRAG_DROP,
                         "Can't set the field miss_send_len")

class ConfigSet_FRAG_REASM(base_tests.SimpleProtocol):
    """

    Verify that a basic Get Config Request does not generate an error.    """

    def runTest(self):
        request = ofp.message.set_config(flags=ofp.OFPC_FRAG_REASM)
        response, _ = self.controller.transact(request)

        request = ofp.message.get_config_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        "No response to get config request")
        self.assertEqual(response.flags, ofp.OFPC_FRAG_REASM,
                         "Can't set the field miss_send_len")


class ConfigSet_FRAG_MASK(base_tests.SimpleProtocol):
    """
    Verify that a basic Get Config Request does not generate an error.

    """

    def runTest(self):
        request = ofp.message.set_config(flags=ofp.OFPC_FRAG_MASK)
        response, _ = self.controller.transact(request)

        request = ofp.message.get_config_request()
        response, _ = self.controller.transact(request)
        self.assertTrue(response is not None,
                        "No response to get config request")
        self.assertEqual(response.flags, ofp.OFPC_FRAG_MASK,
                         "Can't set the field miss_send_len")
