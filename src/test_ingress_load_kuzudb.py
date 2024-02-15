import os
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


def create_node_table_statement_from_parquet(parquet_path, table_name, primary_key):
    """Generate a CREATE NODE TABLE statement for KuzuDB based on a Parquet file schema."""
    table = pq.read_table(parquet_path)
    schema = table.schema

    columns = []
    for field in schema:
        column_name = field.name
        column_type = "STRING"  # Assuming all columns default to STRING type
        columns.append(f"{column_name} {column_type}")

    column_definitions = ",\n".join(columns)
    primaryKeyStatement = f",\nPRIMARY KEY ({primary_key})" if primary_key else ""

    create_statement = f"CREATE NODE TABLE {table_name} (\n{column_definitions}{primaryKeyStatement}\n);"
    print(f'create_statement:{create_statement}')
    return create_statement


def create_rel_table_statement_from_parquet(parquet_path, table_name):
    """Generate a CREATE REL TABLE statement for KuzuDB, specifically for the WORkS_AT relationship table."""
    table = pq.read_table(parquet_path)
    schema = table.schema

    # Prepare dynamic columns, excluding predefined ones
    dynamic_columns = []
    for field in schema:
        column_name = field.name
        # Exclude predefined columns
        if column_name not in ['person_id', 'company_id', 'id']:
            column_type = "STRING"  # Default to STRING type for simplicity
            dynamic_columns.append(f"{column_name} {column_type}")

    dynamic_column_definitions = ",\n".join(dynamic_columns)

    # Formulating the CREATE REL TABLE statement according to the specified format
    
    create_statement = f"""CREATE REL TABLE {table_name} (
FROM Person TO Company,
{dynamic_column_definitions}
);"""
    print(f'create_statement:{create_statement}')
    return create_statement


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
    db = kuzu.Database(os.path.join(DATABASE_DIR, DATABASE_NAME))
    conn = kuzu.Connection(db)

    # Drop existing tables if required
    if DROP_TABLES:
        for table_name in tqdm(["WORkS_AT", "Company", "Person"], desc="Dropping tables"):
            try:
                conn.execute(f"DROP TABLE {table_name}")
                logging.info(f"Table {table_name} dropped.")
            except Exception as e:
                # Check for a specific exception indicating the table doesn't exist
                # This is a generic approach; adjust based on your DB's API
                if 'does not exist' in str(e).lower():
                    logging.info(
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
            logging.info(f'Successfully executed: {statement.split()[2]}')
        except Exception as e:
            logging.error(f"Failed to execute statement. Error details: {e}")

    
    try:
        conn.execute(
            f'COPY Person  FROM "{PERSON_PARQUET_PATH}" (HEADER = true)')
        logging.info(f'Imported persons data into "Person" Node Table.')
    except RuntimeError as e:
        logging.info(
            f"Failed to import persons data into Person Node Table. Error details: {e}")
    try:
        conn.execute(
            f'COPY Company FROM "{COMPANY_PARQUET_PATH}" (HEADER = true)')
        logging.info('Imported data into "Company" Node Table.')
    except RuntimeError as e:
        logging.info(
            f"Failed to import data into Company node table. Error details: {e}")

    try:
        conn.execute(
            f'COPY WORkS_AT FROM "{RELATIONSHIP_PARQUET_PATH}" (HEADER = true)')
        logging.info('Imported data into "WORkS_AT" Relationship Table.')
    except RuntimeError as e:
        logging.info(
            f"Failed to import data into WORkS_AT relationship table. Error details: {e}")

  # Execute queries and display results
    count_table = PrettyTable()
    count_table.field_names = ["Label", "Node Count", "Relationship Count"]
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
    logging.info(count_table)


    print("Processing completed.")

if __name__ == "__main__":
    main()
