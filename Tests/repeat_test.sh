#!/usr/bin/env bash

#
# cd ~/Workspace/ble_auto_testing/Tests
# ./repeat_test.sh 2>&1 | tee test.log
# start: 09:43
#   end: 
#
cd ~/Workspace/ble_auto_testing
echo
echo "PWD:" `pwd`
echo

for((i=1;i<=20;i++)); do
    printf "\n#------------------------------------------------------------------------------------"
    printf "\nTEST: ${i}"
    printf "\n#------------------------------------------------------------------------------------\n"

    bash -c "~/Workspace/ble_auto_testing/run.sh 1 ~/Workspace/msdk_open `date +%Y-%m-%d_%H-%M-%S`"

    printf "\n--- END OF TEST ---\n\n"
done

printf "\n\n--- END OF ALL THE TESTS ---\n\n"
