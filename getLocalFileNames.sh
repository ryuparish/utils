#!/bin/bash
# R: Gathers all the file and directory names of every file in every subdirectory in the current subdirectory

# Creating file that contains all the problem relative paths 
touch files.txt

# R: Adds all the directories in the current directoy into a file called "fiels.txt"
for dir in */; do
    if [ "$dir" != "humblers" ]; then
        for file in "$dir"*; do
            echo "$file" >> files.txt
        done
    fi
done

# R: Getting only the second value in a separated string such as "first_thing/second_thing/third_thing..."
# Creating a cleaned version of the problems file
cat files.txt | cut -d / -f 2 > problems.txt
rm -f files.txt
