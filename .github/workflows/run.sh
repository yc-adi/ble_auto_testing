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

echo "--- PWD: $PWD"
ls -hal

#set -x
set -e
set -o pipefail

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
        
        max32665_daplink=`/usr/bin/python3 -c   "import sys, json; print(json.load(open('$FILE'))['max32665_board_2']['daplink'])"`
        max32665_cn2_uart1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32665_board_2']['uart1'])"`
        max32665_uart0=`/usr/bin/python3 -c     "import sys, json; print(json.load(open('$FILE'))['max32665_board_2']['uart0'])"`

        max32690_daplink=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32690_board_3']['daplink'])"`
        max32690_cn2_uart2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32690_board_3']['uart2'])"`
        max32690_uart3=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32690_board_3']['uart3'])"`
    else
        jtag_sn_1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board1']['daplink'])"`
        jtag_sn_2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board2']['daplink'])"`
        DevKitUart0Sn_1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board1']['uart0'])"`
        DevKitUart0Sn_2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board2']['uart0'])"`
        DevKitUart3Sn_1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board1']['uart3'])"`
        DevKitUart3Sn_2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32655_board2']['uart3'])"`
    
        max32665_daplink=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32665_board1']['daplink'])"`
        max32665_cn2_uart1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32665_board1']['uart1'])"`
        max32665_uart0=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32665_board1']['uart0'])"`

        max32690_daplink=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32690_board_w1']['daplink'])"`
        max32690_cn2_uart2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32690_board_w1']['uart2'])"`
        max32690_uart3=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32690_board_w1']['uart3'])"`
    fi
else
    if [ `hostname` == "yingcai-OptiPlex-790" ]; then
        sniffer_sn="C7526B63B7BD5962"
        jtag_sn_1=0444170169c5c14600000000000000000000000097969906
        jtag_sn_2=044417016bd8439a00000000000000000000000097969906
        
        DevKitUart0Sn_1="D3073IDG"
        DevKitUart0Sn_2="D309ZDE9"
        DevKitUart3Sn_1="DT03OFRJ"
        DevKitUart3Sn_2="DT03NSU1"

        # MAX32665
        # usb-ARM_DAPLink_CMSIS-DAP_0409000069f9823300000000000000000000000097969906-if01
        max32665_daplink=0409000069f9823300000000000000000000000097969906
        # CN2 - UART1
        # usb-FTDI_FT230X_Basic_UART_D30A1X9V-if00-port0
        max32665_cn2_uart1="D30A1X9V"
        # usb-FTDI_FT230X_Basic_UART_DT03OEFO-if00-port0
        max32665_uart0="DT03OGQ4"

        # MAX32690
        # 
        max32690_daplink=04091702b55e4e9600000000000000000000000097969906
        # CN2 - UART2
        #
        max32690_cn2_uart2="D30AKVTH"

        #
        max32690_uart3="DT03OEFO"
    else  # wall-e
        sniffer_sn="47F745082791B043"
        jtag_sn_1=04091702d4f18ac600000000000000000000000097969906
        jtag_sn_2=04091702f7f18a2900000000000000000000000097969906
        DevKitUart0Sn_1="D309ZDFB"
        DevKitUart0Sn_2="D3073ICQ"
        DevKitUart3Sn_1="DT03O9WB"
        DevKitUart3Sn_2="DT03OFQ0"

        # MAX32665, SN: 13
        # usb-ARM_DAPLink_CMSIS-DAP_0409000098d9439b00000000000000000000000097969906-if01 -> ../../ttyACM2
        max32665_daplink=0409000098d9439b00000000000000000000000097969906
        # CN2 - UART1
        #  usb-FTDI_FT230X_Basic_UART_D30A1X9X-if00-port0 -> ../../ttyUSB1
        max32665_cn2_uart1="D30A1X9X"
        # usb-FTDI_FT230X_Basic_UART_DT03O747-if00-port0 -> ../../ttyUSB13
        max32665_uart0="DT03O747"

        # board w1
        max32690_daplink=0409170246dfc09500000000000000000000000097969906
        max32690_cn2_uart2="D30ALJPW"
        max32690_uart3="0409170246dfc09500000000000000000000000097969906"
    fi
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

./venv/bin/python ./ble_test.py --interface ${snifferSerial}-None --device "" \
    --brd0-addr 00:11:22:33:44:21 --brd1-addr 00:11:22:33:44:22 --sp0 $devUart3Serial_1 --sp1 $devUart3Serial_2 \
    --time 35 --tshark /usr/bin/tshark
