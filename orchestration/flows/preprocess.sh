#!/bin/bash

environ=${1}
uuid=${2}
echo ${environ}, ${uuid}

set -o allexport
source ${environ}.env
set +o allexport

mkdir -p ${uuid}
apt-get install -y python3-venv
python3 -m venv env
source env/bin/activate
pip install --index-url http://${PYPI}:8080 mlcode==0.0.1 --trusted-host ${PYPI}
spam_preproc -c configs/${environ}.yaml -t -r ${uuid}
