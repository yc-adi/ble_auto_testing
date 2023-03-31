#!/bin/bash

echo "#####################################################"
echo "# The working folder is the root of this repo.      #"
echo "# .github/workflows/run.sh 2nd_board_type           #"
echo "#####################################################"
echo

ERR_INVALID_2ND_BRD_TYPE=1

if [ $# != 1 ]; then
    SEC_BRD_TYPE=1
    echo "The 2nd board is MAX32655 by default."
else
    SEC_BRD_TYPE=$1
    case $SEC_BRD_TYPE in
        1)
            echo "The 2nd board is MAX32655."
        ;;

        2)
            echo "The 2nd board is MAX32665."
        ;;

        3)
            echo "The 2nd board is MAX32690."
        ;;

        *)
            echo "Invalid 2nd board type. 1: MAX32655, 2: MAX32665, 3: MAX32690."
            exit $ERR_INVALID_2ND_BRD_TYPE
        ;;
    esac
fi

echo "PWD: $PWD"
echo

ls -hal

set -e
set -o pipefail

#echo "Create the Python env."
#python -m venv venv
#source ./venv/bin/activate
#python -m pip install -r requirements.txt
source ~/anaconda3/etc/profile.d/conda.sh
conda activate py3_10

# Note: index of the two DevKit boards are 1-based.
echo

FILE=/home/$USER/Workspace/ci_config/boards_config.json
# get the test boards
TEST_CONFIG_FILE=/home/$USER/Workspace/ci_config/timing_tests.json

HOST_NAME=`hostname`
sniffer=`python3 -c "import sys, json; print(json.load(open('$TEST_CONFIG_FILE'))['ble_timing_verify.yml']['$HOST_NAME']['sniffer'])"
BRD1=`python3 -c "import sys, json; print(json.load(open('$TEST_CONFIG_FILE'))['']['$HOST_NAME']['max32655'][0])"`
BRD2=`python3 -c "import sys, json; print(json.load(open('$TEST_CONFIG_FILE'))['']['$HOST_NAME']['max32655'][1])"`

echo "     sniffer board: ${sniffer}"
echo "              BRD1: ${BRD1}"
echo "              BRD2: ${BRD2}"
echo

sniffer_sn=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${sniffer}']['sn'])"`
jtag_sn_1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${BRD1}']['DAP_sn'])"`
jtag_sn_2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${BRD2}']['DAP_sn'])"`
DevKitUart0Sn_1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${BRD1}']['con_sn'])"`
DevKitUart0Sn_2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${BRD2}']['con_sn'])"`
DevKitUart3Sn_1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${BRD1}']['hci_sn'])"`
DevKitUart3Sn_2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${BRD2}']['hci_sn'])"`

max32665_daplink=`/usr/bin/python3 -c   "import sys, json; print(json.load(open('$FILE'))['${BRD2}']['DAP_sn'])"`
max32665_cn2_uart1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${BRD2}']['con_sn'])"`
max32665_uart0=`/usr/bin/python3 -c     "import sys, json; print(json.load(open('$FILE'))['${BRD2}']['hci_sn'])"`

max32690_daplink=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${BRD2}']['DAP_sn'])"`
max32690_cn2_uart2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${BRD2}']['con_sn'])"`
max32690_uart3=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${BRD2}']['hci_sn'])"`


echo "        sniffer_sn: $sniffer_sn"
echo
echo "         jtag_sn_1: $jtag_sn_1"
echo "   DevKitUart0Sn_1: $DevKitUart0Sn_1"
echo "   DevKitUart0Sn_2: $DevKitUart0Sn_2"
echo
echo "         jtag_sn_2: $jtag_sn_2"
echo "   DevKitUart3Sn_1: $DevKitUart3Sn_1"
echo "   DevKitUart3Sn_2: $DevKitUart3Sn_2"
echo
echo "  max32665_daplink: $max32665_daplink"
echo "max32665_cn2_uart1: $max32665_cn2_uart1"
echo "    max32665_uart0: $max32665_uart0"
echo
echo "  max32690_daplink: $max32690_daplink"
echo "max32690_cn2_uart2: $max32690_cn2_uart2"
echo "    max32690_uart3: $max32690_uart3"
echo

export snifferSerial=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $sniffer_sn | awk -F tty '{print $2}')"

export devSerial_1=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $DevKitUart0Sn_1 | awk -F tty '{print $2}')"
export devUart3Serial_1=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $DevKitUart3Sn_1 | awk -F tty '{print $2}')"

case $SEC_BRD_TYPE in
    1)
        export devSerial_2=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $DevKitUart0Sn_2 | awk -F tty '{print $2}')"
        export devUart3Serial_2=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $DevKitUart3Sn_2 | awk -F tty '{print $2}')"
    ;;
    2)
        export devSerial_2=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $max32665_cn2_uart1 | awk -F tty '{print $2}')"
        export devUart3Serial_2=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $max32665_uart0 | awk -F tty '{print $2}')"
    ;;
    3)
        export devSerial_2=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $max32690_cn2_uart2 | awk -F tty '{print $2}')"
        export devUart3Serial_2=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $max32690_uart3 | awk -F tty '{print $2}')"
    ;;
esac

echo "           sniffer: $snifferSerial"
echo
unset devSerial_1
echo "board 1 trace port: $devSerial_1"
echo "  board 1 HCI port: $devUart3Serial_1"
echo 
echo "board 2 trace port: $devSerial_2"
echo "  board 2 HCI port: $devUart3Serial_2"
echo 

if [ `hostname` == "yingcai-OptiPlex-790" ]; then
    ADDR1=00:12:23:34:45:01
    ADDR2=00:12:23:34:45:02
else
    ADDR1=00:11:22:33:44:21
    ADDR2=00:11:22:33:44:22
fi

unbuffer python3 ble_test.py --interface ${snifferSerial}-None --device "" \
    --brd0-addr $ADDR1 --brd1-addr $ADDR2 \
    --sp0 $devUart3Serial_1 --sp1 $devUart3Serial_2 \
    --tp0 "$devSerial_1" --tp1 $devSerial_2 \
    --time 35 --tshark /usr/bin/tshark

yes | cp -p output/*.* /tmp/ci_test/timing/
