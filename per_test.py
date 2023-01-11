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
from datetime import datetime
import io
from nrf_sniffer_ble import capture_write, run_sniffer as exe_sniffer
from os.path import exists
from SnifferAPI import Packet
from pcapng_file_parser import parse_pcapng_file, all_tifs
from pprint import pprint
from queue import Queue
import shutil
import statistics
import sys
from terminal import Terminal
import time
import threading


q = Queue()  # used to share data between threads

failed_files = []  # used to keep all failed files

PERs = []
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

    print(f"{datetime.now()} - All threads are terminated.")


def start_threads(sp0, sp1, tp0, tp1):
    stdout = sys.stdout  # store it
    sys.stdout = TeeTextIO(sys.stdout)  # apply the TEE function

    all_threads = []

    terminal_thread = Terminal("terminal_thread")
    all_threads.append(terminal_thread)

    # prepare the BLE HCI consoles
    params = {'serialPort': sp0, 'monPort': tp0, 'id': 1}
    index = terminal_thread.add_hci_parser(params)

    params['serialPort'] = sp1
    params['monPort'] = tp1
    params["id"] = 2
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


def per_test(terminal_thd, addr1, addr2, new_phy):
    """

    """
    global PERs

    ret = 0

    phy_cmd = ["1M", "2M", "S8", "S2"]

    if new_phy < 1 or new_phy > 4:        
        print(f'{new_phy} is invalid new phy. Changed to 1 (1M).')
        new_phy = 1

    print(f'\n---------------------------------------------------------------------------------------')
    print(f'packetLen: {250}, phy: {new_phy}, txPower: {0}\n')

    terminal_thd.input_cmd(0, "reset")
    time.sleep(0.2)
    terminal_thd.input_cmd(1, "reset")
    time.sleep(0.2)

    print(f'\n{datetime.now()} -- Reset the attenuation to 30.\n')
    #mini_RCDAT = mini_RCDAT_USB(Namespace(atten=30))
    #time.sleep(0.1)

    print(f'\n{datetime.now()} -- Set the addresses.\n')
    terminal_thd.input_cmd(0, "addr " + addr1)
    time.sleep(0.2)
    terminal_thd.input_cmd(1, "addr " + addr2)
    time.sleep(0.2)

    print(f'\n{datetime.now()} -- Set PHY.\n')
    terminal_thd.input_cmd(0, "phy " + str(new_phy))
    time.sleep(0.2)

    print(f'\n{datetime.now()} -- Set TX power.\n')
    terminal_thd.input_cmd(1, 'txPower --handle 0 0')
    time.sleep(1)  # remove me !!!
    terminal_thd.input_cmd(0, 'txPower --handle 0 0')
    time.sleep(1)

    print(f'\n{datetime.now()} -- Start advertising and connection.\n')
    terminal_thd.input_cmd(0, "adv -i 60 -c True -l False")  # no -s -m
    time.sleep(0.2)
    terminal_thd.input_cmd(1, "init -i 6 -t 64 -l False " + addr1)
    time.sleep(0.2)

    print(f'\n{datetime.now()} -- listen.\n')
    terminal_thd.input_cmd(1, "listen -t 1")
    time.sleep(0.2)
    terminal_thd.input_cmd(0, "listen -t 1")
    time.sleep(0.2)

    print(f'\n{datetime.now()} -- dataLen.\n')
    terminal_thd.input_cmd(1, "dataLen")
    time.sleep(0.2)
    terminal_thd.input_cmd(0, "dataLen")
    time.sleep(0.2)

    print(f'\n{datetime.now()} -- listen.\n')
    terminal_thd.input_cmd(1, "listen -t 1")
    time.sleep(0.2)
    terminal_thd.input_cmd(0, "listen -t 1")
    time.sleep(0.2)

    print(f'\n{datetime.now()} -- sinkAcl.\n')
    terminal_thd.input_cmd(1, "sinkAcl")
    time.sleep(0.2)
    terminal_thd.input_cmd(0, "sinkAcl")
    time.sleep(0.2)
    terminal_thd.input_cmd(1, "listen -t 1")
    time.sleep(0.2)

    terminal_thd.input_cmd(1, "sendAcl 250 0")
    time.sleep(0.2)
    terminal_thd.input_cmd(0, "sendAcl 250 0")
    time.sleep(0.2)
    terminal_thd.input_cmd(1, "listen -t 1")
    time.sleep(0.2)

    terminal_thd.input_cmd(1, "sendAcl 250 1")
    time.sleep(0.2)
    terminal_thd.input_cmd(0, "sendAcl 250 1")
    time.sleep(0.2)
    terminal_thd.input_cmd(1, "listen -t 1")
    time.sleep(0.2)
    
    per_100 = False
    for atten in range(20, 35, 55):
        print('\n-------------------------------------------------')
        print(f'packetLen: {250}, phy: {new_phy}, txPower: {0}, atten: {atten}\n')

        print(f"{datetime.now()} -  Set the required attenuation: {atten}")
        #mini_RCDAT = mini_RCDAT_USB(Namespace(atten=atten))
        time.sleep(0.1)

        terminal_thd.input_cmd(1, 'cmd 0102FF00')
        time.sleep(0.2)
        terminal_thd.input_cmd(0, 'cmd 0102FF00')
        time.sleep(0.2)
        terminal_thd.input_cmd(1, "listen -t 1")
        time.sleep(0.2)

        print(f'\n{datetime.now()} -- Sleep requested delay seconds.\n')
        time.sleep(5)

        # Read any pending events
        terminal_thd.input_cmd(1, "listen -t 1")
        time.sleep(0.2)
        terminal_thd.input_cmd(0, "listen -t 1")
        time.sleep(0.2)

        slv_per = terminal_thd.input_cmd(1, "connStats")
        time.sleep(0.2)

        mst_per = terminal_thd.input_cmd(0, "connStats")
        time.sleep(0.2)
        
        if slv_per is None or mst_per is None:
            print(f'\n{datetime.now()} -- TEST FAILED!.\n')
            ret = 0            
            break

        if float(slv_per) >= 99.99 or float(mst_per) >= 99.99:
            print(f'\n{datetime.now()} -- TEST FAILED!.\n')
            ret = 1
            break
        
        PERs.append((slv_per, mst_per))


    #print(f'\n{datetime.now()} -- Reset before exit.\n')
    #terminal_thd.input_cmd(0, "reset")
    #time.sleep(0.2)
    #terminal_thd.input_cmd(1, "reset")
    #time.sleep(0.2)

    terminal_thd.input = "exit"

    print(f'{str(datetime.now())} - Finish PHY timing test ({phy_cmd[new_phy - 1]}).\n')

    return ret


