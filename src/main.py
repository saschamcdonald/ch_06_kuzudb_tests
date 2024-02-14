
import sys
import os
import test_create_test_data as test_create_test_data
import test_ingress_load_kuzudb as test_ingress_load_kuzudb

# to make sure that all packages inside 'src' can be found by Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now we can do absolute imports without the 'src.' prefix


def main():
    # Generate test data
    # print("Generating test data...")
    # test_create_test_data.main()
    # print("Finished generating test data.")
    
    # Generate test data
    print("Create and load Kuzu test data...")
    test_ingress_load_kuzudb.main()
    print("Game Over...")



if __name__ == "__main__":
    main()
