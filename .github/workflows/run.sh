#!/bin/bash

set -e
set -o pipefail

echo "in run.sh"
echo "PWD: "$PWD
ls

python -m venv venv
source ./venv/bin/activate
python -m pip install -r requirements.txt

# Note: index of the two DevKit boards are 1-based.
if [ `hostname` == "yingcai-OptiPlex-790" ]
then
    sniffer_sn="000680435664"
    jtag_sn_1=0409000069c5c14600000000000000000000000097969906
    jtag_sn_2=040900006bd8439a00000000000000000000000097969906
    DevKitUart0Sn_1="D3073IDG"
    DevKitUart0Sn_2="D309ZDE9"
    DevKitUart3Sn_1="DT03OFRJ"
    DevKitUart3Sn_2="DT03NSU1"    
else  # wall-e
    sniffer_sn="000680435664"
    jtag_sn_1=04091702f7f18a2900000000000000000000000097969906
    jtag_sn_2=0409170246dfc09500000000000000000000000097969906
    DevKitUart0Sn_1="D309ZDFB"
    DevKitUart0Sn_2="D3073ICQ"
    DevKitUart3Sn_1="DT03O9WB"
    DevKitUart3Sn_2="DT03OFQ0"
fi

export snifferSerial=/dev/"$(ls -la /dev/serial/by-id | grep -n $sniffer_sn | rev | cut -b 1-7 | rev)"

export devSerial_1=/dev/"$(ls -la /dev/serial/by-id | grep -n $DevKitUart0Sn_1 | rev | cut -b 1-7 | rev)"
export devUart3Serial_1=/dev/"$(ls -la /dev/serial/by-id | grep -n $DevKitUart3Sn_1 | rev | cut -b 1-7 | rev)"

export devSerial_2=/dev/"$(ls -la /dev/serial/by-id | grep -n $DevKitUart0Sn_2 | rev| cut -b 1-7| rev)"
export devUart3Serial_2=/dev/"$(ls -la /dev/serial/by-id | grep -n $DevKitUart3Sn_2 | rev| cut -b 1-7| rev)"

./venv/bin/python ./ble_auto_testing.py --interface ${snifferSerial}-None --device "" --brd0-addr 00:11:22:33:44:11 --brd1-addr 00:11:22:33:44:12 --sp0 $devUart3Serial_1 --sp1 $devUart3Serial_2 --time 30 --tshark /usr/bin/tshark
