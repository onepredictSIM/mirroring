#!/bin/usr/env bash
if [ $# -eq 0 ]
    then
        read -a paths
        for path in ${paths}
        do
            if [ $path == *.py ]
                then
                    poetry run isort $path
                    poetry run black $path
            fi
        done
else
    poetry run isort .
    poetry run black .
fi
