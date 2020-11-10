#!/bin/bash
## Script til at sætte ejer på klasser for frederikshavn

MOX_URL="${MOX_URL:-http://localhost:8080}"

CLI="venv/bin/python os2mo_data_import/med/mox_util.py cli --mox-base ${MOX_URL}"

#Find UUID'er med: curl localhost:5001/service/o/${UUID}/children | jq .
MED="6dc35977-710e-86c0-4d68-b13ea0b16910"
MAIN="4f79e266-4080-4300-a800-000006180002"

UUID=$(curl --silent localhost:5001/service/o/ | jq -r .[0].uuid)
CLASSES=$(curl localhost:5001/service/o/${UUID}/f/association_type/)
TOTAL_CLASSES=$(echo $CLASSES | jq -r  .data.total)
echo "Found ${TOTAL_CLASSES} association_types"

LIST='"AMR" "AMR, næstformand" "FTR" "FTR, næstformand" "LR" "LR, formand" "Medarb.rep, næstformand" "Stedfortræder" "TR" "TR, næstformand"'

echo $CLASSES | jq -c .data.items[] | while read line; do
    NAME=$(echo $line | jq .user_key)
    NAME=${NAME//\"/}
    
    if [[ -z $(echo $LIST | grep -w "$NAME") ]]; then
        OWNER=$MED
    else
        OWNER=$MAIN
    fi
    echo $NAME : $OWNER
    ${CLI} ensure-class-value --bvn "${NAME}" --variable ejer --new_value "$OWNER" 
done
