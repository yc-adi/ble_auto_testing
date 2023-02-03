#!/bin/bash

echo "#########################################################################"
echo "# The working folder is the root of this repo.                          #"
echo "# .github/workflows/run_per_test.sh 2nd_board_type                      #"
echo "#########################################################################"
echo 
echo $0 $@
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

cd ~/Workspace/ble_auto_testing
echo "PWD: $(pwd)"
ls -d */
echo

#set -x
#set -e
#set -o pipefail

python -m venv venv
source ./venv/bin/activate
python -m pip install -r requirements.txt

# Note: index of the two DevKit boards are 1-based.
echo

FILE=/home/$USER/Workspace/Resource_Share/boards_config.json
if [ -f "$FILE" ]; then
    sniffer_sn=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['sniffer']['sn'])"`

    if [ `hostname` == "yingcai-OptiPlex-790" ]; then
        jtag_sn_1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board_y1']['daplink'])"`
        jtag_sn_2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board_y2']['daplink'])"`
        DevKitUart0Sn_1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board_y1']['uart0'])"`
        DevKitUart0Sn_2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board_y2']['uart0'])"`
        DevKitUart3Sn_1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board_y1']['uart3'])"`
        DevKitUart3Sn_2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board_y2']['uart3'])"`

        max32665_daplink=`/usr/bin/python3   -c "import sys, json; print(json.load(open('$FILE'))['max32665_board_2']['daplink'])"`
        max32665_cn2_uart1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32665_board_2']['uart1'])"`
        max32665_uart0=`/usr/bin/python3     -c "import sys, json; print(json.load(open('$FILE'))['max32665_board_2']['uart0'])"`

        max32690_daplink=`/usr/bin/python3   -c "import sys, json; print(json.load(open('$FILE'))['max32690_board_3']['daplink'])"`
        max32690_cn2_uart2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32690_board_3']['uart2'])"`
        max32690_uart3=`/usr/bin/python3     -c "import sys, json; print(json.load(open('$FILE'))['max32690_board_3']['uart3'])"`
    else
        jtag_sn_1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board1']['daplink'])"`
        jtag_sn_2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board2']['daplink'])"`
        DevKitUart0Sn_1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board1']['uart0'])"`
        DevKitUart0Sn_2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board2']['uart0'])"`
        DevKitUart3Sn_1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board1']['uart3'])"`
        DevKitUart3Sn_2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board2']['uart3'])"`

        max32665_daplink=`/usr/bin/python3   -c "import sys, json; print(json.load(open('$FILE'))['max32665_board1']['daplink'])"`
        max32665_cn2_uart1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32665_board1']['uart1'])"`
        max32665_uart0=`/usr/bin/python3     -c "import sys, json; print(json.load(open('$FILE'))['max32665_board1']['uart0'])"`

        max32690_daplink=`/usr/bin/python3   -c "import sys, json; print(json.load(open('$FILE'))['max32690_board_w1']['daplink'])"`
        max32690_cn2_uart2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32690_board_w1']['uart2'])"`
        max32690_uart3=`/usr/bin/python3     -c "import sys, json; print(json.load(open('$FILE'))['max32690_board_w1']['uart3'])"`
    fi
else
    echo "Err: can't find the board configuration file ${FILE}."
    exit 1
fi

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
echo "board 1 trace port: $devSerial_1"
echo "  board 1 HCI port: $devUart3Serial_1"
echo 
echo "board 2 trace port: $devSerial_2"
echo "  board 2 HCI port: $devUart3Serial_2"
echo 
echo "---------------------------------------------------------------------------------------------"
echo "./venv/bin/python ./per_test.py --interface ${snifferSerial}-None --device "" --brd0-addr 00:11:22:33:44:21 --brd1-addr 00:11:22:33:44:22 --sp0 $devUart3Serial_1 --sp1 $devUart3Serial_2 --tp0 $devSerial_1 --tp1 $devSerial_2 --time 35 --tshark /usr/bin/tshark
"
./venv/bin/python ./per_test.py --interface ${snifferSerial}-None --device "" --brd0-addr 00:11:22:33:44:21 --brd1-addr 00:11:22:33:44:22 --sp0 $devUart3Serial_1 --sp1 $devUart3Serial_2 --tp0 $devSerial_1 --tp1 $devSerial_2 --time 35 --tshark /usr/bin/tshark
