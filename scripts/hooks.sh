#!/usr/bin/env bash
poetry run pre-commit run --all-files -c ./.github/.pre-commit-config-only-hooks.yaml
