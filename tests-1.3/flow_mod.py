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
from loxi.pp import pp

import oftest.testutils as testutils
from oftest.parse import parse_ipv6
import FuncUtils


class Overwrite(base_tests.SimpleDataPlane):
    """
    Verify that overwriting a flow changes most fields but preserves stats
    """

    def runTest(self):
        in_port, out_port1, out_port2 = openflow_ports(3)

        delete_all_flows(self.controller)

        table_id = test_param_get("table", 0)
        match = ofp.match([
            ofp.oxm.in_port(in_port),
        ])
        priority = 1000

        logging.info("Inserting flow")
        request = ofp.message.flow_add(
            table_id=table_id,
            match=match,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port1)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            priority=priority,
            flags=ofp.OFPFF_SEND_FLOW_REM,
            cookie=0x1234,
            hard_timeout=1000,
            idle_timeout=2000)
        self.controller.message_send(request)
        do_barrier(self.controller)

        # Send a packet through so that we can check stats were preserved
        self.dataplane.send(in_port, str(simple_tcp_packet(pktlen=100)))
        verify_flow_stats(self, ofp.match(), table_id=table_id, pkts=1)

        # Send a flow-add with the same table_id, match, and priority, causing
        # an overwrite
        logging.info("Overwriting flow")
        request = ofp.message.flow_add(
            table_id=table_id,
            match=match,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port2)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            priority=priority,
            flags=0,
            cookie=0xabcd,
            hard_timeout=3000,
            idle_timeout=4000)
        self.controller.message_send(request)
        do_barrier(self.controller)

        # Should not get a flow-removed message
        msg, _ = self.controller.poll(exp_msg=ofp.message.flow_removed,
                                      timeout=oftest.ofutils.default_negative_timeout)
        self.assertEquals(msg, None)

        # Check that the fields in the flow stats entry match the second flow-add
        stats = get_flow_stats(self, ofp.match())
        self.assertEquals(len(stats), 1)
        entry = stats[0]
        logging.debug(entry.show())
        self.assertEquals(entry.instructions, request.instructions)
        self.assertEquals(entry.flags, request.flags)
        self.assertEquals(entry.cookie, request.cookie)
        self.assertEquals(entry.hard_timeout, request.hard_timeout)
        self.assertEquals(entry.idle_timeout, request.idle_timeout)

        # Flow stats should have been preserved
        verify_flow_stats(self, ofp.match(), table_id=table_id, pkts=1)


@testutils.group('TestSuite40')
class OverlapChecking(base_tests.SimpleProtocol):
    """
    TestCase 40.10 --> Overlap checking
    Verify that overlap checking generates an error when the controller
    attempts to add an overlapping flow to the flow table.
    """

    def runTest(self):
        logging.info("TestCase 40.10 --> Overlap checking")
        # delete all entrys
        testutils.delete_all_flows(self.controller)

        logging.info("Inserting flow: flow-mod cmd=add,table=0,prio=15 in_port=1 apply:output=2")
        table_id = testutils.test_param_get("table", 0)
        request = ofp.message.flow_add(
            table_id=table_id,
            match=ofp.match([ofp.oxm.in_port(2)]),
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(1)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=15)
        self.controller.message_send(request)

        logging.info("Inserting flow:  flow-mod cmd=add,table=0,prio=15,flags=0x2 apply:output=1")
        table_id = testutils.test_param_get("table", 0)
        request = ofp.message.flow_add(
            table_id=table_id,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(1)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            flags=ofp.OFPFF_CHECK_OVERLAP,
            priority=15)
        self.controller.message_send(request)

        testutils.do_barrier(self.controller)

        # Verify the correct error message is returned
        response, _ = self.controller.poll(exp_msg=ofp.message.flow_mod_failed_error_msg)
        self.assertTrue(response is not None,
                        "No Flow Mod Failed Error message was received")


