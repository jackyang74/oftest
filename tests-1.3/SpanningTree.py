"""
Test suite 30 checks for implementation of Spanning Tree Protocol related functions
"""


import logging

from oftest import config
import oftest.base_tests as base_tests
import ofp
import time

from oftest.testutils import *


@group('TestSuite30')
class HelloVersionAnnouncement(base_tests.SimpleProtocol):
    """
    Test case 30.40: Port administratively down
    """

    def runTest(self):
        logging.info("Test case 30.40: Port administratively down")
        for of_port, _ in config["port_map"].items():  # Grab first port
            break

        (_, config1, _) = port_config_get(self.controller, of_port)
        self.assertTrue(config is not None, "Did not get port config")

        rv = port_config_set(self.controller, of_port,
                             config1 ^ ofp.OFPPC_NO_PACKET_IN,
                             ofp.OFPPC_NO_PACKET_IN)
        self.assertTrue(rv != -1, "Error sending port mod")

        # Verify change took place with same feature request
        (_, config2, _) = port_config_get(self.controller, of_port)
        self.assertTrue(config2 is not None, "Did not get port config2")
        logging.debug("OFPPC_NO_PACKET_IN bit port " + str(of_port) + " is now " +
                      str(config2 & ofp.OFPPC_NO_PACKET_IN))
        self.assertTrue(config2 & ofp.OFPPC_NO_PACKET_IN !=
                        config1 & ofp.OFPPC_NO_PACKET_IN,
                        "Bit change did not take")
        # Set it back
        rv = port_config_set(self.controller, of_port, config1,
                             ofp.OFPPC_NO_PACKET_IN)
        self.assertTrue(rv != -1, "Error sending port mod")


