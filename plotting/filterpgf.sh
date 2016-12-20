#!/usr/bin/env bash

infile="$1"
outfile="$2"
decimator="$3"

i=0
j=0
while read line;do
    if [[ "$line" =~ ^\pgfpathlineto ]];then
        if [[ $(($i % $decimator)) -eq 0 ]];then
            echo "$line" >> "$outfile"
            j=$((j+1))
        fi
        i=$((i+1))
    else
        echo "$line" >> "$outfile"
    fi
done < "$infile"
