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

import argparse
import ble_hci_console
import datetime
import os
import serial
import sys
from time import sleep


class BleHciParser:
    def __init__(self, params):
        self.args = None

        self.hci_console = ble_hci_console.BleHciConsole(params)

        self.hci_parser = argparse.ArgumentParser(prog='', formatter_class=argparse.RawDescriptionHelpFormatter)
        subs = self.hci_parser.add_subparsers()

        # parser for cmd "addr"
        addr_parser = subs.add_parser('addr', description="Set the device address.")
        addr_parser.add_argument('addr', help="Set the device address, ex: 00:11:22:33:44:55 ")
        addr_parser.set_defaults(func=self.hci_console.addrFunc)

        # parser for cmd "adv"
        adv_parser = subs.add_parser('adv', description="Send the advertising commands.",
                                     formatter_class=argparse.RawTextHelpFormatter)
        adv_parser.add_argument('-i', '--interval', default=str(ble_hci_console.defaultAdvInterval),
                                help="Advertising interval in units of 0.625 ms, 16-bit hex number 0x0020 - 0x4000,"
                                     " default: " + str(ble_hci_console.defaultAdvInterval))
        adv_parser.add_argument('-c', '--connect', default="True",
                                help="Advertise as a connectable device, default: True")
        adv_parser.add_argument('-l', '--listen', default="False",
                                help="Listen for events \n\t\"True\" for indefinitely, ctrl-c to exit"
                                     " \n\t\"False\" to return \n\tnumber of seconds")
        adv_parser.add_argument('-s', '--stats', action='store_true',
                                help="Periodically print the connection stats if listening")
        adv_parser.add_argument('-m', '--maintain', action='store_true',
                                help="Setup an event listener to restart advertising if we disconnect")
        adv_parser.set_defaults(func=self.hci_console.advFunc)

        # parser for cmd "scan"
        scan_parser = subs.add_parser('scan',
                                      description="Send the scanning commands and print scan reports. ctrl-c to exit")
        scan_parser.add_argument('-i', '--interval', default=str(ble_hci_console.defaultAdvInterval),
                                 help="Advertising interval in units of 0.625 ms, 16-bit hex number 0x0020 - 0x4000, "
                                      "default: " + str(ble_hci_console.defaultAdvInterval))
        scan_parser.set_defaults(func=self.hci_console.scanFunc)

        # parser for cmd "init"
        init_parser = subs.add_parser('init', description="Send the initiating commands to open a connection",
                                      formatter_class=argparse.RawTextHelpFormatter)
        init_parser.add_argument('addr', help="Address of peer to connect with, ex: 00:11:22:33:44:55 ")
        init_parser.add_argument('-i', '--interval', default=str(ble_hci_console.defaultConnInterval),
                                 help="Connection interval in units of 1.25 ms, 16-bit hex number 0x0006 - 0x0C80, "
                                      "default: " + str(ble_hci_console.defaultConnInterval))
        init_parser.add_argument('-t', '--timeout', default=str(ble_hci_console.defaultSupTimeout),
                                 help="Supervision timeout in units of 10 ms, 16-bit hex number 0x000A - 0x0C80, "
                                      "default: " + str(ble_hci_console.defaultSupTimeout))
        init_parser.add_argument('-l', '--listen', default="False",
                                 help="Listen for events \n\t\"True\" for indefinitely, ctrl-c to exit "
                                      "\n\t\"False\" to return \n\tnumber of seconds")
        init_parser.add_argument('-s', '--stats', action='store_true',
                                 help="Periodically print the connection stats if listening")
        init_parser.add_argument('-m', '--maintain', action='store_true',
                                 help="Setup an event listener to restart the connection if we disconnect")
        init_parser.set_defaults(func=self.hci_console.initFunc)

        # parser for cmd "dataLen"
        dataLen_parser = subs.add_parser('dataLen', description="Set the max data length",
                                         formatter_class=argparse.RawTextHelpFormatter)
        dataLen_parser.set_defaults(func=self.hci_console.dataLenFunc)

        # parser for cmd "sendAcl"
        sendAcl_parser = subs.add_parser('sendAcl', description="Send ACL packets",
                                         formatter_class=argparse.RawTextHelpFormatter)
        sendAcl_parser.add_argument('packetLen',
                                    help="Number of bytes per ACL packet, 16-bit decimal ex: 128, 0 to disable")
        sendAcl_parser.add_argument('numPackets',
                                    help="Number of packets to send, 8-bit decimal ex: 255, 0 to enable auto-generate ")
        sendAcl_parser.set_defaults(func=self.hci_console.sendAclFunc)

        # parser for cmd "sinkAcl"
        sinkAcl_parser = subs.add_parser('sinkAcl', description="Sink ACL packets, do not send events to host",
                                         formatter_class=argparse.RawTextHelpFormatter)
        sinkAcl_parser.set_defaults(func=self.hci_console.sinkAclFunc)

        # parser for cmd "connStats"
        connStats_parser = subs.add_parser('connStats', help="Get the connection stats",
                                           formatter_class=argparse.RawTextHelpFormatter)
        connStats_parser.set_defaults(func=self.hci_console.connStatsFunc)

        # parser for cmd "phy"
        phy_parser = subs.add_parser('phy', description="Update the PHY in the active connection",
                                     formatter_class=argparse.RawTextHelpFormatter)
        phy_parser.add_argument('phy', help=
        """
                                Desired PHY
                                1: 1M
                                2: 2M
                                3: S8 
                                4: S2
                                default: 1M
                                """)
        phy_parser.set_defaults(func=self.hci_console.phyFunc)

        # parser for cmd "reset"
        reset_parser = subs.add_parser('reset', description="Sends a HCI reset command")
        reset_parser.set_defaults(func=self.hci_console.resetFunc)

        # parser for cmd "listen"
        listen_parser = subs.add_parser('listen', description="Listen for HCI events, print to screen")
        listen_parser.add_argument('-t', '--time', default="0", help="Time to listen in seconds, default: 0(indef)")
        listen_parser.add_argument('-s', '--stats', action='store_true',
                                   help="Periodically print the connection stats if listening")
        listen_parser.set_defaults(func=self.hci_console.listenFunc)

        # parser for cmd "txTest"
        txTest_parser = subs.add_parser('txTest', aliases=['tx'], description="Execute the transmitter test",
                                        formatter_class=argparse.RawTextHelpFormatter)
        txTest_parser.add_argument('-c', '--channel', default="0", help="TX test channel, 0-39, default: 0")
        txTest_parser.add_argument('--phy', default="1", help=
                                   """TX test PHY
                                       1: 1M
                                       2: 2M
                                       3: S8 
                                       4: S2
                                       default: 1M
                                   """)
        txTest_parser.add_argument('-p', '--payload', default="0", help=
                                   """TX test Payload
                                       0: PRBS9
                                       1: 11110000
                                       2: 10101010
                                       3: PRBS15
                                       4: 11111111
                                       5: 00000000
                                       6: 00001111
                                       7: 01010101
                                       default: PRBS9
                                   """)
        txTest_parser.add_argument('-pl', '--packetLength', default="0", help=
                                   """"TX packet length, number of bytes per packet, 0-255
                                       default: 0
                                   """)
        txTest_parser.set_defaults(func=self.hci_console.txTestFunc)

        # parser for cmd "rxTest"
        rxTest_parser = subs.add_parser('rxTest', aliases=['rx'], description="Execute the receiver test")
        rxTest_parser.add_argument('-c', '--channel', default="0", help="RX test channel, 0-39, default: 0")
        rxTest_parser.add_argument('--phy', default="1", help=
                                   """RX test PHY
                                       1: 1M
                                       2: 2M
                                       3: S8 
                                       4: S2
                                       default: 1M
                                   """)
        rxTest_parser.set_defaults(func=self.hci_console.rxTestFunc)

        # parser for cmd "endTest"
        endTest_parser = subs.add_parser('endTest', aliases=['end'], description="End the TX/RX test, "
                                         "print the number of correctly received packets")
        endTest_parser.set_defaults(func=self.hci_console.endTestFunc)

        # parser for cmd "txPower"
        txPower_parser = subs.add_parser('txPower', aliases=['txp'], description="Set the TX power",
                                         formatter_class=argparse.RawTextHelpFormatter)
        txPower_parser.add_argument('power', help="Integer power setting in units of dBm")
        txPower_parser.add_argument('--handle', help="Connection handle, integer")
        txPower_parser.set_defaults(func=self.hci_console.txPowerFunc)

        # parser for cmd "discon"
        discon_parser = subs.add_parser('discon', aliases=['dc'],
                                        description="Send the command to disconnect")
        discon_parser.set_defaults(func=self.hci_console.disconFunc)

        # parser for cmd "setChMap"
        setChMap_parser = subs.add_parser('setChMap', formatter_class=argparse.RawTextHelpFormatter,
                                          description="""Set the connection channel map to a given channel.""")
        setChMap_parser.add_argument('chan', help="""Channel to use in channel map
            Will set the channel map to the given channel, plus one additional channel.""", nargs="?")
        setChMap_parser.add_argument('-m', '--mask', help="""40 bit hex number to use a channel map
            0xFFFFFFFFFF will use all channels, 0x000000000F will use channels 0-3""")
        setChMap_parser.add_argument('--handle', help="Connection handle, integer", default="0")
        setChMap_parser.set_defaults(func=self.hci_console.setChMapFunc)

        # parser for cmd "cmd"
        cmd_parser = subs.add_parser('cmd', formatter_class=argparse.RawTextHelpFormatter,
                                     description="Send raw HCI commands")
        cmd_parser.add_argument('cmd', help="String of hex bytes LSB first\nex: \"01030C00\" to send HCI Reset command")
        cmd_parser.add_argument('-l', '--listen', action='store_true',
                                help="Listen for events indefinitely, ctrl-c to exit")
        cmd_parser.set_defaults(func=self.hci_console.cmdFunc)

        # parser for cmd "readReg"
        readReg_parser = subs.add_parser('readReg', formatter_class=argparse.RawTextHelpFormatter,
                                         description="Read register, device performs a memcpy from address"
                                         " and returns the value")
        readReg_parser.add_argument('addr', help="Address to read, 32-bit hex value\nex: \"0x20000000\"")
        readReg_parser.add_argument('length', help="Number of bytes to read, hex value\nex: \"0x2\"")
        readReg_parser.set_defaults(func=self.hci_console.readRegFunc)

        # parser for cmd "readWrite"
        readWrite_parser = subs.add_parser('writeReg', formatter_class=argparse.RawTextHelpFormatter,
                                           description="Write register, device performs a memcpy to memory address")
        readWrite_parser.add_argument('addr', help="Address to write, 32-bit hex value\nex: \"0x20000000\"")
        readWrite_parser.add_argument('value', help="Data to write, 8,16, or 32 bit hex value,\nex: \"0x12\"")
        readWrite_parser.set_defaults(func=self.hci_console.writeRegFunc)

        # parser for cmd "exit"
        exit_parser = subs.add_parser('exit', aliases=['quit'], description="Exit the program")
        exit_parser.set_defaults(func=self.hci_console.exitFunc)

        # parser for cmd "help"
        help_parser = subs.add_parser('help', aliases=['h'], description="Show help message")
        help_parser.set_defaults(func=self.hci_parser.print_help)


if __name__ == "__main__":
    print('Done!')
