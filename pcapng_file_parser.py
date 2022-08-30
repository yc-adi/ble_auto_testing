#
# @see PCAP Next Generation Dump File Format
# @see https://github.com/pcapng/pcapng
# @see https://www.tcpdump.org/linktypes/LINKTYPE_NORDIC_BLE.html
#
import copy
from datetime import datetime
import logging
import os
from os.path import exists
from SnifferAPI import Logger, Packet, Exceptions, SnifferCollector
from SnifferAPI.Types import *
import time
from SnifferAPI.Packet import all_tifs
import sys
from pcapng import FileScanner
from pprint import pprint

parser_log_handler = None


class BleSnifferPacketParser(object):
    """Nordic BLE Sniffer Packet"""

    def __init__(self, **kwargs):
        self.parsed_packet = {}  # board, payload_len, protocol_ver, packet_counter
        # packet_id, packet_len, flags,


def parse_pcapng_file(file_type, file):
    """parse the saved pcapng file.
    @see [python-pcapng wireshark 包解析](https://blog.csdn.net/weifengdq/article/details/117751828)
    """
    #
    # utilize the nRF sniffer code
    #
    packet_reader = Packet.PacketReader(pcapng_parser=True)

    with open(file, 'rb') as fp:
        scanner = FileScanner(fp)
        block_ndx = 1
        packet_ndx = 1
        for block in scanner:
            if block_ndx == 1:  # SectionHeader 信息(cpu, os, wireshark version等)
                # print(f'1st block: {block}')
                block_ndx = 2
            elif block_ndx == 2:  # InterfaceDescription, 主要是接口的信息, 如以太网网卡信息等
                # print(f'2nd block: {block}')
                block_ndx = 3
            else:  # EnhancedPacket
                # <EnhancedPacket interface_id=0 timestamp_high=377899 timestamp_low=1033621862 packet_payload_info=(
                # 93, 93, b'\x11"3DUfH\xb0-\x13G*\x08\x00E\x00\x00O^e@\x00@\x11NN\xc0\xa8\x06B\xc0\xa8\x06X\xe2\x15
                # \x0f\xa1\x00;\xbc\xd3\xaa\x00\x00\x00\x19\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
                # \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
                # \x00\x00\x00\x00\x00\x00\x00\x00') options=Options({})>
                # <EnhancedPacket interface_id=0
                # timestamp_high=386514 timestamp_low=3889417204 captured_len=43 packet_len=43
                # packet_data=b'\x07$\x00\x03@\x10\x02\n\x01%.\x00\x00\x000\x82\x01\xd6\xbe\x89\x8e\x00\x11\xd8R\x04
                # \x80\x18\x00\x02\x01\x06\x07\tPeriphs5\xec' options=Options({})> print(f'{packet_ndx:>6}: {
                # block.timestamp_high}, {block.timestamp_low}, {block.timestamp}')
                block_time = datetime.utcfromtimestamp(block.timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")
                data = ' '.join(format(x, '02x') for x in block.packet_data)
                # print(f'{packet_ndx:}: {block_time}, len: {block.packet_len}, data: {data}')

                #if packet_ndx == 10:
                #    print("break")

                try:
                    packet_list = block.packet_data[1:]
                    packet = Packet.Packet(packet_list, is_parser=True, packet_reader=packet_reader,
                                           file_type=file_type)

                    if packet.valid:
                        packet_reader.handlePacketCompatibility(packet)

                    if packet is None or not packet.valid:
                        raise Exceptions.InvalidPacketException("")
                except Exceptions.InvalidPacketException:
                    pass
                else:
                    if packet.id == EVENT_PACKET_DATA_PDU or packet.id == EVENT_PACKET_ADV_PDU:
                        pass
                    elif packet.id == EVENT_FOLLOW:
                        # This packet has no value for the user.
                        pass
                    elif packet.id == EVENT_CONNECT:
                        pass
                    elif packet.id == EVENT_DISCONNECT:
                        pass
                    elif packet.id == SWITCH_BAUD_RATE_RESP:
                        pass
                    elif packet.id == PING_RESP:
                        if hasattr(packet, 'version'):
                            versions = {1116: '3.1.0',
                                        1115: '3.0.0',
                                        1114: '2.0.0',
                                        1113: '2.0.0-beta-3',
                                        1112: '2.0.0-beta-1'}
                            fwversion = versions.get(packet.version, 'SVN rev: %d' % packet.version)
                            print(f'fw version: {fwversion}')
                    elif packet.id == RESP_VERSION:
                        pass
                    elif packet.id == RESP_TIMESTAMP:
                        """
                        # Use current time as timestamp reference
                        packet_reader._last_time = time.time()
                        packet_reader._last_timestamp = packet.timestamp

                        lt = time.localtime(packet_reader._last_time)
                        usecs = int((packet_reader._last_time - int(packet_reader._last_time)) * 1_000_000)
                        logging.info(f'Firmware timestamp {packet_reader._last_timestamp} reference: '
                                     f'{time.strftime("%b %d %Y %X", lt)}.{usecs} {time.strftime("%Z", lt)}')
                        """
                    else:
                        logging.info("Unknown packet ID")

                    packet_reader.handlePacketHistory(packet)  # Will save this packet as last packet
                packet_ndx += 1

            if packet_ndx > 10:
                #break
                pass


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f'Please give the pcapng file type and name with full path.')
        exit(1)

    # file_name = r'C:\Users\Ycai3\Documents\Ellisys\Captures\fit_01.pcapng'
    file_type = int(sys.argv[1])
    if file_type != 0 and file_type != 1:
        print(f'file type should be 0 (Wireshark saved pcapng file) or 1 (pcap converted pcapng file).')
        exit(2)

    file_name = sys.argv[2]

    if not exists(file_name):
        print(f'File "{file_name}" does not exist.')
        exit(3)

    parse_pcapng_file(file_type, file_name)

    if len(all_tifs) > 0:
        max_tifs = max(all_tifs)
        min_tifs = min(all_tifs)
        avg = sum(all_tifs) / len(all_tifs)

        print(f'TIFS, total: {len(all_tifs)}, max: {max_tifs}, min: {min_tifs}, average: {avg:.1f}')
        if max_tifs <= 152 and min_tifs >= 148:
            print("TIFS verification: PASS")
        else:
            print("TIFS verification: FAIL")
            exit(11)
    else:
        print("No TIFS captured.")
        exit(10)

    # print("Done!")
