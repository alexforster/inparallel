#!/bin/bash

SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd $SCRIPT_DIR &>/dev/null

rm -rf ./dist
rm -rf ./*.egg-info

source env2/bin/activate
python setup.py --quiet --no-user-cfg sdist
deactivate

rm -rf ./*.egg-info

cd - &>/dev/null
