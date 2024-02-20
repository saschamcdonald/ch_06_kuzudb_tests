#!/bin/bash

# Function to deactivate pyenv if active
deactivate_pyenv_if_active() {
    if command -v pyenv &>/dev/null; then
        # Check if a pyenv virtualenv is currently active
        if [ -n "$PYENV_VERSION" ]; then
            echo "Deactivating current pyenv environment: $PYENV_VERSION"
            pyenv deactivate || true  # Ignore error if no environment is active
        else
            echo "No pyenv virtualenv is currently active."
        fi
    else
        echo "pyenv is not installed. Please install pyenv."
        exit 1
    fi
}

# Function to set up and test a specific KuzuDB version
test_kuzu_version() {
    local version=$1
    local requirements_file="requirements-kuzu-$version.in"
    local compiled_requirements_file="requirements-kuzu-$version.txt"

    echo "Setting up environment for KuzuDB version $version..."

    # Check and deactivate any currently active pyenv environment
    deactivate_pyenv_if_active

    # Clean up all `__pycache__` directories from the project root
    find . -type d -name '__pycache__' -exec rm -r {} +

    # Create and activate a new virtual environment for the specified KuzuDB version
    pyenv virtualenv 3.11.6 "dc-kuzu-$version" && pyenv activate "dc-kuzu-$version"

    # Upgrade pip, setuptools, and wheel to the latest versions
    pip install --upgrade pip setuptools wheel

    # Install pip-tools for dependency management
    pip install pip-tools

    # Compile dependencies from the .in file to a .txt file
    pip-compile $requirements_file

    # Install dependencies from the compiled requirements file
    pip install --no-cache-dir -r $compiled_requirements_file

    # Run the main script to generate and load data into KuzuDB
    # Uncomment the next line if data creation needs to be part of the script
    # python src/main.py

    echo "Test for KuzuDB version $version completed."
    echo "Cleaning up..."

    # Deactivate the virtual environment
    pyenv deactivate || true  # Ignore error if no environment is active

    # Remove the compiled requirements file to clean up
    rm -f $compiled_requirements_file
}

# Ensure pyenv is correctly initialized
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Array of KuzuDB versions to test
versions=("0.0.11" "0.2.1" "latest")

# Iterate over versions and test each one
for version in "${versions[@]}"; do
    test_kuzu_version "$version"
done

echo "All tests completed."
