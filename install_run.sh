#!/bin/bash

set -x

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

pip3 install -r ${SCRIPT_DIR}/requirements.txt && \
python ${SCRIPT_DIR}/app.py $1