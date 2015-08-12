# Distributed under the OpenFlow Software License (see LICENSE)
# Copyright (c) 2010 The Board of Trustees of The Leland Stanford Junior University
# Copyright (c) 2012, 2013 Big Switch Networks, Inc.
"""
Action test cases

These tests check the behavior of each type of action. The matches used are
exact-match, to satisfy the OXM prerequisites of the set-field actions.
These tests use a single apply-actions instruction.
"""

import logging

from oftest import config
import oftest.base_tests as base_tests
import ofp
from loxi.pp import pp

from oftest.testutils import *
from oftest.parse import parse_ipv6
import FuncUtils
import time


@group("standard")
class NoActionDrops(base_tests.SimpleDataPlane):
    """
    Verify that flows without a forward action drop matching packets

    TestCase 70.10: No action drops packet
    """

    def runTest(self):
        delete_all_flows(self.controller)
        # config
        in_port, out_port = openflow_ports(2)
        request = FuncUtils.flow_entry_install(self.controller,
                                               "flow_add",
                                               match=ofp.match([ofp.oxm.in_port(in_port)]))
        # tests
        pkt_num = 10
        pkt = str(simple_tcp_packet())
        for i in range(10):
            self.dataplane.send(in_port, pkt)

        verify_no_packet(self, pkt, out_port)
        verify_flow_stats(self, request.match, table_id=request.table_id, pkts=pkt_num)


@group("standard")
class ForwardALL(base_tests.SimpleDataPlane):
    """
    Verify implementation of the Forward: ALL function
    """

    def runTest(self):
        delete_all_flows(self.controller)

        # config
        in_port, out_port1, out_port2, out_port3 = openflow_ports(4)
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions(
                                         [ofp.action.output(ofp.OFPP_ALL)])]
                                     )

        # tests
        pkt = str(simple_tcp_packet())
        self.dataplane.send(in_port, pkt)

        verify_no_packet(self, pkt, in_port)
        verify_packets(self, pkt, [out_port1, out_port2, out_port3])


@group("standard")
class ForwardController(base_tests.SimpleDataPlane):
    """
    Verify implementation of the Forward: CONTROLLER function

    TestCase 70.40: Forward: Controller
    """

    def runTest(self):
        logging.info("TestCase 70.30: Forward: Controller")
        # delete all entries
        delete_all_flows(self.controller)

        in_port, out_port = openflow_ports(2)
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions(
                                         [ofp.action.output(
                                             port=ofp.OFPP_CONTROLLER,
                                             max_len=ofp.OFPCML_NO_BUFFER
                                         )])])

        pkt = str(simple_tcp_packet())
        self.dataplane.send(in_port, pkt)
        verify_packet_in(self, pkt, in_port, ofp.OFPR_ACTION)


@group("standard")
class ForwardTable(base_tests.SimpleDataPlane):
    """
    ForwardTable : Perform actions in flow table. Only for packet-out messages.
    If the output action.port in the packetout message = OFP.TABLE , then
    the packet implements the action specified in the matching flow of the FLOW-TABLE
    """

    def runTest(self):
        logging.info("Running Forward_Table test")

        # delete all entries
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)
        # add flow
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[ofp.instruction.apply_actions([ofp.action.output(out_port)])])
        # Create a packet out message
        pkt = str(simple_tcp_packet())
        pkt_out = ofp.message.packet_out()
        pkt_out.data = pkt
        pkt_out.in_port = in_port
        pkt_out.buffer_id = ofp.OFP_NO_BUFFER
        act = ofp.action.output()
        act.port = ofp.OFPP_TABLE
        pkt_out.actions.append(act)
        self.controller.message_send(pkt_out)

        # Verifying packet out message recieved on the expected dataplane port.
        verify_packets(self, pkt, [out_port])


