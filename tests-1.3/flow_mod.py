# Distributed under the OpenFlow Software License (see LICENSE)
# Copyright (c) 2014 Big Switch Networks, Inc.
"""
Flow-mod test cases
"""

import logging

import oftest
from oftest import config
import oftest.base_tests as base_tests
import ofp
import time
from loxi.pp import pp
from oftest.testutils import *
from oftest.parse import parse_ipv6
import FuncUtils


@group('standard')
class OverlapChecking(base_tests.SimpleProtocol):
    """
    Verify that overlap checking generates an error when the controller
    attempts to add an overlapping flow to the flow table.

    Derived from TestCase 40.10 --> Overlap checking
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])])

        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])],
                                     flags=ofp.OFPFF_CHECK_OVERLAP)

        # Verify the correct error message is returned
        response, _ = self.controller.poll(exp_msg=ofp.message.flow_mod_failed_error_msg)
        self.assertTrue(response is not None,
                        "No Flow Mod Failed Error message was received")


@group('standard')
class NoOverlapChecking(base_tests.SimpleProtocol):
    """
    Verify that overlap checking generates an error when the controller
    attempts to add an overlapping flow to the flow table.

    Derived from TestCase 40.20 --> No Overlap checking
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)
        request1 = FuncUtils.flow_entry_install(self.controller,
                                                "flow_add",
                                                match=ofp.match([ofp.oxm.in_port(in_port)]),
                                                instructions=[
                                                    ofp.instruction.apply_actions([ofp.action.output(out_port)])])

        request2 = FuncUtils.flow_entry_install(self.controller,
                                                "flow_add",
                                                instructions=[
                                                    ofp.instruction.apply_actions([ofp.action.output(out_port)])])

        # Verify the correct error message is returned
        response, _ = self.controller.poll(exp_msg=ofp.message.flow_mod_failed_error_msg)
        self.assertTrue(response is None,
                        "Flow Mod Failed Error message was received")

        # read flow entries to ensure the new entry is inserted
        flow_stats = get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 2)
        self.assertTrue(request1.instructions, flow_stats[0].instructions)
        self.assertTrue(request2.instructions, flow_stats[1].instructions)


@group('standard')
class IdenticalFlows(base_tests.SimpleDataPlane):
    """
    Verify that adding an identical flow overwrites the existing flow and
    clears the counters

    Derived from Test case 40.30: Identical flows
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        request = FuncUtils.flow_entry_install(self.controller,
                                               "flow_add",
                                               match=ofp.match([ofp.oxm.in_port(in_port)]),
                                               instructions=[
                                                   ofp.instruction.apply_actions([ofp.action.output(out_port)])])
        # send matching packets
        pkt = str(simple_icmp_packet())
        times = 10
        for i in range(times):
            self.dataplane.send(in_port, pkt)

        # send same flow into the table to reset counters
        self.controller.message_send(request)

        # check result
        flow_stats = get_flow_stats(self, ofp.match())
        for entry in flow_stats:
            logging.debug(entry.show())

        self.assertEqual(len(flow_stats), 1)
        self.assertEqual(flow_stats[0].packet_count, 0)


@group('standard')
class NoTableAdd(base_tests.SimpleProtocol):
    """
    Verify that flow table full error messages are generated.

    Test case 40.40: No table to add
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


@group('standard')
class NeverValidOutputPort(base_tests.SimpleProtocol):
    """
    Verify that adding a flow with a never valid output port number triggers
    correct error

    Derived from Test case 40.50: Never valid output port
    """

    def runTest(self):
        delete_all_flows(self.controller)

        # serach unavalible port
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


