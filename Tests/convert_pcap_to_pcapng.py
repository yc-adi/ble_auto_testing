#!/usr/bin/env python3

import ble_auto_testing

if __name__ == "__main__":
    file = "../Temp/dev-ttyACM6-3.6__2023-04-26_15-47-16.pcap"
    ble_auto_testing.convert_pcap_to_pcapng(file, "new.pcapng", "/usr/bin/tshark")