@testutils.group('TestSuite40')
class NoOverlapChecking(base_tests.SimpleProtocol):
    """
    TestCase 40.20 --> No Overlap checking
    Verify that overlap checking generates an error when the controller
    attempts to add an overlapping flow to the flow table.
    """

    def runTest(self):
        logging.info("TestCase 40.10 --> Overlap checking")
        # delete all entries
        testutils.delete_all_flows(self.controller)

        logging.info("Inserting flow: flow-mod cmd=add,table=0,prio=15 in_port=2 apply:output=1")
        request1 = FuncUtils.dpctl_cmd_to_msg("flow-mod cmd=add,table=0,prio=15 in_port=2 apply:output=1")
        # table_id = testutils.test_param_get("table", 0)
        # request1 = ofp.message.flow_add(
        #     table_id=table_id,
        #     match=ofp.match([ofp.oxm.in_port(2)]),
        #     instructions=[
        #         ofp.instruction.apply_actions([ofp.action.output(1)]),
        #     ],
        #     buffer_id=ofp.OFP_NO_BUFFER,
        #     out_port=ofp.OFPP_ANY,
        #     out_group=ofp.OFPG_ANY,
        #     priority=15)
        self.controller.message_send(request1)

        logging.info("Inserting flow:  flow-mod cmd=add,table=0,prio=15,flags=0x2 apply:output=1")
        table_id = testutils.test_param_get("table", 0)
        request2 = ofp.message.flow_add(
            table_id=table_id,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(1)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            # flags=ofp.OFPFF_CHECK_OVERLAP,
            priority=15)
        self.controller.message_send(request2)

        testutils.do_barrier(self.controller)

        # Verify the correct error message is returned
        response, _ = self.controller.poll(exp_msg=ofp.message.flow_mod_failed_error_msg)
        self.assertTrue(response is None,
                        "Flow Mod Failed Error message was received")

        # read flow entries to ensure the new entry is inserted
        flow_stats = testutils.get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 2)
        for entry in flow_stats:
            logging.debug(entry.show())

        self.assertTrue(request1.instructions, flow_stats[0].instructions)
        self.assertTrue(request2.instructions, flow_stats[1].instructions)


@testutils.group('TestSuite40')
class IdenticalFlows(base_tests.SimpleDataPlane):
    """
    Test case 40.30: Identical flows
    Verify that adding an identical flow overwrites the existing flow and
    clears the counters
    """

    def runTest(self):
        logging.info("Test case 40.30: Identical flows")
        in_port, out_port = testutils.openflow_ports(2)
        # delete all entries
        testutils.delete_all_flows(self.controller)

        logging.info(
            "Inserting flow: flow-mod cmd=add,table=0,prio=15 in_port={0}"
            " apply:output={1}".format(in_port, out_port))
        table_id = testutils.test_param_get("table", 0)
        request = ofp.message.flow_add(
            table_id=table_id,
            match=ofp.match([ofp.oxm.in_port(in_port)]),
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=15)
        self.controller.message_send(request)
        testutils.do_barrier(self.controller)

        # send matching packets
        pkt = str(testutils.simple_icmp_packet())
        times = 10
        for i in range(10):
            self.dataplane.send(in_port, pkt)
        flow_stats = testutils.get_flow_stats(self, ofp.match())
        for entry in flow_stats:
            logging.debug(entry.show())
        self.assertEqual(len(flow_stats), 1)
        self.assertEqual(flow_stats[0].packet_count, times)


@testutils.group('TestSuite40')
class NoTableAdd(base_tests.SimpleProtocol):
    """
    Test case 40.40: No table to add
    Verify that flow table full error messages are generated.
    """

    def runTest(self):
        logging.info("Test case 40.40: No table to add")
        # delete all entries
        testutils.delete_all_flows(self.controller)
        in_port, out_port = testutils.openflow_ports(2)

        logging.info(
            "Inserting flow: flow-mod cmd=add,table=0,prio=15 in_port={0}"
            " apply:output={1}".format(in_port, out_port))
        for i in range(15):
            table_id = testutils.test_param_get("table", 0)
            request = ofp.message.flow_add(
                table_id=table_id,
                match=ofp.match([ofp.oxm.in_port(in_port)]),
                instructions=[
                    ofp.instruction.apply_actions([ofp.action.output(out_port)]),
                ],
                buffer_id=ofp.OFP_NO_BUFFER,
                out_port=ofp.OFPP_ANY,
                out_group=ofp.OFPG_ANY,
                priority=i)
            self.controller.message_send(request)
            testutils.do_barrier(self.controller)

        # read error message
        response, _ = self.controller.poll(ofp.message.flow_mod_failed_error_msg)
        self.assertTrue(response is not None,
                        "No error message was received")
        self.assertEqual(response.code, ofp.OFPFMFC_TABLE_FULL)


