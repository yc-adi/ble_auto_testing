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

LOCK_FILE=/tmp/ci_test/timing/${TEST_TIME}.lock

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

CI_TEST=ble_timing_verify.yml

FILE=/home/$USER/Workspace/ci_config/boards_config.json
TEST_CONFIG_FILE=/home/$USER/Workspace/ci_config/timing_tests.json
CONFIG_FILE=$TEST_CONFIG_FILE

#echo "cat ${CONFIG_FILE}"
#cat ${CONFIG_FILE}
#echo

HOST_NAME=`hostname`
# skip FCC(file change check) or not
SKIP_FCC=`python3 -c "import json; import os; obj=json.load(open('${CONFIG_FILE}')); print(obj['${CI_TEST}']['${HOST_NAME}']['SKIP_FCC'])"`
printf "   SKIP_FCC: ${SKIP_FCC}\n\n"

MSDK_COMMIT=`python3 -c "import json; import os; obj=json.load(open('${CONFIG_FILE}')); print(obj['${CI_TEST}']['${HOST_NAME}']['SKIP_FCC'])"`
printf "MSDK_COMMIT: ${MSDK_COMMIT}\n\n"

if [ "x$MSDK_COMMIT" != "x" ]; then
    # need to switch to required version
    set -x
    cd $MSDK/ble_auto_testing/
    git branch
    git status -u
    git checkout $MSDK_COMMIT
    set +x
