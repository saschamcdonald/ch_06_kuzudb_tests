import os
import sys
import time
import logging
import pyarrow.parquet as pq
import kuzu
from prettytable import PrettyTable
from importlib.metadata import version  # For Python 3.8 and newer
from tqdm import tqdm




def setup_logging():
    """Set up basic logging for the script."""
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')


def ensure_directories_exist(directories):
    """Ensure all specified directories exist."""
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def import_table_data(conn, copy_statement, table_name):
    """Executes a COPY statement to import data into a table and measures the time taken."""
    start_time = time.time()
    try:
        conn.execute(copy_statement)
        end_time = time.time()
        duration_seconds = end_time - start_time
        logging.info(f'Imported data into "{table_name}" Node Table in {duration_seconds:.2f} seconds.')
        return duration_seconds
    except RuntimeError as e:
        logging.error(f"Failed to import data into {table_name} Node Table. Error details: {e}")
        return None

def format_duration(seconds):
    """Formats the duration from seconds to minutes and seconds for readability."""
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{int(minutes)}m {int(seconds)}s"


def create_node_table_statement_from_parquet(parquet_path, table_name, primary_key):
    try:
        table = pq.read_table(parquet_path)
        schema = table.schema

        columns = [f"{field.name} STRING" for field in schema]
        primaryKeyStatement = f", PRIMARY KEY ({primary_key})" if primary_key else ""
        create_statement = f"CREATE NODE TABLE {table_name} ({', '.join(columns)}{primaryKeyStatement});"

        logging.debug(f'CREATE statement for {table_name}: {create_statement}')
        return create_statement
    except Exception as e:
        logging.error(f"Failed to generate CREATE statement for {table_name}: {e}")
        return None


def create_rel_table_statement_from_parquet(parquet_path, table_name):
    try:
        table = pq.read_table(parquet_path)
        schema = table.schema

        dynamic_columns = [f"{field.name} STRING" for field in schema if field.name not in ['person_id', 'company_id', 'id']]
        create_statement = f"CREATE REL TABLE {table_name} (FROM Person TO Company, {', '.join(dynamic_columns)});"

        logging.debug(f'CREATE statement for {table_name}: {create_statement}')
        return create_statement
    except Exception as e:
        logging.error(f"Failed to generate CREATE statement for {table_name}: {e}")
        return None


def execute_query_and_display(conn, query):
    """Execute a query against KuzuDB and display results using PrettyTable."""
    try:
        result = conn.execute(query)
        # Assuming 'result' is an iterable of dictionaries or similar structure
        if result:
            table = PrettyTable()
            # Assuming the first row contains all keys/column names
            table.field_names = result[0].keys()
            for row in result:
                table.add_row(row.values())
            print(table)
        else:
            print("No results found.")
    except Exception as e:
        logging.error(f"Query execution failed. Error details: {e}")


