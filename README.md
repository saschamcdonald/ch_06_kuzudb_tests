```markdown
# Getting Started with Your Python Project

Welcome to your Python project setup guide. This README provides a comprehensive walkthrough for setting up your Python environment, managing virtual environments, and handling project dependencies with ease.

## Prerequisites

Before you start, you need to have `pyenv` installed on your machine. For a detailed guide on installing `pyenv` and setting up Python environments, refer to the [Fathomtech blog post on Python environments with pyenv and virtualenv](https://fathomtech.io/blog/python-environments-with-pyenv-and-vitualenv/).

## Installation and Setup

### Installing Python

Start by installing the required Python version using `pyenv`:

```bash
pyenv install 3.11.6
```

### Creating a Virtual Environment

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

3. **Create and Activate Virtual Environment:**

   - For version 0.1.1:

     ```bash
     pyenv virtualenv 3.11.6 dc-kuzu-0-1-1
     pyenv activate dc-kuzu-0-1-1
     ```

   - For version 0.2.0:

     ```bash
     pyenv virtualenv 3.11.6 dc-kuzu-0-2-0
     pyenv activate dc-kuzu-0-2-0
     ```

### Managing Dependencies

1. **Upgrade `pip`, `setuptools`, and `wheel`:**

   ```bash
   pip install --upgrade pip setuptools wheel
   ```

2. **Install `pip-tools` for Dependency Management:**

   ```bash
   pip install pip-tools
   ```

3. **Compile and Install Dependencies:**

   - For version 0.1.1:

     ```bash
     pip-compile requirements-kuzu-0.0.11.in
     pip install --no-cache-dir -r requirements-kuzu-0.0.11.txt
     ```

   - For version 0.2.0:

     ```bash
     pip-compile requirements-kuzu-0.2.0.in
     pip install --no-cache-dir -r requirements-kuzu-0.2.0.txt
     ```

### Cleaning Up

After you're done working with a virtual environment, you can deactivate and remove it:

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

This setup ensures that your development environment is clean, organized, and consistent across different versions of your project. Happy coding!
```