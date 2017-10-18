#! /bin/bash

find . -type f -iname "freeplay.bag.active" -print0 | while IFS= read -r -d $'\0' f; do
    
    dir=$(dirname $f)
    bag=$(basename $f)

    cd $dir
    echo "Re-indexing $f..."
    rosbag reindex $bag && mv $bag freeplay.bag && echo "Done $dir. If correct, you can delete the tmp file"
    cd ..
done
