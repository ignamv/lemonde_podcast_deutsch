#!/bin/sh

set -e

black *.py */*.py
env MYPYPATH=stubs mypy *.py
pylint *.py */*.py
