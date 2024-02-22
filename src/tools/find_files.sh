#!/bin/bash

# Define the root directory for the search. Change "/" to a specific directory to narrow the search.
SEARCH_DIR="/"

# Temporary file to store results
RESULT_FILE="/tmp/found_files.txt"

# Corrected variable assignment, no spaces around "="
SEARCH_STRING="STEINRUECKEN"

# Ensure the result file is empty
> "$RESULT_FILE"

# Corrected usage of variable within command, note the use of "$SEARCH_STRING"
# and the correction in how the variable is referenced.
find "$SEARCH_DIR" -type f -exec grep -il "$SEARCH_STRING" {} + 2>/dev/null | xargs grep -il "Slack" >> "$RESULT_FILE" 2>/dev/null

# Check if the result file is empty
if [ -s "$RESULT_FILE" ]
then
    # If the file has content, display it with less for paginated viewing
    less "$RESULT_FILE"
else
    echo "No files found containing '$SEARCH_STRING' and 'Slack'."
fi
