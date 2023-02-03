"""
/*******************************************************************************
* Copyright (C) 2022 Maxim Integrated Products, Inc., All Rights Reserved.
*
* Permission is hereby granted, free of charge, to any person obtaining a
* copy of this software and associated documentation files (the "Software"),
* to deal in the Software without restriction, including without limitation
* the rights to use, copy, modify, merge, publish, distribute, sublicense,
* and/or sell copies of the Software, and to permit persons to whom the
* Software is furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included
* in all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
* OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
* IN NO EVENT SHALL MAXIM INTEGRATED BE LIABLE FOR ANY CLAIM, DAMAGES
* OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
* ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
* OTHER DEALINGS IN THE SOFTWARE.
*
* Except as contained in this notice, the name of Maxim Integrated
* Products, Inc. shall not be used except as stated in the Maxim Integrated
* Products, Inc. Branding Policy.
*
* The mere transfer of this software does not imply any licenses
* of trade secrets, proprietary technology, copyrights, patents,
* trademarks, maskwork rights, or any other form of intellectual
* property whatsoever. Maxim Integrated Products, Inc. retains all
* ownership rights.
*******************************************************************************/
"""

import argparse
from argparse import RawTextHelpFormatter
from BLE_hci import run_terminal
from datetime import datetime
from nrf_sniffer_ble import run_sniffer as exe_sniffer
from os.path import exists
from pcapng_file_parser import parse_pcapng_file, all_tifs
from pprint import pprint
import statistics
from subprocess import call, Popen, PIPE, CalledProcessError, STDOUT
from threading import Thread
import time


serial_ports = [
    "COM9",  # board 0
    "COM10"  # board 1
]

addrs = [
    "00:11:22:33:44:21",  # board 0
    "00:11:22:33:44:22"  # board 1
]

test_time = 30  # secs

# RESULT CODE
RES_FAIL = 11
RES_NO_TIFS_CAPTURED = 12
RES_PCAP_FILE_NOT_EXIST = 13

def control_board(serial_port: str, baud: int, sleep_secs: int, cmd: str) -> list:
    """Send hci commands to the board through the selected serial port

        Args:
            serial_port: serial port
            baud: baudrate
            sleep_secs: time to sleep in secs
            cmd: the hci commands

        Returns:
            [thread1, thread2]
    """
    if sleep_secs > 0:
        print(f'{datetime.now()}: start to sleep')
        time.sleep(sleep_secs)
        print(f'{datetime.now()}: end sleeping')

    print("--- Thread started ---")
    print(cmd)
    print("----------------------")

    params = dict()
    params["serialPort"] = serial_port
    params["baud"] = baud
    params["command"] = cmd

    run_terminal(params)

    print("--------------------")
    print(cmd)
    print("--- Thread ended ---")


def run_ble_app():
    """Run the BLE application on two DevKit boards

    """
    board = 0
    timeout = test_time
    cmd = f'addr_{addrs[board]};adv_-l_5;exit'
    thd1 = Thread(target=control_board, args=(serial_ports[board], 115200, 0, cmd,))
    thd1.start()

    time.sleep(8)

    board = 1
    delay = 8   # secs
    timeout = test_time - 8 - delay
    cmd = f'addr_{addrs[board]};init_-l_{timeout}_-s_{addrs[0]};reset;exit'
    thd2 = Thread(target=control_board, args=(serial_ports[board], 115200, delay, cmd,))
    thd2.start()

    time.sleep(1)

    return thd1, thd2


def run_sniffer(interface_name: str, device_name: str, dev_adv_addr: str, timeout: int) -> dict:
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

        Returns:
            res (dict): sniffer result info are saved in a dictionary
                        keys: 'pcap_file_name'

    if device_name == "":
        cmd = f'python -m nrf_sniffer_ble --capture --extcap-interface {interface_name} --fifo FIFO ' \
              f'--extcap-control-in EXTCAP_CONTROL_IN --extcap-control-out EXTCAP_CONTROL_OUT ' \
              f'--dev-addr {dev_adv_addr} --auto-test --timeout {timeout}'
    else:
        cmd = f'python -m nrf_sniffer_ble --capture --extcap-interface {interface_name} --fifo FIFO '\
            f'--extcap-control-in EXTCAP_CONTROL_IN --extcap-control-out EXTCAP_CONTROL_OUT '\
            f'--device {device_name} --auto-test --timeout {timeout}'
    print(cmd)

    res = dict()
    try:
        p = Popen(cmd, stdout=PIPE, shell=True)
        for line in iter(p.stdout.readline, b''):
            temp = line.split(': ')
            if temp[0] == 'pcap file':
                res['pcap_file_name'] = temp[1].replace('\n', '')
        p.stdout.close()
        p.wait()

    except Exception as e:
        print(f'Error: {e}')
        p.stdout.close()
    return res
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

    res = dict()
    res['pcap_file_name'] = exe_sniffer(params)

    return res


