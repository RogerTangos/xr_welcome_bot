#!/bin/bash

# set working directory to script path
cd "$(basename $(dirname "$0"))"

python src/welcome_bot.py
