import json
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
from oftest.testutils import *
from time import sleep
import string

# Test file format.
KEY_DESC = 'description'
KEY_FLOW_ENTRY = 'flow_entry'
KEY_PORTS_NUM = 'ports_num'
KEY_INSTRUCTIONS = 'instructions'
KEY_TESTS = 'tests'
KEY_MATCH = 'match'
KEY_MATCH_FIELD = 'field'
KEY_MATCH_VELUE = 'value'
KEY_FLOW_TYPE = 'flow_type'
KEY_METER = 'OFPMeterMod'
KEY_GROUP = 'OFPGroupMod'
KEY_INGRESS = 'ingress'
KEY_EGRESS = 'egress'
KEY_PKT_IN = 'PACKET_IN'
KEY_TBL_MISS = 'table-miss'
KEY_PACKETS = 'packets'
KEY_DATA = 'data'
KEY_KBPS = 'kbps'
KEY_PKTPS = 'pktps'
KEY_DURATION_TIME = 'duration_time'
KEY_THROUGHPUT = 'throughput'

flow_mod_class_dict = {'add': ofp.message.flow_add,
                       'del': ofp.message.flow_delete,
                       'dels': ofp.message.flow_delete_strict,
                       'mod': ofp.message.flow_modify,
                       'mods': ofp.message.flow_modify_strict}

match_class_dict = {'eth_dst': ofp.oxm.eth_dst,
                    'eth_src': ofp.oxm.eth_src,
                    'in_port': ofp.oxm.in_port,
                    'meta': ofp.oxm.metadata,
                    "udp_src": ofp.oxm.udp_src,
                    "ip_src": ofp.oxm.ipv4_src,
                    "ip_dst": ofp.oxm.ipv4_dst,
                    "ip_proto": ofp.oxm.ip_proto,
                    "vlan_vid": ofp.oxm.vlan_vid,
                    "eth_type": ofp.oxm.eth_type,
                    "tcp_src": ofp.oxm.tcp_src,
                    "tcp_dst": ofp.oxm.tcp_dst,
                    }
apply_action_class_dict = {'output': ofp.action.output}
flow_mod_setting = {
    'table': 0,
    'prio': 0,
    'flags': 0,
    'out_group': ofp.OFPG_ANY,
    'out_port': ofp.OFPP_ANY,
    'buffer_id': ofp.OFP_NO_BUFFER
}


def json_tester(test_class, file):
    with open(file) as f:
        param = json.load(f)
        test_name = param[0]
        logging.info("Executing TestCase -> " + test_name)
        test_cases = param[1]
        for test_case in test_cases:
            execute_one_case(test_cases, test_case)


def execute_one_case(test_class, test_case):
    description = test_case[KEY_DESC]
    ports_num = test_case[KEY_PORTS_NUM]

    flow_entries = test_case[KEY_FLOW_ENTRY]
    for flow_entry in flow_entries.items():
        flow_msg_class = flow_mod_class_dict[flow_entry[KEY_FLOW_TYPE]]

        match = []
        for match_item in flow_entry[KEY_MATCH]:
            match_class = match_class_dict[match_item[KEY_MATCH_FIELD]]
            value = match_item[KEY_MATCH_VELUE]
            match.append(match_class(value))

        instruction = []
        for instr_name, instr_param in flow_entry[KEY_INSTRUCTIONS]:
            if instr_name == "apply_actions":
                apply_action_list = []
                for item in instr_param:
                    for action_name, action_param in item:
                        action_class = apply_action_class_dict[action_name]()
                        for name, value in action_param:
                            setattr(action_class, name, value)
                        apply_action_list.append(action_class)
                instruction.append(ofp.instruction.apply_actions(apply_action_list))
            elif instr_param == "set_field":
                pass

        request = flow_msg_class()

        # check flow entry options
        for name, value in flow_mod_setting:
            pass
