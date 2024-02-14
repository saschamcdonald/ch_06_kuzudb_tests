
import sys
import os

# Add the directory above 'src' to the Python path
# to make sure that all packages inside 'src' can be found by Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now we can do absolute imports without the 'src.' prefix


def main():
    # Generate the .env file
    print("Generating .env file...")
    config_generate_env.main()
    print("Finished generating .env file.")



if __name__ == "__main__":
    main()
