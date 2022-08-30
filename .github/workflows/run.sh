#!/bin/bash

set -e
set -o pipefail

echo "in run.sh"
echo "GITHUB_WORKSPACE: "$GITHUB_WORKSPACE
echo "PWD: "$PWD

cd $GITHUB_WORKSPACE
python -m venv venv
ls -hal
source venv/bin/activate
python -m pip install -r requirements.txt

$GITHUB_WORKSPACE/venv/bin/python $GITHUB_WORKSPACE/ble_auto_testing.py --interface /dev/ttyACM0-None --device "" --brd0-addr 00:11:22:33:44:11 --brd1-addr 00:11:22:33:44:12 --sp0 /dev/ttyUSB1 --sp1 /dev/ttyUSB3 --time 30 --tshark /usr/bin/tshark

echo "--- DONE! ---"