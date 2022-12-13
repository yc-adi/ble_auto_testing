#!/bin/bash

_DEBUG="ON"
function DEBUG()
{
    [ "$_DEBUG" == "ON" ] && $@
}

echo "###############################################################################"
echo "# usage: ./build_flash_max32655_max32665.sh path_of_MaximSDK 2nd_board_type   #"
echo "# example: ./build_flash_max32655_max32665.sh /home/\$USER/Workspace/msdk  1   #"
echo "###############################################################################"
echo

ERR_INVALID_ARGS=1
ERR_INVALID_BORAD_TYPE=2
ERR_INVALID_MSDK_PATH=3

if [ $# != 2 ]; then
    echo "usage: ./build_flash_max32655_max32665.sh path_of_MaximSDK 2nd_board_type"
    exit $ERR_INVALID_ARGS
fi

export MSDK_DIR=$1
DEBUG echo MSDK_DIR: $MSDK_DIR

SEC_BRD_TYPE=$2
DEBUG echo "2nd board type: $SEC_BRD_TYPE"
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
        exit $ERR_INVALID_BORAD_TYPE
    ;;
esac

if [ ! -d $MSDK_DIR ] || [ -z "$MSDK_DIR" ]; then
    echo "The input MSDK_DIR does not exist."
    exit $ERR_INVALID_MSDK_PATH
fi

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

        max32690_daplink=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32690_board_24']['daplink'])"`
        max32690_cn2_uart2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32690_board_24']['uart2'])"`
        max32690_uart3=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['max32690_board_24']['uart3'])"`
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

export TARGET_1_LC=max32655
export TARGET_1_UC=MAX32655
export TARGET_1_CFG=${TARGET_1_LC}.cfg

export TARGET_2_LC=max32665
export TARGET_2_UC=MAX32665
export TARGET_2_CFG=${TARGET_2_LC}.cfg

export TARGET_3_LC=max32690
export TARGET_3_UC=MAX32690
export TARGET_3_CFG=${TARGET_3_LC}.cfg

export CMSIS_DAP_ID_1=$jtag_sn_1
export devSerial_1=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $DevKitUart0Sn_1 | awk -F tty '{print $2}')"
export devUart3Serial_1=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $DevKitUart3Sn_1 | awk -F tty '{print $2}')"

export CMSIS_DAP_ID_2=$jtag_sn_2
export devSerial_2=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $DevKitUart0Sn_2 | awk -F tty '{print $2}')"
export devUart3Serial_2=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $DevKitUart3Sn_2 | awk -F tty '{print $2}')"

# MAX32665
export CMSIS_DAP_ID_MAX32665=$max32665_daplink
export max32665_mon=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $max32665_cn2_uart1 | awk -F tty '{print $2}')"
export max32665_hci=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $max32665_uart0 | awk -F tty '{print $2}')"

# MAX32690
export CMSIS_DAP_ID_MAX32690=$max32690_daplink
export max32690_mon=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $max32690_cn2_uart2 | awk -F tty '{print $2}')"
export max32690_hci=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $max32690_uart3 | awk -F tty '{print $2}')"

export APP_EXAMPLES_PATH=$MSDK_DIR/Examples
export EXAMPLE_TEST_PATH=$MSDK_DIR/Examples_tests
export OPENOCD_TOOL_PATH=/home/lparm/Tools/openocd/tcl

export VERBOSE_TEST=1

echo
echo "         nRF51 dongle: $snifferSerial"
echo
echo "       DevKit UART0 1: $devSerial_1"
echo "       DevKit UART3 1: $devUart3Serial_1"
echo
echo "       DevKit UART0 2: $devSerial_2"
echo "       DevKit UART3 2: $devUart3Serial_2"
echo
echo "MAX32665 monitor port: $max32665_mon"
echo "    MAX32665 HCI port: $max32665_hci"
echo
echo "MAX32690 monitor port: $max32690_mon"
echo "    MAX32690 HCI port: $max32690_hci"
echo

export failedTestList=" "

if [ `hostname` == "wall-e" ] 
then
    export OPENOCD_TCL_PATH=/home/btm-ci/Tools/openocd/tcl
    export OPENOCD=/home/btm-ci/Tools/openocd/src/openocd
    export ROBOT=/home/btm-ci/.local/bin/robot
else
    export OPENOCD_TCL_PATH=/home/$USER/softwares/openocd/tcl
    export OPENOCD=/home/$USER/softwares/openocd/src/openocd
    export ROBOT=/home/btm-ci/.local/bin/robot
