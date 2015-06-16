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

def match_send_flowadd(self, match, priority, port):
    msg = ofp.message.flow_add()
    msg.out_port = ofp.OFPP_ANY
    # msg.cookie = random.randint(0,9007199254740992)
    msg.buffer_id = 0xffffffff
    msg.match = match
    if priority != None :
        msg.priority = priority
    act = ofp.action.output()
    act.port = port 
    msg.instructions.append(act)
    self.controller.message_send(msg)
    do_barrier(self.controller)

def exact_match(self,of_ports,priority=None):
# Generate ExactMatch flow .

    #Create a simple tcp packet and generate exact flow match from it.
    pkt_exactflow = simple_tcp_packet()
    match = parse.packet_to_flow_match(pkt_exactflow)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")
    match.in_port = of_ports[0]
    #match.ipv4_src = 1
    match.wildcards=0
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_exactflow,match)

def exact_match_with_prio(self,of_ports,priority=None):
    # Generate ExactMatch with action output to port 2

    #Create a simple tcp packet and generate exact flow match from it.
    pkt_exactflow = simple_tcp_packet()
    match = parse.packet_to_flow_match(pkt_exactflow)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")
    match.in_port = of_ports[0]
    #match.ipv4_src = 1
    match.wildcards=0
    match_send_flowadd(self, match, priority, of_ports[2])
    return (pkt_exactflow,match)         
       

def match_all_except_source_address(self,of_ports,priority=None):
# Generate Match_All_Except_Source_Address flow
        
    #Create a simple tcp packet and generate match all except src address flow.
    pkt_wildcardsrc= simple_tcp_packet()
    match1 = parse.packet_to_flow_match(pkt_wildcardsrc)
    self.assertTrue(match1 is not None, "Could not generate flow match from pkt")
    match1.in_port = of_ports[0]
    #match1.ipv4_src = 1
    match1.wildcards = ofp.OFPFW_DL_SRC
    match_send_flowadd(self, match1, priority, of_ports[1])
    return (pkt_wildcardsrc,match1)

def match_ethernet_src_address(self,of_ports,priority=None):
    #Generate Match_Ethernet_SrC_Address flow

    #Create a simple tcp packet and generate match on ethernet src address flow
    pkt_MatchSrc = simple_eth_packet(eth_src='00:01:01:01:01:01')
    match = parse.packet_to_flow_match(pkt_MatchSrc)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")
    match.wildcards = ofp.OFPFW_ALL ^ofp.OFPFW_DL_SRC
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_MatchSrc,match)
      
def match_ethernet_dst_address(self,of_ports,priority=None):
    #Generate Match_Ethernet_Dst_Address flow

    #Create a simple tcp packet and generate match on ethernet dst address flow
    pkt_matchdst = simple_eth_packet(eth_dst='00:01:01:01:01:01')
    match = parse.packet_to_flow_match(pkt_matchdst)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")

    match.wildcards = ofp.OFPFW_ALL ^ofp.OFPFW_DL_DST
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_matchdst,match)

def wildcard_all(self,of_ports,priority=None):
# Generate a Wildcard_All Flow 

    #Create a simple tcp packet and generate wildcard all flow match from it.  
    pkt_wildcard = simple_tcp_packet()
    match2 = parse.packet_to_flow_match(pkt_wildcard)
    self.assertTrue(match2 is not None, "Could not generate flow match from pkt")
    match2.wildcards=(1<<20)-1
    match2.in_port = of_ports[0]
    match_send_flowadd(self, match2, priority, of_ports[1])
    return (pkt_wildcard,match2)

def wildcard_all_except_ingress(self,of_ports,priority=None):
# Generate Wildcard_All_Except_Ingress_port flow

    #Create a simple tcp packet and generate wildcard all except ingress_port flow.
    pkt_matchingress = simple_tcp_packet()
    match3 = parse.packet_to_flow_match(pkt_matchingress)
    self.assertTrue(match3 is not None, "Could not generate flow match from pkt")
    match3.wildcards = ofp.OFPFW_ALL-ofp.OFPFW_IN_PORT
    match3.in_port = of_ports[0]
    match_send_flowadd(self, match3, priority, of_ports[1])
    return (pkt_matchingress,match3)

