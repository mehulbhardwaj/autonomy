#!/bin/bash
set -e

LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$LAST_TAG" ]; then
  RANGE="$LAST_TAG..HEAD"
else
  RANGE="HEAD"
fi

echo "Generating release notes for $RANGE"

git log $RANGE --pretty=format:'- %s' > NEXT_RELEASE_NOTES.md

echo "Notes written to NEXT_RELEASE_NOTES.md"
