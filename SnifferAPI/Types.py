# Copyright (c) Nordic Semiconductor ASA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form, except as embedded into a Nordic
#    Semiconductor ASA integrated circuit in a product or a software update for
#    such product, must reproduce the above copyright notice, this list of
#    conditions and the following disclaimer in the documentation and/or other
#    materials provided with the distribution.
#
# 3. Neither the name of Nordic Semiconductor ASA nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# 4. This software, with or without modification, must only be used with a
#    Nordic Semiconductor ASA integrated circuit.
#
# 5. Any software provided in binary form under this license must not be reverse
#    engineered, decompiled, modified and/or disassembled.
#
# THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

SLIP_START = 0xAB
SLIP_END   = 0xBC
SLIP_ESC   = 0xCD
SLIP_ESC_START = SLIP_START + 1
SLIP_ESC_END   = SLIP_END   + 1
SLIP_ESC_ESC   = SLIP_ESC   + 1

PROTOVER_V3  = 3
PROTOVER_V2  = 2
PROTOVER_V1  = 1

# UART protocol packet codes (see sniffer_uart_protocol.pdf)
# https://github.com/homewsn/bsniffhub
REQ_FOLLOW                = 0x00
EVENT_FOLLOW              = 0x01
EVENT_PACKET_ADV_PDU      = 0x02
EVENT_CONNECT             = 0x05
EVENT_PACKET_DATA_PDU     = 0x06
REQ_SCAN_CONT             = 0x07
EVENT_DISCONNECT          = 0x09
SET_TEMPORARY_KEY         = 0x0C
PING_REQ                  = 0x0D
PING_RESP                 = 0x0E
SWITCH_BAUD_RATE_REQ      = 0x13
SWITCH_BAUD_RATE_RESP     = 0x14
SET_ADV_CHANNEL_HOP_SEQ   = 0x17
SET_PRIVATE_KEY           = 0x18
SET_LEGACY_LONG_TERM_KEY  = 0x19
SET_SC_LONG_TERM_KEY      = 0x1A
REQ_VERSION               = 0x1B
RESP_VERSION              = 0x1C
REQ_TIMESTAMP             = 0x1D
RESP_TIMESTAMP            = 0x1E
SET_IDENTITY_RESOLVING_KEY= 0x1F
GO_IDLE                   = 0xFE

uart_proto_id_str = {
    0x00: "REQ_FOLLOW",
    0x01: "EVENT_FOLLOW",
    0x02: "EVENT_PACKET_ADV_PDU",
    0x05: "EVENT_CONNECT",
    0x06: "EVENT_PACKET_DATA_PDU",
    0x07: "REQ_SCAN_CONT",
    0x09: "EVENT_DISCONNECT",
    0x0C: "SET_TEMPORARY_KEY",
    0x0D: "PING_REQ",
    0x0E: "PING_RESP",
    0x13: "SWITCH_BAUD_RATE_REQ",
    0x14: "SWITCH_BAUD_RATE_RESP",
    0x17: "SET_ADV_CHANNEL_HOP_SEQ",
    0x18: "SET_PRIVATE_KEY",
    0x19: "SET_LEGACY_LONG_TERM_KEY",
    0x1A: "SET_SC_LONG_TERM_KEY",
    0x1B: "REQ_VERSION",
    0x1C: "RESP_VERSION",
    0x1D: "REQ_TIMESTAMP",
    0x1E: "RESP_TIMESTAMP",
    0x1F: "SET_IDENTITY_RESOLVING_KEY",
    0xFE: "GO_IDLE"
}

PACKET_TYPE_UNKNOWN       = 0x00
PACKET_TYPE_ADVERTISING   = 0x01
PACKET_TYPE_DATA          = 0x02

ADV_TYPE_ADV_IND          = 0x0
ADV_TYPE_ADV_DIRECT_IND   = 0x1
ADV_TYPE_ADV_NONCONN_IND  = 0x2
ADV_TYPE_ADV_SCAN_IND     = 0x6
ADV_TYPE_SCAN_REQ         = 0x3
ADV_TYPE_SCAN_RSP         = 0x4
ADV_TYPE_CONNECT_REQ      = 0x5
ADV_TYPE_ADV_EXT_IND      = 0x7

PHY_1M                    = 0
PHY_2M                    = 1
PHY_CODED                 = 2

PHY_CODED_CI_S8           = 0
PHY_CODED_CI_S2           = 1

# @see [BLE Series Part 1: A Brief Overview of Bluetooth Low Energy](https://medium.com/rtone-iot-security/a-brief-overview-of-bluetooth-low-energy-79be06eab4df)
# @see https://microchipdeveloper.com/wireless:ble-link-layer-packet-types
PDU_TYPE_ADV_IND            = 0
PDU_TYPE_ADV_DIRECT_IND     = 1
PDU_TYPE_ADV_NONCONN_IND    = 2
PDU_TYPE_SCAN_REQ           = 3
PDU_TYPE_SCAN_RSP           = 4
PDU_TYPE_CONNECT_IND        = 5
PDU_TYPE_ADV_SCAN_IND       = 6
PDU_TYPE_ADV_EXT_IND        = 7
PDU_TYPE_AUX_CONNECT_RSP    = 8

PDU_Types = [
    'ADV_IND',              # 0
    'ADV_DIRECT_IND',       # 1
    'ADV_NONCONN_IND',      # 2
    'SCAN_REQ',
    'SCAN_RSP',
    'CONNECT_IND',
    'ADV_SCAN_IND',
    'ADV_EXT_IND',
    'AUX_CONNECT_RSP'
]
