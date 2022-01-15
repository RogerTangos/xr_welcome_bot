#!/bin/bash

# set working directory to script path
cd "$(basename $( dirname $(dirname "$0")))"

# collect all python files and store to a temporary file
tmp_file=/tmp/xr_welcome_bot_py_files
find . -name "*.py" > $tmp_file

# do the actual extraction
xgettext --keyword=translate:1 --from-code=UTF-8 --output=locale/base.pot --files-from=$tmp_file

# remove temporary file
rm $tmp_file
