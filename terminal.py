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

import ble_hci_parser
from pytimedinput import timedInput
import os
import select
import sys
import time
import threading

ERR_EXIT = 1
ERR_INVALID_DUT_ID = 2

all_threads = []


class Terminal(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.kill_received = False
        self.hci_parsers = []
        self.input = ""

    def add_hci_parser(self, params):
        """add a ble_hci_parser object
            param params: the parameters for ble_hci_console
            return: the index in the hci_parsers list
        """
        hci_parser = ble_hci_parser.BleHciParser(params)
        self.hci_parsers.append(hci_parser)
        return len(self.hci_parsers)

    def input_cmd(self, dut, cmd):
        """directly input cmd to the terminal
            param dut: the board index
            param cmd: the cmd string

            return: none
        """
        print(f'DUT {dut}: {cmd}')

        args = cmd.split()
        try:
            cmd_parser = self.hci_parsers[dut].hci_parser
            cmd_parser.args = cmd_parser.parse_args(args)
            cmd_parser.args.func(cmd_parser.args)
        except SystemExit:
            # ignore the exit from argparse help option
            pass

    def run(self):
        print(f'{self.name} starts to run.')

        err_id = 0
        input_time_out = False
        while not self.kill_received:
            # Get the terminal input
            if input_time_out:
                #term_input, timed_out = timedInput(prompt="", timeout=1)
                pass
            else:
                #term_input, timed_out = timedInput(prompt=">>>", timeout=1)
                print(">>>", end="")
            with_input, o, e = select.select([sys.stdin], [], [], 1)

            if not with_input:
                input_time_out = True

                if self.input != "":
                    print(f'INPUT: {self.input}')

                    args = self.input.split()

                    self.input = ""
                else:
                    continue
            else:
                input_time_out = False
                term_input = sys.stdin.readline().strip()
                args = term_input.split()

            # Parse the input and execute the appropriate function
            try:
                # print(f'{args}')

                if len(args) == 0:
                    continue

                if args[0] == 'exit':
                    err_id = ERR_EXIT
                    break

                if not args[0].isnumeric():
                    err_id = ERR_INVALID_DUT_ID
                    break

                dut = int(args[0])
                size = len(self.hci_parsers)
                if dut < 0 or dut >= size:
                    err_id = ERR_INVALID_DUT_ID
                    break

                # process the command
                try:
                    cmd_parser = self.hci_parsers[dut].hci_parser
                    cmd_parser.args = cmd_parser.parse_args(args[1:])
                    cmd_parser.args.func(cmd_parser.args)
                except SystemExit:
                    # ignore the exit from argparse help option
                    continue

            except AttributeError:
                continue

        if err_id == ERR_EXIT:
            print(f'Exited by command exit.')
        elif err_id == ERR_INVALID_DUT_ID:
            print(f'Invalid DUT ID "{args[0]}" in the command "{term_input}"')


def has_live_threads(threads):
    return True in [t.is_alive() for t in threads]


def main():
    global all_threads

    term_thd = Terminal("term_thd")
    term_thd.start()

    all_threads.append(term_thd)

    while has_live_threads(all_threads):
        try:
            # synchronization timeout of threads kill
            [t.join(1) for t in all_threads if t is not None and t.is_alive()]
        except KeyboardInterrupt:
            # Ctrl-C handling and send kill to threads
            print("\nThe test has been terminated.")
            for t in all_threads:
                t.kill_received = True

    print("Done!")


if __name__ == "__main__":
    main()
