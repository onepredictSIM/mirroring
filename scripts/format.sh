#!/usr/bin/env bash
poetry run isort $@
poetry run black $@
