# Datacue-Kuzu: Test Data and Bulk Load Generator

Welcome to Datacue-Kuzu, your go-to solution for generating test data and managing bulk data loading efficiently. This guide will help you get started with setting up your environment and running the Data Engineering Pipeline.

## Prerequisites

Before you begin, ensure you have `pyenv` installed to manage your Python versions effectively. If you need assistance installing `pyenv`, refer to the [Fathomtech blog post on Python environments with pyenv and virtualenv](https://fathomtech.io/blog/python-environments-with-pyenv-and-vitualenv/).

## Installation Guide

Follow these steps to set up your environment:

### 1. Install Python

Install the required Python version using `pyenv`:

```bash
pyenv install 3.11.6
```

### 2. Install and Configure pyenv-virtualenv

To manage virtual environments, you'll need `pyenv-virtualenv`. If it's not already installed, follow these steps:

- **Install `pyenv-virtualenv` Plugin:**

  Clone the `pyenv-virtualenv` repository into the `pyenv` plugins directory:

  ```bash
  git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv
  ```

- **Configure Shell:**

  Add `pyenv virtualenv-init` to your shell startup file (e.g., `~/.bashrc`, `~/.zshrc`):

  ```bash
  eval "$(pyenv virtualenv-init -)"
  ```

  Restart your shell or source your startup file to apply the changes.

- **Create a Virtual Environment:**

  ```bash
  pyenv virtualenv 3.11.6 dc-kuzu-test-gen
  ```

### 3. Activate the Virtual Environment and Install Dependencies

Activate your virtual environment and set up your project dependencies:

```bash
pyenv activate dc-kuzu-test-gen
pip install --upgrade pip setuptools wheel
pip install pip-tools
pip-compile --upgrade
pip install --no-cache-dir -r requirements.txt
```

### 4. Run the Data Engineering Pipeline

Execute the following commands to start the pipeline:

```bash
python src/config_generate_env.py
python src/main.py
```

## Additional Commands

Here are some useful commands for managing your environment and project:

- **Deactivate the Virtual Environment:**

  ```bash
  pyenv deactivate
  ```

- **Clean Python Caches:**

  Remove all `__pycache__` directories within the project:

  ```bash
  find . -type d -name '__pycache__' -exec rm -r {} +
  ```

- **Uninstall the Virtual Environment:**

  ```bash
  pyenv uninstall -f dc-kuzu-test-gen
  ```

- **Update Dependencies with pip-tools:**

  First, install `pip-tools`:

  ```bash
  pip install pip-tools
  ```

  Then, update all package versions and regenerate `requirements.txt`:

  ```bash
  pip-compile --upgrade
  pip install --no-cache-dir -r requirements.txt
  ```
