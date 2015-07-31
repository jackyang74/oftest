from ctypes import *
import time


class OSNT_Tester:
    def __init__(self):
        # load dynamic library
        self.library_path = "./libosnt.so"
        self.osnt = CDLL(self.library_path)

        # reset register status
        self.reset_stats()

    def get_rcv_pkts_cnt(self, port_num):
        func = self.osnt.get_rcv_pkts_cnt
        func.argtypes = [c_int]
        func.restype = c_int
        return func(port_num)

    def get_rcv_bytes_cnt(self, port_num):
        func = self.osnt.get_rcv_bytes_cnt
        func.argtypes = [c_int]
        func.restype = c_int
        return func(port_num)

    def get_rcv_rate_pps(self, port_num):
        func = self.osnt.get_rcv_rate_pps
        func.argtypes = [c_int]
        func.restype = c_int
        return func(port_num)

    def get_rcv_rate_bps(self, port_num):
        func = self.osnt.get_rcv_rate_bps
        func.argtypes = [c_int]
        func.restype = c_int
        return func(port_num)

    def reset_stats(self):
        func = self.osnt.reset_stats
        return func()

    def set_enable(self, port_num):
        """
        Enable transmit queue num, return none

        """
        func = self.osnt.set_enable
        func.argtypes = [c_int]
        return func(port_num)

    def set_disable(self, port_num):
        func = self.osnt.set_disable
        func.argtypes = [c_int]
        return func(port_num)

    def set_replay_cnt(self, port_num):
        func = self.osnt.set_replay_cnt
        func.argtypes = [c_int]
        return func(port_num)

    def set_replay_rate(self, port_num):
        func = self.osnt.set_replay_rate
        func.argtypes = [c_int]
        return func(port_num)

    def set_begin_replay(self, port_num):
        func = self.osnt.set_begin_replay
        func.argtypes = [c_int]
        return func(port_num)

    def set_stop_replay(self, port_num):
        func = self.osnt.set_stop_replay
        func.argtypes = [c_int]
        return func(port_num)

    def reset_replay(self, port_num):
        func = self.osnt.set_replay_cnt
        return func(port_num)


if __name__ == '__main__':
    tester = OSNT_Tester()
    while True:
        time.sleep(1)
        print("pkts={0:d}".format(tester.get_rcv_pkts_cnt(0)))
        print("bytes={0:d}".format(tester.get_rcv_bytes_cnt(0)))
        print("bps={0:d}".format(tester.get_rcv_rate_bps(0)))
        print("pps={0:d}".format(tester.get_rcv_rate_pps(0)))
        print("<=============================>\n")
