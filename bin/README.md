# This directory contains instructions inputs and outputs for running
# Steve Kent's ghost & scattered light blacklisting tools.

# NOTE: The name of the output file needs to be "y[0-9]+" where [0-9]+
# is one or more integers (see decam/shutter.tcl).  If year is 'y0' or
# 'y1', the ray tracing will try to run scattered light (which we
# usually don't want). This should be used for exposures taken before
# 2014-03-14

# Go to this working directory:
cd /home/s1/kadrlica/projects/delve/proc/exclude/work
# Setup python
source setup.sh

# Link the scripts to the working directory

# Query the sispi database for the DECam exposures
# Note that you need the decam_reader password in your ~/.pgpass
python query_exposures.py --db sispi

# Loop through the years running the bright star list job
# This takes a while, so run in screen
screen -S bstar -m ./bin/run_bstar.sh
# Or run for a single year
screen -S bstar -m bash -c 'echo "set year 1; source run_bstar.tcl" | ./ktools'

# Loop through the years running the ray tracing
# This is fast and pops up a gui, so don't run in screen
./bin/run_ray_trace.sh
# Or for a single year
cd decam; echo "set year 1; source ../run_ray_trace.tcl" | ../trace; cd -