@group('standard')
class ModifyNonExistentFlow(base_tests.SimpleProtocol):
    """
    Verify that modifying a non-existent flow adds the flow with zeroed
    counters.

    Derived from Test case 40.80: Modify non-existent flow
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        request = FuncUtils.flow_entry_install(self.controller,
                                               "flow_mod",
                                               match=ofp.match([ofp.oxm.in_port(in_port)]),
                                               instructions=[
                                                   ofp.instruction.apply_actions([ofp.action.output(out_port)])
                                               ])
        # verilog the flow entry was added and its counter was 0
        flow_stats = get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 0)
        verify_flow_stats(self, request.match, pkts=0)


@group('standard')
class ModifyAction(base_tests.SimpleDataPlane):
    """
    Verify that modifying the action of a flow does not reset counters

    Derived from Test case 40.90: Modify action preserves counters
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port1, out_port2 = openflow_ports(3)

        request = FuncUtils.flow_entry_install(self.controller,
                                               "flow_add",
                                               match=ofp.match([ofp.oxm.in_port(in_port)]),
                                               instructions=[
                                                   ofp.instruction.apply_actions([ofp.action.output(out_port1)])
                                               ])
        pkg_num = 10
        FuncUtils.send_packets(self, simple_icmp_packet(), in_port, pkg_num)

        FuncUtils.flow_entry_install(self.controller,
                                     "flow_mod",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[
                                         ofp.instruction.apply_actions([ofp.action.output(out_port2)])
                                     ])

        # verify flow entry pkg num
        flow_stats = get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 1)
        verify_flow_stats(self, request.match, pkts=pkg_num)


@group('standard')
class ModifyStrictAction(base_tests.SimpleDataPlane):
    """
    Verify that modifying the action of a flow does not reset counters for
    modify_strict

    Derived from Test case 40.100: Modify_strict of action preserves counters
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port1, out_port2 = openflow_ports(3)

        request = FuncUtils.flow_entry_install(self.controller,
                                               "flow_add",
                                               match=ofp.match([ofp.oxm.in_port(in_port)]),
                                               instructions=[
                                                   ofp.instruction.apply_actions([ofp.action.output(out_port1)])
                                               ])

        pkg_num = 10
        FuncUtils.send_packets(self, simple_icmp_packet(), in_port, pkg_num)

        FuncUtils.flow_entry_install(self.controller,
                                     "flow_mods",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[
                                         ofp.instruction.apply_actions([ofp.action.output(out_port2)])
                                     ])

        # verify flow entry pkg num
        flow_stats = get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 1)
        verify_flow_stats(self, request.match, pkts=pkg_num)


@group('standard')
class DeleteNonexistentFlow(base_tests.SimpleProtocol):
    """
    Verify that deleting a non-existent flow does not generate an error

    Test case 40.110: Delete non-existent flow
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        FuncUtils.flow_entry_install(self.controller,
                                     "flow_del",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[
                                         ofp.instruction.apply_actions([ofp.action.output(out_port)])
                                     ])
        # test
        error_msg, _ = self.controller.poll(ofp.OFPT_ERROR)
        self.assertTrue(error_msg is None, "Error message was received")


@group('standard')
class DeleteFlowWithFlag(base_tests.SimpleProtocol):
    """
    Verify that deleting a flow with send flow removed flag set triggers a
    flow removed message, and deleting a flow without the send flow
    removed flag set does not trigger a flow removed message.

    Derived from Test case 40.120: Delete flows with and without flow_removed flag set
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[
                                         ofp.instruction.apply_actions([ofp.action.output(out_port)])
                                     ])
        # test
        delete_all_flows(self.controller)
        error_msg, _ = self.controller.poll(ofp.message.flow_removed)
        self.assertTrue(error_msg is None, "Error message was received")

        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[
                                         ofp.instruction.apply_actions([ofp.action.output(out_port)])
                                     ],
                                     flags=ofp.OFPFF_SEND_FLOW_REM)
        # test
        delete_all_flows(self.controller)
        error_msg, _ = self.controller.poll(ofp.message.flow_removed)
        self.assertTrue(error_msg is not None, "Error message was not received")


@group('standard')
class DeleteWithoutWildcards(base_tests.SimpleProtocol):
    """
    Verify that flow_mod delete and strict_delete map to the correct flows

    Derived from Test case 40.140: Delete without wildcards
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        # flow add and delete
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])],
                                     prio=15)
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_del",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     )
        # flow add and delete strict
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])],
                                     prio=125)
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_dels",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     prio=125)

        # verify the num of flow entry is 0
        flow_stats = get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 0)


