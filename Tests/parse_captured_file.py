#!/usr/bin/env python3

import ble_test 
import os

from SnifferAPI.Packet import all_tifs

if __name__ == "__main__":
    file = "../Temp/phy4.pcapng"
    file_path = os.path.expanduser(file)
    print(f'captured file: {file_path}')

    ble_test.parse_phy_timing_test_results(0, file_path)

    res = ble_test.check_results(3)


    