#! /usr/bin/env python3

################################################################################
# Copyright (C) 2022 Analog Devices, Inc., All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL MAXIM INTEGRATED BE LIABLE FOR ANY CLAIM, DAMAGES
# OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of Maxim Integrated
# Products, Inc. shall not be used except as stated in the Maxim Integrated
# Products, Inc. Branding Policy.
#
# The mere transfer of this software does not imply any licenses
# of trade secrets, proprietary technology, copyrights, patents,
# trademarks, maskwork rights, or any other form of intellectual
# property whatsoever. Maxim Integrated Products, Inc. retains all
# ownership rights.
#
###############################################################################

"""
The terminal console could control more than one DUTs. The input commands must
indicate which DUT the commands would go to. The input command format is:
"DUT_ID command_str", in which DUT_ID is 0-based.
"""

from ble_auto_testing import convert_pcap_to_pcapng, get_args
import datetime
import io
from nrf_sniffer_ble import capture_write, run_sniffer as exe_sniffer
from os.path import exists
from SnifferAPI import Packet
from pcapng_file_parser import parse_pcapng_file, all_tifs
from queue import Queue
import statistics
import sys
from terminal import Terminal
import time
import threading


RETRY_LIMIT = 3

q = Queue()  # used to share data between threads


class TeeTextIO(io.TextIOBase):
    """Similar to the Linux TEE command.
    """
    def __init__(self, target):
        self.target = target
        self.stringio = io.StringIO()

    def write(self, s):
        write_count = self.target.write(s)
        self.stringio.write(s[:write_count])
        return write_count


def has_live_threads(threads):
    return True in [t.is_alive() for t in threads]


def start_main(all_thds, term_thd):
    print(f'main thread starts to run.')

    term_thd.start()

    all_thds.append(term_thd)

    while has_live_threads(all_thds):
        try:
            # synchronization timeout of threads kill
            [t.join(1) for t in all_thds if t is not None and t.is_alive()]
        except KeyboardInterrupt:
            # Ctrl-C handling and send kill to threads
            print("\nThe test has been terminated.")
            for t in all_thds:
                t.kill_received = True

    print(f"{datetime.datetime.now()} - All threads are terminated.")


def start_threads(sp0, sp1):
    stdout = sys.stdout  # store it
    sys.stdout = TeeTextIO(sys.stdout)  # apply the TEE function

    all_threads = []

    terminal_thread = Terminal("terminal_thread")
    all_threads.append(terminal_thread)

    # prepare the BLE HCI consoles
    params = {'serialPort': sp0}
    index = terminal_thread.add_hci_parser(params)
    params['serialPort'] = sp1
    index = terminal_thread.add_hci_parser(params)

    main_thread = threading.Thread(target=start_main, args=(all_threads, terminal_thread))
    main_thread.daemon = True
    main_thread.start()

    # wait the terminal thread to start
    while True:
        output = sys.stdout.stringio.getvalue()
        if output.find('>>>') >= 0:
            break

    sys.stdout = stdout  # restore the original stdout

    return terminal_thread


def phy_timing_test(terminal_thd, addr1, addr2, new_phy):
    """

    """
    phy_cmd = ["1M", "2M", "S8", "S2"]

    if new_phy < 2 or new_phy > 4:
        new_phy = 2
        print(f'{new_phy} is invalid new phy. Changed to 2 (2M).')
    print(f'\nStart PHY timing test ({phy_cmd[new_phy - 1]}).')

    terminal_thd.input_cmd(0, "addr " + addr1)
    time.sleep(0.1)
    terminal_thd.input_cmd(1, "addr " + addr2)
    time.sleep(0.1)

    terminal_thd.input_cmd(0, "adv -l 1")
    #time.sleep(3)

    terminal_thd.input_cmd(1, "init -l 1 " + addr1)
    time.sleep(3)

    #terminal_thd.input_cmd(0, "phy 2")  # the PHY switching time is about 59.7 ms.
    terminal_thd.input_cmd(1, "phy " + str(new_phy))  # the PHY switching time is about 67.5 ms.
    #time.sleep(3)

    terminal_thd.input_cmd(0, "reset")
    time.sleep(0.1)
    terminal_thd.input_cmd(1, "reset")
    time.sleep(0.1)

    terminal_thd.input = "exit"

    print(f'{str(datetime.datetime.now())} - Finish PHY timing test ({phy_cmd[new_phy - 1]}).\n')


def run_sniffer(interface_name: str, device_name: str, dev_adv_addr: str, timeout: int, queue: Queue) -> dict:
    """Run the BLE packet sniffer on specified interface and device

        Example command:
        With a selected device name
        --capture --extcap-interface COM4-None --device Periph --fifo FIFO
            --extcap-control-in EXTCAP_CONTROL_IN --extcap-control-out EXTCAP_CONTROL_OUT --auto-test --timeout 10

        With a selected device advertisings address
        --capture --extcap-interface COM4-None --fifo FIFO
            --extcap-control-in EXTCAP_CONTROL_IN --extcap-control-out EXTCAP_CONTROL_OUT
            --dev-addr 00:11:22:33:44:11 --auto-test --timeout 20

        No device selected:
        --capture --extcap-interface COM4-None --fifo FIFO --extcap-control-out EXTCAP_CONTROL_OUT
            --auto-test --timeout 10

        Args:
            interface_name: the nRF dongle interface name
            device_name: the BLE device name
            dev_adv_addr: the device advertising address in the BLE packet
            timeout: how long the sniffer should run
            captured_file: the saved captured file path

        Returns:
            None
    """
    params = dict()
    params["capture"] = True
    params["coded"] = False
    params["extcap_interfaces"] = False
    params["extcap_interface"] = interface_name
    params["auto_test"] = True
    params["device"] = device_name
    params["baudrate"] = None
    params["fifo"] = "FIFO"
    params["extcap_control_in"] = "EXTCAP_CONTROL_IN"
    params["extcap_control_out"] = "EXTCAP_CONTROL_OUT"
    params["timeout"] = timeout
    params["dev_addr"] = dev_adv_addr

    print(f"{str(datetime.datetime.now())} - Sniffer started.")

    captured_file = exe_sniffer(params)

    queue.put(captured_file)
    print(f'{str(datetime.datetime.now())} - Sniffer finished.')


