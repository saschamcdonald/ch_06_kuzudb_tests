import sys
import os
import logging
import test_create_test_data
import test_ingress_load_kuzudb



# to make sure that all packages inside 'src' can be found by Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    try:
        # Generate test data
        logging.info("Generating test data...")
        test_create_test_data.main()
        logging.info("Finished generating test data.")
    except Exception as e:
        logging.error(f"An error occurred while generating test data: {e}")
        # Optionally, exit the script if you don't want to proceed after a failure
        sys.exit(1)
    
    try:
        # Load Kuzu test data
        logging.info("Creating and loading Kuzu test data...")
        test_ingress_load_kuzudb.main()
        logging.info("Kuzu test data processing completed.")
    except Exception as e:
        logging.error(f"An error occurred while processing Kuzu test data: {e}")
        # Optionally, exit the script if you don't want to proceed after a failure
        sys.exit(1)


    logging.info("Game Over...")

if __name__ == "__main__":
    main()