def wildcard_all_except_ingress1(self,of_ports,priority=None):
# Generate Wildcard_All_Except_Ingress_port flow with action output to port egress_port 2 

    #Create a simple tcp packet and generate wildcard all except ingress_port flow.
    pkt_matchingress = simple_tcp_packet()
    match3 = parse.packet_to_flow_match(pkt_matchingress)
    self.assertTrue(match3 is not None, "Could not generate flow match from pkt")
    match3.wildcards = ofp.OFPFW_ALL-ofp.OFPFW_IN_PORT
    match3.in_port = of_ports[0]
    match_send_flowadd(self, match3, priority, of_ports[2])
    return (pkt_matchingress,match3)


def match_vlan_id(self,of_ports,priority=None):
    #Generate Match_Vlan_Id

    #Create a simple tcp packet and generate match on ethernet dst address flow
    pkt_matchvlanid = simple_tcp_packet(dl_vlan_enable=True,vlan_vid=1)
    match = parse.packet_to_flow_match(pkt_matchvlanid)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")

    match.wildcards = ofp.OFPFW_ALL^ofp.OFPFW_DL_TYPE ^ofp.OFPFW_DL_VLAN
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_matchvlanid,match)

def match_vlan_pcp(self,of_ports,priority=None):
    #Generate Match_Vlan_Priority

    #Create a simple tcp packet and generate match on ethernet dst address flow
    pkt_matchvlanpcp = simple_tcp_packet(dl_vlan_enable=True,vlan_vid=1,vlan_pcp=5)
    match = parse.packet_to_flow_match(pkt_matchvlanpcp)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")

    match.wildcards = ofp.OFPFW_ALL ^ofp.OFPFW_DL_TYPE^ofp.OFPFW_DL_VLAN^ofp.OFPFW_DL_VLAN_PCP 
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_matchvlanpcp,match)


def match_mul_l2(self,of_ports,priority=None):
    #Generate Match_Mul_L2 flow

    #Create a simple eth packet and generate match on ethernet protocol flow
    pkt_mulL2 = simple_eth_packet(eth_type=0x88cc,eth_src='00:01:01:01:01:01',eth_dst='00:01:01:01:01:02')
    match = parse.packet_to_flow_match(pkt_mulL2)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")

    match.wildcards = ofp.OFPFW_ALL ^ofp.OFPFW_DL_TYPE ^ofp.OFPFW_DL_DST ^ofp.OFPFW_DL_SRC
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_mulL2,match)


def match_mul_l4(self,of_ports,priority=None):
    #Generate Match_Mul_L4 flow

        #Create a simple tcp packet and generate match on tcp protocol flow
    pkt_mulL4 = simple_tcp_packet(tcp_sport=111,tcp_dport=112)
    match = parse.packet_to_flow_match(pkt_mulL4)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")
    match.wildcards = ofp.OFPFW_ALL^ofp.OFPFW_DL_TYPE ^ofp.OFPFW_NW_PROTO^ofp.OFPFW_TP_SRC ^ofp.OFPFW_TP_DST 
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_mulL4,match)  

def match_ip_tos(self,of_ports,priority=None):
    #Generate a Match on IP Type of service flow

    #Create a simple tcp packet and generate match on Type of service 
    pkt_iptos = simple_tcp_packet(ip_tos=28)
    match = parse.packet_to_flow_match(pkt_iptos)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")

    match.wildcards = ofp.OFPFW_ALL^ofp.OFPFW_DL_TYPE^ofp.OFPFW_NW_PROTO ^ofp.OFPFW_NW_TOS
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_iptos,match)

