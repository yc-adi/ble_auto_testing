#!/usr/bin/env python3

import argparse
from pprint import pprint
import subprocess


def get_inputs():
    parser = argparse.ArgumentParser(description="", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--model', help='nrf51_dongle, nrf52840_dongle, nrf52840_dk', default="")
    parser.add_argument('--sn', help='serial number', default="")

    args = parser.parse_args()
    print(f'args:')
    pprint(f'{vars(args)}')

    return args


def reset_board(sn):
    # Run JLinkExe in a subprocess
    # JLinkExe -USB 680435664 -device NRF52840_XXAA -if SWD -speed 20000 -autoconnect 1
    jlink_process = subprocess.Popen(['/opt/SEGGER/JLink/JLinkExe', '-USB', f'{sn}', 
                                      '-device', 'NRF52840_XXAA', '-if', 'swd',
                                      '-speed', '2000', '-autoconnect', '1'], 
                                      stdin=subprocess.PIPE, 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE)
    jlink_process.stdin.flush()
    output = jlink_process.stdout.readline().decode().strip()
    print(output)
    
    # Send another command to JLinkExe and read the output
    jlink_process.stdin.write(b'r\n')  # Send 'r' command to reset target
    jlink_process.stdin.flush()
    output = jlink_process.stdout.readline().decode().strip()
    print(output)

    # Close the subprocess
    jlink_process.stdin.close()
    jlink_process.wait()


if __name__ == "__main__":
    inputs = get_inputs()

    reset_board(inputs.sn)