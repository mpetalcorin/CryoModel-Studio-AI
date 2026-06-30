#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/mpetalcorin/CryoModel-Studio-AI.git"

echo "Preparing CryoModel Studio AI for GitHub..."

git init
git branch -M main

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REPO_URL"
else
  git remote add origin "$REPO_URL"
fi

git add .
git commit -m "Update Streamlit width API and workflow planner" || echo "Nothing new to commit."

git fetch origin main

git pull --rebase origin main || {
  echo "Rebase failed. If this is only your own repo, run:"
  echo "git push --force-with-lease origin main"
  exit 1
}

git push -u origin main
echo "Done. Repository pushed to $REPO_URL"
