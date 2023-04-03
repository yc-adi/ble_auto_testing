#!/usr/bin/env bash
FORMAT="run_timing_test.sh 1MSDK 2TEST_TIME"
printf "\n#########################################################################################\n"
printf "# ${FORMAT}\n"
printf "#########################################################################################\n"

echo $0 $@
echo
printf "$0 $@\n\n"

if [ $# -ne 2 ]; then
    printf "Invalid command. \"${FORMAT}\"\n\n"
    exit 1
fi

MSDK=$1
TEST_TIME=$2

source ~/anaconda3/etc/profile.d/conda.sh
conda activate py3_10

#cd ${MSDK}/ble_auto_testing
#echo "Create the Python env."
#python -m venv venv
#source ./venv/bin/activate
#python -m pip install -r requirements.txt

#--------------------------------------------------------------------------------------------------
declare -A DUTs
DUT_num=4
DUTs[0,0]=MAX32655
DUTs[0,1]=EvKit_V1
DUTs[1,0]=MAX32665
DUTs[1,1]=EvKit_V1
DUTs[2,0]=MAX32690
DUTs[2,1]=EvKit_V1
DUTs[3,0]=MAX32690
DUTs[3,1]=WLP_V1

CONFIG_FILE=~/Workspace/ci_config/timing_tests.json
CI_TEST=ble_timing_verify.yml
echo "cat ${CONFIG_FILE}"
cat ${CONFIG_FILE}
echo

HOST_NAME=`hostname`
# skip file change check
SKIP_FCC=`python3 -c "import json; import os; obj=json.load(open('${CONFIG_FILE}')); print(obj['${CI_TEST}']['${HOST_NAME}']['SKIP_FCC'])"`
printf "SKIP_FCC: ${SKIP_FCC}\n\n"

RUN_TEST=0
for ((i=0; i<DUT_num; i++))
do
    CHIP_UC=${DUTs[$i,0]}
    BRD_TYPE=${DUTs[$i,1]}

    echo "#----------------------------------------------------------------------------------------------------"
    echo "# Check ${CHIP_UC} ${BRD_TYPE}"
    echo "#----------------------------------------------------------------------------------------------------"
    echo
    set +e
    bash $MSDK/Libraries/RF-PHY-closed/.github/workflows/scripts/rf_phy_timing_test_file_change_check.sh \
        $SKIP_FCC \
        $MSDK     \
        $CHIP_UC  \
        $BRD_TYPE

    RETVAL=$?
    set -e

    if [[ $RETVAL -eq 0 ]]; then
        RUN_TEST=1
        echo "Test is required."
        break
    fi
done

if [ $RUN_TEST -eq 0 ]; then
    printf "\nNo test is required.\n------ Done! ------\n\n"
    exit 0
fi

#--------------------------------------------------------------------------------------------------
for ((i=0; i<DUT_num; i++))
do
    CHIP_UC=${DUTs[$i,0]}
    BRD_TYPE=${DUTs[$i,1]}

    CHIP_LC=${CHIP_UC,,}
    BRD_TYPE_LC=${BRD_TYPE,,}

    CHIP_BRD_TYPE=${CHIP_LC}_${BRD_TYPE_LC}

    printf "\n#====================================================================================\n"
    printf "# Test on ${CHIP_BRD_TYPE}"
    printf "\n#====================================================================================\n"
    
    # check the configuration
    DO_THIS=`python3 -c "import json; import os; obj=json.load(open('${CONFIG_FILE}')); print(obj['${CI_TEST}']['${HOST_NAME}']['${CHIP_BRD_TYPE}']['do_this'])"`
    printf "DO_THIS: ${DO_THIS}\n\n"

    if [ ${DO_THIS} == "0" ]; then
        printf "Skip this ${CHIP_BRD_TYPE} board according to the configuration file.\n"
        continue
    fi

    printf "\n#----------------------------------------------------------------\n"
    printf "# acquire the lock of the test boards. save the info into the test .lock file"
    printf "\n#----------------------------------------------------------------\n\n"
    BRD_CONFIG_FILE=~/Workspace/ci_config/boards_config.json

    BRD1=`python3 -c "import json; import os; obj=json.load(open('${CONFIG_FILE}')); print(obj['${CI_TEST}']['${HOST_NAME}']['${CHIP_BRD_TYPE}']['board1'])"`
    BRD2=`python3 -c "import json; import os; obj=json.load(open('${CONFIG_FILE}')); print(obj['${CI_TEST}']['${HOST_NAME}']['${CHIP_BRD_TYPE}']['board2'])"`
    printf "\nBRD1: $BRD1\n"
    printf "BRD2: $BRD2\n"

    BRD1_LOCK=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD1}']['lockfile'])"`
    BRD2_LOCK=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD2}']['lockfile'])"`

    printf "\nTry to lock the files...\n"    
    python3 ~/Workspace/Resource_Share/Resource_Share_multiboard.py -l -t 3600 -b ${BRD1_LOCK} -b ${BRD2_LOCK}
    if [ $? -ne 0 ]; then
        printf "\nFail to acquire the resources.\n"
        continue
    fi

    LOCK_FILE=/tmp/ci_test/timing/${TEST_TIME}.lock
    touch $LOCK_FILE
    echo "python3 ~/Workspace/Resource_Share/Resoure_Share_multiboard.py -b ${BRD1_LOCK} -b ${BRD2_LOCK}" >> $LOCK_FILE
    bash -x -c "cat $LOCK_FILE"

    printf "\n#----------------------------------------------------------------\n"
    printf "# Build the project and flash the board"
    printf "\n#----------------------------------------------------------------\n\n"

    BRD1_CHIP_UC=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD1}']['chip_uc'])"`
    BRD2_CHIP_UC=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD2}']['chip_uc'])"`
    
    BRD1_TYPE=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD1}']['type'])"`
    BRD2_TYPE=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD2}']['type'])"`
    
    BRD1_DAP_SN=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD1}']['DAP_sn'])"`
    BRD2_DAP_SN=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD2}']['DAP_sn'])"`
    
    printf "<<<<<< build and flash ${BRD1}\n\n"
    if [ $BRD1 != "nRF52840_2" ]; then
        set -x
        bash -e $MSDK/Libraries/RF-PHY-closed/.github/workflows/scripts/RF-PHY_build_flash.sh \
            ${MSDK}                     \
            /home/$USER/Tools/openocd   \
            ${BRD1_CHIP_UC}             \
            ${BRD1_TYPE}                \
            BLE5_ctr                    \
            ${BRD1_DAP_SN}              \
            False                        \
            False
        set +x
        echo
    fi

    printf "<<<<<< build and flash ${BRD2}\n\n"
    set -x
    bash -e $MSDK/Libraries/RF-PHY-closed/.github/workflows/scripts/RF-PHY_build_flash.sh \
        ${MSDK}                     \
        /home/$USER/Tools/openocd   \
        ${BRD2_CHIP_UC}             \
        ${BRD2_TYPE}                \
        BLE5_ctr                    \
        ${BRD2_DAP_SN}              \
        True                        \
        True
    set +x
    echo

    printf "\n#----------------------------------------------------------------\n"
    printf "# run test"
    printf "\n#----------------------------------------------------------------\n\n"
    SNIFFER=`python3 -c "import json; import os; obj=json.load(open('${CONFIG_FILE}')); print(obj['${CI_TEST}']['${HOST_NAME}']['sniffer'])"`
    snifferSerial=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${SNIFFER}']['sn'])"`

    BRD1_HCI=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD1}']['hci_id'])"`
    BRD2_HCI=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD2}']['hci_id'])"`
    BRD1_CON=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD1}']['con_id'])"`
    BRD2_CON=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD2}']['con_id'])"`
        
    if [ `hostname` == "yingcai-OptiPlex-790" ]; then
        ADDR1=00:12:23:34:45:01
        ADDR2=00:12:23:34:45:02
    else
        ADDR1=00:11:22:33:44:21
        ADDR2=00:11:22:33:44:22
    fi

    set -x
    NEW_METHOD=0
    if [ $NEW_METHOD -eq 1 ]; then
        unbuffer python3 ${MSDK}/ble_auto_testing/timing_test.py    \
            --interface ${snifferSerial}-None --device ""           \
            --addr1 $ADDR1 --addr2 $ADDR2                           \
            --hci1 $BRD1_HCI --hci2 $BRD2_HCI                       \
            --mon1 "$BRD1_CON" --mon2 "$BRD2_CON"                   \
            --time 35 --tshark /usr/bin/tshark
    else
        unbuffer python3 ${MSDK}/ble_auto_testing/ble_test.py       \
            --interface ${snifferSerial}-None --device ""           \
            --brd0-addr $ADDR1 --brd1-addr $ADDR2                   \
            --sp0 $BRD1_HCI --sp1 $BRD2_HCI                         \
            --tp0 "$BRD1_CON" --tp1 "$BRD2_CON"                     \
            --time 35 --tshark /usr/bin/tshark
    fi
    
    echo
    yes | cp -p output/*.* /tmp/ci_test/timing/
    set +x

    printf "\n#----------------------------------------------------------------\n"
    printf "# release locked resources"
    printf "\n#----------------------------------------------------------------\n\n"
done

printf "\n\n#------\n"
printf "# DONE!"
printf "\n#------\n\n"

