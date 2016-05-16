#!/bin/bash

printf "Starting as `whoami`\n"

source venv/bin/activate
exec $@
