#!/bin/bash
set -e

usage() {
  echo "Usage: $0 <patch|minor|major>" >&2
  exit 1
}

TYPE=${1:-}
[ -z "$TYPE" ] && usage

CURRENT=$(grep -m1 -Po '(?<=version = ")([0-9]+\.[0-9]+\.[0-9]+)' pyproject.toml)
IFS=. read -r MAJ MIN PAT <<<"$CURRENT"
case "$TYPE" in
  patch)
    PAT=$((PAT + 1))
    ;;
  minor)
    MIN=$((MIN + 1))
    PAT=0
    ;;
  major)
    MAJ=$((MAJ + 1))
    MIN=0
    PAT=0
    ;;
  *)
    usage
    ;;
esac
NEW="$MAJ.$MIN.$PAT"

if ! git diff --quiet; then
  echo "Uncommitted changes present, aborting" >&2
  exit 1
fi

echo "Bumping version: $CURRENT -> $NEW"
# Update files
sed -i -E "s/version = \"$CURRENT\"/version = \"$NEW\"/" pyproject.toml
sed -i -E "s/__version__ = \"$CURRENT\"/__version__ = \"$NEW\"/" src/__init__.py

echo "Creating git commit and tag"
git add pyproject.toml src/__init__.py
git commit -m "Bump version to $NEW"

# Check if tag already exists
if git tag -l "v$NEW" | grep -q "v$NEW"; then
  echo "Tag v$NEW already exists, reusing it"
  git tag -d "v$NEW" 2>/dev/null || true
fi
git tag -a "v$NEW" -m "Release v$NEW"

# Create a branch for the version bump
BRANCH_NAME="release/v$NEW"
# Check if branch already exists locally or remotely
if git show-ref --verify --quiet refs/heads/"$BRANCH_NAME" 2>/dev/null || git ls-remote --heads origin "$BRANCH_NAME" | grep -q "$BRANCH_NAME"; then
  echo "Branch $BRANCH_NAME already exists, switching to it"
  git checkout "$BRANCH_NAME" 2>/dev/null || git checkout -b "$BRANCH_NAME" origin/"$BRANCH_NAME"
else
  git checkout -b "$BRANCH_NAME"
fi

# Push the branch and tag
git push origin "$BRANCH_NAME"
git push origin "v$NEW"

# Check if PR already exists for this version
PR_EXISTS=$(gh pr list --head "$BRANCH_NAME" --json number --jq '.[0].number' 2>/dev/null || echo "")

if [ -n "$PR_EXISTS" ]; then
  echo "Pull request for version $NEW already exists: #$PR_EXISTS"
  echo "Please review and merge the existing PR to complete the release"
else
  # Create pull request using GitHub CLI
  echo "Creating pull request for version bump"
  gh pr create \
    --title "Release v$NEW" \
    --body "Automated version bump to $NEW

This PR was created by the release workflow to bump the version from $CURRENT to $NEW.

- [x] Version bumped in pyproject.toml
- [x] Version bumped in src/__init__.py
- [x] Git tag v$NEW created
- [x] Release notes generated

Please review and merge to complete the release." \
    --base main \
    --head "$BRANCH_NAME" \
    --label "release" \
    --assignee "@me"

  echo "Pull request created for version $NEW"
  echo "Please review and merge the PR to complete the release"
fi 