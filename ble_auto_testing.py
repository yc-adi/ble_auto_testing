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

from os.path import exists
from pcapng_file_parser import parse_pcapng_file, all_tifs
from subprocess import Popen, PIPE, CalledProcessError


def run_ble_app():
    """Run the BLE application

    """
    pass


def run_sniffer(interface_name: str, device_name: str, timeout: int) -> dict:
    """Run the BLE packet sniffer on specified interface and device

        Example command: --capture --extcap-interface COM4-None --device Periph --fifo FIFO
            --extcap-control-in EXTCAP_CONTROL_IN --extcap-control-out EXTCAP_CONTROL_OUT --auto-test --timeout 10

        Args:
            interface_name: the nRF dongle interface name
            device_name: the BLE device name
            timeout: how long the sniffer should run

        Returns:
            res (dict): sniffer result info are saved in a dictionary
                        keys: 'pcap_file_name'
    """
    cmd = f'python -m nrf_sniffer_ble --capture --extcap-interface {interface_name} --fifo FIFO '\
          f'--extcap-control-in EXTCAP_CONTROL_IN --extcap-control-out EXTCAP_CONTROL_OUT '\
          f'--device {device_name} --auto-test --timeout {timeout}'

    # p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    # out, err = p.communicate()
    # result = out.split('\n')
    # result = subprocess.check_call(cmd, shell=True)
    res = dict()
    with Popen(cmd, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            temp = line.split(': ')
            if temp[0] == 'pcap file':
                res['pcap_file_name'] = temp[1].replace('\n', '')

    if p.returncode != 0:
        raise CalledProcessError(p.returncode, p.args)

    return res


def run_parser(file_type: int, pcapng_file: str):
    """Run the pcap/pcapng file parser on the saved sniffer file
        Example command: python -m pcapng_file_parser

        Args:
            file_type:
                0: Wireshark saved pcapng file
                1: pcap file converted pcapng file
            pcapng_file: the saved sniffer pcapng file name with path

        Returns:
            None
    """
    parse_pcapng_file(file_type, pcapng_file)

    if len(all_tifs) > 0:
        max_tifs = max(all_tifs)
        min_tifs = min(all_tifs)
        avg = sum(all_tifs) / len(all_tifs)

        # print(f'TIFS, max: {max_tifs}, min: {min_tifs}, average: {avg:.1f}')
        if max_tifs <= 152 and min_tifs >= 148:
            print("PASS")
        else:
            print("FAIL")
    else:
        print("No TIFS captured.")


def convert_pcap_to_pcapng(pcap_file: str, pcapng_file: str):
    """Convert pcap file to pcapng file

        C:\Program Files\Wireshark\tshark.exe -F pcapng -r {pcap file} -w {pcapng file}
        Args:
            pcap_file: pcap format file name
            pcapng_file: pcapng format file name

        Returns:
            None
    """
    cmd = f'"C:\\Program Files\\Wireshark\\tshark.exe" -F pcapng -r {pcap_file} -w {pcapng_file}'
    with Popen(cmd, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(line)

    if p.returncode != 0:
        print('Fail to convert pcap file to pcapng file.')
        raise CalledProcessError(p.returncode, p.args)


if __name__ == "__main__":
    # TODO: develop serial port control to run the application on BLE devices
    run_ble_app()

    # TODO: set/get the interface and device names
    interface = "COM4-None"
    device = "Periph"
    timeout = 10  # secs
    res = run_sniffer(interface, device, timeout)
    pcap_file = res["pcap_file_name"]
    print(f'Parse file: {pcap_file}')

    if exists(pcap_file):
        pcapng_file = pcap_file.replace(".pcap", ".pcapng")
        convert_pcap_to_pcapng(pcap_file, pcapng_file)

        file_type = 1
        run_parser(file_type, pcapng_file)
