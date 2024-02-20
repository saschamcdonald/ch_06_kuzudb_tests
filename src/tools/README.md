
# Automated Download and Setup Script

This script automates the process of downloading, decompressing, and organizing files from a specified URL. It is designed to streamline the setup of software or tools, specifically by creating a well-organized directory structure that includes versioning information.

## Features

- **Customizable Download URL**: Allows specifying a custom download URL, with a default option provided.
- **Version Extraction**: Automatically extracts the version number from the download URL and incorporates it into the directory structure for easy version management.
- **Automatic Decompression**: Decompresses the downloaded `.tar.gz` file into a structured directory format.
- **Permission Setting**: Sets executable permissions on the decompressed files.
- **Clean-up Option**: Offers the option to remove the original downloaded `.tar.gz` file after decompression.
- **Non-interactive Mode**: Supports a `--default` flag for running the script with all default options, requiring no user interaction.

## Prerequisites

- Unix-like operating system (e.g., Linux, macOS)
- Bash shell
- `curl` and `tar` utilities available

## Usage

### Interactive Mode

1. **Run the Script**: Navigate to the script's directory and execute:

   ```bash
   ./get_cli.sh
   ```

2. **Follow Prompts**: The script will prompt for a download URL (optional) and whether to remove the downloaded file after decompression.

### Non-interactive Mode

Run the script with the `--default` flag to use the default settings without any prompts:

```bash
./get_cli.sh --default
```

This mode automatically uses the predefined download URL and cleans up the downloaded `.tar.gz` file.

## Customization

To customize the default settings, such as the default download URL or the target directory, edit the `default_url` and `default_directory` variables at the beginning of the script.

## Directory Structure

The script creates a directory under `utils/`, named after the downloaded file and its version. For example, for version `v0.2.1` of `kuzu_cli-osx-universal.tar.gz`, the directory would be `utils/kuzu_cli-osx-universal-v0.2.1/`.

## Contributing

Contributions to the script are welcome. Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

## License MIT
