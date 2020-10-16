#!/bin/bash

export DIPEXAR=${DIPEXAR:=$(cd $(dirname $0); pwd )/../..}
export VENV=${VENV:=${DIPEXAR}/venv}
cd ${DIPEXAR}

source tools/job-runner.sh

venv/bin/python integrations/SD_Lon/fix_departments.py --department-uuid="$1"
