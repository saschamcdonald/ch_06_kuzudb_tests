import os
import sys
import time
import logging
import json
import pyarrow.parquet as pq
import kuzu
import pandas as pd
from prettytable import PrettyTable
from importlib.metadata import version  # For Python 3.8 and newer
from tqdm import tqdm
from io import StringIO
from DashboardCreator import DashboardCreator


# Update setup_logging to capture log messages for the HTML report
def setup_logging():
    log_stream = StringIO()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=log_stream)
    return log_stream

# Generate and save the HTML report
def generate_html_report(load_times, database_summary, logs):
    load_times_df = pd.DataFrame(load_times, columns=['Table Name', 'Load Time (Seconds)'])
    database_summary_df = pd.DataFrame(database_summary, columns=['Entity', 'Node Count', 'Relationship Count'])

    load_times_html = load_times_df.to_html(index=False)
    database_summary_html = database_summary_df.to_html(index=False)

    html_report = f"""
    <html>
    <head>
        <title>Database Report</title>
        <style>table, th, td {{border: 1px solid black; border-collapse: collapse;}}</style>
    </head>
    <body>
        <h1>KuzuDB Report</h1>
        <h2>Log Messages</h2>
        <pre>{logs.getvalue()}</pre>
        <h2>Load Times</h2>
        {load_times_html}
        <h2>Database Summary</h2>
        {database_summary_html}
    </body>
    </html>
    """

    with open('database_report.html', 'w') as f:
        f.write(html_report)

# Ensure all specified directories exist
def ensure_directories_exist(directories):
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# Import data into a table and measures the time taken
def import_table_data(conn, copy_statement, table_name):
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

# Formats the duration from seconds to minutes and seconds for readability
def format_duration(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{int(minutes)}m {int(seconds)}s"

# Creates a CREATE NODE TABLE statement from a Parquet file
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

# Creates a CREATE REL TABLE statement from a Parquet file
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

# Execute a query against KuzuDB and display results using PrettyTable
def execute_query_and_display(conn, query):
    try:
        result = conn.execute(query)
        if result:
            table = PrettyTable()
            table.field_names = result[0].keys()
            for row in result:
                table.add_row(row.values())
            print(table)
        else:
            print("No results found.")
    except Exception as e:
        logging.error(f"Query execution failed. Error details: {e}")



# Add this function to your script
def save_data_for_dashboard(load_times, database_summary, logs):
    data = {
        "load_times": load_times,
        "database_summary": database_summary,
        "logs": logs.getvalue()  # Assuming logs is a StringIO object
    }
    with open('dashboard_data.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
def main():
    log_stream = setup_logging()

    TEST_DATA_PATH = os.getenv('TEST_DATA_PATH')
    kuzu_version = version("kuzu")
    DATABASE_NAME = f'test_kuzu_db_v{kuzu_version.replace(".", "_")}'
    DATABASE_DIR = os.path.join(TEST_DATA_PATH, DATABASE_NAME)

    DROP_TABLES = True

    COMPANY_PARQUET_PATH = os.path.join(TEST_DATA_PATH, 'companies_0.parquet')
    PERSON_PARQUET_PATH = os.path.join(TEST_DATA_PATH, 'persons_0.parquet')
    RELATIONSHIP_PARQUET_PATH = os.path.join(TEST_DATA_PATH, 'relationships_0.parquet')

    ensure_directories_exist([DATABASE_DIR])
    logging.info("Starting KuzuDB processing...")

    try:
        db = kuzu.Database(os.path.join(DATABASE_DIR))
        conn = kuzu.Connection(db)
        logging.info("KuzuDB connection initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize KuzuDB connection: {e}")
        sys.exit(1)

    if DROP_TABLES:
        for table_name in ["WorksAt", "Company", "Person"]:
            try:
                conn.execute(f"DROP TABLE {table_name}")
                logging.info(f"Table {table_name} dropped.")
            except Exception as e:
                if 'does not exist' in str(e).lower():
                    logging.debug(f"Table {table_name} does not exist. No need to drop.")
                else:
                    logging.error(f"Error dropping table {table_name}: {e}")

    create_statement_company = create_node_table_statement_from_parquet(COMPANY_PARQUET_PATH, "Company", "company_id")
    create_statement_person = create_node_table_statement_from_parquet(PERSON_PARQUET_PATH, "Person", "person_id")
    create_statement_relationship = create_rel_table_statement_from_parquet(RELATIONSHIP_PARQUET_PATH, "WorksAt")

    for statement in [create_statement_company, create_statement_person, create_statement_relationship]:
        try:
            conn.execute(statement)
            logging.info(f'Successfully created kuzu table: {statement.split()[3]}')
        except Exception as e:
            logging.error(f'Failed to execute statement. Error details: {e}')

    load_times = []
    table_names = ["Person", "Company", "WorksAt"]
    parquet_paths = {
        "Person": PERSON_PARQUET_PATH,
        "Company": COMPANY_PARQUET_PATH,
        "WorksAt": RELATIONSHIP_PARQUET_PATH
    }

    for table_name in table_names:
        duration = import_table_data(conn, f'COPY {table_name} FROM "{parquet_paths[table_name]}" (HEADER = true)', table_name)
        if duration is not None:
            load_times.append((table_name, duration))

    database_summary = []

    try:

        company_node_count = conn.execute(
            'MATCH (n:Company) RETURN COUNT(n) AS CompanyNodeCount;').get_next()[0]
        person_node_count = conn.execute(
            'MATCH (n:Person) RETURN COUNT(n) AS PersonNodeCount;').get_next()[0]
        WorksAt_rel_count = conn.execute(
            'MATCH ()-[r:WorksAt]-() RETURN COUNT(r) AS RelationshipCount;').get_next()[0]

        database_summary = [
            ["Company", format(company_node_count, ','), "-"],
            ["Person", format(person_node_count, ','), "-"],
            ["-", "-", format(WorksAt_rel_count, ',')]
        ]
    except Exception as e:
        logging.error(f"Error compiling database summary: {e}")

    # logs_html = log_stream
    # generate_html_report(load_times, database_summary, logs_html)
    save_data_for_dashboard(load_times, database_summary, log_stream)

    logging.info("Processing completed.")

    save_data_for_dashboard(load_times, database_summary, log_stream)

    # Create the dashboard after saving the data
    dashboard_creator = DashboardCreator()
    dashboard_creator.generate_dashboard()

    logging.info("Dashboard created successfully.")

if __name__ == "__main__":
    main()