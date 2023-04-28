#!/usr/bin/env bash
target=$(git diff --diff-filter=d --name-only --staged)
echo $target
