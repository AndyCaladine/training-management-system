#!/bin/bash

echo "Resetting database..."

set -e  # stop if anything fails

rm -f instance/database.db*
python init_db.py

echo "Database reset complete."