fi

function script_clean_up()
{
    # check if some runoff opeocd instance is running
    set +e
    if ps -p $openocd_dapLink_pid > /dev/null
    then
    kill -9 $openocd_dapLink_pid || true
    fi

    set -e
}
trap script_clean_up EXIT SIGINT

# Function accepts parameters: filename, CMSIS_DAP_ID_x 
function flash_with_openocd()
{
    # mass erase and flash
    set +e
    $OPENOCD -f $OPENOCD_TCL_PATH/interface/cmsis-dap.cfg -f $OPENOCD_TCL_PATH/target/$TARGET_1_CFG -s $OPENOCD_TCL_PATH -c "cmsis_dap_serial $2" -c "gdb_port 3333" -c "telnet_port 4444" -c "tcl_port 6666"  -c "init; reset halt;max32xxx mass_erase 0" -c "program $1 verify reset exit" > /dev/null &
    openocd_dapLink_pid=$!
    # wait for openocd to finish
    while kill -0 $openocd_dapLink_pid ; do
    sleep 1
    # we can add a timeout here if we want
    done
    set -e
    # Attempt to verify the image, prevent exit on error
    $OPENOCD -f $OPENOCD_TCL_PATH/interface/cmsis-dap.cfg -f $OPENOCD_TCL_PATH/target/$TARGET_1_CFG -s $OPENOCD_TCL_PATH/ -c "cmsis_dap_serial  $2" -c "gdb_port 3333" -c "telnet_port 4444" -c "tcl_port 6666"  -c "init; reset halt; flash verify_image $1; reset; exit"

    # Check the return value to see if we received an error
    if [ "$?" -ne "0" ]
    then
    # Reprogram the device if the verify failed
    $OPENOCD -f $OPENOCD_TCL_PATH/interface/cmsis-dap.cfg -f $OPENOCD_TCL_PATH/target/$TARGET_1_CFG -s $OPENOCD_TCL_PATH  -c "cmsis_dap_serial  $2" -c "gdb_port 3333" -c "telnet_port 4444" -c "tcl_port 6666"  -c "init; reset halt;max32xxx mass_erase 0" -c "program $1 verify reset exit" > /dev/null &
    openocd_dapLink_pid=$!
    fi
}

# This function accepts a CMSIS device ID as a parameter
function erase_with_openocd()
{
    $OPENOCD -f $OPENOCD_TCL_PATH/interface/cmsis-dap.cfg -f $OPENOCD_TCL_PATH/target/$TARGET_2_CFG -s $OPENOCD_TCL_PATH/  -c "cmsis_dap_serial  $1" -c "gdb_port 3333" -c "telnet_port 4444" -c "tcl_port 6666"  -c "init; reset halt; flash erase_address 0x10004000 0x40000; reset exit" &
    openocd_dapLink_pid=$!
    # wait for openocd to finish
    wait $openocd_dapLink_pid
}

function run_notConntectedTest()
{
    project_marker
    cd $PROJECT_NAME
    set +x
    echo "> Flashing $PROJECT_NAME"
    make -j8 > /dev/null
    cd build/
    flash_with_openocd $TARGET_1_LC.elf $CMSIS_DAP_ID_1
    #place to store robotframework results
    mkdir $EXAMPLE_TEST_PATH/results/$PROJECT_NAME
    cd $EXAMPLE_TEST_PATH/tests
    # do not let a single failed test stop the testing of the rest
    set +e
    #runs desired test 
    $ROBOT -d $EXAMPLE_TEST_PATH/results/$PROJECT_NAME/ -v VERBOSE:$VERBOSE_TEST -v SERIAL_PORT:$devSerial_1 $PROJECT_NAME.robot
    let "testResult=$?"
    if [ "$testResult" -ne "0" ] 
    then
    # update failed test count
    let "numOfFailedTests+=$testResult"  
    failedTestList+="| $PROJECT_NAME "
    fi
    set -e     
    #get back to target directory
    cd $MSDK_DIR/Examples/$TARGET_1_UC
}

