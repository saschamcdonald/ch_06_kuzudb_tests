import os
import logging
from faker import Faker
import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base path for test data
TEST_DATA_PATH = os.getenv('TEST_DATA_PATH')

# User-defined settings for number of records and dynamic property columns
NUM_COMPANIES = int(os.getenv('NUM_COMPANIES', 4000000))
NUM_PERSONS = int(os.getenv('NUM_PERSONS', 10000000))
NUM_RELATIONSHIPS = int(os.getenv('NUM_RELATIONSHIPS', 45000000))
NUM_DYNAMIC_COMPANY_COLUMNS = int(os.getenv('NUM_DYNAMIC_COMPANY_COLUMNS', 5))
NUM_DYNAMIC_PERSON_COLUMNS = int(os.getenv('NUM_DYNAMIC_PERSON_COLUMNS', 5))
NUM_DYNAMIC_RELATIONSHIP_COLUMNS = int(os.getenv('NUM_DYNAMIC_RELATIONSHIP_COLUMNS', 5))

# Define paths for output Parquet files using the base path
COMPANY_PARQUET_PATH = os.path.join(TEST_DATA_PATH, 'companies.parquet')
PERSON_PARQUET_PATH = os.path.join(TEST_DATA_PATH, 'persons.parquet')
RELATIONSHIP_PARQUET_PATH = os.path.join(TEST_DATA_PATH, 'relationships.parquet')

def setup_logging():
    """Set up basic logging for the script."""
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def ensure_directories_exist():
    """Ensure that the directories for the Parquet files exist."""
    os.makedirs(os.path.dirname(COMPANY_PARQUET_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(PERSON_PARQUET_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(RELATIONSHIP_PARQUET_PATH), exist_ok=True)

def generate_dynamic_properties(num_columns):
    """Generate a dictionary of dynamic properties with Faker generator functions."""
    fake = Faker()
    return {f'property_{i}': (lambda f=fake.word: f()) for i in range(1, num_columns + 1)}

def generate_test_data(num_records, num_dynamic_columns, entity_type):
    """Generate test data for a specified number of dynamic properties."""
    fake = Faker()
    id_column_name = 'company_id' if entity_type == 'company' else 'person_id' if entity_type == 'person' else None
    base_attributes = {id_column_name: lambda: fake.unique.bothify(text='###???')} if id_column_name else {}
    dynamic_properties = generate_dynamic_properties(num_dynamic_columns)

    all_attributes = {**base_attributes, **dynamic_properties}
    data = {}

    for attr, generator in tqdm(all_attributes.items(), desc=f"Generating {entity_type} data"):
        data[attr] = [generator() for _ in range(num_records)]

    df = pd.DataFrame(data)
    return pa.Table.from_pandas(df), df

def save_data_to_parquet(table, path):
    """Save the generated PyArrow Table to a Parquet file with error handling."""
    try:
        pq.write_table(table, path, compression='snappy')
        logging.info(f"Data successfully saved to {path}.")
    except Exception as e:
        logging.error(f"Failed to save data to {path}. Error: {e}")

def main():
    setup_logging()
    ensure_directories_exist()

    # Generate and save Company data with dynamic properties
    company_table, company_df = generate_test_data(NUM_COMPANIES, NUM_DYNAMIC_COMPANY_COLUMNS, 'company')
    save_data_to_parquet(company_table, COMPANY_PARQUET_PATH)

    # Generate and save Person data with dynamic properties
    person_table, person_df = generate_test_data(NUM_PERSONS, NUM_DYNAMIC_PERSON_COLUMNS, 'person')
    save_data_to_parquet(person_table, PERSON_PARQUET_PATH)

    # Generate Relationship data
    try:
        _, relationship_df = generate_test_data(NUM_RELATIONSHIPS, NUM_DYNAMIC_RELATIONSHIP_COLUMNS, 'relationship')
        relationship_df['person_id'] = np.random.choice(person_df['person_id'], size=NUM_RELATIONSHIPS)
        relationship_df['company_id'] = np.random.choice(company_df['company_id'], size=NUM_RELATIONSHIPS)

        # Reorder columns to have 'person_id' and 'company_id' first
        cols = ['person_id', 'company_id'] + [col for col in relationship_df.columns if col not in ['person_id', 'company_id']]
        relationship_df = relationship_df[cols]
        relationship_table = pa.Table.from_pandas(relationship_df)
        save_data_to_parquet(relationship_table, RELATIONSHIP_PARQUET_PATH)
    except Exception as e:
        logging.error(f"Failed to generate or save relationship data. Error: {e}")

    logging.info("Data generation and saving completed.")

if __name__ == "__main__":
    main()
