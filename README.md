
# Project Overview

This repository is designed to facilitate the creation and loading of test data into KuzuDB, highlighting the flexibility and ease of managing data across different database versions. It offers a comprehensive setup for generating test data and a simplistic model tailored for bulk loading into various versions of KuzuDB within isolated virtual environments. Additionally, this setup aims to replicate and analyze a known bulk loading error that occurs between two specified versions of KuzuDB, providing insights and potential workarounds for such issues.

Through detailed logging and observation, users can compare the behavior of different KuzuDB versions under identical conditions, shedding light on the error's nature and its impact on bulk data loading processes. This repository serves as a tool for troubleshooting, optimization, and ensuring the reliability of database operations, related to bulk loading a simple property graph. The test data creates Company Nodes Person Nodes and WORKS_AT Relationships dynamically based on user configs. Keep the defaults in the .env file to replicate the working and failing versions for testing this specific issue.

---

### Test Data Creation and Loading

Note the defaults in the .env replicate the error but you can configure for your own requirements

The project includes scripts for generating test data, which can then be loaded into KuzuDB. This process is automated and configurable, allowing for a seamless transition between different database versions or testing scenarios. The objective is to create a robust and repeatable process for data handling, which is crucial for testing database performance and error diagnostics.

### Configuration via `.env` file
Note the defaults in the .env replicate the error for kuzu version 0.2.0 and runs sucessfuly with kuzu versio 0.0.11 but you can configure for your own requirements
To offer maximum flexibility and ease of use, this project utilizes a `.env` file located in the `src` directory for all configuration settings. Users can specify various parameters, including paths, database connection details, and version-specific settings, without altering the core scripts. This approach ensures that the environment remains clean and that changes can be easily managed and replicated.

#### .env Settings Explained

The `.env` file allows you to customize the behavior of the test data generation and loading process. Below are the settings you can configure:

- `TEST_DATA_PATH`: Specifies the directory where test data files are stored. This path is used to locate the data files for loading into KuzuDB.
  
- `NUM_COMPANIES`: Defines the total number of company records to generate for test data.
  
- `NUM_PERSONS`: Sets the total number of person records to generate for test data.
  
- `NUM_RELATIONSHIPS`: Determines the total number of relationships to establish between persons and companies in the test data.

- `NUM_DYNAMIC_COMPANY_COLUMNS`: Specifies the number of dynamic property columns for companies. 

- `NUM_DYNAMIC_PERSON_COLUMNS`: Similar to companies, this setting defines the number of dynamic property columns for persons.
  
- `NUM_DYNAMIC_RELATIONSHIP_COLUMNS`: Sets the number of dynamic property columns for relationships, further enhancing the data model's realism.

 `.env` content (the following defaults offer the error between the versions):


```bash
# Base path for test data storage
TEST_DATA_PATH=./data
# User-defined settings for the number of records
NUM_COMPANIES=4000000 # Total number of companies
NUM_PERSONS=10000000 # Total number of persons
NUM_RELATIONSHIPS=45000000 # Total number of relationships

# Settings for dynamic property columns, intended as Dynamic Property columns STRING (Default) columns
NUM_DYNAMIC_COMPANY_COLUMNS=5 # Dynamic Property columns STRING for companies, default settings
NUM_DYNAMIC_PERSON_COLUMNS=5 # Dynamic Property columns STRING for persons, default settings
NUM_DYNAMIC_RELATIONSHIP_COLUMNS=5 # Dynamic Property columns STRING for relationships, default settings

```


# Getting Started

Setting up your Python environment, managing virtual environments, and handling project dependencies with ease.

## Prerequisites

