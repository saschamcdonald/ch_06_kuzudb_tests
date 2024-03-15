#!/bin/bash

# Default behavior is to uninstall and recreate the environment
# REUSE_ENV="false"
REUSE_ENV="true"
# Check for command-line arguments
while getopts ":r" opt; do
  case ${opt} in
    r )
      REUSE_ENV="true"
      ;;
    \? )
      echo "Usage: cmd [-r]"
      echo "-r: Reuse existing virtual environment if found."
      exit 1
      ;;
  esac
done

# Function to check if pyenv is installed and deactivate any active environment
deactivate_pyenv_if_active() {
    if ! command -v pyenv &>/dev/null; then
        echo "pyenv is not installed. Please install pyenv."
        exit 1
    fi

    if [ -n "$PYENV_VERSION" ]; then
        echo "Deactivating current pyenv environment: $PYENV_VERSION"
        pyenv deactivate || true  # Proceed even if no environment is active
    else
        echo "No pyenv virtualenv is currently active."
    fi
}

# Function to uninstall virtual environment if it exists and reuse is not requested
uninstall_virtualenv_if_exists() {
    local env_name=$1
    if [ "$REUSE_ENV" == "false" ]; then
        if pyenv virtualenvs | grep -q "$env_name"; then
            echo "Virtualenv $env_name already exists. Uninstalling..."
            pyenv uninstall -f "$env_name"
        fi
    else
        echo "Reusing existing virtualenv $env_name."
    fi
}

# Function to set up and test a specific KuzuDB version
test_kuzu_version() {
    local version=$1
    local env_name="dc-kuzu-$version"
    local requirements_file="requirements-kuzu-$version.in"
    local compiled_requirements_file="requirements-kuzu-$version.txt"

    echo "Setting up environment for KuzuDB version $version..."

    # Check and deactivate any currently active pyenv environment
    deactivate_pyenv_if_active

    # Handle existing virtualenv based on user choice
    uninstall_virtualenv_if_exists "$env_name"

    if [ "$REUSE_ENV" == "false" ]; then
        # Clean up and recreate the virtual environment
        pyenv virtualenv 3.11.6 "$env_name"
    fi

    pyenv activate "$env_name" || {
        echo "Failed to activate virtual environment for version $version."
        exit 1
    }

    if [ "$REUSE_ENV" == "false" ]; then
        # Install or upgrade dependencies if not reusing the environment
        pip install --upgrade pip setuptools wheel
        pip install pip-tools
        pip-compile $requirements_file
        pip install --no-cache-dir -r $compiled_requirements_file
    fi

    # Run the main script to generate and load data into KuzuDB
    python src/main.py || {
        echo "Failed to execute main script for version $version."
        exit 1
    }

    echo "Test for KuzuDB version $version completed."
    echo "Cleaning up..."

    # Optionally deactivate and cleanup
    pyenv deactivate || true

    if [ "$REUSE_ENV" == "false" ]; then
        rm -f $compiled_requirements_file
    fi
}

# Ensure pyenv is correctly initialized
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Array of KuzuDB versions to test, focusing on "latest" as specified
# versions=("0.0.12")
versions=("latest")
# versions=("0.0.11")
# versions=("0.0.11" "0.2.1" "latest")
# Iterate over versions and test each one
for version in "${versions[@]}"; do
    test_kuzu_version "$version"
done

echo "All tests completed."
