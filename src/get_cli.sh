#!/bin/bash
# get_cli.sh
# Define the directory and the download URL
directory="utils"
url="https://github.com/kuzudb/kuzu/releases/download/v0.2.1/kuzu_cli-osx-universal.tar.gz"
filename="kuzu_cli-osx-universal.tar.gz"

# Create the directory if it doesn't exist
if [ ! -d "$directory" ]; then
    mkdir "$directory"
    echo "Directory $directory created."
else
    echo "Directory $directory already exists."
fi

# Change to the directory
cd "$directory"

# Download the file
echo "Downloading $filename..."
curl -L -O "$url"

# Decompress the file
echo "Decompressing $filename..."
tar -xzf "$filename"

# Change permissions of the extracted files to make them executable
echo "Changing permissions of extracted files..."
chmod +x kuzu
echo "Process completed."
