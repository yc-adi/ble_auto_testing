# ble_auto_testing

This project is used to automatically run BLE applications remotely, sniff the BLE packets, save to a file, and parse the file to verify TIFS.  

The related project is [pcapng_parser](https://github.com/yc-adi/pcapng_parser).

## Usage
### Hardware setup 
In this test, two MAX32655 DevKit boards are used. 

Following the instructions in the README of project [VSCode-Maxim](https://github.com/Analog-Devices-MSDK/VSCode-Maxim), program the [BLE5_ctr project](https://github.com/Analog-Devices-MSDK/msdk/tree/main/Examples/MAX32655/BLE5_ctr) into the two DevKit boards. 

Then the setup for this test is illustrated in the following figure.

![Hardware setup](./images/setup.png)


### Local test
In a Windows terminal, cd the source code folder.
```
.\venv\Scripts\activate
python -m ble-auto-testing -h
```
In the virtual environment, run the test.
```
python -m ble-auto-testing --interface COM4-None --device "" --brd0-addr 00:11:22:33:44:11 --brd1-addr 00:11:22:33:44:12 --sp0 COM9 --sp1 COM10 --time 30 --tshark "C:\Program Files\Wireshark\tshark.exe" 
```

