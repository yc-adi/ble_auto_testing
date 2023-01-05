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

import codecs
import datetime
import os
import serial
import sys
import threading
from time import sleep


# Setup the default serial port settings
defaultBaud = 115200
defaultSP = "/dev/ttyUSB1"

# Set up the default Bluetooth settings
defaultAdvInterval = "0x60"
defaultScanInterval = "0x100"

defaultConnInterval = "0x6"  # 7.5 ms
defaultSupTimeout = "0x64"  # 1 s

defaultDevAddr = "00:11:22:33:44:55"
defaultInitAddr = defaultDevAddr

# Magic value for the exit function to properly return
exitFuncMagic = 999


## Convert integer to hex.
#
# Converts integer to hex with a given number of bits for sign extension.
################################################################################
def tohex(val, nbits):
    return hex((val + (1 << nbits)) % (1 << nbits))


## Parse BD address.
#
# Reverses a Bluetooth address to bytes, LSB first.
################################################################################
def parseBdAddr(addr):
    # Reorder the address
    addr = addr.split(":")
    if (len(addr) != 6):
        print("Address is wrong length, needs to be 6 bytes separated by ':'")
        return ""
    addrBytes = addr[5] + addr[4] + addr[3] + addr[2] + addr[1] + addr[0]
    return addrBytes


## Parse register address.
#
# Reverses a hex number to bytes, LSB first.
################################################################################
def parseAddr(addr, numNibbles=8):
    # Make sure it's a hex number starting with 0x
    if (addr[:2] != "0x"):
        print("Address must be a hex number starting with 0x")

    # Remove the 0x
    addr = addr[2:]

    # Make sure this is a 32 bit address
    if (len(addr) != numNibbles):
        print("Address must be 32 bit hex number")

    # Split the address into bytes
    chunks, chunk_size = len(addr), 2
    addrBytes = [addr[i:i + chunk_size] for i in range(0, chunks, chunk_size)]

    # Reverse the bytes to LSB first

    addrString = ""
    for i in range(int(numNibbles / 2) - 1, -1, -1):
        addrString = addrString + addrBytes[i]

    return addrString


## Parse bytes string.
#
# Parses a string of 4 hex bytes, LSB first. Returns 32 bit int.
################################################################################
def parseBytes32(byteString):
    return int(byteString[3] + byteString[2] + byteString[1] + byteString[0], 16)


