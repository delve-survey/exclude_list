#!/usr/bin/env bash

cd decam

# This loop is outside of tcl because variables are not being unset in
# the way I'd expect...
for year in $(seq 0 12); do
    filename="../survey-y${year}.par"
    if [[ -e $filename ]]; then 
        echo "Running ${filename}..."
        echo "set year ${year}; source ../bin/run_ray_trace.tcl" | ../trace
    else
        echo "Didn't find ${filename}; skipping..."
        continue
    fi

done

cd -