def match_ip_protocol(self,of_ports,priority=None):
    #Generate a Match on IP Protocol

    #Create a simple tcp packet and generate match on Type of service 
    pkt_iptos = simple_tcp_packet()
    match = parse.packet_to_flow_match(pkt_iptos)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")

    match.wildcards = ofp.OFPFW_ALL^ofp.OFPFW_DL_TYPE^ofp.OFPFW_NW_PROTO 
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_iptos,match)

def match_tcp_src(self,of_ports,priority=None):
    #Generate Match_Tcp_Src

    #Create a simple tcp packet and generate match on tcp source port flow
    pkt_matchtSrc = simple_tcp_packet(tcp_sport=111)
    match = parse.packet_to_flow_match(pkt_matchtSrc)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")

    match.wildcards = ofp.OFPFW_ALL^ofp.OFPFW_DL_TYPE ^ofp.OFPFW_NW_PROTO ^ofp.OFPFW_TP_SRC  
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_matchtSrc,match)  

def match_tcp_dst(self,of_ports,priority=None):
    #Generate Match_Tcp_Dst

    #Create a simple tcp packet and generate match on tcp destination port flow
    pkt_matchdst = simple_tcp_packet(tcp_dport=112)
    match = parse.packet_to_flow_match(pkt_matchdst)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")

    match.wildcards = ofp.OFPFW_ALL ^ofp.OFPFW_DL_TYPE^ofp.OFPFW_NW_PROTO^ofp.OFPFW_TP_DST  
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_matchdst,match)        


def match_udp_src(self,of_ports,priority=None):
    #Generate Match_Udp_Src

    #Create a simple udp packet and generate match on udp source port flow
    pkt_matchtSrc = simple_udp_packet(udp_sport=111)
    match = parse.packet_to_flow_match(pkt_matchtSrc)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")

    match.wildcards = ofp.OFPFW_ALL^ofp.OFPFW_DL_TYPE ^ofp.OFPFW_NW_PROTO ^ofp.OFPFW_TP_SRC  
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_matchtSrc,match)  

def match_udp_dst(self,of_ports,priority=None):
    #Generate Match_Udp_Dst

    #Create a simple udp packet and generate match on udp destination port flow
    pkt_matchdst = simple_udp_packet(udp_dport=112)
    match = parse.packet_to_flow_match(pkt_matchdst)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")

    match.wildcards = ofp.OFPFW_ALL ^ofp.OFPFW_DL_TYPE^ofp.OFPFW_NW_PROTO^ofp.OFPFW_TP_DST  
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_matchdst,match)        


def match_icmp_type(self,of_ports,priority=None):
    #Generate Match_Icmp_Type

    #Create a simple icmp packet and generate match on icmp type flow
    pkt_match = simple_icmp_packet(icmp_type=1)
    match = parse.packet_to_flow_match(pkt_match)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")

    match.wildcards = ofp.OFPFW_ALL^ofp.OFPFW_DL_TYPE ^ofp.OFPFW_NW_PROTO ^ofp.OFPFW_TP_SRC  
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_match, match)

def match_icmp_code(self,of_ports,priority=None):
    #Generate Match_Icmp_Code

    #Create a simple icmp packet and generate match on icmp code flow
    pkt_match = simple_icmp_packet(icmp_code=3)
    match = parse.packet_to_flow_match(pkt_match)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")

    match.wildcards = ofp.OFPFW_ALL^ofp.OFPFW_DL_TYPE ^ofp.OFPFW_NW_PROTO ^ofp.OFPFW_TP_DST
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_match, match)  

def match_arp_opcode(self,of_ports,priority=None):
    #Generate Match_Arp_Opcode

    #Create a simple arp packet and generate match on arp opcode 
    pkt_match = simple_arp_packet(arp_op=1)
    match = parse.packet_to_flow_match(pkt_match)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")

    match.wildcards = ofp.OFPFW_ALL^ofp.OFPFW_DL_TYPE^ofp.OFPFW_NW_PROTO
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_match, match)  

