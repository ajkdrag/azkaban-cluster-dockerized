#!/bin/bash

environ=${1}
uuid=${2}
input=${3}
echo ${environ}, ${uuid}, ${input}

set -o allexport
source ${environ}.env
set +o allexport

mkdir -p ${uuid}
apt-get install -y python3-venv
python3 -m venv env
source env/bin/activate
pip install --index-url http://${PYPI}:8080 mlcode==0.0.1 --trusted-host ${PYPI}
spam_infer -c configs/${environ}.yaml -s "${input}"
