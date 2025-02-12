import sqlite3
import pandas as pd
import os
import json
import re


class CSVtoSQLite:
    """
    db_path = "./databases"  # Change this to your desired directory
    db_name = "example.db"
    csv_file = "data1.csv"
    table_name = "custom_table"

    db_handler = CSVtoSQLite(db_path, db_name)
    db_handler.create_table_from_csv(csv_file, table_name)
    db_handler.close_connection()
    """
    def __init__(self, db_path, db_name):
        """Initialize the database with a given name and save it in the specified path."""
        self.db_path = db_path
        self.db_name = db_name
        self.full_db_path = os.path.join(self.db_path, self.db_name)

        # Ensure directory exists
        os.makedirs(self.db_path, exist_ok=True)

        self.conn = sqlite3.connect(self.full_db_path)
        self.cursor = self.conn.cursor()

    def create_table_from_csv(self, csv_file, table_name):
        """Create a table and insert data from a CSV file."""
        try:
            if not os.path.exists(csv_file):
                raise FileNotFoundError(f"File '{csv_file}' not found.")
            
            df = pd.read_csv(csv_file)
            if df.empty:
                raise ValueError(f"CSV file '{csv_file}' is empty.")
            
            df.to_sql(table_name, self.conn, if_exists='replace', index=False)
            print(f"Table '{table_name}' created in database '{self.full_db_path}' from '{csv_file}'.")
        
        except FileNotFoundError as fnf_error:
            print(fnf_error)
        except ValueError as val_error:
            print(val_error)
        except Exception as e:
            print(f"An error occurred while processing '{csv_file}': {e}")

    def close_connection(self):
        """Close the database connection."""
        self.conn.close()
        print(f"Database '{self.full_db_path}' connection closed.")



def read_table_from_db(db_name, table_name):
    """Read data from a specified table in the SQLite database.
    # Example usage:
    db_name = "example.db"  # Use the correct path if saved in a different directory
    table_name = "custom_table"

    df = read_table_from_db(db_name, table_name)
    print(df)
    """
    try:
        conn = sqlite3.connect(db_name)
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error reading table '{table_name}' from '{db_name}': {e}")







def get_database_structure(db_path: str) -> str:
    """
    Retrieves the database structure (tables and columns with data types) from an SQLite database.
    
    Args:
    db_path (str): The path to the SQLite database file.

    Returns:
    str: JSON string representing the database structure, including table names and column names with their data types.

    # Example usage:
    # db_path = 'path_to_your_database.db'
    # try:
    #     db_structure = get_database_structure(db_path)
    #     print(db_structure)
    # except Exception as e:
    #     print(str(e))

    """
    
    # Validate the database path
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file at '{db_path}' does not exist.")
    
    if not db_path.lower().endswith('.db'):
        raise ValueError(f"The provided file '{db_path}' is not a valid SQLite database.")
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch the list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            raise ValueError("No tables found in the database.")

        # Prepare the structure information
        database_info = {"database": db_path, "tables": []}

        # Loop through each table to get column names and data types
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()

            if not columns:
                raise ValueError(f"Could not retrieve columns for table '{table_name}'.")

            table_info = {
                "table": table_name,
                "columns": [{"name": col[1], "datatype": col[2]} for col in columns]
            }
            
            database_info["tables"].append(table_info)

        # Convert the structure information to JSON format
        return json.dumps(database_info, indent=4)

    except sqlite3.Error as e:
        raise RuntimeError(f"An error occurred while accessing the database: {e}")
    
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()


def extract_sql_query(text):
    """
    Extracts an SQL query from a given text input.

    Parameters:
        text (str): The input text containing an SQL query.

    Returns:
        str: Extracted SQL query or None if not found.
    """
    # Regular expression to match SQL queries
    sql_pattern = re.compile(r"(SELECT\s.*?;)", re.IGNORECASE | re.DOTALL)

    # Search for the SQL query
    match = sql_pattern.search(text)
    
    if match:
        return match.group(1).strip()  # Return the matched SQL query
    
    return None  # Return None if no query found



def clean_response(response_str):
    # Remove the surrounding triple backticks and 'json' keyword
    response_str = response_str.strip('"').strip('"')
    response_str = response_str.strip("'").strip("'")
    return response_str


def is_sql_related(user_input: str) -> bool:
    """
    Check if the user input is related to SQL queries.
    """
    sql_keywords = ["select", "from", "where", "join", "group by", "order by", "insert", "update", "delete"]
    return any(keyword in user_input.lower() for keyword in sql_keywords)


def check_tables_in_query(response_query, database_name):
    """
    Checks if all tables referenced in a SQL query exist in the specified SQLite database.
    Args:
        response_query (str): The SQL query to check for table references.
        database_name (str): The name of the SQLite database file.
    Returns:
        bool: True if all tables in the query exist in the database, False otherwise.
    Example:
        response_query = "SELECT * FROM users JOIN orders ON users.id = orders.user_id"
        database_name = "example.db"
        result = check_tables_in_query(response_query, database_name)
        if result:
            print("All tables exist in the database.")
        else:
            print("Some tables do not exist in the database.")
    """
    # Connect to the database
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # Extract table names from the query (basic implementation)
    # This is a simple approach and may need to be enhanced for complex queries
    tables_in_query = set()
    words = response_query.split()
    for word in words:
        if word.lower() in ["from", "join", "into", "update"]:
            # The next word is likely a table name
            table_name = words[words.index(word) + 1].strip(";").strip(",")
            tables_in_query.add(table_name)

    # Get all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables_in_db = {row[0] for row in cursor.fetchall()}

    # Check if all tables in the query exist in the database
    for table in tables_in_query:
        if table not in tables_in_db:
            # print(f"Table '{table}' does not exist in the database.")
            conn.close()
            return False

    conn.close()
    return True


import json

def extract_list_from_string(input_string):
    """
    Extracts a list from a given input string that contains JSON data.

    Args:
        input_string (str): The input string containing JSON data.

    Returns:
        list: The extracted list from the JSON data, or ['None'] if an error occurs.
    """
    try:
        # Extract the JSON part from the string
        json_part = input_string.strip("```json\n").strip("\n```")
        
        # Replace single quotes with double quotes to make it valid JSON
        json_part = json_part.replace("'", '"')
        
        # Parse the JSON part to get the list
        result_list = json.loads(json_part)
        
        # Ensure the result is a list
        if not isinstance(result_list, list):
            return ['None']
        
        return result_list
    except Exception:
        return ['None']


