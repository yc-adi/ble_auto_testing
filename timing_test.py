#!/usr/bin/env python3

################################################################################
 # Copyright (C) 2023 Analog Devices, Inc., All Rights Reserved.
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

import argparse
from BLE_hci import Namespace
import datetime
from nrf_sniffer_ble import run_sniffer_with_hci
import os
from pcapng_file_parser import parse_pcapng_file, all_tifs
from pprint import pprint
from SnifferAPI import Packet
from subprocess import Popen, PIPE
import statistics
from time import sleep


sniffer_res = dict()
RETRY_LIMIT = 1

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', help='sniffer interface name like "COM4-None", "/dev/ttyACM0"',
                        default="/dev/ttyACM0-None")
    parser.add_argument('--device', help='sniffer target device name', default="")
    parser.add_argument('--addr1', help='board 1 address', default="00:11:22:33:44:21")
    parser.add_argument('--addr2', help='board 2 address', default="00:11:22:33:44:22")
    parser.add_argument('--hci1', help='BLE hci serial port for board 1', default="")
    parser.add_argument('--hci2', help='BLE hci serial port for board 2', default="")
    parser.add_argument('--mon1', help='BLE serial port for board 1 TRACE msg', default="")
    parser.add_argument('--mon2', help='BLE serial port for board 2 TRACE msg', default="")
    parser.add_argument('--time', help='test time in seconds', type=int, default=30)
    parser.add_argument('--tshark', help='tshark program to convert pcap to pcapng', default=
                        "/usr/bin/tshark")
    args = parser.parse_args()
    
    print(f'\ninput args:')
    pprint(vars(args))

    return args


def run_hci_and_sniffer(inputs: Namespace):
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
    global sniffer_res

    params = dict()
    params["capture"] = True
    params["coded"] = False
    params["extcap_interfaces"] = False
    params["extcap_interface"] = inputs.interface
    params["auto_test"] = True
    params["device"] = inputs.device
    params["baudrate"] = None
    params["fifo"] = "FIFO"
    params["extcap_control_in"] = "EXTCAP_CONTROL_IN"
    params["extcap_control_out"] = "EXTCAP_CONTROL_OUT"
    params["timeout"] = inputs.time
    params["dev_addr"] = inputs.addr2

    print(f'\nparams:')
    pprint(params)

    sniffer_res['pcap_file_name'] = run_sniffer_with_hci(inputs, params)

    print(f'sniffer_res:')
    pprint(sniffer_res)
    print(f'\n--- sniffer: Done!\n')


def run_test(inputs, new_phy):

    



    print(f'\nmaster changes the PHY to 1')
    mst_hci.phyFunc(Namespace(phy=str(1), timeout=1))
    sleep(5)

    print("\nmaster reset")
    mst_hci.resetFunc(None)
    sleep(0.5)
    print("\nslave reset")
    slv_hci.resetFunc(None)
    sleep(3)

    #print("\nmaster exit")
    #mst_hci.exitFunc(None)
    #sleep(1)
    #print("\nslave exit")
    #slv_hci.exitFunc(None)
    #sleep(1)

    print(f"\nfinish test on phy {new_phy}\n")


def parse_phy_timing_test_results(captured_file: str):
    file_type = 1  # see parse_pcapng_file() description
    parse_res = parse_pcapng_file(file_type, captured_file)
    return parse_res


def check_results(new_phy):
    global all_tifs

    phy_cmd = ["1M", "2M", "S8", "S2"]
    res = 0

    #
    # check T_IFS
    #
    if len(all_tifs) > 0:
        first_readings = min(20, len(all_tifs))
        print(f'The first TIFS {first_readings} readings:\n{all_tifs[0:first_readings]}')

        max_tifs = max(all_tifs)
        min_tifs = min(all_tifs)
        avg = sum(all_tifs) / len(all_tifs)

        print(f'TIFS, total: {len(all_tifs)}, max: {max_tifs} at {all_tifs.index(max_tifs)}, '
              f'min: {min_tifs} at {all_tifs.index(min_tifs)}, average: {avg:.1f}, median: {statistics.median(all_tifs)}')
        print(f'\nall_tifs @ {id(all_tifs)}')

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
        res = 3
    else:
        if Packet.phy_switch_time > 70.0 / 1E3:  # ms
            print(f'PHY switch time verification ({phy_cmd[new_phy - 1]}): FAIL')
            res = 4
        else:
            print(f'PHY switch time verification ({phy_cmd[new_phy - 1]}): PASS')

    #
    # check connection timing
    #
    if Packet.conn_timing_time is None:
        print("connection_timing_time is None.")
        res = 5
    else:
        if Packet.conn_timing_time > 8800:  # 8750
            print(f'   Connection timing verification: FAIL')
            res = 6
        else:
            print(f'   Connection timing verification: PASS')

    print("-------------------------------------------------------------------\n\n")

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
    print(f'{str(datetime.datetime.now())} - {cmd}')

    try:
        p = Popen(cmd, stdout=PIPE, shell=True)
        for line in iter(p.stdout.readline, b''):
            pass
        p.stdout.close()
        p.wait()

    except Exception as e:
        print(f'Error: {e}')
        p.stdout.close()


def run_test_on_phy(inputs, phy):
    """this function will control the two DUT boards to start the BLE DTM test and start the sniffer
        to capture the packets.
    """
    # the captured file info will be saved in sniffer_res['pcap_file_name']
    inputs.new_phy = phy
    run_hci_and_sniffer(inputs)

    pcap_file = sniffer_res['pcap_file_name']
    print(f'Processing the captured file: {pcap_file}')
    if os.path.exists(pcap_file):
        pcapng_file = pcap_file.replace(".pcap", ".pcapng")
        print(f'convert pcap file to pcapng format: {pcapng_file}')
        convert_pcap_to_pcapng(pcap_file, pcapng_file, inputs.tshark)
    else:
        return 1

    check_res = 0
    #remove me !!!parse_phy_timing_test_results(pcapng_file)
    #remove me !!!check_res = check_results(phy)
    return check_res


if __name__ == "__main__":
    inputs = get_args()

    for phy in range(2, 4):  # 2 (2M), 3 (S8), 4 (S2)
        tried = 0
        res = 0
        while tried < RETRY_LIMIT:
            res = run_test_on_phy(inputs, phy)

            if res == 0:
                break
            else:
                print(f'Return: {res}')
                tried += 1

            sleep(1)
            print(f'======\nFAILED {tried} times.\n======')

        if res > 0:
            exit(res)

    print(f"\n{str(datetime.datetime.now())} - Done!")
    exit(0)