def run_parser(file_type: int, pcapng_file: str) -> int:
    """Run the pcap/pcapng file parser on the saved sniffer file
        Example command: python -m pcapng_file_parser

        Args:
            file_type:
                0: Wireshark saved pcapng file
                1: pcap file converted pcapng file
            pcapng_file: the saved sniffer pcapng file name with path

        Returns:
            err_code: or test result, 0, pass, 1, fail, 2, no TIFS captured
    """
    parse_pcapng_file(file_type, pcapng_file)

    res = 0
    if len(all_tifs) > 0:
        max_tifs = max(all_tifs)
        min_tifs = min(all_tifs)
        avg = sum(all_tifs) / len(all_tifs)

        print(f'TIFS, total: {len(all_tifs)}, max: {max_tifs}, min: {min_tifs}, average: {avg:.1f}, '
              f'median: {statistics.median(all_tifs)}')
        if max_tifs <= 152 and min_tifs >= 148:
            print( "                TIFS verification: PASS")
            res = 0
        else:
            print("                 TIFS verification: FAIL")
            res = 1
    else:
        print("No TIFS captured.")
        res = 2
    
    return res

def convert_pcap_to_pcapng(pcap_file: str, pcapng_file: str, tshark: str):
    """Convert pcap file to pcapng file

        "C:\\Program Files\\Wireshark\\tshark.exe" -F pcapng -r {pcap file} -w {pcapng file}
        Args:
            pcap_file: pcap format file name
            pcapng_file: pcapng format file name
            tshark: the full path of tshark

        Returns:
            None
    """
    cmd = f'{tshark} -F pcapng -r {pcap_file} -w {pcapng_file}'
    print(f'{str(datetime.now())} - {cmd}')

    try:
        p = Popen(cmd, stdout=PIPE, shell=True)
        for line in iter(p.stdout.readline, b''):
            pass
        p.stdout.close()
        p.wait()

    except Exception as e:
        print(f'Error: {e}')
        p.stdout.close()


def get_args():
    """Get the program arguments
        Args:
            None

        Return:
            args
    """
    # Setup the command line description text
    desc = """
    BLE auto testing tool.

    This tool is used to control two DevKit boards to run BLE5_ctr projects at the same time. Meanwhile, the packets
    between these two BLE devices are sniffed by a nRF51 dongle. The captured packets will be saved to a pcap and a
    pcapng file, which can be used to analyze the BLE performance. 
    """
    parser = argparse.ArgumentParser(description=desc, formatter_class=RawTextHelpFormatter)
    parser.add_argument('--interface', help='sniffer interface name like "COM4-None", "/dev/ttyACM0"',
                        default="/dev/ttyACM0-None")
    parser.add_argument('--device', help='sniffer target device name', default="")
    parser.add_argument('--brd0-addr', help='DevKit board 0 advertising address', default="00:11:22:33:44:21")
    parser.add_argument('--brd1-addr', help='DevKit board 1 advertising address', default="00:11:22:33:44:22")
    parser.add_argument('--sp0', help='BLE hci serial port for board 0', default="/dev/ttyUSB2")
    parser.add_argument('--sp1', help='BLE hci serial port for board 1', default="/dev/ttyUSB7")
    parser.add_argument('--tp0', help='BLE hci serial port for board 0 TRACE msg', default="/dev/ttyUSB8")
    parser.add_argument('--tp1', help='BLE hci serial port for board 1 TRACE msg', default="/dev/ttyUSB5")
    parser.add_argument('--time', help='test time in seconds', type=int, default=30)
    parser.add_argument('--tshark', help='tshark program to convert pcap to pcapng', default=
                        "/usr/bin/tshark")
    args = parser.parse_args()
    pprint(args)

    return args


def run_tifs_test(args) -> int:
    """Run TIFS test once.
        Args:
            args: the user input arguments

        Returns:
            res: 0, Pass the TIFS verification
                 1, Fail to capture TIFS packets
                 2, Pcap file not exist
    """
    # Update the parameters
    interface = args.interface
    device = args.device
    addrs[0] = args.brd0_addr
    addrs[1] = args.brd1_addr
    dev_adv_addr = addrs[0]
    serial_ports[0] = args.sp0
    serial_ports[1] = args.sp1
    test_time = args.time

    # Run the BLE5_ctr on two DevKit boards. Get the control thread for each board.
    thd1, thd2 = run_ble_app()
    print(f'{datetime.now()}: Test started. Run sniffer.')

    timeout = test_time + 10   # secs
    res = run_sniffer(interface, device, dev_adv_addr, timeout)
    if "pcap_file_name" not in res:
        thd1.join()
        thd2.join()
        print("Sniffer failed!")
        return 2

    # Wait the threads to finish.
    thd1.join()
    thd2.join()

    pcap_file = res["pcap_file_name"]
    print(f'Next: parse file "{pcap_file}"')

    # Parse the saved file.
    if exists(pcap_file):
        # Need to convert pcap file to pcapng format.
        pcapng_file = pcap_file.replace(".pcap", ".pcapng")
        convert_pcap_to_pcapng(pcap_file, pcapng_file, args.tshark)

        # Parse the results.
        file_type = 1
        result = run_parser(file_type, pcapng_file)

        if result == 0:
            return 0
        elif result == 1:
            exit(RES_FAIL)
        elif result == 2:
            return 1
    else:
        print(f'File {pcap_file} not exist.')
        return 2


if __name__ == "__main__":
    args = get_args()

    tried = 0
    res = 0
    while tried < 3:
        res = run_tifs_test(args)

        if res == 0:
            break
        else:
            tried += 1

        time.sleep(1)
        print(f'Tried {tried} times.')

    if res > 0:
        exit(res)