fi

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
    bash ${MSDK}/Libraries/RF-PHY-closed/.github/workflows/scripts/rf_phy_timing_test_file_change_check.sh \
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
        printf "\n#--------------------------------------------------------------------"
        printf "# Skip this ${CHIP_BRD_TYPE} board according to the configuration file."
        printf "#--------------------------------------------------------------------\n"
        continue
    fi

    BRD_AND_TYPE=${CHIP_BRD_TYPE..}  # convert to lower case

    sniffer=`python3 -c "import sys, json; print(json.load(open('$TEST_CONFIG_FILE'))['ble_timing_verify.yml']['$HOST_NAME']['sniffer'])"`
    echo "     sniffer board: ${sniffer}"
    sniffer_sn=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${sniffer}']['sn'])"`
    echo "        sniffer_sn: ${sniffer_sn}"
    SNIFFER_PROG_SN=`/usr/bin/python3 -c "import sys, json; print(json.load(open('$FILE'))['${sniffer}']['prog_sn'])"`
    echo "   SNIFFER_PROG_SN: ${SNIFFER_PROG_SN}"
    SNIFFER_USB=/dev/tty"$(ls -la /dev/serial/by-id | grep -n ${sniffer_sn} | awk -F tty '{print $2}')"
    echo "       SNIFFER_USB: ${SNIFFER_USB}"
    echo

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

    echo "         jtag_sn_1: $jtag_sn_1"
    echo "         jtag_sn_2: $jtag_sn_2"
    echo
    echo "           con_sn1: $con_sn1"
    echo "           con_sn2: $con_sn2"
    echo
    echo "           hci_sn1: $hci_sn1"
    echo "           hci_sn2: $hci_sn2"
    echo

    if [[ $BRD1 =~ "nRF" ]]; then
        echo "Board 1 is a nrf52840 board."
        CON_PORT1=
    else
        echo "Board 1 is not a nRF52840 board."
        CON_PORT1=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $con_sn1 | awk -F tty '{print $2}')"
    fi
    HCI_PORT1=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $hci_sn1 | awk -F tty '{print $2}')"

    if [[ $BRD2 =~ "nRF" ]]; then
        echo "Board 2 is a nrf52840 board."
        export CON_PORT2=
    else
        echo "Board 2 is not a nRF52840 board."
        export CON_PORT2=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $con_sn2 | awk -F tty '{print $2}')"
    fi
    HCI_PORT2=/dev/tty"$(ls -la /dev/serial/by-id | grep -n $hci_sn2 | awk -F tty '{print $2}')"

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

    LIMIT=3
    SH_RESET_BRD1=/tmp/ci_test/timing/${TEST_TIME}_brd1_reset.sh
    SH_RESET_BRD2=/tmp/ci_test/timing/${TEST_TIME}_brd2_reset.sh

    # not support coded
    # https://devzone.nordicsemi.com/f/nordic-q-a/54401/sniffing-ble-5-0-le-coded-phy-packets-using-nrf52840
    for ((phy=2;phy<=4;phy++)); do
        rm $MSDK/ble_auto_testing/EXTCAP_CONTROL_*
        rm $MSDK/ble_auto_testing/FIFO

        touch $MSDK/ble_auto_testing/EXTCAP_CONTROL_IN
        touch $MSDK/ble_auto_testing/EXTCAP_CONTROL_OUT
        touch $MSDK/ble_auto_testing/FIFO

        printf "\n<<<<<< phy: $phy >>>>>>\n\n"
        tried=0
        while true
        do
            printf "\n<<< reset the sniffer\n\n"
            set -x
            if [ $sniffer == "nRF52840_2" ] || [ $sniffer == "nRF52840_3" ] || [ $sniffer == "nRF52840_4" ]; then
                nrfjprog --family nrf52 -s ${SNIFFER_PROG_SN} --debugreset
            else
                python3 $MSDK/ble_auto_testing/control_sniffer.py --model nrf52840_dongle --sn $SNIFFER_PROG_SN
            fi
            set +x

            if [[ $BRD1 =~ "nRF" ]]; then
                printf "\n<<<<<< reset board 1: nRF board\n\n"
                set -x
                nrfjprog --family nrf52 -s ${BRD1_DAP_SN} --debugreset
                set +x

                echo $SH_RESET_BRD1
                echo "#!/usr/bin/env bash" > $SH_RESET_BRD1
                echo "nrfjprog --family nrf52 -s ${BRD1_DAP_SN} --debugreset" >> $SH_RESET_BRD1
                chmod u+x $SH_RESET_BRD1
                cat $SH_RESET_BRD1
            else
                printf "\n<<<<<< build and flash board 1: ${BRD1}\n\n"
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

            if [[ $BRD2 =~ "nRF" ]]; then
                printf "\n<<<<<< reset board 2: nRF board\n\n"
                set -x
                nrfjprog --family nrf52 -s ${BRD2_DAP_SN} --debugreset
                set +x

                echo $SH_RESET_BRD2
                echo "#!/usr/bin/env bash" > $SH_RESET_BRD2
                echo "nrfjprog --family nrf52 -s ${BRD2_DAP_SN} --debugreset" >> $SH_RESET_BRD2
                chmod u+x $SH_RESET_BRD2
                cat $SH_RESET_BRD2
            else
                printf "\n<<<<<< build and flash board 2: ${BRD2}\n\n"
                echo
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

                echo $SH_RESET_BRD2
                echo "#!/usr/bin/env bash" > $SH_RESET_BRD2
                echo "bash -e $MSDK/.github/workflows/scripts/build_flash.sh ${MSDK} /home/$USER/Tools/openocd ${BRD2_CHIP_UC} ${BRD2_TYPE} BLE5_ctr ${BRD2_DAP_SN} False True" >> $SH_RESET_BRD2
                echo "sleep 10" >> $SH_RESET_BRD2
                chmod u+x $SH_RESET_BRD2
                cat $SH_RESET_BRD2
                echo
            fi
            
            TEMP1=`date +%M`
            TEMP2=`date +%S`
            ADDR1=00:18:80:$TEMP1:$TEMP2:01
            ADDR2=00:18:80:$TEMP1:$TEMP2:02
            #ADDR1=00:18:80:01:02:01
            #ADDR2=00:18:80:01:02:02

            #set -x
            unbuffer python3 ble_test.py --interface ${SNIFFER_USB}-3.6 --device "" \
                --brd0-addr $ADDR1 --brd1-addr $ADDR2   \
                --sp0 $HCI_PORT1 --sp1 $HCI_PORT2       \
                --tp0 "$CON_PORT1" --tp1 "$CON_PORT2"   \
                --time 35 --tshark /usr/bin/tshark      \
                --phy $phy
            #set +x
            if [[ $? == 0 ]]; then
                printf "\nreturned: 0\n"
                break
            else
                echo "returned: $?"
            fi

            tried=$((tried+1))
            printf "\n<<< tried: $tried\n\n"
            if [[ $tried -ge $LIMIT ]]; then
                printf "\n<<< FAILED! GIVE UP!\n\n"
                phy=55
                break
            fi
        done
    done

    yes | cp -p output/*.* /tmp/ci_test/timing/

    # release locked boards
    python3 ~/Workspace/Resource_Share/Resource_Share_multiboard.py -b ${BRD1_LOCK} -b ${BRD2_LOCK}

    printf "\n#------------------------------------------------\n"
    if [[ $phy -gt 5 ]]; then
        printf "\n# FAILED\n"

        break  # no need to do the reset
    else
        printf "\n# PASSED\n"
    fi
done

printf "\n\n#------------------------------------------------------------------"
printf "# DONE!"
printf "#------------------------------------------------------------------------\n\n"

