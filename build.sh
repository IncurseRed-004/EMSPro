#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "=== Installing dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Collecting static files ==="
python manage.py collectstatic --no-input

echo "=== Applying database migrations ==="
python manage.py migrate --no-input

echo "=== Build finished successfully ==="
