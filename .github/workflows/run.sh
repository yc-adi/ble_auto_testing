#!/bin/bash
echo
echo "####################################################################"
echo "# The working folder is the root of repo ble_auto_testing.         #"
echo "# .github/workflows/run.sh 1_2nd_board_type 2_MSKD 3_TEST_TIME     #"
echo "####################################################################"
echo
echo $0 $@
echo

VERBOSE=0

if [ $# -ne 3 ]; then
    echo "Invalid input arguments."
    echo
fi

ERR_INVALID_2ND_BRD_TYPE=1
FAIL_TO_ACQUIRE_BOARDS=2

SEC_BRD_TYPE=$1
case $SEC_BRD_TYPE in
    1)
        echo "The 2nd board is MAX32655."
        BRD_AND_TYPE=max32655_evkit_v1
    ;;

    2)
        BRD_AND_TYPE=max32665_evkit_v1
        echo "The 2nd board is MAX32665."
    ;;

    3)
        BRD_AND_TYPE=max32690_evkit_v1
        echo "The 2nd board is max32690_evkit_v1."
    ;;

    *)
        echo "Invalid 2nd board type. 1: MAX32655, 2: MAX32665, 3: MAX32690."
        exit $ERR_INVALID_2ND_BRD_TYPE
    ;;
esac

MSDK=$2

echo "PWD: $PWD"
echo

TEST_TIME=$3

if [ $VERBOSE -eq 1 ]; then
    ls -hal
fi

set -e
set -o pipefail

mkdir -p /tmp/ci_test/timing
LOCK_FILE=/tmp/ci_test/timing/${TEST_TIME}.lock

#--------------------------------------------------------
function cleanup {
    set +x
    printf "\n<<<<<<< cleanup before exit\n"
    if [ -f $LOCK_FILE ]; then
        set -x
        bash $LOCK_FILE
        set +x
    fi
    printf "\n<<<<<< EXIT <<<<<<\n\n"
}
#--------------------------------------------------------
trap cleanup EXIT
#--------------------------------------------------------

source ~/anaconda3/etc/profile.d/conda.sh
conda activate py3_10

# Note: index of the two DevKit boards are 1-based.
echo
FILE=/home/$USER/Workspace/ci_config/boards_config.json
if [ $VERBOSE -eq 1 ]; then
    cat $FILE
fi
echo

# get the test boards
TEST_CONFIG_FILE=/home/$USER/Workspace/ci_config/timing_tests.json
if [ $VERBOSE -eq 1 ]; then
    cat $TEST_CONFIG_FILE
fi
echo

HOST_NAME=`hostname`
sniffer=`python3 -c "import sys, json; print(json.load(open('$TEST_CONFIG_FILE'))['ble_timing_verify.yml']['$HOST_NAME']['sniffer'])"`
echo "     sniffer board: ${sniffer}"
BRD1=`python3 -c "import sys, json; print(json.load(open('$TEST_CONFIG_FILE'))['ble_timing_verify.yml']['$HOST_NAME']['$BRD_AND_TYPE']['board1'])"`
echo "              BRD1: ${BRD1}"
BRD2=`python3 -c "import sys, json; print(json.load(open('$TEST_CONFIG_FILE'))['ble_timing_verify.yml']['$HOST_NAME']['$BRD_AND_TYPE']['board2'])"`
echo "              BRD2: ${BRD2}"
echo

BRD1_CHIP_UC=`python3 -c "import json; import os; obj=json.load(open('${FILE}')); print(obj['${BRD1}']['chip_uc'])"`
BRD1_TYPE=`python3 -c "import json; import os; obj=json.load(open('${FILE}')); print(obj['${BRD1}']['type'])"`
BRD1_DAP_SN=`python3 -c "import json; import os; obj=json.load(open('${FILE}')); print(obj['${BRD1}']['DAP_sn'])"`

BRD2_CHIP_UC=`python3 -c "import json; import os; obj=json.load(open('${FILE}')); print(obj['${BRD2}']['chip_uc'])"`
BRD2_TYPE=`python3 -c "import json; import os; obj=json.load(open('${FILE}')); print(obj['${BRD2}']['type'])"`
BRD2_DAP_SN=`python3 -c "import json; import os; obj=json.load(open('${FILE}')); print(obj['${BRD2}']['DAP_sn'])"`

sniffer_sn=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${sniffer}']['sn'])"`
jtag_sn_1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${BRD1}']['DAP_sn'])"`
jtag_sn_2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${BRD2}']['DAP_sn'])"`

con_sn1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${BRD1}']['con_sn'])"`
con_sn2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${BRD2}']['con_sn'])"`
hci_sn1=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${BRD1}']['hci_sn'])"`
hci_sn2=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${BRD2}']['hci_sn'])"`

# get the lock file for each board
BRD1_LOCK=`python3 -c "import json; import os; obj=json.load(open('${FILE}')); print(obj['${BRD1}']['lockfile'])"`
echo "   BRD1 lock file: $BRD1_LOCK"
BRD2_LOCK=`python3 -c "import json; import os; obj=json.load(open('${FILE}')); print(obj['${BRD2}']['lockfile'])"`
echo "   BRD2 lock file: $BRD2_LOCK"
echo 

echo "        sniffer_sn: $sniffer_sn"
echo
echo "         jtag_sn_1: $jtag_sn_1"
echo "           con_sn1: $con_sn1"
echo "           con_sn2: $con_sn2"
echo
echo "         jtag_sn_2: $jtag_sn_2"
echo "           hci_sn1: $hci_sn1"
echo "           hci_sn2: $hci_sn2"
echo
echo

