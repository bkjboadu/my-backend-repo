#!/bin/bash

echo "checking out to the main branch"
git checkout main

echo "Resetting local main branch to match origin/main"
git reset --hard origin/main

echo "Force pushing to heroku main ..."
git push heroku main --force

echo "deployment to heroku completed successfully"
