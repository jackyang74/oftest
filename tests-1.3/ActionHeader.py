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


class OFPCML_NO_BUFFER(base_tests.SimpleDataPlane):
    """
    Verify packet_in OFPR_NO _MATCH implements buffer handling correct
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
        pkt = str(simple_tcp_packet(pktlen=700))
        self.dataplane.send(in_port, pkt)

        verify_packet_in(self, pkt, in_port, ofp.OFPR_ACTION)
