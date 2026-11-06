#!/bin/sh
# Rebuilds Checkpoint2-dbase.sqlite3 from scratch.
set -e
cd "$(dirname "$0")"
python3 gen_seed.py > seed.sql
rm -f Checkpoint2-dbase.sqlite3
sqlite3 -bail Checkpoint2-dbase.sqlite3 < schema.sql
sqlite3 -bail Checkpoint2-dbase.sqlite3 < seed.sql
