#!/bin/bash

# Usage:
# 1. Create the folder /opt/cron/
# 2. Copy this script to /opt/cron/os2mo-data.sh
# 3. Add the script to root's crontab: "05 06 * SCRIPT=/.../job-runner.sh /opt/cron/os2mo-data.sh"
# 4. Verify

# Configuration
#--------------
# Absolute path to the job-runner.sh script
# SCRIPT=... (must be set via environmental variable).

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT=${SCRIPT:-${DIR}/job-runner.sh}

# Unix service account to run job-runner.sh under
RUNAS=${RUNAS:-svc_os2mo}

# Installation type for backup (docker, legacy or none)
INSTALLATION_TYPE=${INSTALLATION_TYPE:-docker}

# Preconditions
#--------------

# Check if the script exists
if [ ! -f "${SCRIPT}" ]; then
    echo "Unable to locate script in specified path: ${SCRIPT}"
    exit 1
fi

# Check if the user exists
if ! id "${RUNAS}" >/dev/null 2>&1; then
    echo "Unable to locate the specified runas user: ${RUNAS}"
    exit 1
fi

# Check for necessary tools
if ! [ -x "$(command -v jq)" ]; then
    echo "Unable to locate the 'jq' executable."
    echo "Try: sudo apt-get install jq"
    exit 1
fi

# Database snapshot
#------------------
if [ "${INSTALLATION_TYPE}" == "docker" ]; then
    # Check preconditions
    CONTAINER_NAME=${CONTAINER_NAME:-"mox_database"}
    if ! [ -x "$(command -v docker)" ]; then
        echo "Unable to locate the 'docker' executable."
        exit 1
    fi
    if [ ! "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
        echo "Unable to locate a running mox database container: ${CONTAINER_NAME}"
        exit 1
    fi

    # Create backup
    DATABASE_NAME=${DATABASE_NAME:-"mox"}
    HOST_SNAPSHOT_DESTINATION=${HOST_SNAPSHOT_DESTINATION:-"/opt/docker/os2mo/database_snapshot/os2mo_database.sql"}
    DOCKER_SNAPSHOT_DESTINATION=${DOCKER_SNAPSHOT_DESTINATION:-"/database_snapshot/os2mo_database.sql"}
    echo "Snapshotting ${DATABASE_NAME}"
    docker exec -t ${CONTAINER_NAME} \
        su --shell /bin/bash \
           --command "pg_dump --data-only ${DATABASE_NAME} -f ${DOCKER_SNAPSHOT_DESTINATION}" \
           postgres
    EXIT_CODE=$?
    if [ ${EXIT_CODE} -ne 0 ]; then
        echo "Unable to snapshot database"
        exit 1
    fi
    chmod 755 ${HOST_SNAPSHOT_DESTINATION}

    # Create confdb
    CONFDB_DATABASE_NAME=${CONFDB_DATABASE_NAME:-"mora"}
    CONFDB_HOST_SNAPSHOT_DESTINATION=${CONFDB_HOST_SNAPSHOT_DESTINATION:-"/opt/docker/os2mo/database_snapshot/confdb.sql"}
    CONFDB_DOCKER_SNAPSHOT_DESTINATION=${CONFDB_DOCKER_SNAPSHOT_DESTINATION:-"/database_snapshot/confdb.sql"}
    echo "Snapshotting ${CONFDB_DATABASE_NAME}"
    docker exec -t ${CONTAINER_NAME} \
        su --shell /bin/bash \
           --command "pg_dump --data-only --inserts ${CONFDB_DATABASE_NAME} -f ${CONFDB_DOCKER_SNAPSHOT_DESTINATION}" \
           postgres
    EXIT_CODE=$?
    if [ ${EXIT_CODE} -ne 0 ]; then
        echo "Unable to snapshot database"
        exit 1
    fi
    chmod 755 ${CONFDB_HOST_SNAPSHOT_DESTINATION}

    # Create sessions
    SESSIONS_DATABASE_NAME=${SESSIONS_DATABASE_NAME:-"sessions"}
    SESSIONS_HOST_SNAPSHOT_DESTINATION=${SESSIONS_HOST_SNAPSHOT_DESTINATION:-"/opt/docker/os2mo/database_snapshot/sessions.sql"}
    SESSIONS_DOCKER_SNAPSHOT_DESTINATION=${SESSIONS_DOCKER_SNAPSHOT_DESTINATION:-"/database_snapshot/sessions.sql"}
    echo "Snapshotting ${SESSIONS_DATABASE_NAME}"
    docker exec -t ${CONTAINER_NAME} \
        su --shell /bin/bash \
           --command "pg_dump --data-only --inserts ${SESSIONS_DATABASE_NAME} -f ${SESSIONS_DOCKER_SNAPSHOT_DESTINATION}" \
           postgres
    EXIT_CODE=$?
    if [ ${EXIT_CODE} -ne 0 ]; then
        echo "Unable to snapshot database"
        exit 1
    fi
    chmod 755 ${SESSIONS_HOST_SNAPSHOT_DESTINATION}
elif [ "${INSTALLATION_TYPE}" == "legacy" ]; then
    echo "WARNING: No snapshotting configured"
    exit 1
elif [ "${INSTALLATION_TYPE}" == "none" ]; then
    echo "WARNING: No snapshotting configured"
else
    echo "Unknown installation type: ${INSTALLATION_TYPE}"
    exit 1
fi



# Run script between pre and post-hooks
#-----------
PREOUT=(${DIR}/cronhook.sh pre)
SCRIPT_OUTPUT=$(su --preserve-environment --shell /bin/bash --command "${SCRIPT}" ${RUNAS})
EXIT_CODE=$?
POSTOUT=(${DIR}/cronhook.sh post)
SCRIPT_OUTPUT="${PREOUT}${SCRIPT_OUTPUT}${POSTOUT}"


EVENT_NAMESPACE=magenta/project/os2mo/integration/script

JSON_FRIENDLY_SCRIPT_OUTPUT=$(echo "${SCRIPT_OUTPUT}" | jq -aRs .)
DATA="{\"script_executed\": \"${SCRIPT}\", \"exit_code\": ${EXIT_CODE}, \"output\": ${JSON_FRIENDLY_SCRIPT_OUTPUT}}"
echo "Sending event with payload: ${DATA}"

if [ "${EXIT_CODE}" -eq 0 ]; then
    echo "Script ran succesfully"
    salt-call event.send ${EVENT_NAMESPACE}/complete data="${DATA}"
    exit 0
else
    echo "Script has failed to execute"
    salt-call event.send ${EVENT_NAMESPACE}/failed data="${DATA}"
    exit ${EXIT_CODE}
fi
