#!/usr/bin/env bash
# Create GitHub repo and push current dir
set -e
REPO_NAME=${1:-trading_fun}
GH_USER=${2:-}

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found. Install from https://cli.github.com/ or create a repo on GitHub and set remote manually."
  echo "Manual commands:"
  echo "  git init"
  echo "  git add ."
  echo "  git commit -m \"Initial commit\""
  echo "  git branch -M main"
  echo "  git remote add origin git@github.com:<user>/${REPO_NAME}.git"
  echo "  git push -u origin main"
  exit 1
fi

if [ -z "$GH_USER" ]; then
  echo "Creating repo under your account"
  gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
else
  echo "Creating repo under org/user: $GH_USER"
  gh repo create "$GH_USER/$REPO_NAME" --public --source=. --remote=origin --push
fi

echo "Repository created and pushed. Configure secrets in GitHub if needed (CR_PAT, MLFLOW_TRACKING_URI, AWS keys etc)."