def match_arp_sender(self,of_ports,priority=None):
    #Generate Match_Arp_Sender

    #Create a simple icmp packet and generate match on arp sender flow
    pkt_match = simple_arp_packet()
    match = parse.packet_to_flow_match(pkt_match)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")

    match.wildcards = ofp.OFPFW_ALL^ofp.OFPFW_DL_TYPE ^ofp.OFPFW_NW_PROTO ^ofp.OFPFW_NW_SRC_MASK
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_match, match)  

def match_arp_target(self,of_ports,priority=None):
    #Generate Match_Arp_Target

    #Create a simple icmp packet and generate match on arp target flow
    pkt_match = simple_arp_packet()
    match = parse.packet_to_flow_match(pkt_match)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")

    match.wildcards = ofp.OFPFW_ALL^ofp.OFPFW_DL_TYPE ^ofp.OFPFW_NW_PROTO ^ofp.OFPFW_NW_DST_MASK
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_match, match)  


def match_ethernet_type(self,of_ports,priority=None):
    #Generate a Match_Ethernet_Type flow

    #Create a simple tcp packet and generate match on ethernet type flow
    pkt_matchtype = simple_eth_packet(eth_type=0x88cc)
    match = parse.packet_to_flow_match(pkt_matchtype)
    self.assertTrue(match is not None, "Could not generate flow match from pkt")

    match.wildcards = ofp.OFPFW_ALL ^ofp.OFPFW_DL_TYPE
    match_send_flowadd(self, match, priority, of_ports[1])
    return (pkt_matchtype,match)

   
   

def strict_modify_flow_action(self,egress_port,match,priority=None):
# Strict Modify the flow Action 
        
    #Create a flow_mod message , command MODIFY_STRICT
    msg5 = ofp.message.flow_modify_strict()
    msg5.match = match
    msg5.cookie = random.randint(0,9007199254740992)
    msg5.buffer_id = 0xffffffff
    act5 = ofp.action.output()
    act5.port = egress_port
    msg5.actions.append(act5)

    if priority != None :
        msg5.priority = priority

    # Send the flow with action A'
    self.controller.message_send (msg5)
    do_barrier(self.controller)

def modify_flow_action(self,of_ports,match,priority=None):
# Modify the flow action
        
    #Create a flow_mod message , command MODIFY 
    msg8 = ofp.message.flow_modify()
    msg8.match = match
    msg8.cookie = random.randint(0,9007199254740992)
    #out_port will be ignored for flow adds and flow modify (here for test-case Add_Modify_With_Outport)
    msg8.out_port = of_ports[3]
    msg8.buffer_id = 0xffffffff
    act8 = ofp.action.output()
    act8.port = of_ports[2]
    msg8.actions.append(act8)

    if priority != None :
        msg8.priority = priority

    # Send the flow with action A'
    self.controller.message_send (msg8)
    do_barrier(self.controller)

def enqueue(self,ingress_port,egress_port,egress_queue_id):
#Generate a flow with enqueue action i.e output to a queue configured on a egress_port

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
    act.port     = egress_port
    act.queue_id = egress_queue_id
    request.actions.append(act)
    
    logging.info("Inserting flow")
    self.controller.message_send(request)
    do_barrier(self.controller)
    return (pkt,match)


###########################   Verify Stats Functions   ###########################################################################################
def get_flowstats(self,match):
    # Generate flow_stats request
    
    stat_req = ofp.message.flow_stats_request()
    stat_req.match = match
    stat_req.table_id = 0xff
    stat_req.out_port = ofp.OFPP_NONE

    logging.info("Sending stats request")
    response, pkt = self.controller.transact(stat_req,
                                                     timeout=5)
    self.assertTrue(response is not None,"No response to stats request")


def get_portstats(self,port_num):

# Return all the port counters in the form a tuple 
    entries = get_port_stats(self, port_num)
    rx_pkts=0
    tx_pkts=0
    rx_byts=0
    tx_byts=0
    rx_drp =0
    tx_drp = 0
    rx_err=0
    tx_err =0 
    rx_fr_err=0
    rx_ovr_err=0
    rx_crc_err=0
    collisions = 0
    tx_err=0


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
        collisions+= obj.collisions
        tx_err += obj.tx_errors

    return (rx_pkts,tx_pkts,rx_byts,tx_byts,rx_drp,tx_drp,rx_err,tx_err,rx_fr_err,rx_ovr_err,rx_crc_err,collisions,tx_err)