def run_phy_timing_test(args, new_phy):
    if args.interface is None:
        interface = '/dev/ttyACM0-None'
    else:
        interface = args.interface

    device = args.device

    if args.brd0_addr is None:
        brd0_addr = "00:11:22:33:44:11"
    else:
        brd0_addr = args.brd0_addr

    if args.brd1_addr is None:
        brd1_addr = "00:11:22:33:44:12"
    else:
        brd1_addr = args.brd1_addr

    if args.time is None:
        timeout = 30
    else:
        timeout = args.time

    if args.sp0 is None:
        sp0 = "/dev/ttyUSB0"
    else:
        sp0 = args.sp0

    if args.sp1 is None:
        sp1= "/dev/ttyUSB1"
    else:
        sp1 = args.sp1

    term_thread = start_threads(sp0, sp1)

    sniffer_thd = threading.Thread(target=run_sniffer, args=(interface, device, brd0_addr, timeout, q))
    sniffer_thd.daemon = True
    sniffer_thd.start()

    phy_timing_test(term_thread, brd0_addr, brd1_addr, new_phy)

    sniffer_thd.join()  # wait the test to finish

    if q.empty():  # check if there is captured file
        return None
    else:
        pcap_file = q.get()
        print(f'{str(datetime.datetime.now())} - Captured file: {pcap_file}')

        if exists(pcap_file):
            # Need to convert pcap file to pcapng format.
            pcapng_file = pcap_file.replace(".pcap", ".pcapng")
            # "C:\\Program Files\\Wireshark\\tshark.exe"
            convert_pcap_to_pcapng(pcap_file, pcapng_file, "/usr/bin/tshark")

            return pcapng_file


def parse_phy_timing_test_results(captured_file: str):
    file_type = 1  # see parse_pcapng_file() description
    res = parse_pcapng_file(file_type, captured_file)
    return res


def check_results(new_phy):
    phy_cmd = ["1M", "2M", "S8", "S2"]
    res = 0

    #
    # check T_IFS
    #
    if len(all_tifs) > 0:
        max_tifs = max(all_tifs)
        min_tifs = min(all_tifs)
        avg = sum(all_tifs) / len(all_tifs)

        print(f'TIFS, total: {len(all_tifs)}, max: {max_tifs}, min: {min_tifs}, average: {avg:.1f}, '
              f'median: {statistics.median(all_tifs)}')
        if max_tifs <= 152 and min_tifs >= 148:
            print("TIFS verification: PASS")
            res = 0
        else:
            print("TIFS verification: FAIL")
            res = 1
    else:
        print("No TIFS captured.")
        res = 2

    #
    # check PHY switch time
    #
    if Packet.phy_switch_time is None:
        print("phy_switch_time is None.")
        res = 2
    else:
        if Packet.phy_switch_time > 70.0 / 1E3:  # ms
            print(f'PHY switch time verification ({phy_cmd[new_phy - 1]}): FAIL')
            res = 3
        else:
            print(f'PHY switch time verification ({phy_cmd[new_phy - 1]}): PASS')

    #
    # check connection timing
    #
    if Packet.conn_timing_time is None:
        print("connection_timing_time is None.")
        res = 2
    else:
        if Packet.conn_timing_time > 8800:  # 8750
            print(f'Connection timing verification: FAIL')
            res = 4
        else:
            print(f'Connection timing verification: PASS')

    return res


def full_test(args, parse_captured_file, new_phy):
    if parse_captured_file:
        captured_file = "/home/ying-cai/Workspace/ble_auto_testing/output/dev-ttyACM0-None__2022-11-18_10-10-07" \
                        ".pcapng"
    else:
        # This test includes the connection, T_IFS, and PHY switch tests.
        captured_file = run_phy_timing_test(args, new_phy)
        print(f'{captured_file}')

    if captured_file is not None:
        if exists(captured_file):
            parse_phy_timing_test_results(captured_file)

        res = check_results(new_phy)
    else:
        res = 2

    return res



if __name__ == "__main__":
    parse_captured_file = False
    args = get_args()

    for new_phy in range(2, 5):  # 2 (2M), 3 (S8), 4 (S2)
        tried = 0
        res = 0
        while tried < RETRY_LIMIT:
            res = full_test(args, parse_captured_file, new_phy)

            if res == 0:
                break
            else:
                tried += 1

            time.sleep(1)
            print(f'Tried {tried} times.')

        if res > 0:
            exit(res)

    print(f"\n{str(datetime.datetime.now())} - Done!")

