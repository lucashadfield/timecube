#!/bin/bash

for file in *.bmp; do
    echo "Converting $file"
    base="${file%.bmp}"
    output_file="${base}.c"
    python ~/projects/third_party/python-bmp2hex/bmp2hex.py -w 12 $file -r > $output_file
    sed -i '1,2d' $output_file
    cat file_header.txt $output_file > tmp
    mv tmp $output_file
#    echo '#define out_width 64\n#define out_height 64\nstatic unsigned char out_bits[] = {/' | cat $output_file > $output_file
#    sed -i '1,2s/.*/#define out_width 64\n#define out_height 64\nstatic unsigned char out_bits[] = {/' $output_file
done

