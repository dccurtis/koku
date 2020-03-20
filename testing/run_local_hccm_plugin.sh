#!/bin/bash
COMMANDS=$@
HCCM_PLUGIN_PATH=$1
COMMAND=$2
PLUGIN_INSTALL_CMD="iqe plugin uninstall hccm && iqe plugin install --editable /hccm_plugin && "
FULL_COMMAND=$PLUGIN_INSTALL_CMD$COMMAND

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
echo "Running Editable IQE Tests"

ENV_FOR_DYNACONF=local $SCRIPTPATH/run_editable.sh ${HCCM_PLUGIN_PATH} ${FULL_COMMAND}
