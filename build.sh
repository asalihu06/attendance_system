#!/usr/bin/env bash
# exit on error
set -o errexit


# 1. Add all files
git add .

# 2. Fix the permissions for the build script (Crucial for Render)
git update-index --chmod=+x build.sh

# 3. Commit the changes
git commit -m "Deployment files and orange logo update"
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate