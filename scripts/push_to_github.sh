#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/mpetalcorin/CryoModel-Studio-AI.git"

echo "Preparing CryoModel Studio AI for GitHub..."
git init
git branch -M main

git add .
git commit -m "Enhance CryoModel Studio AI modules and visuals" || echo "Nothing new to commit."

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REPO_URL"
else
  git remote add origin "$REPO_URL"
fi

git push -u origin main
echo "Done. Repository pushed to $REPO_URL"