@testutils.group('TestSuite40')
class NeverValidOutputPort(base_tests.SimpleProtocol):
    """
    Test case 40.50: Never valid output port
    Verify that adding a flow with a never valid output port number triggers
    correct error
    """

    def runTest(self):
        logging.info("Test case 40.50: Never valid output port")
        # delete all entries
        testutils.delete_all_flows(self.controller)
        # serach unavalible port
        port_nonvalid = 0
        for port_nonvalid in range(30):
            _, port_config, _ = testutils.port_config_get(self.controller, port_nonvalid)
            print(port_config)
            if port_config is None:
                break
        logging.info(
            "Inserting flow: flow-mod cmd=add,table=0,prio=15 "
            "apply:output={}".format(port_nonvalid))

        table_id = testutils.test_param_get("table", 0)
        request = ofp.message.flow_add(
            table_id=table_id,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(port_nonvalid)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=15,
        )
        self.controller.message_send(request)
        testutils.do_barrier(self.controller)

        # read error message
        response, _ = self.controller.poll(ofp.message.bad_action_error_msg)
        self.assertTrue(response is not None,
                        "No error message was received")
        self.assertEqual(response.code, ofp.OFPBAC_BAD_OUT_PORT)


@testutils.group('TestSuite40')
class ModifyNonExistentFlow(base_tests.SimpleProtocol):
    """
    Test case 40.80: Modify non-existent flow
    Verify that modifying a non-existent flow adds the flow with zeroed
    counters.
    """

    def runTest(self):
        logging.info("Test case 40.80: Modify non-existent flow")
        in_port, out_port = testutils.openflow_ports(2)
        # delete all entries
        testutils.delete_all_flows(self.controller)

        logging.info(
            "Inserting flow: flow-mod cmd=mod,table=0,prio=15 in_port={0}"
            " apply:output={1}".format(in_port, out_port))
        table_id = 0
        match_req = ofp.match([ofp.oxm.in_port(in_port)])
        request = ofp.message.flow_modify(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=15)
        self.controller.message_send(request)
        testutils.do_barrier(self.controller)

        # verilog the flow entry was added and its counter was 0
        flow_stats = testutils.get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 0)
        testutils.verify_flow_stats(self, match_req, pkts=0)


@testutils.group('TestSuite40')
class ModifyAction(base_tests.SimpleDataPlane):
    """
    Test case 40.90: Modify action preserves counters
    Verify that modifying the action of a flow does not reset counters
    """

    def runTest(self):
        logging.info("Test case 40.90: Modify action preserves counters")
        in_port, out_port1, out_port2 = testutils.openflow_ports(3)
        # delete all entries
        testutils.delete_all_flows(self.controller)

        logging.info(
            "Inserting flow: flow-mod cmd=add,table=0,prio=15 in_port={0}"
            " apply:output={1}".format(in_port, out_port1))
        table_id = 0
        match_req = ofp.match([ofp.oxm.in_port(in_port)])
        request = ofp.message.flow_add(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port1)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=15
        )
        self.controller.message_send(request)
        testutils.do_barrier(self.controller)
        pkg_num = 10
        FuncUtils.send_packets(self, testutils.simple_icmp_packet(), in_port, pkg_num)

        # modify the flow
        logging.info(
            "Inserting flow: flow-mod cmd=mod,table=0,prio=15 in_port={0}"
            " apply:output={1}".format(in_port, out_port2))
        table_id = 0
        match_req = ofp.match([ofp.oxm.in_port(in_port)])
        request = ofp.message.flow_modify(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port2)]),
            ],
        )
        self.controller.message_send(request)
        testutils.do_barrier(self.controller)

        # verify flow entry pkg num
        flow_stats = testutils.get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 1)
        testutils.verify_flow_stats(self, match_req, pkts=pkg_num)


@testutils.group('TestSuite40')
class ModifyStrictAction(base_tests.SimpleDataPlane):
    """
    Test case 40.100: Modify_strict of action preserves counters
    Verify that modifying the action of a flow does not reset counters for
    modify_strict
    """

    def runTest(self):
        logging.info("Test case 40.100: Modify_strict of action preserves counters")
        in_port, out_port1, out_port2 = testutils.openflow_ports(3)
        # delete all entries
        testutils.delete_all_flows(self.controller)

        logging.info(
            "Inserting flow: flow-mod cmd=add,table=0,prio=15 in_port={0}"
            " apply:output={1}".format(in_port, out_port1))
        table_id = 0
        match_req = ofp.match([ofp.oxm.in_port(in_port)])
        request = ofp.message.flow_add(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port1)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=15
        )
        self.controller.message_send(request)
        testutils.do_barrier(self.controller)

        pkg_num = 10
        FuncUtils.send_packets(self, testutils.simple_icmp_packet(), in_port, pkg_num)

        # modify the flow
        logging.info(
            "Inserting flow: flow-mod cmd=mod,table=0,prio=15 in_port={0}"
            " apply:output={1}".format(in_port, out_port2))
        table_id = 0
        match_req = ofp.match([ofp.oxm.in_port(in_port)])
        request = ofp.message.flow_modify_strict(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port2)]),
            ],
        )
        self.controller.message_send(request)
        testutils.do_barrier(self.controller)

        # verify flow entry pkg num
        flow_stats = testutils.get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 1)
        testutils.verify_flow_stats(self, match_req, pkts=pkg_num)


