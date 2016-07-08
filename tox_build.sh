#!/usr/bin/env bash

if [ ! -e venv-app ]; then
    virtualenv venv-app --python=python2.7
fi

venv-app/bin/pip install tox -q
venv-app/bin/tox "$@"
