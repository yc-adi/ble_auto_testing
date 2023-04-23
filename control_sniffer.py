#!/usr/bin/env python3

"""
Example
    python3 control_sniffer.py --model x --sn 680435664
"""
import argparse
import pexpect
from pprint import pprint
import subprocess
import time

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
    #jlink_process.stdin.flush()
    while True:
        output = jlink_process.stdout.readline()
        if output == '' and jlink_process.poll() is not None:
            break
        if output:
            line = output.decode().strip()
            print(line)
            if line.find("Cortex-M0 identified") != -1:
                break

    #print("Send command to JLinkExe to reset the board")
    jlink_process.stdin.write(b'r\n')  # Send 'r' command to reset target
    #jlink_process.stdin.flush()
    #output = jlink_process.stdout.readline().decode().strip()
    #print(output)
    
    while False:
        output = jlink_process.stdout.readline()
        if output == '' and jlink_process.poll() is not None:
            break
        if output:
            line = output.decode().strip()
            print(line)
            if line.find("Reset device via AIRCR.SYSRESETREQ") != -1:
                break

    time.sleep(1)
    
    #print('\nClose the subprocess')
    jlink_process.stdin.close()
    jlink_process.wait()


def board_reset(sn):
    cmd = f'JLinkExe -USB {sn} -device NRF52840_XXAA -if SWD -speed 20000 -autoconnect 1'
    print(f'run cmd: {cmd}')
    child = pexpect.spawn(cmd)
    child.expect("Cortex-M0 identified")
    child.sendline('r')
    child.expect("AIRCR.SYSRESETREQ")
    child.sendline('exit')

    #print(child.before.decode())
    #child.interact()


if __name__ == "__main__":
    inputs = get_inputs()

    reset_board(inputs.sn)
    #board_reset(inputs.sn)