#!/usr/bin/bash
coverage run  -m unittest discover
coverage report --omit=lib/*,test/* "$@"
