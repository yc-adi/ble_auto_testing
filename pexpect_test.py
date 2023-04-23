#!/usr/bin/env python3

import pexpect

# Start the script in the terminal console
command = 'python3 ./input_test.py'
process = pexpect.spawn(command)

process.expect_exact('input A:')
print("--- " + process.after.decode() + " ---")

process.sendline('1')

process.expect_exact('1 done')
print("=== " + process.before.decode() + " x " + process.after.decode() + " ===")

process.sendline('2')

process.expect_exact('2 done')
print("... " + process.before.decode() + " x " + process.after.decode() + " ...")

process.sendline('exit')

process.close()

def reset_board(sn):
    """
    $ JLinkExe -USB 680435664 -device NRF52840_XXAA -if SWD -speed 20000 -autoconnect 1
    SEGGER J-Link Commander V7.80c (Compiled Sep 27 2022 16:06:19)
    DLL version V7.80c, compiled Sep 27 2022 16:05:56

    Connecting to J-Link via USB...O.K.
    Firmware: J-Link OB-SAM3U128-V2-NordicSemi compiled Sep 21 2022 09:57:39
    Hardware version: V1.00
    J-Link uptime (since boot): 0d 03h 34m 21s
    S/N: 680435664
    License(s): RDI, FlashBP, FlashDL, JFlash, GDB
    USB speed mode: High speed (480 MBit/s)
    VTref=3.300V
    Device "NRF52840_XXAA" selected.


    Connecting to target via SWD
    InitTarget() start
    InitTarget() end
    Found SW-DP with ID 0x0BB11477
    DPIDR: 0x0BB11477
    CoreSight SoC-400 or earlier
    Scanning AP map to find all available APs
    AP[1]: Stopped AP scan as end of AP map has been reached
    AP[0]: AHB-AP (IDR: 0x04770021)
    Iterating through AP map to find AHB-AP to use
    AP[0]: Core found
    AP[0]: AHB-AP ROM base: 0xF0000000
    CPUID register: 0x410CC200. Implementer code: 0x41 (ARM)
    Found Cortex-M0 r0p0, Little endian.
    Identified core does not match configuration. (Found: Cortex-M0, Configured: Cortex-M4)
    FPUnit: 4 code (BP) slots and 0 literal slots
    CoreSight components:
    ROMTbl[0] @ F0000000
    [0][0]: E00FF000 CID B105100D PID 000BB471 ROM Table
    ROMTbl[1] @ E00FF000
    [1][0]: E000E000 CID B105E00D PID 000BB008 SCS
    [1][1]: E0001000 CID B105E00D PID 000BB00A DWT
    [1][2]: E0002000 CID B105E00D PID 000BB00B FPB
    [0][1]: F0002000 CID B105900D PID 000BB9A3 ???
    Cortex-M0 identified.
    J-Link>r
    Reset delay: 0 ms
    Reset type NORMAL: Resets core & peripherals via SYSRESETREQ & VECTRESET bit.
    Reset: Halt core after reset via DEMCR.VC_CORERESET.
    Reset: Reset device via AIRCR.SYSRESETREQ.
    J-Link>exit
    """
    cmd = f"JLinkExe -USB {sn} -device NRF52840_XXAA -if SWD -speed 20000 -autoconnect 1"
    print(f'run cmd: {cmd}')
    child = pexpect.spawn(cmd)

    child.expect("J-Link>")
    
    child.sendline("r")

    child.expect("J-Link>")
    
    child.sendline("exit")

    child.close()
