#!/bin/sh

set -e

black *.py */*.py
pylint *.py */*.py
