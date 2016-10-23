#!/bin/sh
#
# Will generate additional images between downloaded maps
# Required: gmic >= 1.7
#

GEN_FRAMES=4

dir=$1

[ -d "$dir" ] || exit 1

cd $dir

for day in `seq 1 31`; do
    for hour in `seq 0 3 21`; do
        day=`echo "$day" | sed 's/^\(.\)$/0\1/'`
        hour=`echo "$hour" | sed 's/^\(.\)$/0\1/'`
        echo "Processing ${day} ${hour}..."
        curr=`ls clouds_${dir}-${day}_${hour}*.jpg 2>/dev/null`
        if [ "${curr}" ]; then
            echo "  found ${curr}"
            if [ "${prev}" ]; then
                frames=$(($GEN_FRAMES+$skipped+$GEN_FRAMES*$skipped))
                output="${prev_namepart}_gen.jpg"
                echo "  exec gmic on ${curr} ${prev} with gen ${frames}"
                gmic -input ${prev} -input ${curr} -morph ${frames},0.1,4 -output ${output},90
            fi
            skipped=0
            prev=$curr
            prev_namepart="clouds_${dir}-${day}_${hour}"
        else
            skipped=$(($skipped+1))
            echo "  not found $skipped"
        fi
    done
done