Before you start, you need to have `pyenv` installed on your machine. For a detailed guide on installing `pyenv` and setting up Python environments, refer to the [Fathomtech blog post on Python environments with pyenv and virtualenv](https://fathomtech.io/blog/python-environments-with-pyenv-and-vitualenv/).

## Installation and Setup

### Installing Python

Start by installing the required Python version using `pyenv`:

```bash
pyenv install 3.11.6
```

### Install pyenv-virtualenv

After installing the desired Python version, you can create a virtual environment to isolate your project dependencies. Follow these steps if you haven't already installed the `pyenv-virtualenv` plugin:

1. **Install the `pyenv-virtualenv` Plugin:**

   Clone the plugin into the `pyenv` plugins directory:

   ```bash
   git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv
   ```

2. **Configure Your Shell:**

   Add `pyenv virtualenv-init` to your shell's startup script:

   ```bash
   echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
   ```

   Restart your shell or source your profile to apply the changes:

   ```bash
   source ~/.bashrc
   ```

---

### Create and Activate Virtual Environment and Run the First Test for Kuzu Version 0.1.1:

**NOTE:** This version successfully loads all the data (PASSES using defaults provided in this repository).

- **For Kuzu version 0.1.1**:

  ```bash
  # Deactivate any currently active pyenv environment
  pyenv deactivate
  # Clean up all `__pycache__` directories from the project root:
  find . -type d -name '__pycache__' -exec rm -r {} +
  # Create and activate a new virtual environment for KuzuDB version 0.1.1
  pyenv virtualenv 3.11.6 dc-kuzu-0-1-1
  pyenv activate dc-kuzu-0-1-1
  # Upgrade pip, setuptools, and wheel to the latest versions
  pip install --upgrade pip setuptools wheel
  # Install pip-tools for dependency management
  pip install pip-tools
  # Compile dependencies from the .in file to a .txt file
  pip-compile requirements-kuzu-0.0.11.in
  # Install dependencies from the compiled requirements file
  pip install --no-cache-dir -r requirements-kuzu-0.0.11.txt
  # Run the main script to generate and load data into KuzuDB
  # (Comment out data creation script in main.py if data has already been generated)
  python src/main.py
  ```

### Create and Activate Virtual Environment and run the second test for Kuzu Version 0.2.0:

**NOTE:** This version successfully loads the Company and Person tables but ERRORS on loading the Relationship data (FAILS using defaults provided in this repository). : `ERROR - Failed to import data into WORkS_AT Node Table. Error details: Buffer manager exception: Failed to claim a frame.`

- **For Kuzu version 0.2.0**:

  ```bash
  # Deactivate any currently active pyenv environment
  pyenv deactivate
  # Clean up all `__pycache__` directories from the project root:
  find . -type d -name '__pycache__' -exec rm -r {} +
  # Create and activate a new virtual environment for KuzuDB version 0.2.0
  pyenv virtualenv 3.11.6 dc-kuzu-0-2-0
  pyenv activate dc-kuzu-0-2-0
  # Upgrade pip, setuptools, and wheel to the latest versions
  pip install --upgrade pip setuptools wheel
  # Install pip-tools for dependency management
  pip install pip-tools
  # Compile dependencies from the .in file to a .txt file
  pip-compile requirements-kuzu-0.2.0.in
  # Install dependencies from the compiled requirements file
  pip install --no-cache-dir -r requirements-kuzu-0.2.0.txt
  # Run the main script to generate and load data into KuzuDB
  # (Comment out data creation call in main.py if data has already been generated)
  python src/main.py
  ```

---

### Cleaning Up

After testing with a virtual environment deactivate and remove it:

- **Deactivate the Virtual Environment:**

  ```bash
  pyenv deactivate
  ```

- **Uninstall the Virtual Environment:**

  - For version 0.1.1:

    ```bash
    pyenv uninstall -f dc-kuzu-0-1-1
    ```

  - For version 0.2.0:

    ```bash
    pyenv uninstall -f dc-kuzu-0-2-0
    ```

- **Remove Python Caches:**

  Run the following command from the project root to clean up all `__pycache__` directories:

  ```bash
  find . -type d -name '__pycache__' -exec rm -r {} +
  ```

---

# License

This project is licensed under the MIT License.

Copyright (c) 2024 Datacue Limited

Author: Sascha McDonald

For more details, see the LICENSE file included in this repository.