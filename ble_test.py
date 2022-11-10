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

import io
import os
import select
import sys
from terminal import Terminal
import time
import threading


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

    print("Done!")


def start_threads():
    stdout = sys.stdout  # store it
    sys.stdout = TeeTextIO(sys.stdout)  # apply the TEE function

    all_threads = []

    terminal_thread = Terminal("terminal_thread")
    all_threads.append(terminal_thread)

    # prepare the BLE HCI consoles
    params = {'serialPort': '/dev/ttyUSB1'}
    index = terminal_thread.add_hci_parser(params)
    params['serialPort'] = '/dev/ttyUSB3'
    index = terminal_thread.add_hci_parser(params)

    main_thread = threading.Thread(target=start_main, args=(all_threads, terminal_thread))
    main_thread.start()

    # wait the terminal thread to start
    while True:
        output = sys.stdout.stringio.getvalue()
        if output.find('>>>') >= 0:
            break

    sys.stdout = stdout  # restore the original stdout

    return terminal_thread


def phy_timing_test(terminal_thd):
    """

    """
    print('\nStart PHY timing test.')
    terminal_thd.input_cmd(0, "addr 00:11:22:33:44:11")
    time.sleep(0.1)
    terminal_thd.input_cmd(1, "addr 00:11:22:33:44:12")
    time.sleep(0.1)

    terminal_thd.input_cmd(0, "adv -l 2")
    time.sleep(2)

    terminal_thd.input_cmd(0, "phy 2")
    time.sleep(0.1)
    terminal_thd.input_cmd(0, "phy 1")
    time.sleep(0.1)

    time.sleep(2)

    terminal_thd.input_cmd(0, "reset")
    time.sleep(0.1)
    terminal_thd.input_cmd(1, "reset")
    time.sleep(0.1)

    terminal_thd.input = "exit"

    print('Finish PHY timing test.\n')


if __name__ == "__main__":
    term_thread = start_threads()

    phy_timing_test(term_thread)