def get_queuestats(self,port_num,queue_id):
#Generate Queue Stats request 

    request = ofp.message.queue_stats_request()
    request.port_no  = port_num
    request.queue_id = queue_id
    (queue_stats, p) = self.controller.transact(request)
    self.assertNotEqual(queue_stats, None, "Queue stats request failed")

    return (queue_stats,p)

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
        current_matched  += obj.matched_count
        current_active += obj.active_count

    return (current_lookedup,current_matched,current_active)



def verify_tablestats(self,expect_lookup=None,expect_match=None,expect_active=None):

    stat_req = ofp.message.table_stats_request()
    
    for i in range(0,100):

        logging.info("Sending stats request")
        # TODO: move REPLY_MORE handling to controller.transact?
        response, pkt = self.controller.transact(stat_req,
                                                     timeout=5)
        self.assertTrue(response is not None,"No response to stats request")

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

    if expect_lookup != None :
        self.assertLessEqual(expect_lookup, lookedup, "lookup counter is not incremented properly")
    if expect_match != None :
        self.assertLessEqual(expect_match, matched, "matched counter is not incremented properly")
    if expect_active != None :
        self.assertLessEqual(expect_active, active ,"active counter is not incremented properly")


############################## Various delete commands #############################################################################################

def strict_delete(self,match,priority=None):
# Issue Strict Delete 
        
    #Create flow_mod message, command DELETE_STRICT
    msg4 = ofp.message.flow_delete_strict()
    msg4.out_port = ofp.OFPP_NONE
    msg4.buffer_id = 0xffffffff
    msg4.match = match

    if priority != None :
        msg4.priority = priority
    self.controller.message_send(msg4)
    do_barrier(self.controller)



def nonstrict_delete(self,match,priority=None):
# Issue Non_Strict Delete 
        
    #Create flow_mod message, command DELETE
    msg6 = ofp.message.flow_delete()
    msg6.out_port = ofp.OFPP_NONE
    msg6.buffer_id = 0xffffffff
    msg6.match = match

    if priority != None :
        msg6.priority = priority

    self.controller.message_send(msg6)
    do_barrier(self.controller)


###########################################################################################################################################################

def send_packets(obj, pkt, ingress_port, num):
#Send Packets on a specified ingress_port

    for i in range(num):
        obj.dataplane.send(ingress_port, str(pkt))


def sw_supported_actions(parent,use_cache=False):
#Returns the switch's supported actions

    cache_supported_actions = None
    if cache_supported_actions is None or not use_cache:
        request = ofp.message.features_request()
        (reply, pkt) = parent.controller.transact(request)
        parent.assertTrue(reply is not None, "Did not get response to ftr req")
        cache_supported_actions = reply.actions
    return cache_supported_actions

##############################################################################################################################################################

def add_simple_flow(self,table_id=0, in_port=None,out_port=None,priority=15,flags=0):
    #add simple entry that forward data from in_port to out_port
    match_req = None
    instruction_req = None
    if in_port != None:
        match_req =ofp.match([ofp.oxm.in_port(in_port)])
    if out_port is not None:
        instruction_req=[ofp.instruction.apply_actions([ofp.action.output(out_port)])]


    request = ofp.message.flow_add(
        table_id=table_id,
        match= match_req,
        instructions= instruction_req,
        buffer_id=ofp.OFP_NO_BUFFER,
        out_port=ofp.OFPP_ANY,
        out_group=ofp.OFPG_ANY,
        priority=priority,
        flags = flags
    )
    self.controller.message_send(request)
    testutils.do_barrier(self.controller)

