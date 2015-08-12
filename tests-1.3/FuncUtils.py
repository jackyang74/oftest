""" Defined Some common functions used by Conformance tests -- OF-SWITCH 1.0.0 Testcases """

import sys
import copy
import random

import oftest.controller as controller
import ofp
import oftest.dataplane as dataplane
import oftest.parse as parse
import logging
import types
import re
import oftest.base_tests as base_tests
import oftest.testutils as testutils
from time import sleep
import string
#################### Functions for various types of flow_mod  ##########################################################################################


def strict_modify_flow_action(self, egress_port, match, priority=None):
    # Strict Modify the flow Action

    # Create a flow_mod message , command MODIFY_STRICT
    msg5 = ofp.message.flow_modify_strict()
    msg5.match = match
    msg5.cookie = random.randint(0, 9007199254740992)
    msg5.buffer_id = 0xffffffff
    act5 = ofp.action.output()
    act5.port = egress_port
    msg5.actions.append(act5)

    if priority != None:
        msg5.priority = priority

    # Send the flow with action A'
    self.controller.message_send(msg5)
    do_barrier(self.controller)


def modify_flow_action(self, of_ports, match, priority=None):
    # Modify the flow action

    # Create a flow_mod message , command MODIFY
    msg8 = ofp.message.flow_modify()
    msg8.match = match
    msg8.cookie = random.randint(0, 9007199254740992)
    # out_port will be ignored for flow adds and flow modify (here for test-case Add_Modify_With_Outport)
    msg8.out_port = of_ports[3]
    msg8.buffer_id = 0xffffffff
    act8 = ofp.action.output()
    act8.port = of_ports[2]
    msg8.actions.append(act8)

    if priority != None:
        msg8.priority = priority

    # Send the flow with action A'
    self.controller.message_send(msg8)
    do_barrier(self.controller)


def enqueue(self, ingress_port, egress_port, egress_queue_id):
    # Generate a flow with enqueue action i.e output to a queue configured on a egress_port

    pkt = simple_tcp_packet()
    match = packet_to_flow_match(self, pkt)
    match.wildcards &= ~ofp.OFPFW_IN_PORT
    self.assertTrue(match is not None,
                    "Could not generate flow match from pkt")

    match.in_port = ingress_port
    request = ofp.message.flow_add()
    request.match = match
    request.buffer_id = 0xffffffff
    act = ofp.action.enqueue()
    act.port = egress_port
    act.queue_id = egress_queue_id
    request.actions.append(act)

    logging.info("Inserting flow")
    self.controller.message_send(request)
    do_barrier(self.controller)
    return (pkt, match)


###########################   Verify Stats Functions   ###########################################################################################
def get_flowstats(self, match):
    # Generate flow_stats request

    stat_req = ofp.message.flow_stats_request()
    stat_req.match = match
    stat_req.table_id = 0xff
    stat_req.out_port = ofp.OFPP_NONE

    logging.info("Sending stats request")
    response, pkt = self.controller.transact(stat_req,
                                             timeout=5)
    self.assertTrue(response is not None, "No response to stats request")


def get_portstats(self, port_num):
    # Return all the port counters in the form a tuple
    entries = get_port_stats(self, port_num)
    rx_pkts = 0
    tx_pkts = 0
    rx_byts = 0
    tx_byts = 0
    rx_drp = 0
    tx_drp = 0
    rx_err = 0
    tx_err = 0
    rx_fr_err = 0
    rx_ovr_err = 0
    rx_crc_err = 0
    collisions = 0
    tx_err = 0

    for obj in entries:
        rx_pkts += obj.rx_packets
        tx_pkts += obj.tx_packets
        rx_byts += obj.rx_bytes
        tx_byts += obj.tx_bytes
        rx_drp += obj.rx_dropped
        tx_drp += obj.tx_dropped
        rx_err += obj.rx_errors
        rx_fr_err += obj.rx_frame_err
        rx_ovr_err += obj.rx_over_err
        rx_crc_err += obj.rx_crc_err
        collisions += obj.collisions
        tx_err += obj.tx_errors

    return (
        rx_pkts, tx_pkts, rx_byts, tx_byts, rx_drp, tx_drp, rx_err, tx_err, rx_fr_err, rx_ovr_err, rx_crc_err,
        collisions,
        tx_err)


def get_queuestats(self, port_num, queue_id):
    # Generate Queue Stats request

    request = ofp.message.queue_stats_request()
    request.port_no = port_num
    request.queue_id = queue_id
    (queue_stats, p) = self.controller.transact(request)
    self.assertNotEqual(queue_stats, None, "Queue stats request failed")

    return (queue_stats, p)


def get_tablestats(self):
    # Send Table_Stats request (retrieve current table counters )

    stat_req = ofp.message.table_stats_request()
    response, pkt = self.controller.transact(stat_req,
                                             timeout=5)
    self.assertTrue(response is not None,
                    "No response to stats request")
    current_lookedup = 0
    current_matched = 0
    current_active = 0

    for obj in response.entries:
        current_lookedup += obj.lookup_count
        current_matched += obj.matched_count
        current_active += obj.active_count

    return (current_lookedup, current_matched, current_active)


