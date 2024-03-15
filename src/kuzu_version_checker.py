import subprocess


def get_kuzu_version():
    try:
        # Run the "pip show" command and capture its output
        result = subprocess.run(['pip', 'show', 'kuzu'], capture_output=True, text=True)
        if result.returncode == 0:
            # Process the output to find the version line
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(' ')[1]
            return 'Version not found'
        else:
            return 'Error executing pip command'
    except Exception as e:
        return f'Error: {e}'


def main():
    get_kuzu_version()

    
if __name__ == "__main__":
    main()