@group("standard")
class ForwardInPort(base_tests.SimpleDataPlane):
    """
    Verify implementation of the Forward: INPORT function
    """

    def runTest(self):
        delete_all_flows(self.controller)
        in_port, out_port = openflow_ports(2)

        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=ofp.match([ofp.oxm.in_port(in_port)]),
                                     instructions=[
                                         ofp.instruction.apply_actions([ofp.action.output(ofp.OFPP_IN_PORT)])])
        # send packets
        pkt = str(simple_tcp_packet())
        self.dataplane.send(in_port, pkt)
        verify_packets(self, pkt, [in_port])


@group("standard")
class Output(base_tests.SimpleDataPlane):
    """
    Output to a single port
    """

    def runTest(self):
        in_port, out_port = openflow_ports(2)

        actions = [ofp.action.output(out_port)]

        pkt = simple_tcp_packet()

        logging.info("Running actions test for %s", pp(actions))

        delete_all_flows(self.controller)

        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=packet_to_flow_match(self, pkt),
                                     instructions=[ofp.instruction.apply_actions(actions)]
                                     )

        pktstr = str(pkt)

        logging.info("Sending packet, expecting output to port %d", out_port)
        self.dataplane.send(in_port, pktstr)
        verify_packets(self, pktstr, [out_port])


@group("standard")
class ForwardOutputMultiple(base_tests.SimpleDataPlane):
    """
    Output to three ports
    """

    def runTest(self):
        ports = openflow_ports(4)

        in_port = ports[0]
        out_ports = ports[1:4]

        actions = [ofp.action.output(x) for x in out_ports]

        pkt = simple_tcp_packet()

        logging.info("Running actions test for %s", pp(actions))

        delete_all_flows(self.controller)

        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=packet_to_flow_match(self, pkt),
                                     instructions=[ofp.instruction.apply_actions(actions)]
                                     )
        logging.info("Sending packet, expecting output to ports %r", out_ports)
        pktstr = str(pkt)
        self.dataplane.send(in_port, pktstr)
        verify_packets(self, pktstr, out_ports)


class BaseModifyPacketTest(base_tests.SimpleDataPlane):
    """
    Base class for action tests that modify a packet
    """

    def verify_modify(self, actions, pkt, exp_pkt):
        in_port, out_port = openflow_ports(2)

        actions = actions + [ofp.action.output(out_port)]

        logging.info("Running actions test for %s", pp(actions))

        delete_all_flows(self.controller)

        logging.info("Inserting flow")
        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=packet_to_flow_match(self, pkt),
                                     instructions=[ofp.instruction.apply_actions(actions)]
                                     )

        logging.info("Sending packet, expecting output to port %d", out_port)
        self.dataplane.send(in_port, str(pkt))
        verify_packets(self, str(exp_pkt), [out_port])