def run_sniffer(interface_name: str, device_name: str, dev_adv_addr: str, timeout: int, queue: Queue) -> dict:
    """Run the BLE packet sniffer on specified interface and device

        Example command:
        With a selected device name
        --capture --extcap-interface COM4-None --device Periph --fifo FIFO
            --extcap-control-in EXTCAP_CONTROL_IN --extcap-control-out EXTCAP_CONTROL_OUT --auto-test --timeout 10

        With a selected device advertisings address
        --capture --extcap-interface COM4-None --fifo FIFO
            --extcap-control-in EXTCAP_CONTROL_IN --extcap-control-out EXTCAP_CONTROL_OUT
            --dev-addr 00:11:22:33:44:21 --auto-test --timeout 20

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

    print(f"{str(datetime.now())} - Sniffer started.")

    captured_file = exe_sniffer(params)

    queue.put(captured_file)
    print(f'{str(datetime.now())} - Sniffer finished.')


def run_per_test(args, new_phy):
    if args.interface is None:
        interface = '/dev/ttyACM0-None'
    else:
        interface = args.interface
    print(f'sniffer interface: {interface}')

    device = args.device

    if args.brd0_addr is None:
        brd0_addr = "00:11:22:33:44:21"
    else:
        brd0_addr = args.brd0_addr
    print(f'board 1 addr: {brd0_addr}')

    if args.brd1_addr is None:
        brd1_addr = "00:11:22:33:44:22"
    else:
        brd1_addr = args.brd1_addr
    print(f'board 2 addr: {brd1_addr}')

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

    term_thread = start_threads(sp0, sp1, args.tp0, args.tp1)

    #sniffer_thd = threading.Thread(target=run_sniffer, args=(interface, device, brd0_addr, timeout, q))
    #sniffer_thd.daemon = True
    #sniffer_thd.start()

    res = per_test(term_thread, brd0_addr, brd1_addr, new_phy)
    return res

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
    
        print("\n\n-------------------------------------------------------------------")
        if max_tifs <= 152 and min_tifs >= 148:
            print("                TIFS verification: PASS")
            res = 0
        else:
            print("                TIFS verification: FAIL")
            res = 1

        all_tifs.clear()  # clear for the next test
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
            print(f'   Connection timing verification: FAIL')
            res = 4
        else:
            print(f'   Connection timing verification: PASS')

    print("-------------------------------------------------------------------\n\n")

    return res


def full_test(args, parse_captured_file, new_phy):
    global failed_files
    res = run_per_test(args, new_phy)
    return res


if __name__ == "__main__":
    parse_captured_file = False
    args = get_args()

    for i in range(20):
        print(f'-----------------------------------------------------------------------------------')
        print(f'Test: {i +1}')
        print(f'-----------------------------------------------------------------------------------')

        res = full_test(args, parse_captured_file, 1)
        if res != 0:
            break

        pprint(PERs)

    print(f"\n{str(datetime.now())} - Done with return value: {res}.")

