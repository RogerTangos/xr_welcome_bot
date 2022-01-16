#!/bin/bash

# set working directory to script path
cd "$(basename $(dirname "$0"))"

while true; do
    nohup python src/welcome_bot.py >> bot_logs.out 2>&1
done &