@group("optional")
class PushVlanVid(BaseModifyPacketTest):
    """
    Verify implementation of the Set VLAN ID action
    Push a vlan tag (vid=2, pcp=0)

    Derived from Verify implementation of the Set VLAN ID action
    """

    def runTest(self):
        actions = [ofp.action.push_vlan(ethertype=0x8100),
                   ofp.action.set_field(ofp.oxm.vlan_vid(2))]
        pkt = simple_tcp_packet()
        exp_pkt = simple_tcp_packet(dl_vlan_enable=True, vlan_vid=2, pktlen=104)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetVlanVid(BaseModifyPacketTest):
    """
    Verify implementation of the Set VLAN ID action
    Set the vlan vid

    Derived from Test case 70.130: Set VLAN ID
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.vlan_vid(2))]
        pkt = simple_tcp_packet(dl_vlan_enable=True, vlan_vid=1)
        exp_pkt = simple_tcp_packet(dl_vlan_enable=True, vlan_vid=2)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class PushVlanVidPcp(BaseModifyPacketTest):
    """
    Verify implementation of the Set VLAN priority action
    Push a vlan tag (vid=2, pcp=3)

    Derived from Test case 70.140: Add VLAN priority
    """

    def runTest(self):
        actions = [ofp.action.push_vlan(ethertype=0x8100),
                   ofp.action.set_field(ofp.oxm.vlan_vid(2)),
                   ofp.action.set_field(ofp.oxm.vlan_pcp(3))]
        pkt = simple_tcp_packet()
        exp_pkt = simple_tcp_packet(dl_vlan_enable=True, vlan_vid=2, vlan_pcp=3, pktlen=104)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class PushVlan(BaseModifyPacketTest):
    """
    Push a vlan tag (vid=0, pcp=0)
    """

    def runTest(self):
        actions = [ofp.action.push_vlan(ethertype=0x8100)]
        pkt = simple_tcp_packet()
        exp_pkt = simple_tcp_packet(dl_vlan_enable=True, pktlen=104)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class PushVlanPcp(BaseModifyPacketTest):
    """
    Verify implementation of the Set VLAN priority action
    Push a vlan tag (vid=2, pcp=3)

    Derived from Test case 70.140: Add VLAN priority
    """

    def runTest(self):
        actions = [ofp.action.push_vlan(ethertype=0x8100),
                   ofp.action.set_field(ofp.oxm.vlan_pcp(3))]
        pkt = simple_tcp_packet()
        exp_pkt = simple_tcp_packet(dl_vlan_enable=True, vlan_vid=0, vlan_pcp=3, pktlen=104)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetVlanPcp(BaseModifyPacketTest):
    """
    Set the vlan priority

    Derived from Test case 70.150: Set VLAN priority
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.vlan_pcp(2))]
        pkt = simple_tcp_packet(dl_vlan_enable=True, vlan_pcp=1)
        exp_pkt = simple_tcp_packet(dl_vlan_enable=True, vlan_pcp=2)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class PopVlan(BaseModifyPacketTest):
    """
    Pop a vlan tag

    Derived from Test case 70.160: Strip VLAN header
    """

    def runTest(self):
        actions = [ofp.action.pop_vlan()]
        pkt = simple_tcp_packet(dl_vlan_enable=True, pktlen=104, vlan_vid=5)
        exp_pkt = simple_tcp_packet()
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetEthSrc(BaseModifyPacketTest):
    """
    Set Eth Src address

    Derived from Test case 70.170: Modify Ethernet source MAC address
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.eth_src([0x00, 0xA1, 0xCD, 0x53, 0xC6, 0x55]))]
        pkt = simple_tcp_packet()
        exp_pkt = simple_tcp_packet(eth_src="00:A1:CD:53:C6:55")
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetEthDst(BaseModifyPacketTest):
    """
    Set Eth Dst address

    Derived from Test case 70.180: Modify Ethernet destination MAC address
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.eth_dst([0x00, 0xA1, 0xCD, 0x53, 0xC6, 0x55]))]
        pkt = simple_tcp_packet()
        exp_pkt = simple_tcp_packet(eth_dst="00:A1:CD:53:C6:55")
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetIPv4Src(BaseModifyPacketTest):
    """
    Set IPv4 srouce address

    Derived from Test case 70.190: Modify IPv4 source address
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.ipv4_src(167772161))]
        pkt = simple_tcp_packet()
        exp_pkt = simple_tcp_packet(ip_src="10.0.0.1")
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetIPv4Dst(BaseModifyPacketTest):
    """
    Set IPv4 destination address

    Derive from Test case 70.200: Modify IPv4 destination address
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.ipv4_dst(167772161))]
        pkt = simple_tcp_packet()
        exp_pkt = simple_tcp_packet(ip_dst="10.0.0.1")
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetIpv4Dscp(BaseModifyPacketTest):
    """
    Set IPv4 DSCP

    Derived from Test case 70.210: Modify IPv4 ToS bits
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.ip_dscp(0x01))]
        pkt = simple_tcp_packet()
        exp_pkt = simple_tcp_packet(ip_tos=0x04)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetIpv4ECN(BaseModifyPacketTest):
    """
    Set IPv4 ECN

    Derived from Test case 70.210: Modify IPv4 ToS bits
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.ip_ecn(0x01))]
        pkt = simple_tcp_packet()
        exp_pkt = simple_tcp_packet(ip_tos=0x01)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetIpv4DSCP_NonZeroECN(BaseModifyPacketTest):
    """
    Set IPv4 DSCP and make sure ECN is not modified

     Derived from Test case 70.210: Modify IPv4 ToS bits
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.ip_dscp(0x01))]
        pkt = simple_tcp_packet(ip_tos=0x11)
        exp_pkt = simple_tcp_packet(ip_tos=0x05)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetIpv4ECN_NonZeroDSCP(BaseModifyPacketTest):
    """
    Set IPv4 ECN and make sure DSCP is not modified

    Derived from Test case 70.210: Modify IPv4 ToS bits3
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.ip_ecn(0x02))]
        pkt = simple_tcp_packet(ip_tos=0x11)
        exp_pkt = simple_tcp_packet(ip_tos=0x12)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetIpv4TTL(BaseModifyPacketTest):
    """
    Set IPv4 TTL

    Derived from Test case 70.210: Modify IPv4 ToS bits3
    """

    def runTest(self):
        actions = [ofp.action.set_nw_ttl(10)]
        pkt = simple_tcp_packet()
        exp_pkt = simple_tcp_packet(ip_ttl=10)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetTCPSrc(BaseModifyPacketTest):
    """
    Set TCP source port

    Derived from Test case 70.220: Modify TCP/UDP source port
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.tcp_src(800))]
        pkt = simple_tcp_packet()
        exp_pkt = simple_tcp_packet(tcp_sport=800)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetTCPDst(BaseModifyPacketTest):
    """
    Set TCP destination port

    Derived from Test case 70.230: Modify TCP/UDP destination port
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.tcp_dst(800))]
        pkt = simple_tcp_packet()
        exp_pkt = simple_tcp_packet(tcp_dport=800)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetUDPSrc(BaseModifyPacketTest):
    """
    Set UDP source port

    Derived from Test case 70.220: Modify TCP/UDP source port
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.udp_src(800))]
        pkt = simple_udp_packet()
        exp_pkt = simple_udp_packet(udp_sport=800)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetUDPDst(BaseModifyPacketTest):
    """
    Set UDP destination port

    Derived from Test case 70.230: Modify TCP/UDP destination port
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.udp_dst(800))]
        pkt = simple_udp_packet()
        exp_pkt = simple_udp_packet(udp_dport=800)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetIPv6Src(BaseModifyPacketTest):
    """
    Set IPv6 source address 
    """

    def runTest(self):
        actions = [
            ofp.action.set_field(ofp.oxm.ipv6_src("\x20\x01\xab\xb1\x34\x56\xbc\xcb\x00\x00\x00\x00\x03\x70\x73\x36"))]
        pkt = simple_tcpv6_packet()
        exp_pkt = simple_tcpv6_packet(ipv6_src="2001:abb1:3456:bccb:0000:0000:0370:7336")
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetIPv6Dst(BaseModifyPacketTest):
    """
    Set IPv6 destination address 
    """

    def runTest(self):
        actions = [
            ofp.action.set_field(ofp.oxm.ipv6_dst("\x20\x01\xab\xb1\x34\x56\xbc\xcb\x00\x00\x00\x00\x03\x70\x73\x36"))]
        pkt = simple_tcpv6_packet()
        exp_pkt = simple_tcpv6_packet(ipv6_dst="2001:abb1:3456:bccb:0000:0000:0370:7336")
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetIpv6Dscp(BaseModifyPacketTest):
    """
    Set IPv6 DSCP 
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.ip_dscp(0x01))]
        pkt = simple_tcpv6_packet()
        exp_pkt = simple_tcpv6_packet(ipv6_tc=0x04)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetIpv6ECN(BaseModifyPacketTest):
    """
    Set IPv6 ECN
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.ip_ecn(0x01))]
        pkt = simple_tcpv6_packet()
        exp_pkt = simple_tcpv6_packet(ipv6_tc=0x01)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetIPv6Flabel(BaseModifyPacketTest):
    """
    Set IPv6 Flabel 
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.ipv6_flabel(10))]
        pkt = simple_tcpv6_packet()
        exp_pkt = simple_tcpv6_packet(ipv6_fl=10)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetIpv6DSCP_NonZeroECNandFlabel(BaseModifyPacketTest):
    """
    Set IPv6 DSCP and make sure ECN is not modified 
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.ip_dscp(0x01))]
        pkt = simple_tcpv6_packet(ipv6_tc=0x11, ipv6_fl=10)
        exp_pkt = simple_tcpv6_packet(ipv6_tc=0x05, ipv6_fl=10)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetIpv6ECN_NonZeroDSCPandFlabel(BaseModifyPacketTest):
    """
    Set IPv6 ECN and make sure DSCP is not modified
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.ip_ecn(0x02))]
        pkt = simple_tcpv6_packet(ipv6_tc=0x11, ipv6_fl=10)
        exp_pkt = simple_tcpv6_packet(ipv6_tc=0x12, ipv6_fl=10)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetIPv6Flabel_NonZeroDSCPandECN(BaseModifyPacketTest):
    """
    Set IPv6 Flabel 
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.ipv6_flabel(10))]
        pkt = simple_tcpv6_packet(ipv6_tc=0x11, ipv6_fl=9)
        exp_pkt = simple_tcpv6_packet(ipv6_tc=0x11, ipv6_fl=10)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SetIpv6HopLimit(BaseModifyPacketTest):
    """
    Set Ipv6 Hop Limit 
    """

    def runTest(self):
        actions = [ofp.action.set_nw_ttl(10)]
        pkt = simple_tcpv6_packet()
        exp_pkt = simple_tcpv6_packet(ipv6_hlim=10)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class DecIpv4TTL(BaseModifyPacketTest):
    """
    Decrement Ipv4 TTL 
    """

    def runTest(self):
        actions = [ofp.action.dec_nw_ttl()]
        pkt = simple_tcp_packet(ip_ttl=10)
        exp_pkt = simple_tcp_packet(ip_ttl=9)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class DecIpv6HopLimit(BaseModifyPacketTest):
    """
    Decrement Ipv6 Hop Limit 
    """

    def runTest(self):
        actions = [ofp.action.dec_nw_ttl()]
        pkt = simple_tcpv6_packet(ipv6_hlim=10)
        exp_pkt = simple_tcpv6_packet(ipv6_hlim=9)
        self.verify_modify(actions, pkt, exp_pkt)