def verify_tablestats(self, expect_lookup=None, expect_match=None, expect_active=None):
    stat_req = ofp.message.table_stats_request()

    for i in range(0, 100):

        logging.info("Sending stats request")
        # TODO: move REPLY_MORE handling to controller.transact?
        response, pkt = self.controller.transact(stat_req,
                                                 timeout=5)
        self.assertTrue(response is not None, "No response to stats request")

        lookedup = 0
        matched = 0
        active = 0

        for item in response.entries:
            lookedup += item.lookup_count
            matched += item.matched_count
            active += item.active_count

        logging.info("Packets Looked up: %d", lookedup)
        logging.info("Packets matched: %d", matched)
        logging.info("Active flow entries: %d", active)

        if (expect_lookup == None or lookedup >= expect_lookup) and \
                (expect_match == None or matched >= expect_match) and \
                (expect_active == None or active >= expect_active):
            break

        sleep(0.1)

    if expect_lookup != None:
        self.assertLessEqual(expect_lookup, lookedup, "lookup counter is not incremented properly")
    if expect_match != None:
        self.assertLessEqual(expect_match, matched, "matched counter is not incremented properly")
    if expect_active != None:
        self.assertLessEqual(expect_active, active, "active counter is not incremented properly")


############################## Various delete commands #############################################################################################

def strict_delete(self, match, priority=None):
    # Issue Strict Delete

    # Create flow_mod message, command DELETE_STRICT
    msg4 = ofp.message.flow_delete_strict()
    msg4.out_port = ofp.OFPP_NONE
    msg4.buffer_id = 0xffffffff
    msg4.match = match

    if priority != None:
        msg4.priority = priority
    self.controller.message_send(msg4)
    do_barrier(self.controller)


def nonstrict_delete(self, match, priority=None):
    # Issue Non_Strict Delete

    # Create flow_mod message, command DELETE
    msg6 = ofp.message.flow_delete()
    msg6.out_port = ofp.OFPP_NONE
    msg6.buffer_id = 0xffffffff
    msg6.match = match

    if priority != None:
        msg6.priority = priority

    self.controller.message_send(msg6)
    do_barrier(self.controller)


###########################################################################################################################################################

def send_packets(obj, pkt, ingress_port, num):
    # Send Packets on a specified ingress_port

    for i in range(num):
        obj.dataplane.send(ingress_port, str(pkt))


def sw_supported_actions(parent, use_cache=False):
    # Returns the switch's supported actions

    cache_supported_actions = None
    if cache_supported_actions is None or not use_cache:
        request = ofp.message.features_request()
        (reply, pkt) = parent.controller.transact(request)
        parent.assertTrue(reply is not None, "Did not get response to ftr req")
        cache_supported_actions = reply.actions
    return cache_supported_actions


##############################################################################################################################################################

def add_simple_flow(self, table_id=0, in_port=None, out_port=None, priority=15, flags=0):
    # add simple entry that forward data from in_port to out_port
    match_req = None
    instruction_req = None
    if in_port != None:
        match_req = ofp.match([ofp.oxm.in_port(in_port)])
    if out_port is not None:
        instruction_req = [ofp.instruction.apply_actions([ofp.action.output(out_port)])]

    request = ofp.message.flow_add(
        table_id=table_id,
        match=match_req,
        instructions=instruction_req,
        buffer_id=ofp.OFP_NO_BUFFER,
        out_port=ofp.OFPP_ANY,
        out_group=ofp.OFPG_ANY,
        priority=priority,
        flags=flags
    )
    self.controller.message_send(request)
    testutils.do_barrier(self.controller)


############################################################################################################
def entry_mod(controller, message_class,
              match=None,
              instructions=None,
              buffer_id=ofp.OFP_NO_BUFFER,
              out_group=ofp.OFPG_ANY,
              out_port=ofp.OFPP_ANY,
              priority=0,
              flags=0):
    request = message_class(
        table_id=cmd_param['table'],
        match=match,
        instructions=instructions,
        buffer_id=buffer_id,
        out_group=out_group,
        out_port=out_port,
        priority=priority,
        flags=flags,
    )
    controller.message_send(request)


flow_mod_class = {'flow_add': ofp.message.flow_add,
                  'flow_del': ofp.message.flow_delete,
                  'flow_dels': ofp.message.flow_delete_strict,
                  'flow_mod': ofp.message.flow_modify,
                  'flow_mods': ofp.message.flow_modify_strict}


def flow_entry_install(controller, flow_type, match=None, instructions=None, prio=None, flags=None,
                       table_id=0,
                       hard_timeout=None,
                       idle_timeout=None,
                       out_group=ofp.OFPG_ANY,
                       out_port=ofp.OFPP_ANY,
                       buffer_id=ofp.OFP_NO_BUFFER):
    request = flow_mod_class[flow_type](
        table_id=table_id,
        match=match,
        instructions=instructions,
        buffer_id=buffer_id,
        out_group=out_group,
        out_port=out_port,
        priority=prio,
        flags=flags,
        hard_timeout=hard_timeout,
        idle_timeout=idle_timeout
    )
    controller.message_send(request)
    # print(request.show())
    return request
