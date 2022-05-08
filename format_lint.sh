#!/bin/sh

set -e

black *.py
env MYPYPATH=stubs mypy *.py
pylint *.py