@group("optional")
class SequentialExecution(BaseModifyPacketTest):
    """
    Set the vlan vid
    """

    def runTest(self):
        actions = [ofp.action.set_field(ofp.oxm.vlan_vid(1)), ofp.action.set_field(ofp.oxm.vlan_vid(2))]
        pkt = simple_tcp_packet(dl_vlan_enable=True, vlan_vid=1)
        exp_pkt = simple_tcp_packet(dl_vlan_enable=True, vlan_vid=2)
        self.verify_modify(actions, pkt, exp_pkt)


@group("standard")
class ActionSetOutput(base_tests.SimpleDataPlane):
    """
    Output to a single port
    """

    def runTest(self):
        in_port, out_port = openflow_ports(2)

        actions = [ofp.action.output(out_port)]

        pkt = simple_tcp_packet()

        logging.info("Running actions test for %s", pp(actions))

        delete_all_flows(self.controller)

        FuncUtils.flow_entry_install(self.controller,
                                     "flow_add",
                                     match=packet_to_flow_match(self, pkt),
                                     instructions=[ofp.instruction.write_actions(actions)]
                                     )

        pktstr = str(pkt)

        logging.info("Sending packet, expecting output to port %d", out_port)
        self.dataplane.send(in_port, pktstr)
        verify_packets(self, pktstr, [out_port])