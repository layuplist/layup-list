#!/bin/bash
# Must run as `source setup_enviornment.sh`
# start heroku enviornment, source user .bashrc, add (ll) to prompt, activate venv

heroku local:run bash --rcfile <(echo "source $HOME/.bashrc; export PS1='(ll)$PS1'; source venv/bin/activate;")