class BleHciConsole:
    port = serial.Serial()
    serialPort = ""
    trace_port = ""

    def __init__(self, params):
        try:
            print(f'BleHciConsole init params: {params}')
            
            if "id" in params.keys():
                self.id = params["id"]
            else:
                self.id = "0"

            baudrate = defaultBaud
            if "baud" in params.keys():
                baudrate = params['baud']
            
            # Open serial port
            serialPort = params["serialPort"]
            self.port = serial.Serial(
                port=str(serialPort),
                baudrate=baudrate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                rtscts=False,
                dsrdtr=False,
                timeout=1.0
            )
            self.port.isOpen()
                
            if "monPort" in params.keys():
                trace_port = params["monPort"]                

            if trace_port == "":
                self.trace_port = None
            else:
                self.trace_port = serial.Serial(
                    port=str(trace_port),
                    baudrate=baudrate,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    rtscts=False,
                    dsrdtr=False,
                    timeout=1.0
                )
                self.trace_port.isOpen()

        except serial.SerialException as err:
            print(err)
            sys.exit(1)

        except OverflowError as err:
            print("baud rate exception, " + str(baudrate) + " is too large")
            print(err)
            sys.exit(1)

        if self.trace_port != None:
            TraceMsgThread = threading.Thread(target=self.monitorTraceMsg, daemon=True)
            TraceMsgThread.start()

    ## Monitor the TRACE port
    #
    # Listen for the trace message from the board UART0
    ################################################################################
    def monitorTraceMsg(self):
        first = True
        while True:
            if self.trace_port is not None:
                msg = self.trace_port.readline().decode("utf-8")
                msg = msg.replace("\r\n", "")
                if msg != "":
                    if first:
                        print(f'\n{str(datetime.datetime.now())} {self.id} {msg}')
                        first = False
                    else:
                        print(f'{str(datetime.datetime.now())} {self.id} {msg}')

    def closeListenDiscon(self):
        # Close the listener thread if active
        self.listenDisconThread
        self.listenDisconStop

        if (self.listenDisconThread.is_alive()):
            self.listenDisconStop = True
            self.listenDisconThread.join()

    ## Exit function.
    #
    # Sends an exit code that is handled below.
    ################################################################################
    def helpFunc(self, args):
        print('helpFunc')

    ## Exit function.
    #
    # Sends an exit code that is handled below.
    ################################################################################
    def exitFunc(self, args):

        # Close the serial port
        if (self.port.open == True):
            self.port.flush()
            self.port.close()
        print("")

        # Close the listener thread if active
        self.closeListenDiscon()

        try:
            if (args.returnVal != None):
                sys.exit(int(args.returnVal))
        except AttributeError:
            sys.exit(exitFuncMagic)

        sys.exit(exitFuncMagic)

    ## Wait for an HCI event.
    #
    # Waits for an HCI event, optionally prints the received event.
    # Will timeout on the serial port if nothing arrives.
    ################################################################################
    def wait_event(self, print_evt=True, timeout=1.0):

        # Set the serial port timeout
        self.port.timeout = timeout

        # Receive the event
        evt = self.port.read(size=1)
        if (len(evt) == 0):
            # TODO: Read flush
            self.port.flush()
            return ""

        evt = int(codecs.encode(evt, 'hex_codec'), 16)
        status_string = '%02X' % evt

        # ACL data
        if (evt == 2):
            # Receive the rest of the header
            hdr = self.port.read(size=4)
            packet_len = hdr[2] + (hdr[3] << 8)
            hdr = int(codecs.encode(hdr, 'hex_codec'), 16)
            status_string += '%08X' % hdr

        # HCI Event
        elif (evt == 4):
            # Receive the rest of the header
            hdr = self.port.read(size=2)
            packet_len = hdr[1]
            hdr = int(codecs.encode(hdr, 'hex_codec'), 16)
            status_string += '%04X' % hdr

        else:
            print("Error: unknown evt = " + str(evt))
            return

        payload = self.port.read(size=packet_len)

        # Print the packet
        if (print_evt):
            for i in range(0, packet_len):
                status_string += '%02X' % payload[i]
            print(str(datetime.datetime.now()) + f" {self.id}<", status_string)

        return status_string

    ## Wait for HCI events.
    #
    # Waits to receive HCI events, prints the timestamp every 30 seconds.
    ################################################################################
    def wait_events(self, seconds=2, print_evt=True):
        # Read events from the device for a few seconds
        start_time = datetime.datetime.now()
        delta = datetime.datetime.now() - start_time
        while ((delta.seconds < seconds) or (seconds == 0)):
            self.wait_event(print_evt=print_evt, timeout=0.1)
            delta = datetime.datetime.now() - start_time
            if ((delta.seconds > 30) and ((delta.seconds % 30) == 0)):
                print(str(datetime.datetime.now()) + " |")

    ## Send HCI command.
    #
    # Send a HCI command to the serial port. Will add a small delay and wait for
    # and print an HCI event by default.
    ################################################################################
    def send_command(self, packet, resp=True, delay=0.01, print_cmd=True):
        # Send the command and data
        if (print_cmd):
            print(str(datetime.datetime.now()) + f" {self.id}>", packet)

        self.port.write(bytearray.fromhex(packet))
        sleep(delay)

        if (resp):
            return self.wait_event()

    ## Parse connection stats event.
    #
    # Parses a connection stats event and prints the results.
    ################################################################################
        ## Parse connection stats event.
    #
    # Parses a connection stats event and prints the results.
    ################################################################################
    def parseConnStatsEvt(self, evt):
        print(f'parseConnStatsEvt() evt: {evt}')
        try:
            # Offset into the event where the stats start, each stat is 32 bits, or
            # 8 hex nibbles
            i = 14
            rxDataOk = int(evt[6 + i:8 + i] + evt[4 + i:6 + i] + evt[2 + i:4 + i] + evt[0 + i:2 + i], 16)
            i += 8
            rxDataCRC = int(evt[6 + i:8 + i] + evt[4 + i:6 + i] + evt[2 + i:4 + i] + evt[0 + i:2 + i], 16)
            i += 8
            rxDataTO = int(evt[6 + i:8 + i] + evt[4 + i:6 + i] + evt[2 + i:4 + i] + evt[0 + i:2 + i], 16)
            i += 8
            txData = int(evt[6 + i:8 + i] + evt[4 + i:6 + i] + evt[2 + i:4 + i] + evt[0 + i:2 + i], 16)
            i += 8
            errTrans = int(evt[6 + i:8 + i] + evt[4 + i:6 + i] + evt[2 + i:4 + i] + evt[0 + i:2 + i], 16)
        except ValueError as err:
            print(err)
            return None

        print(self.serialPort)
        print("rxDataOk   : " + str(rxDataOk))
        print("rxDataCRC  : " + str(rxDataCRC))
        print("rxDataTO   : " + str(rxDataTO))
        print("txData     : " + str(txData))
        print("errTrans   : " + str(errTrans))

        per = 100.0
        if ((rxDataCRC + rxDataTO + rxDataOk) != 0):
            per = round(float((rxDataCRC + rxDataTO) / (rxDataCRC + rxDataTO + rxDataOk)) * 100, 2)
            print("PER        : " + str(per) + " %")
        return per

    ## Listen for disconnection events.
    #
    #  Listen for events and print them to the terminal. Send command if we get a disconnect event.
    ################################################################################
    def listenDiscon(self):

        # TODO: Add a way to cancel this
        if (self.listenDisconCommand != ""):
            self.send_command(listenDisconCommand)

        while (True):
            evt = self.wait_event(timeout=0.1)
            if (self.listenDisconStop):
                sys.exit(1)
            if ("040504" in evt):
                if (self.listenDisconCommand != ""):
                    self.send_command(listenDisconCommand)

    # Thread used to listen for disconnection events
    listenDisconThread = threading.Thread(target=listenDiscon)
    listenDisconStop = False
    listenDisconCommand = ""

    ## Set BD address command.
    #
    #  Sets the public BD address for the device.
    ################################################################################
    def addrFunc(self, args):
        # Reorder the address
        addrBytes = parseBdAddr(args.addr)

        # Send the vendor specific set address command
        self.send_command("01F0FF06" + addrBytes)

    ## Start advertising function.
    #
    # Sends HCI commands to start advertising.
    ################################################################################
    def advFunc(self, args):
        # Bogus address to use for commands, allows any peer to connect
        peer_addr = "000000000000"

        # Setup the event masks
        self.send_command("01010C08FFFFFFFFFFFFFFFF")
        self.send_command("01630C08FFFFFFFFFFFFFFFF")
        self.send_command("01010C08FFFFFFFFFFFFFFFF")
        self.send_command("01012008FFFFFFFFFFFFFFFF")

        # Reset the connection stats
        if (args.stats):
            self.send_command("0102FF00")

        # Set default PHY to enable all PHYs
        self.send_command("01312003" + "00" + "07" + "07")

        advType = "03"  # Non connectable undirected advertising (ADV_NONCONN_IND)
        if (args.connect == "True"):
            advType = "00"  # Connectable and scannable undirected advertising (ADV_IND)

        # Convert advertising interval string to int
        advIntervalInt = int(args.interval, 16)

        # Convert int to 2 hex bytes, LSB first
        advInterval = "%0.2X" % (advIntervalInt & 0xFF)
        advInterval += "%0.2X" % ((advIntervalInt & 0xFF00) >> 8)

        # LeSetAdvParam(Advertising_Interval_Min=advInterval,
        # Advertising_Interval_Max=advInterval,
        # Advertising_Type=advType,
        # Own_Address_Type=0 (public),
        # Peer_Address_Type=0 (public),
        # Peer_Address=peer_addr,
        # Advertising_Channel_Map=7 (all 3 advertising channels),
        # Advertising_Filter_Policy=0 (don't do any filtering))
        self.send_command("0106200F" + advInterval + advInterval + advType + "0000" + peer_addr + "0700")

        # Start advertising
        connCommand = "010A200101"

        # Start a thread to listen for disconnection events and restart advertising
        if (args.maintain == True):
            global listenDisconCommand
            global listenDisconStop
            global listenDisconThread

            listenDisconThread = threading.Thread(target=listenDiscon)
            listenDisconCommand = connCommand
            listenDisconStop = False

            # Start the thread and wait for it to startup
            listenDisconThread.start()
            sleep(1)

            return
        else:
            self.send_command(connCommand)

        if (args.listen == "False"):
            return

        # Listen for events indef
        if (args.stats):
            per = 100.0
            listenTime = int(args.listen)
            while (listenTime > 0):
                self.wait_events(10)

                # Send the command to get the connection stats, save the event
                statEvt = self.send_command("01FDFF00")

                # Parse the connection stats event
                per = self.parseConnStatsEvt(statEvt)

                listenTime = listenTime - 10

            return per

        # Listen for events for a few seconds
        if (args.listen != "True"):
            self.wait_events(int(args.listen))
            return
        else:
            while True:
                self.wait_events(0)

    ## Start scanning function.
    #
    # Sends HCI commands to start scanning.
    ################################################################################
    def scanFunc(self, args):

        # Setup the event masks
        self.send_command("01010C08FFFFFFFFFFFFFFFF")
        self.send_command("01630C08FFFFFFFFFFFFFFFF")
        self.send_command("01010C08FFFFFFFFFFFFFFFF")
        self.send_command("01012008FFFFFFFFFFFFFFFF")

        # Set scan parameters
        # Active scanning
        # window and interval 0xA0
        # Own address type is 0, public
        # Not doing any filtering
        self.send_command("010B200701A000A0000000")

        # Start scanning, don't filter duplicates
        self.send_command("010C20020100")

        while True:
            self.wait_event()

    ## Start initiating function.
    #
    # Sends HCI commands to start initiating and create a connection.
    ################################################################################
    def initFunc(self, args):
        # Reorder the address
        addrBytes = parseBdAddr(args.addr)

        # Setup the event masks
        self.send_command("01010C08FFFFFFFFFFFFFFFF")
        self.send_command("01630C08FFFFFFFFFFFFFFFF")
        self.send_command("01010C08FFFFFFFFFFFFFFFF")
        self.send_command("01012008FFFFFFFFFFFFFFFF")

        # Reset the connection stats
        if (args.stats):
            self.send_command("0102FF00")

        # Set default PHY to enable all PHYs
        self.send_command("01312003" + "00" + "07" + "07")

        # Convert connection interval string to int
        connIntervalInt = int(args.interval, 16)

        # Convert int to 2 hex bytes, LSB first
        connInterval = "%0.2X" % (connIntervalInt & 0xFF)
        connInterval += "%0.2X" % ((connIntervalInt & 0xFF00) >> 8)

        # Convert supervision timeout string to int
        supTimeoutInt = int(args.timeout, 16)

        # Convert int to 2 hex bytes, LSB first
        supTimeout = "%0.2X" % (supTimeoutInt & 0xFF)
        supTimeout += "%0.2X" % ((supTimeoutInt & 0xFF00) >> 8)

        # Create the connection, using a public address for peer and local
        ownAddrType = "00"
        connLatency = "0000"
        connCommand = "010D2019A000A00000" + "00" + addrBytes + ownAddrType + connInterval + connInterval + connLatency + supTimeout + "0F100F10"

        # Start a thread to listen for disconnection events and restart the connection
        if (args.maintain == True):
            global listenDisconCommand
            global listenDisconStop
            global listenDisconThread

            listenDisconThread = threading.Thread(target=self.listenDiscon)
            listenDisconCommand = connCommand
            listenDisconStop = False

            # Start the thread and wait for it to startup
            listenDisconThread.start()
            sleep(1)

            return
        else:
            self.send_command(connCommand)

        if (args.listen == "False"):
            return

        # Listen for events indef
        if (args.stats):
            per = 100.0
            listenTime = int(args.listen)
            while (listenTime > 0):
                self.wait_events(10)

                # Send the command to get the connection stats, save the event
                statEvt = self.send_command("01FDFF00")

                # Parse the connection stats event
                per = self.parseConnStatsEvt(statEvt)

                listenTime = listenTime - 10

            return per

        # Listen for events for a few seconds
        if (args.listen != "True"):
            self.wait_events(int(args.listen))
            return
        else:
            while True:
                self.wait_events(0)

    ## Set the data length.
    #
    #  Sets the TX data length in octets and time for handle 0.
    ################################################################################
    def dataLenFunc(self, args):
        # Send the set data length command with max length
        self.send_command("01222006" + "0000" + "FB00" + "9042")

    ## Set the length of empty packets.
    #
    #  Sets the length of empty packets.
    ################################################################################
    def sendAclFunc(self, args):

        packetLen = "%0.2X" % (int(args.packetLen) & 0xFF)
        packetLen += "%0.2X" % ((int(args.packetLen) & 0xFF00) >> 8)

        if (args.numPackets == "0"):
            self.send_command("01E5FF02" + packetLen)
            return

        numPackets = "%0.2X" % (int(args.numPackets) & 0xFF)

        # Send the vendor specific command to send ACL packets, handle 0
        self.send_command("01E4FF05" + "0000" + packetLen + numPackets)

        ## Set the length of empty packets.

    #
    #  Sets the length of empty packets.
    ################################################################################
    def sinkAclFunc(self, args):

        # Send the vendor specific command to sink ACL packets
        self.send_command("01E3FF0101")

    ## PHY switch function.
    #
    # Sends HCI command to switch PHYs. Assumes that we can't do asymmetric PHY settings.
    # Assumes we're using connection handle 0000
    ################################################################################
    def phyFunc(self, args):
        # Convert PHY options to bits
        phy = "01"
        phyOptions = "0000"
        if (args.phy == "4"):
            phy = "04"
            phyOptions = "0100"
        elif (args.phy == "3"):
            phy = "04"
            phyOptions = "0200"
        elif (args.phy == "2"):
            phy = "02"
        elif (args.phy != "1"):
            print("Invalid PHY selection, using 1M")

        self.send_command("01322007" + "0000" + "00" + phy + phy + phyOptions)
        self.wait_events(3)

    ## Rest function.
    #
    # Sends HCI reset command.
    ################################################################################
    def resetFunc(self, args):

        # Close the listener thread if active
        self.closeListenDiscon()

        # Send the HCI command for HCI Reset
        self.send_command("01030C00")

    ## Listen for events.
    #
    # Listen for HCI events.
    ################################################################################
    def listenFunc(self, args):
        waitSeconds = int(args.time)

        per = 100.0

        if (args.stats):

            startTime = datetime.datetime.now()
            while True:

                # Wait for at least 10 seconds
                waitPrintSeconds = waitSeconds
                if (waitSeconds == 0):
                    waitPrintSeconds = 10
                self.wait_events(waitPrintSeconds)

                # Send the command to get the connection stats, save the event
                statEvt = self.send_command("01FDFF00")

                # Parse the connection stats event
                per = self.parseConnStatsEvt(statEvt)

                timeNow = datetime.datetime.now()

                if ((waitSeconds != 0) and ((timeNow - startTime).total_seconds() > waitSeconds)):
                    return per

        else:
            self.wait_events(waitSeconds)

        return per

    ## Get connection stats.
    #
    # Send the command to get the connection stats, parse the return value, return the PER.
    ################################################################################
    def connStatsFunc(self, args):

        # Send the command to get the connection stats, save the event
        statEvt = self.send_command("01FDFF00")

        # Parse the connection stats event
        per = self.parseConnStatsEvt(statEvt)

        print(f'PER: {per}')
        return per

    ## txTest function.
    #
    # Sends HCI command for the transmitter test.
    ################################################################################
    def txTestFunc(self, args):
        channel = "%0.2X" % int(args.channel)
        packetLength = "%0.2X" % int(args.packetLength)
        payload = "%0.2X" % int(args.payload)
        phy = "%0.2X" % int(args.phy)
        self.send_command("01342004" + channel + packetLength + payload + phy)

    ## rxTest function.
    #
    # Sends HCI command for the receiver test.
    ################################################################################
    def rxTestFunc(self, args):
        channel = "%0.2X" % int(args.channel)
        phy = "%0.2X" % int(args.phy)
        modulationIndex = "00"
        self.send_command("01332003" + channel + phy + modulationIndex)

    ## End Test function.
    #
    # Sends HCI command for the end test command.
    ################################################################################
    def endTestFunc(self, args):
        # Send the end test command, store the event
        evtString = self.send_command("011F2000")

        # Parse the event and print the number of received packets
        evtData = int(evtString, 16)
        rxPackets = int((evtData & 0xFF00) >> 8) + int((evtData & 0xFF) << 8)
        print("Received PKTS  : " + str(rxPackets))
        return rxPackets

    ## txPower function.
    #
    # Sends HCI command to set the TX power.
    ################################################################################
    def txPowerFunc(self, args):

        # Get an 8 bit signed integer
        power = "%0.2X" % int(tohex(int(args.power), nbits=8), base=16)

        # Set the advertising TX power level
        self.send_command("01F5FF01" + power)

        if (args.handle):
            # Convert int handle to 2 hex bytes, LSB first
            handle = "%0.2X" % (int(args.handle) & 0xFF)
            handle += "%0.2X" % ((int(args.handle) & 0xFF00) >> 8)

            # Set the connection TX power level
            self.send_command("01F6FF03" + handle + power)

            ## Disconnect function.

    #
    # Sends HCI command to disconnect from a connection.
    ################################################################################
    def disconFunc(self, args):
        # Send the disconnect command, handle 0, reason 0x16 Local Host Term
        self.send_command("01060403000016")

    ## Set channel map function.
    #
    # Sends vendor specific HCI commands to set the channel map.
    ################################################################################
    def setChMapFunc(self, args):

        chMask = 0xFFFFFFFFFF
        if (args.mask == None):
            if (args.chan == None):
                # Use all of the channels
                chMask = 0xFFFFFFFFFF
            elif (args.chan == "0"):
                # Use channels 0 and 1
                chMask = 0x0000000003
            else:
                chMask = 0x0000000001
                chMask = chMask | (1 << int(args.chan))

        else:
            chMask = int(args.mask, 16)

        # Mask off the advertising channels
        chMask = chMask & ~(0xE000000000)

        # Convert to a string
        chMaskString = "0x%0.16X" % (chMask)
        print(chMaskString)
        maskString = parseAddr(chMaskString, numNibbles=16)

        # Convert int handle to 2 hex bytes, LSB first
        handle = "%0.2X" % (int(args.handle) & 0xFF)
        handle += "%0.2X" % ((int(args.handle) & 0xFF00) >> 8)

        print(maskString)
        self.send_command("01F8FF0A" + handle + maskString)

    ## Command function.
    #
    # Sends HCI commands.
    ################################################################################
    def cmdFunc(self, args):
        self.send_command(args.cmd)

    ## Read register function.
    #
    # Sends HCI command to read a register.
    ################################################################################
    def readRegFunc(self, args):

        # Get the addr string
        addr = args.addr

        # Reverse the bytes to LSB first
        addrBytes = parseAddr(addr)

        # Get the read length
        readLen = args.length
        if (readLen[:2] != "0x"):
            print("Length must be a hex number starting with 0x")
            return
        readLen = readLen[2:]
        readLenString = "%0.2X" % int(readLen, 16)

        # Calculate the total length, 1 for the read len, 4 for the address length
        totalLen = "%0.2X" % (1 + 4)

        # Send the command and save the event
        evtString = self.send_command("0101FF" + totalLen + readLenString + addrBytes)

        # Get the data
        evtString = evtString[14:]

        # Split the data into bytes
        chunks, chunk_size = len(evtString), 2
        evtBytes = [evtString[i:i + chunk_size] for i in range(0, chunks, chunk_size)]

        # Print the data
        startingAddr = int(args.addr, 16)

        # Pad the length so we can print 32-bit numbers
        readLen = int(readLen, 16)
        readLenPad = readLen
        if (readLen % 4):
            readLenPad += (4 - readLen % 4)

        for i in range(0, readLenPad):
            addr = startingAddr + i

            # Print the address every 4 bytes
            if (i % 4 == 0):
                print("0x%0.8X" % addr, end=": 0x")

            # Print from MSB to LSB in the 32 bit value
            lineAddr = int(i / 4) * 4 + (4 - (i % 4)) - 1

            # Print spaces if we're padding the length
            if (lineAddr >= readLen):
                print("__", end="")
            else:
                print(evtBytes[lineAddr], end="")

            # Print a new line at the end of the 32 bit value
            if (i % 4 == 3):
                print()

        return evtBytes

    ## Write register function.
    #
    # Sends HCI command to write a register.
    ################################################################################
    def writeRegFunc(self, args):

        # Get the data string
        data = args.value

        # Make sure input value is a hex number starting with 0x
        if (data[:2] != "0x"):
            print("Input value must be a hex number starting with 0x")

        data = data[2:]

        # Get the total length, minus 2 for the 0x
        writeLen = len(data)

        # Make sure the writeLen is an even number
        if (writeLen % 2 != 0):
            print("Input value must be on a byte boundary, even number of digits")
            return

        # Convert nibbles to number of bytes
        writeLen = int(writeLen / 2)

        if ((writeLen != 4) and (writeLen != 2) and (writeLen != 1)):
            print("Input value must be either 8, 16, or 32 bits")
            return

        # Calculate the length, convert to string
        totalLen = "%0.2X" % (writeLen + 5)
        writeLen = "%0.2X" % (writeLen)

        # Get the addr string
        addr = args.addr

        # Make sure it's a hex number starting with 0x
        if (addr[:2] != "0x"):
            print("Address must be a hex number starting with 0x")

        addr = addr[2:]

        if (len(addr) != 8):
            print("Address must be 32 bit hex number")

        # Split the address into bytes
        chunks, chunk_size = len(addr), len(addr) // 4
        addrBytes = [addr[i:i + chunk_size] for i in range(0, chunks, chunk_size)]

        # Reverse the bytes to LSB first
        addrBytes = addrBytes[3] + addrBytes[2] + addrBytes[1] + addrBytes[0]

        self.send_command("0100FF" + totalLen + writeLen + addrBytes + data)

