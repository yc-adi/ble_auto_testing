#!/usr/bin/env bash

FORMAT="run_timing_test.sh 1MSDK 2TEST_TIME"

printf "\n#########################################################################################\n"
printf "# ${FORMAT}\n"
printf "#########################################################################################\n"

echo $0 $@
echo

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

mkdir -p /tmp/ci_test/timing/
rm ${MSDK}/ble_auto_testing/output/*.pc*
rm ${MSDK}/ble_auto_testing/output/sniffer.log


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
#cat ${CONFIG_FILE}
echo

HOST_NAME=`hostname`
# skip FCC(file change check) or not
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
    bash ${MSDK}/ble_auto_testing/rf_phy_timing_test_file_change_check.sh \
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

    if [ $HOST_NAME == "wall-e" ]; then
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
    fi

    printf "\n#----------------------------------------------------------------\n"
    printf "# Build the project and flash the board"
    printf "\n#----------------------------------------------------------------\n\n"

    BRD1_CHIP_UC=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD1}']['chip_uc'])"`
    BRD2_CHIP_UC=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD2}']['chip_uc'])"`
    
    BRD1_TYPE=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD1}']['type'])"`
    BRD2_TYPE=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD2}']['type'])"`
    
    BRD1_DAP_SN=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD1}']['DAP_sn'])"`
    BRD2_DAP_SN=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD2}']['DAP_sn'])"`
    
    printf "<<<<<< build and flash the first board: ${BRD1}\n\n"
    if [[ $BRD1 =~ "nRF52840_" ]]; then
        IS_NRF=1
        printf "Don't program the nRF52840 board.\n\n"
    else
        IS_NRF=0
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
        echo
    fi

    printf "<<<<<< build and flash the 2nd board: ${BRD2}\n\n"
    set -x
    bash -e $MSDK/Libraries/RF-PHY-closed/.github/workflows/scripts/RF-PHY_build_flash.sh \
        ${MSDK}                     \
        /home/$USER/Tools/openocd   \
        ${BRD2_CHIP_UC}             \
        ${BRD2_TYPE}                \
        BLE5_ctr                    \
        ${BRD2_DAP_SN}              \
        False                        \
        True
    set +x
    echo

    printf "\n#----------------------------------------------------------------\n"
    printf "# run test"
    printf "\n#----------------------------------------------------------------\n\n"
    SNIFFER=`python3 -c "import json; import os; obj=json.load(open('${CONFIG_FILE}')); print(obj['${CI_TEST}']['${HOST_NAME}']['sniffer'])"`
    printf "      SNIFFER: $SNIFFER\n"
    sniffer_sn=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${SNIFFER}']['sn'])"`
    printf "   sniffer_sn: $sniffer_sn\n"
    snifferSerial=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $sniffer_sn | awk -F tty '{print $2}')"
    printf "snifferSerial: $snifferSerial\n\n"

    BRD1_HCI=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD1}']['hci_id'])"`
    printf "     BRD1_HCI: $BRD1_HCI\n"
    if [ $IS_NRF -eq 1 ]; then
        BRD1_CON=
        printf "     BRD1_CON: $BRD1_CON\n"
    else
        BRD1_CON=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD1}']['con_id'])"`
        printf "     BRD1_CON: $BRD1_CON\n"
    fi

    BRD2_HCI=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD2}']['hci_id'])"`    
    printf "     BRD2_HCI: $BRD2_HCI\n"
    BRD2_CON=`python3 -c "import json; import os; obj=json.load(open('${BRD_CONFIG_FILE}')); print(obj['${BRD2}']['con_id'])"`
    printf "     BRD2_CON: $BRD2_CON\n"

    printf "\n<<< reset the sniffer\n\n"
    SNIFFER_PROG_SN=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$BRD_CONFIG_FILE'))['${SNIFFER}']['prog_sn'])"`
    set -x
    if [ "$sniffer" == "nRF52840_2" ] || [ "$sniffer" == "nRF52840_4" ]; then
        nrfjprog --family nrf52 -s ${SNIFFER_PROG_SN} --debugreset
    else
        python3 $MSDK/ble_auto_testing/control_sniffer.py --model nrf52840_dongle --sn $SNIFFER_PROG_SN
        echo
    fi
    set +x
    printf "sleep 10 secs\n"
    for((i=0;i<10;i++)); do
        echo $((i))
        sleep 1
    done
    
    temp1=`date +%M`
    temp2=`date +%S`
    ADDR1=00:18:80:$temp1:$temp2:01
    ADDR2=00:18:80:$temp1:$temp2:02

    set -x

    unbuffer python3 ${MSDK}/ble_auto_testing/timing_test.py    \
        --interface ${snifferSerial}-None --device ""           \
        --addr1 $ADDR1 --addr2 $ADDR2                           \
        --hci1 $BRD1_HCI --hci2 $BRD2_HCI                       \
        --mon1 "$BRD1_CON" --mon2 "$BRD2_CON"                   \
        --time 40 --tshark /usr/bin/tshark                      \
        --new_phy 2
    
    if [ $? -eq 0 ]; then
        PASS=1
    else
        PASS=0
    fi

    echo
    yes | cp -p output/*.* /tmp/ci_test/timing/
    set +x

    printf "\n#----------------------------------------------------------------\n"
    printf "# release locked resources"
    printf "\n#----------------------------------------------------------------\n\n"
    # TODO

    if [ $PASS -eq 0 ]; then
        break
    fi
done

printf "\n\n#------\n"
printf "# DONE!"
printf "\n#------\n\n"