if [[ $BRD1 =~ "nRF" ]]; then
    export SNIFFER_USB=/dev/tty"$(ls -la /dev/serial/by-id | grep -n ${sniffer_sn} | awk -F tty '{print $2}')"
    export CON_PORT1=
else
    echo here
    export SNIFFER_USB=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $sniffer_sn | awk -F tty '{print $2}')"
    export CON_PORT1=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $con_sn1 | awk -F tty '{print $2}')"
fi
export HCI_PORT1=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $hci_sn1 | awk -F tty '{print $2}')"

export CON_PORT2=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $con_sn2 | awk -F tty '{print $2}')"
export HCI_PORT2=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $hci_sn2 | awk -F tty '{print $2}')"

echo "           sniffer: $SNIFFER_USB"
echo

echo "board 1 trace port: $CON_PORT1"
echo "  board 1 HCI port: $HCI_PORT1"
echo 
echo "board 2 trace port: $CON_PORT2"
echo "  board 2 HCI port: $HCI_PORT2"
echo 

printf "\nTry to lock the files...\n"    
python3 ~/Workspace/Resource_Share/Resource_Share_multiboard.py -l -t 3600 -b ${BRD1_LOCK} -b ${BRD2_LOCK}
if [ $? -ne 0 ]; then
    printf "\nFail to acquire the resources.\n"
    exit FAIL_TO_ACQUIRE_BOARDS
fi

touch $LOCK_FILE
echo "python3 ~/Workspace/Resource_Share/Resource_Share_multiboard.py -b ${BRD1_LOCK} -b ${BRD2_LOCK}" >> $LOCK_FILE
bash -x -c "cat $LOCK_FILE"
echo

SH_RESET_BRD1=/tmp/ci_test/timing/${TEST_TIME}_brd1_reset.sh
if [[ $BRD1 =~ "nRF" ]]; then
    printf "\n<<<reset nRF board\n\n"
    set -x
    nrfjprog --family nrf52 -s ${BRD1_DAP_SN} --debugreset
    set +x

    echo $SH_RESET_BRD1
    echo "#!/usr/bin/env bash" > $SH_RESET_BRD1
    echo "nrfjprog --family nrf52 -s ${BRD1_DAP_SN} --debugreset" >> $SH_RESET_BRD1
    chmod u+x $SH_RESET_BRD1
    cat $SH_RESET_BRD1
else
    printf "\n<<<<<< build and flash ${BRD1}\n\n"
    echo
    set -x
    bash -e $MSDK/Libraries/RF-PHY-closed/.github/workflows/scripts/RF-PHY_build_flash.sh \
        ${MSDK}                     \
        /home/$USER/Tools/openocd   \
        ${BRD1_CHIP_UC}             \
        ${BRD1_TYPE}                \
        BLE5_ctr                    \
        ${BRD1_DAP_SN}              \
        True                        \
        True
    set +x
    
    echo $SH_RESET_BRD1
    echo "#!/usr/bin/env bash" > $SH_RESET_BRD1
    echo "bash -e $MSDK/.github/workflows/scripts/build_flash.sh ${MSDK} /home/$USER/Tools/openocd ${BRD1_CHIP_UC} ${BRD1_TYPE} BLE5_ctr ${BRD1_DAP_SN} False True" >> $SH_RESET_BRD1
    echo "sleep 10" >> $SH_RESET_BRD1
    chmod u+x $SH_RESET_BRD1
    cat $SH_RESET_BRD1

    echo
fi

printf "\n<<<<<< build and flash ${BRD2}\n\n"
echo
set -x
bash -e $MSDK/Libraries/RF-PHY-closed/.github/workflows/scripts/RF-PHY_build_flash.sh \
    ${MSDK}                     \
    /home/$USER/Tools/openocd   \
    ${BRD2_CHIP_UC}             \
    ${BRD2_TYPE}                \
    BLE5_ctr                    \
    ${BRD2_DAP_SN}              \
    False                        \
    False
set +x

SH_RESET_BRD2=/tmp/ci_test/timing/${TEST_TIME}_brd1_reset.sh
echo $SH_RESET_BRD2
echo "#!/usr/bin/env bash" > $SH_RESET_BRD2
echo "bash -e $MSDK/.github/workflows/scripts/build_flash.sh ${MSDK} /home/$USER/Tools/openocd ${BRD2_CHIP_UC} ${BRD2_TYPE} BLE5_ctr ${BRD2_DAP_SN} False True" >> $SH_RESET_BRD2
echo "sleep 10" >> $SH_RESET_BRD2
chmod u+x $SH_RESET_BRD2
cat $SH_RESET_BRD2
echo

TEMP1=`date +%M`
TEMP2=`date +%S`
ADDR1=00:18:80:$TEMP1:$TEMP2:01
ADDR2=00:18:80:$TEMP1:$TEMP2:02

unbuffer python3 ble_test.py --interface ${SNIFFER_USB}-None --device "" \
    --brd0-addr $ADDR1 --brd1-addr $ADDR2 \
    --sp0 $HCI_PORT1 --sp1 $HCI_PORT2 \
    --tp0 "$CON_PORT1" --tp1 $CON_PORT2 \
    --time 35 --tshark /usr/bin/tshark

yes | cp -p output/*.* /tmp/ci_test/timing/

# release locked boards
python3 ~/Workspace/Resource_Share/Resoure_Share_multiboard.py -b ${BRD1_LOCK} -b ${BRD2_LOCK}

echo "#------------------------------------------"
echo "# DONE! "
echo "#------------------------------------------"
