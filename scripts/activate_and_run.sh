#!/bin/bash

# Usefull as wrapper script, for example if a supervisor should start the server

printf "Starting as `whoami`\n"

source venv/bin/activate
exec $@