############################################################################################################
def dpctl_cmd_to_msg(cmd):
    """

    the funciton parse the cmd string and excute them in the oftest

    :rtype : object
    :param cmd: cmd string is a dtctl's parameter
                string format: command+ command param+ match + action
    :return: (matching message, metch , instruction)
    """
    # constants
    # logging.info("Excute cmd:" + cmd)
    print("Excute cmd:" + cmd)
    flow_mod_class = {'add': ofp.message.flow_add,
                      'del': ofp.message.flow_delete,
                      'dels': ofp.message.flow_delete_strict,
                      'mod': ofp.message.flow_modify,
                      'mods': ofp.message.flow_modify_strict}

    flow_mod_setting = {'cmd'  :ofp.message.flow_add,
                        'table': 0,
                        'prio': 0,
                        'flags': 0,
                        'out_group': ofp.OFPG_ANY,
                        'out_port': ofp.OFPP_ANY,
                        'buffer_id': ofp.OFP_NO_BUFFER
                        }
    match_class = {'eth_dst' : ofp.oxm.eth_dst,
                   'eth_src' : ofp.oxm.eth_src,
                   'in_port' : ofp.oxm.in_port,
                   'meta'    : ofp.oxm.metadata,
                   "udp_src" : ofp.oxm.udp_src,
                   "ip_src"  : ofp.oxm.ipv4_src,
                   "ip_dst"  : ofp.oxm.ipv4_dst,
                   "ip_proto": ofp.oxm.ip_proto,
                   "vlan_vid": ofp.oxm.vlan_vid,
                   "eth_type": ofp.oxm.eth_type,
                   "tcp_src" : ofp.oxm.tcp_src,
                   "tcp_dst" : ofp.oxm.tcp_dst,
                   }

    apply_action_class = {'output': ofp.action.output}

    cmd = re.sub("( )(\D)",'@\g<2>',cmd)
    cmd_list = cmd.split('@')
    print(cmd_list)

    match_param_str = None
    apply_action_param_str = None

    cmd_name = cmd_list[0]
    cmd_param_str = cmd_list[1].replace(',', ';')

    metadata = None
    goto_table = None
    for cmd_item in cmd_list[2:]:
        if cmd_item.startswith("apply:"):
            apply_action_param_str = cmd_item[cmd_item.find(":") + 1:].replace(',', ';')
        elif cmd_item.startswith("meta:"):
            metadata = string.atol(cmd_item[5:], 16)
        elif cmd_item.startswith("goto:"):
            goto_table = int(cmd_item[5:])
        else:
            match_param_str = re.sub("(,)([a-zA-Z_])",';\g<2>',cmd_item)

    cmd_param = {}
    match_param = {}
    apply_action_param = {}
    exec(cmd_param_str,{}, cmd_param)
    if match_param_str is not None:
        exec(match_param_str,{}, match_param)
    if apply_action_param_str is not None:
        exec(apply_action_param_str,{}, apply_action_param)

    # generate the reuqest message
    # match
    match_list = []
    for param in match_param.keys():
        match_list.append(match_class[param](match_param[param]))
    match_req = ofp.match(match_list)

    # actions
    apply_action_list = []
    for param in apply_action_param.keys():
        apply_action_list.append(apply_action_class[param](apply_action_param[param]))

    # instructions
    instruction_req = []
    instruction_req.append(ofp.instruction.apply_actions(apply_action_list))
    if metadata is not None:
        instruction_req.append(ofp.instruction.write_metadata(metadata))
    if goto_table is not None:
        instruction_req.append(ofp.instruction.goto_table(goto_table))

    # update command settings
    for item in flow_mod_setting.keys():
        if item in cmd_param.keys():
            flow_mod_setting[item] = cmd_param[item]

    request = flow_mod_class[flow_mod_setting['cmd']](
        table_id=cmd_param['table'],
        match=match_req,
        instructions=instruction_req,
        buffer_id=flow_mod_setting['buffer_id'],
        out_group=flow_mod_setting['out_group'],
        out_port=flow_mod_setting['out_port'],
        priority=flow_mod_setting['prio'],
        flags=flow_mod_setting['flags']
    )
    # print(request.show())
    return request, match_req, instruction_req
