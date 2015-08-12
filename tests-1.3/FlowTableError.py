import logging

from oftest import config
import oftest.base_tests as base_tests
import ofp
import time
import FuncUtils
from oftest.testutils import *


@group('standard')
class NoTableAdd(base_tests.SimpleProtocol):
    """
    Verify that flow table full error messages are generated.
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        for i in range(65539):
            FuncUtils.flow_entry_install(self.controller,
                                         "flow_add",
                                         match=ofp.match([ofp.oxm.in_port(in_port)]),
                                         instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])],
                                         prio=i)
            # read error message
            response, _ = self.controller.poll(ofp.message.flow_mod_failed_error_msg, 0.00001)

            if response is not None and (response.code == ofp.OFPFMFC_TABLE_FULL):
                return
        self.assertTrue(False, "No error message was received")


class OFPBAC_BAD_TYPE(base_tests.SimpleProtocol):
    """
    Verify DUT is able to respond correctly to error condition
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


@group('standard')
class NeverValidOutputPort(base_tests.SimpleProtocol):
    """
    Verify that adding a flow with a never valid output port number triggers
    correct error
    """

    def runTest(self):
        delete_all_flows(self.controller)

        # search unavalible port
        for port_nonvalid in range(1000):
            FuncUtils.flow_entry_install(self.controller,
                                         "flow_add",
                                         instructions=[
                                             ofp.instruction.apply_actions([ofp.action.output(port_nonvalid)])
                                         ])
            _, port_config, _ = port_config_get(self.controller, port_nonvalid)
            if port_config is None:
                break

        # read error message
        response, _ = self.controller.poll(ofp.message.bad_action_error_msg)
        self.assertTrue(response is not None,
                        "No error message was received")
        self.assertEqual(response.code, ofp.OFPBAC_BAD_OUT_PORT)


class OFPBAC_BAD_ARGUMENT(base_tests.SimpleProtocol):
    """
    Verify DUT is able to respond correctly to error condition

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