#!/bin/bash

# Instructions for Use:
# Save the Script: Copy the above script into a new file, for example, get_cli.sh.
# Make It Executable: Run chmod +x get_cli.sh to make the script executable.
# Run the Script:
# To run with prompts for input: ./get_cli.sh
# To run with all defaults (no prompts): ./get_cli.sh --default
# This script now fully supports automated runs using the --default flag, alongside interactive runs that prompt the user for input.
# It handles downloading, extracting, and setting up the software from a provided URL (or a default URL), and organizes the content in a structured manner within the utils directory.


# Check for 'default' command-line argument
if [[ "$1" == "--default" ]]; then
    use_defaults=true
else
    use_defaults=false
fi

# Default values
default_directory="kuzu"
# URL from which the filename is to be extracted
default_url="https://github.com/kuzudb/kuzu/releases/download/v0.2.1/kuzu_cli-osx-universal.tar.gz"

# Extract the filename from the URL
default_filename="${default_url##*/}"

# Print the filename
echo "The filename is $default_filename"

# Function to prompt user input with a default value
prompt_with_default() {
    local prompt_text="$1"
    local default_value="$2"
    if [ "$use_defaults" = true ]; then
        echo "$default_value"
    else
        read -p "$prompt_text" input
        echo "${input:-$default_value}"
    fi
}

# Use function to get URL or default
url=$(prompt_with_default "Enter download URL or press enter to use default [$default_url]: " "$default_url")

# Determine filename from URL
filename="${url##*/}" # Extracts filename from URL

# Extract version more reliably using a regular expression
version_pattern="v[0-9]+\.[0-9]+\.[0-9]+"
if [[ $url =~ $version_pattern ]]; then
    version="${BASH_REMATCH[0]}"
else
    version="unknown"
fi
version_txt="version_${version}.txt"

# Inform the user about the URL, filename, and version being used
echo "Using URL: $url"
echo "Filename determined as: $filename"
echo "Version extracted from URL: $version"

# Creates a subdirectory named after the filename without extension and includes the version
directory="$default_directory/${filename%.tar.gz}-$version"

# Use defaults or prompt for removing the downloaded file
remove_downloaded=$(prompt_with_default "Do you want to remove the downloaded .tar.gz file after decompression? (y/n): " "y")

# Ensure the directories exist
mkdir -p "$default_directory"
mkdir -p "$directory"

cd "$directory" || { echo "Failed to change to directory $directory."; exit 1; }

# Download the file
echo "Downloading $filename to $default_directory..."
curl -L -o "../$filename" "$url" || { echo "Failed to download $filename."; exit 1; }

# Decompress the file
echo "Decompressing $filename into $directory..."
tar -xzf "../$filename" || { echo "Failed to decompress $filename."; exit 1; }

# Optionally remove the downloaded file
if [ "$remove_downloaded" = "y" ]; then
    echo "Removing downloaded file: ../$filename"
    rm -f "../$filename"
fi

# Create a version text file
echo "Creating version file: $version_txt in $directory"
echo "$version" > "$version_txt"

# Change permissions of the extracted files
echo "Changing permissions of extracted files in $directory..."
find . -mindepth 1 -type f -exec chmod +x {} \; || { echo "Failed to change permissions of extracted files."; exit 1; }

echo "Process completed successfully."