@testutils.group('TestSuite40')
class DeleteNonexistentFlow(base_tests.SimpleProtocol):
    """
    Test case 40.110: Delete non-existent flow
    Verify that deleting a non-existent flow does not generate an error
    """

    def runTest(self):
        logging.info("Test case 40.110: Delete non-existent flow")
        in_port, out_port = testutils.openflow_ports(2)
        # delete all entries
        testutils.delete_all_flows(self.controller)

        logging.info(
            "Inserting flow: flow-mod cmd=del,table=0,prio=15 in_port={0}"
            " apply:output={1}".format(in_port, out_port))
        table_id = 0
        match_req = ofp.match([ofp.oxm.in_port(in_port)])
        request = ofp.message.flow_delete(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=15
        )
        self.controller.message_send(request)
        testutils.do_barrier(self.controller)

        error_msg, _ = self.controller.poll(ofp.OFPT_ERROR)
        self.assertTrue(error_msg is None, "Error message was received")


@testutils.group('TestSuite40')
class DeleteFlowWithFlag(base_tests.SimpleProtocol):
    """
    Test case 40.120: Delete non-existent flow
    Verify that deleting a non-existent flow does not generate an error
    """

    def runTest(self):
        logging.info("Test case 40.110: Delete non-existent flow")
        in_port, out_port = testutils.openflow_ports(2)
        # delete all entries
        testutils.delete_all_flows(self.controller)

        logging.info(
            "Inserting flow: flow-mod cmd=del,table=0,prio=15 in_port={0}"
            " apply:output={1}".format(in_port, out_port))
        table_id = 0
        match_req = ofp.match([ofp.oxm.in_port(in_port)])
        request = ofp.message.flow_add(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=15
        )
        self.controller.message_send(request)
        testutils.do_barrier(self.controller)

        logging.info(
            "Inserting flow: flow-mod cmd=del,table=0,prio=15 in_port={0} flags=OFPFF_SEND_FLOW_REM"
            " apply:output={1}".format(in_port, out_port))
        table_id = 0
        match_req = ofp.match([ofp.oxm.in_port(in_port)])
        request = ofp.message.flow_add(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            flags=ofp.OFPFF_SEND_FLOW_REM,
            priority=15
        )
        self.controller.message_send(request)
        testutils.do_barrier(self.controller)

        testutils.delete_all_flows(self.controller)
        error_msg, _ = self.controller.poll(ofp.message.flow_removed)
        self.assertTrue(error_msg is not None, "Error message was received")


@testutils.group('TestSuite40')
class DeleteWithoutWildcards(base_tests.SimpleProtocol):
    """


    """

    def runTest(self):
        logging.info("Test case 40.140: Delete without wildcards")
        in_port, out_port = testutils.openflow_ports(2)
        # delete all entries
        testutils.delete_all_flows(self.controller)

        logging.info(
            "Inserting flow:  flow-mod cmd=add,table=0,prio=15 in_port={0},"
            "eth_dst=00:13:3b:0f:42:1c apply: output={1}".format(in_port, out_port))
        table_id = 0
        match_req = ofp.match([ofp.oxm.in_port(in_port),
                               ofp.oxm.eth_dst("00:13:3b:0f:42:1c")])
        request = ofp.message.flow_add(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=15
        )
        self.controller.message_send(request)

        logging.info(
            "Inserting flow: flow-mod cmd=dels,table=0,prio=15 in_port={0},"
            "eth_dst=00:13:3b:0f:42:1c apply: output={1}".format(in_port, out_port))
        table_id = 0
        request = ofp.message.flow_delete(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=15
        )
        self.controller.message_send(request)
        testutils.do_barrier(self.controller)

        #verify the num of flow entry is 1
        flow_stats = testutils.get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 0)

        logging.info(
            "Inserting flow:  flow-mod cmd=add,table=0,prio=15 in_port={0},"
            "eth_dst=00:13:3b:0f:42:1c apply: output={1}".format(in_port, out_port))
        table_id = 0
        match_req = ofp.match([ofp.oxm.in_port(in_port),
                               ofp.oxm.eth_dst("00:13:3b:0f:42:1c")])
        request = ofp.message.flow_add(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=15
        )
        self.controller.message_send(request)

        logging.info(
            "Inserting flow: flow-mod cmd=dels,table=0,prio=15 in_port={0},"
            "eth_dst=00:13:3b:0f:42:1c apply: output={1}".format(in_port, out_port))
        table_id = 0
        request = ofp.message.flow_delete_strict(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=15
        )
        self.controller.message_send(request)
        testutils.do_barrier(self.controller)

        #verify the num of flow entry is 1
        flow_stats = testutils.get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 0)


