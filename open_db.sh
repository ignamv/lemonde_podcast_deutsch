#!/bin/sh

exec sqlite3 -column -header db/db.sqlite3 "$@"
