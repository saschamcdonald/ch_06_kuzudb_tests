import os
import logging
import pyarrow.parquet as pq
import kuzu
from prettytable import PrettyTable


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
    """Generate a CREATE REL TABLE statement for KuzuDB, specifically for the IS_OFFICER relationship table."""
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

    # Paths and database configurations
    # DATABASE_DIR = '/path/to/Database'
    # DATABASE_NAME = 'test_kuzu_db'
    # DROP_TABLES = True

    # COMPANY_PARQUET_PATH = '/path/to/companies.parquet'
    # PERSON_PARQUET_PATH = '/path/to/persons.parquet'
    # RELATIONSHIP_PARQUET_PATH = '/path/to/relationships.parquet'

    DATABASE_DIR = '/Volumes/G-DRIVE/test_data/Database'
    DATABASE_NAME = 'test_kuzu_db'
    DROP_TABLES = True

    COMPANY_PARQUET_PATH = '/Volumes/G-DRIVE/test_data/companies.parquet'
    PERSON_PARQUET_PATH = '/Volumes/G-DRIVE/test_data/persons.parquet'
    RELATIONSHIP_PARQUET_PATH = '/Volumes/G-DRIVE/test_data/relationships.parquet'

    ensure_directories_exist([DATABASE_DIR])
    logging.info("Starting KuzuDB processing...")

    # Initialize KuzuDB connection
    db = kuzu.Database(os.path.join(DATABASE_DIR, DATABASE_NAME))
    conn = kuzu.Connection(db)

    # Drop existing tables if required
    if DROP_TABLES:
        for table_name in ["IS_OFFICER", "Company", "Person"]:
            try:
                conn.execute(f"DROP TABLE {table_name}")
                logging.info(f'Dropped table "{table_name}" if it existed.')
            except Exception as e:
                logging.error(f"Error while dropping table {table_name}: {e}")

    # Create Company and Person node tables, and IS_OFFICER relationship table
    create_statement_company = create_node_table_statement_from_parquet(
        COMPANY_PARQUET_PATH, "Company", "company_id")
    create_statement_person = create_node_table_statement_from_parquet(
        PERSON_PARQUET_PATH, "Person", "person_id")
    create_statement_relationship = create_rel_table_statement_from_parquet(
        RELATIONSHIP_PARQUET_PATH, "IS_OFFICER")

    for statement in [create_statement_company, create_statement_person, create_statement_relationship]:
        try:
            conn.execute(statement)
            logging.info(f'Successfully executed: {statement.split()[2]}')
        except Exception as e:
            logging.error(f"Failed to execute statement. Error details: {e}")

    logging.info("KuzuDB processing completed.")
    
    
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
            f'COPY IS_OFFICER FROM "{RELATIONSHIP_PARQUET_PATH}" (HEADER = true)')
        logging.info('Imported data into "IS_OFFICER" Relationship Table.')
    except RuntimeError as e:
        logging.info(
            f"Failed to import data into IS_OFFICER relationship table. Error details: {e}")

  # Execute queries and display results
    count_table = PrettyTable()
    count_table.field_names = ["Label", "Node Count", "Relationship Count"]
    company_node_count = conn.execute(
        'MATCH (n:Company) RETURN COUNT(n) AS CompanyNodeCount;').get_next()[0]
    person_node_count = conn.execute(
        'MATCH (n:Person) RETURN COUNT(n) AS PersonNodeCount;').get_next()[0]
    is_officer_rel_count = conn.execute(
        'MATCH ()-[r:IS_OFFICER]-() RETURN COUNT(r) AS RelationshipCount;').get_next()[0]

    # Formatting numbers with commas
    formatted_company_node_count = format(company_node_count, ',')
    formatted_person_node_count = format(person_node_count, ',')
    formatted_is_officer_rel_count = format(is_officer_rel_count, ',')

    count_table.add_row(["Company", formatted_company_node_count, "-"])
    count_table.add_row(["Person", formatted_person_node_count, "-"])
    count_table.add_row(["-", "-", formatted_is_officer_rel_count])
    logging.info(count_table)


    print("Processing completed.")

if __name__ == "__main__":
    main()
