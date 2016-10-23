#!/bin/sh
#
# Will help with downloading clouds for the month
# Required: createcloudmap installed
#

for day in `seq 1 31`; do
    for hour in `seq 0 3 21`; do
        echo "Processing ${day} ${hour}..."
        create_map.py --timestamp "$day/07/16 $hour" --output "%Y-%m/clouds_%Y-%m-%d_%H.jpg" --range 151
    done
done
