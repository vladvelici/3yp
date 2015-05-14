#!/bin/bash


for FRAMENO in $(seq $5)
do
    ./cmd.py dotframe $1 $2 -mu $3 -k $FRAMENO $4_$FRAMENO.dot
    dot -Tpdf -o img_$4_$FRAMENO.pdf $4_$FRAMENO.dot 
done


