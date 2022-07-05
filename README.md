# XR welcome Telegram bot

When new rebels enter into XR Nijmegen's telegram chats, the XR Welcome Bot is used to send them documents and
integrate them into the community.

## Setup

To run the bot, you will need to have the [python 3.8+ language](https://www.python.org/),
the [pip package manager](https://pip.pypa.io/en/stable/installation/) and
the [pipenv environment manager](https://pypi.org/project/pipenv/) installed on your system.

To install requirements via pipenv type `pipenv install` from the project root.

To run the bot, create the file `config/config.ini` and add your API token:

```
[Telegram]
Secret = XXX:YYY
```

Please refer to `config/example_config.ini` for more configuration options.

## Run

The bot can be run in a pipenv shell. It can either be run directly with the `python` command or from a
provided `start_bot.sh` script. The `python` command is better for debugging and development, while `start_bot.sh` is
better for deployment.

Start a pipenv shell by typing `pipenv shell` from the project root. Then, start the bot from
python: `cd src; python welcome_bot` or from the script: `sh start_bot.sh`.

## Turn off

If you ran the bot using the `python` command, `Ctrl-C` to turn it off.

If you ran the bot using the `start_bot.sh` script, you will need to kill both the `start_bot` process and
the `welcome_bot` processes on your system:

`ps aux | grep start_bot` And then `kill [PROCESS_ID]`

`ps aux | grep start_bot` And then `kill [PROCESS_ID]`