@testutils.group('TestSuite40')
class DeleteWithWildcardsSet(base_tests.SimpleProtocol):
    """


    """

    def runTest(self):
        logging.info("Test case 40.150: Delete with wildcards set")
        in_port, out_port = testutils.openflow_ports(2)
        # delete all entries
        testutils.delete_all_flows(self.controller)

        logging.info(
            "Inserting flow:  flow-mod cmd=add,table=0,prio=15 in_port={0},"
            "apply: output={1}".format(in_port, out_port))
        table_id = 0
        match_req = ofp.match([ofp.oxm.in_port(in_port)])
        request = ofp.message.flow_add(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=15
        )
        self.controller.message_send(request)

        logging.info(
            "Inserting flow:  flow-mod cmd=add,table=0,prio=14 in_port={0},"
            "eth_dst=00:13:3b:0f:42:1c apply: output={1}".format(in_port, out_port))
        table_id = 0
        match_req = ofp.match([ofp.oxm.in_port(in_port),
                               ofp.oxm.eth_dst("00:13:3b:0f:42:1c")])
        request = ofp.message.flow_add(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=14
        )
        self.controller.message_send(request)

        logging.info(
            "Inserting flow:  flow-mod cmd=add,table=0,prio=15 in_port={0},"
            "eth_dst=00:13:3b:0f:42:1c apply: output={1}".format(in_port, out_port))
        table_id = 0
        match_req = ofp.match([ofp.oxm.in_port(in_port),
                               ofp.oxm.eth_dst("00:13:3b:0f:42:1c")])
        request = ofp.message.flow_add(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
        )
        self.controller.message_send(request)
        testutils.do_barrier()

        #verify the num of flow entry is 0
        flow_stats = testutils.get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 0)


@testutils.group('TestSuite40')
class StrictDeleteWithWildcardsSet(base_tests.SimpleProtocol):
    """


    """

    def runTest(self):
        logging.info("Test case 40.160: Strict Delete with wildcards set")
        in_port, out_port = testutils.openflow_ports(2)
        # delete all entries
        testutils.delete_all_flows(self.controller)

        logging.info(
            "Inserting flow:  flow-mod cmd=add,table=0,prio=15 in_port={0},"
            "apply: output={1}".format(in_port, out_port))
        table_id = 0
        match_req = ofp.match([ofp.oxm.in_port(in_port)])
        request = ofp.message.flow_add(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=15
        )
        self.controller.message_send(request)

        logging.info(
            "Inserting flow:  flow-mod cmd=add,table=0,prio=14 in_port={0},"
            "eth_dst=00:13:3b:0f:42:1c apply: output={1}".format(in_port, out_port))
        table_id = 0
        match_req = ofp.match([ofp.oxm.in_port(in_port),
                               ofp.oxm.eth_dst("00:13:3b:0f:42:1c")])
        request = ofp.message.flow_add(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
            priority=14
        )
        self.controller.message_send(request)

        logging.info(
            "Inserting flow:  flow-mod cmd=add,table=0,prio=15 in_port={0},"
            "eth_dst=00:13:3b:0f:42:1c apply: output={1}".format(in_port, out_port))
        table_id = 0
        match_req = ofp.match([ofp.oxm.in_port(in_port),
                               ofp.oxm.eth_dst("00:13:3b:0f:42:1c")])
        request = ofp.message.flow_add(
            table_id=table_id,
            match=match_req,
            instructions=[
                ofp.instruction.apply_actions([ofp.action.output(out_port)]),
            ],
            buffer_id=ofp.OFP_NO_BUFFER,
            out_port=ofp.OFPP_ANY,
            out_group=ofp.OFPG_ANY,
        )
        self.controller.message_send(request)
        testutils.do_barrier()

        #verify the num of flow entry is 0
        flow_stats = testutils.get_flow_stats(self, ofp.match())
        self.assertEqual(len(flow_stats), 0)


