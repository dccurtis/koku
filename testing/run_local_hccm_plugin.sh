#!/bin/bash
COMMANDS=$@
HCCM_PLUGIN_PATH=$1
COMMAND=$2
PLUGIN_INSTALL_CMD="iqe plugin uninstall hccm && iqe plugin install --editable /hccm_plugin && "
FULL_COMMAND=$PLUGIN_INSTALL_CMD$COMMAND

printf "Path is %s\n" "$HCCM_PLUGIN_PATH"
printf "Full Command is %s\n" "$FULL_COMMAND"

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
echo "Running Smoke Tests"

ENV_FOR_DYNACONF=local $SCRIPTPATH/run_editable.sh ${HCCM_PLUGIN_PATH} ${FULL_COMMAND}
