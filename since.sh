#!/bin/bash

# R: Origin: Some post on stackoverflow that I cannot seem to remember.

# R: Detects the last time this file was changed or written to.
find $1 -type f -exec gstat --format '%Y :%y %n' "{}" \; | sort -nr | cut -d: -f2- | head
