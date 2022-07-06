#!/bin/bash

# R: This script will remove any cached large files with the given name from the input
git filter-branch -f --index-filter "git rm -r --cached --ignore-unmatch $1" HEAD
