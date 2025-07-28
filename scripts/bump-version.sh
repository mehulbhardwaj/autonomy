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
git tag -a "v$NEW" -m "Release v$NEW"

