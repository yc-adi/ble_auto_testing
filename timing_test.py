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
from BLE_hci import BLE_hci
from BLE_hci import Namespace
from nrf_sniffer_ble import run_sniffer as exe_sniffer
import os
import shutil
import sys
from time import sleep
from threading import Thread

sniffer_res = dict()


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
    
    print(f'\ninput args: {vars(args)}')

    return args


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
    global sniffer_res

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

    print(f'\n--- params: {params}\n')

    sniffer_res['pcap_file_name'] = exe_sniffer(params)

    print(f'\n--- sniffer done!\n')


def run_test(inputs, new_phy):
    sleep(2)
    
    slv_hci = BLE_hci({"serialPort": inputs.hci2, "monPort": inputs.mon2, "baud": 115200, "id": 2})
    mst_hci = BLE_hci({"serialPort": inputs.hci1, "monPort": inputs.mon1, "baud": 115200, "id": 1})

    print("\nslave reset")
    slv_hci.resetFunc(None)
    sleep(1)
    print("\nmaster reset")
    mst_hci.resetFunc(None)
    sleep(0.2)

    print(f"\nset slave address: {inputs.addr2}")
    slv_hci.addrFunc(Namespace(addr=inputs.addr2))
    sleep(0.2)
    print(f"\nset master address: {inputs.addr1}")
    mst_hci.addrFunc(Namespace(addr=inputs.addr1))
    sleep(0.2)

    print("\nslave starts adv")
    slv_hci.advFunc(Namespace(interval="60", stats="False", connect="True", maintain=False, listen="False"))
    sleep(0.5)

    print("\nmaster starts to connect")
    mst_hci.initFunc(Namespace(interval="6", timeout="64", addr=inputs.addr2, stats="False", maintain=False, listen="False"))
    sleep(3)

    print(f'\nslave changes the PHY to {new_phy}')
    slv_hci.phyFunc(Namespace(phy=str(new_phy), timeout=1))
    sleep(3)

    print("\nslave reset")
    slv_hci.resetFunc(None)
    sleep(0.2)
    print("\nmaster reset")
    mst_hci.resetFunc(None)
    sleep(0.2)

    print(f"\ntest on phy: {new_phy} done\n")


if __name__ == "__main__":
    inputs = get_args()

    interface = inputs.interface
    device = inputs.device

    ble_thd = Thread(target=run_test, args=(inputs, 1,))

    ble_thd.start()

    run_sniffer(inputs.interface, inputs.device, inputs.addr2, inputs.time)

    print(f'snifer_res: {sniffer_res}')
    
