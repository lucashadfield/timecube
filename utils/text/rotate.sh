#!/bin/bash

for file in *_r0.bmp; do
    echo "Processing $file..."
    base="${file%_r0.bmp}"
    for (( i=1; i<=3; i++ )); do
        output_file="${base}_r$i.bmp"
        convert -rotate $(( i * 90 )) "$file" "$output_file"
        echo "Created $output_file"
    done
done