@group('standard')
class DeleteWithWildcardsSet(base_tests.SimpleProtocol):
    """
    Verify that delete maps to the correct flows

    Derived from Test case 40.150: Delete with wildcards set
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        # flow add
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])]
                                     )
        # flow add
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port),
                                                      ofp.oxm.eth_dst([0x00, 0x13, 0x3b, 0x0f, 0x42, 0x1c])
                                                      ]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])]
                                     )
        # flow del
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_del",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     )
        # verify the num of flow entry is 0
        flow_stats = get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 0)


@group('standard')
class StrictDeleteWithWildcardsSet(base_tests.SimpleProtocol):
    """
    Verify that strict_delete maps to the correct flows

    Derived from Test case 40.160: Strict_Delete with wildcards set
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        # flow T0 add
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])]
                                     )

        # flow T1 add
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port),
                                                      ofp.oxm.eth_dst([0x00, 0x13, 0x3b, 0x0f, 0x42, 0x1c])
                                                      ]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])]
                                     )
        # flow del
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_dels",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     )

        # verify the num of flow entry is 1
        flow_stats = get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 1)


@group('standard')
class DeleteIgnorePriorities(base_tests.SimpleProtocol):
    """
    Verify that delete maps to the correct flows

    Derived from Test case 40.170: Testing that delete message ignores priorities
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        # flow add
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])]
                                     )
        # flow add
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port),
                                                      ofp.oxm.eth_dst([0x00, 0x13, 0x3b, 0x0f, 0x42, 0x1c])
                                                      ]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])],
                                     prio=15)
        # flow add
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port),
                                                      ofp.oxm.eth_dst([0x00, 0x13, 0x3b, 0x0f, 0x42, 0x1c])
                                                      ]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])],
                                     prio=14)
        # flow del
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_del",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     prio=15
                                     )

        # verify the num of flow entry is 0
        flow_stats = get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 0, "Not All entries are removed")


@group('standard')
class StrictDeleteNotIgnorePriorities(base_tests.SimpleProtocol):
    """
    Verify that delete maps to the correct flows

    Derived from Test case 40.180: Testing that strict_delete message does not ignore priorities
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        # flow add
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])],
                                     prio=15
                                     )
        # flow add
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])],
                                     prio=14
                                     )
        # flow del
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_dels",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     prio=15
                                     )
        # verify the num of flow entry is 1
        flow_stats = get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 1)
        self.assertEqual(flow_stats[0].priority, 14, "Not matching entry is removed")


@group('standard')
class DeleteWithConstraintOutPort(base_tests.SimpleProtocol):
    """
    Verify that delete supports filtering on action out_port

    Derived from Test case 40.190: Delete with constraint out_port
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port1, out_port2 = openflow_ports(3)

        # flow add
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port1)])],
                                     prio=15
                                     )
        # flow add
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port2)])],
                                     prio=14
                                     )
        # check
        flow_stats = get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 2, "Flow was not inserted correctly")
        # flow del
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_del",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     prio=15,
                                     out_port=out_port1
                                     )
        # verify the num of flow entry is 1 and matching entry is removed
        flow_stats = get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 1, len(flow_stats))


@group('standard')
class OutportIgnoredForAddModify(base_tests.SimpleDataPlane):
    """
    Verify that out_port values in FLOW_MOD Add or Modify requests are ignored.
    Derived from Test case 40.200: out_port ignored by Add and Modify requests

    Test case 40.200: out_port ignored by Add and Modify requests
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port1, out_port2 = openflow_ports(3)

        # flow add
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port1)])],
                                     out_port=out_port1
                                     )
        # send packet to in_port and verify
        pkt = str(simple_tcp_packet())
        self.dataplane.send(in_port, pkt)
        verify_packets(self, pkt, [out_port1])
        verify_no_packet(self, pkt, out_port2)

        # flow add
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_mod",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port2)])],
                                     out_port=out_port1
                                     )

        # send packet to in_port and verify
        pkt = str(simple_tcp_packet())
        self.dataplane.send(in_port, pkt)
        verify_packets(self, pkt, [out_port2])
        verify_no_packet(self, pkt, out_port1)


@group('standard')
class TimeoutWithFlowRemovedFlag(base_tests.SimpleDataPlane):
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
        pkt = str(simple_tcp_packet())
        self.dataplane.send(in_port, pkt)
        time.sleep(3)

        msg, _ = self.controller.poll(ofp.message.flow_removed)
        self.assertTrue(msg is not None, "Error message was not received")
        self.assertEqual(msg.duration_sec, 1, "Time is not correct")


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