# In order to verify the TIFS, two DevKit boards are required to be
# programmed with BLE5_ctr project.
function prepare_tifs_test()
{
    project_marker

    cd $MSDK_DIR/Examples/$TARGET_1_UC/$PROJECT_NAME
    set +x
    
    DEBUG echo "---------------------------------------------------"
    DEBUG echo "Build and flash the 1st board."
    DEBUG echo "---------------------------------------------------"
    make MAXIM_PATH=$MSDK_DIR distclean
    make -j8 MAXIM_PATH=$MSDK_DIR
    
    cd build/
    flash_with_openocd $TARGET_1_LC.elf $CMSIS_DAP_ID_1

    case $SEC_BRD_TYPE in
        1)  # MAX32655
            DEBUG echo "---------------------------------------------------"
            DEBUG echo "Flash the 2nd board."
            DEBUG echo "---------------------------------------------------"
            flash_with_openocd $TARGET_1_LC.elf $CMSIS_DAP_ID_2
        ;;

        2)  # MAX32665
            cd $MSDK_DIR/Examples/$TARGET_2_UC/$PROJECT_NAME
            DEBUG echo "---------------------------------------------------"
            DEBUG echo "Build and flash the 2nd board."
            DEBUG echo "---------------------------------------------------"
            DEBUG echo "build $MSDK_DIR/Examples/$TARGET_2_UC/$PROJECT_NAME"
            make MAXIM_PATH=$MSDK_DIR distclean
            make -j8 MAXIM_PATH=$MSDK_DIR
    
            cd build/
            flash_with_openocd $TARGET_2_LC.elf $CMSIS_DAP_ID_MAX32665
        ;;

        3)  # MAX32690
            cd $MSDK_DIR/Examples/$TARGET_3_UC/$PROJECT_NAME
            DEBUG echo "---------------------------------------------------"
            DEBUG echo "Build and flash the 2nd board."
            DEBUG echo "---------------------------------------------------"
            DEBUG echo "build $MSDK_DIR/Examples/$TARGET_3_UC/$PROJECT_NAME"
            make MAXIM_PATH=$MSDK_DIR distclean
            make -j8 MAXIM_PATH=$MSDK_DIR
    
            cd build/
            flash_with_openocd $TARGET_3_LC.elf $CMSIS_DAP_ID_MAX32690
        ;;

        *)
        ;;
    esac

    cd $MSDK_DIR/Examples/$TARGET_1_UC
}

function project_marker()
{
    echo "=============================================================================="
    printf "\r\n$PROJECT_NAME Flashing Procedure \r\n\r\n"
}

###############################################################################
# checkout submodules
# Update the submodules, this will use ssh
cd $MSDK_DIR/
git submodule init
git submodule sync
git submodule update --init --recursive

# build BLE examples
cd $MSDK_DIR/Examples/$TARGET_1_UC
DEBUG echo pwd=$(pwd)
SUBDIRS=$(find . -type d -name "BLE5*")
DEBUG echo SUBDIRS: $SUBDIRS

#for dir in ${SUBDIRS}
#    do
#    echo "---------------------------------------"
#    echo " Validation build for ${dir}"
#    echo "---------------------------------------"
#    make -C ${dir} clean
#    make -C ${dir} libclean
#    make -C ${dir} -j8
#done

project_filter='BLE5_ctr'

cd $MSDK_DIR/Examples/$TARGET_1_UC

# tests projects
for dir in ./*/; do
    #(cd "$dir")
    if [[ "$dir" == *"$project_filter"* ]]; then
    
        export PROJECT_NAME=$(echo "$dir" | tr -d /.) 
        echo PROJECT_NAME: $PROJECT_NAME

        case $PROJECT_NAME in

        "BLE_datc")
            run_notConntectedTest 
            ;;

        "BLE_dats") 
            run_notConntectedTest
            ;;

        "BLE_mcs" )
            run_notConntectedTest 
            ;;

        "BLE_fit" )
            run_notConntectedTest 
            ;;

        # "BLE_fcc" )
        #     # todo:
        #     # execute related test
        #     echo Found BLE_fcc #place holder
        #     ;;

        "BLE_FreeRTOS" )
            run_notConntectedTest 
            ;;

        "BLE_otac" )
            run_notConntectedTest 
            ;;

        "BLE_otas" )
            # gets tested during conencted test below
            
            ;;

        "BLE5_ctr" )
            prepare_tifs_test            
            ;;

        "BLE_periph" )
            # No buttons implemented for this example so lets just make sure it builds, so we can ship it
            # cd $PROJECT_NAME
            # make -j8
            # let "numOfFailedTests+=$?"  
            # cd $MSDK_DIR/Examples/$TARGET_UC          
            ;;

        *)
            
            ;;

        esac

    fi
done
 
echo "=== DONE ==="