def main():
    setup_logging()
    # Get the environment variable for the test data path
    TEST_DATA_PATH = os.getenv('TEST_DATA_PATH')

    # Dynamically get the version of kuzu
    kuzu_version = version("kuzu")

    # Construct the database name dynamically based on the kuzu version
    DATABASE_NAME = f'test_kuzu_db_v{kuzu_version.replace(".", "_")}'
    DATABASE_DIR = os.path.join(TEST_DATA_PATH, DATABASE_NAME)

    DROP_TABLES = True

    # Parquet file paths
    COMPANY_PARQUET_PATH = os.path.join(TEST_DATA_PATH, 'companies.parquet')
    PERSON_PARQUET_PATH = os.path.join(TEST_DATA_PATH, 'persons.parquet')
    RELATIONSHIP_PARQUET_PATH = os.path.join(
        TEST_DATA_PATH, 'relationships.parquet')


    ensure_directories_exist([DATABASE_DIR])
    logging.info("Starting KuzuDB processing...")

    # Initialize KuzuDB connection
    try:
        db = kuzu.Database(os.path.join(DATABASE_DIR, DATABASE_NAME))
        conn = kuzu.Connection(db)
    except Exception as e:
        logging.error(f"Failed to initialize KuzuDB connection: {e}")
        sys.exit(1)  # Exit if database connection cannot be established

    # Drop existing tables if required
    if DROP_TABLES:
        for table_name in ["WORkS_AT", "Company", "Person"]:
            try:
                conn.execute(f"DROP TABLE {table_name}")
                logging.info(f"Table {table_name} dropped.")
            except Exception as e:
                # Check for a specific exception indicating the table doesn't exist
                # This is a generic approach; adjust based on your DB's API
                if 'does not exist' in str(e).lower():
                    logging.debug(
                        f"Table {table_name} does not exist. No need to drop.")
                else:
                    logging.error(f"Error dropping table {table_name}: {e}")

    # Create Company and Person node tables, and WORkS_AT relationship table
    create_statement_company = create_node_table_statement_from_parquet(
        COMPANY_PARQUET_PATH, "Company", "company_id")
    create_statement_person = create_node_table_statement_from_parquet(
        PERSON_PARQUET_PATH, "Person", "person_id")
    create_statement_relationship = create_rel_table_statement_from_parquet(
        RELATIONSHIP_PARQUET_PATH, "WORkS_AT")

    for statement in [create_statement_company, create_statement_person, create_statement_relationship]:
        try:
            conn.execute(statement)
            logging.info(f'Successfully created kuzu table: {statement.split()[3]}')
        except Exception as e:
            logging.error(f"Failed to execute statement. Error details: {e}")

        # Assuming conn is your database connection object
    load_times = []
    table_names = ["Person", "Company", "WORkS_AT"]
    parquet_paths = {
        "Person": os.path.join(TEST_DATA_PATH, 'persons.parquet'),
        "Company": os.path.join(TEST_DATA_PATH, 'companies.parquet'),
        "WORkS_AT": os.path.join(TEST_DATA_PATH, 'relationships.parquet')
    }

    for table_name in table_names:
        duration = import_table_data(conn, f'COPY {table_name} FROM "{parquet_paths[table_name]}" (HEADER = true)', table_name)
        if duration is not None:
            load_times.append((table_name, duration))

    # Displaying load times in a PrettyTable
    load_times_table = PrettyTable()
    load_times_table.title = f"Load Times for {DATABASE_NAME}"
    load_times_table.field_names = ["Table Name", "Load Time (Seconds)"]

    for table_name, duration in load_times:
        load_times_table.add_row([table_name, f"{duration:.2f}"])

    logging.info(f"Kuzu loaded time counts:\n {load_times_table}")

  # Execute queries and display results
    count_table = PrettyTable()
    count_table.title = f"Database Summary for {DATABASE_NAME}"
    count_table.field_names = ["Entity", "Node Count", "Relationship Count"]
    
    
    company_node_count = conn.execute(
        'MATCH (n:Company) RETURN COUNT(n) AS CompanyNodeCount;').get_next()[0]
    person_node_count = conn.execute(
        'MATCH (n:Person) RETURN COUNT(n) AS PersonNodeCount;').get_next()[0]
    WORkS_AT_rel_count = conn.execute(
        'MATCH ()-[r:WORkS_AT]-() RETURN COUNT(r) AS RelationshipCount;').get_next()[0]

    # Formatting numbers with commas
    formatted_company_node_count = format(company_node_count, ',')
    formatted_person_node_count = format(person_node_count, ',')
    formatted_WORkS_AT_rel_count = format(WORkS_AT_rel_count, ',')

    count_table.add_row(["Company", formatted_company_node_count, "-"])
    count_table.add_row(["Person", formatted_person_node_count, "-"])
    count_table.add_row(["-", "-", formatted_WORkS_AT_rel_count])
    logging.info(f"Kuzu loaded query counts:\n {count_table}")


    print("Processing completed.")

if __name__ == "__main__":
    main()
