from flask import Blueprint, request, jsonify, session
import snowflake.connector
from snowflake.connector import errors
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pyodbc
import re

snowflake_bp = Blueprint('snowflake_bp', __name__)


def test_snowflake_connection(account, user, password, warehouse, database, schema):
    """
    Test connection to Snowflake using provided credentials.
    """
    try:
        connection = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema,
        )
        cursor = connection.cursor()
        cursor.execute("SELECT CURRENT_VERSION();")
        version = cursor.fetchone()
        return {"status": "success", "version": version[0]}
    except errors.DatabaseError as e:
        return {"status": "error", "message": f"Database error occurred: {e}"}
    except errors.InterfaceError as e:
        return {"status": "error", "message": f"Interface error occurred: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {e}"}
    finally:
        if 'connection' in locals() and connection.is_closed is False:
            connection.close()


def get_databases_and_schemas(account, user, password, warehouse):
    """
    Get a list of all databases and their schemas from Snowflake.
    """
    try:
        connection = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse
        )
        cursor = connection.cursor()

        cursor.execute("SHOW DATABASES;")
        databases = cursor.fetchall()

        result = {}

        for db in databases:
            database_name = db[1]
            cursor.execute(f"SHOW SCHEMAS IN DATABASE {database_name};")
            schemas = cursor.fetchall()
            schema_names = [schema[1] for schema in schemas]
            result[database_name] = schema_names

        return {"status": "success", "data": result}

    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {e}"}
    finally:
        if 'connection' in locals() and connection.is_closed is False:
            connection.close()


def get_tables_and_views_in_schema(account, user, password, warehouse, database, schema):
    """
    Get a list of all tables and views in the given schema of the selected database.
    """
    try:
        connection = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema
        )
        cursor = connection.cursor()

        # Get list of tables in the selected schema
        cursor.execute(f"SHOW TABLES IN SCHEMA {database}.{schema};")
        tables = cursor.fetchall()

        # Get list of views in the selected schema
        cursor.execute(f"SHOW VIEWS IN SCHEMA {database}.{schema};")
        views = cursor.fetchall()

        # Separate the names of tables and views
        table_names = [table[1] for table in tables]
        view_names = [view[1] for view in views]

        return {"status": "success", "tables": table_names, "views": view_names, "database": database, "schema": schema}

    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {e}"}
    finally:
        if 'connection' in locals() and connection.is_closed is False:
            connection.close()





def send_email(user_email, username, password,account):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    try:
        sender_email = "skinthiyaz9581@gmail.com"  # Your Gmail address
        sender_password = "rivr augu dwbq iwbh"  # App Password generated from Google
        receiver_email = user_email
        

        # Email content
        subject = "Snowflake Account Created"
        body = f"""
        Hello {username},

        Your Snowflake account has been successfully created. Please log in using the following credentials:

        Username: {username}
        Password: {password}
        account_url = f"https://{account}.snowflakecomputing.com"

        You will be prompted to change your password after logging in for the first time.

        Regards,
        Snowflake Admin Team
        """

        # Create email
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Connect to Gmail's SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Email sent successfully")

    except Exception as e:
        print(f"Failed to send email: {e}")


def get_snowflake_connection(account, user, password):
    try:
        conn = snowflake.connector.connect(
            account=account,
            user=user,
            password=password
        )
        return conn
    except Exception as e:
        return str(e)

@snowflake_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    account = data.get("account")
    username = data.get("username")
    password = data.get("password")

    try:
        # Test connection to Snowflake
        conn = snowflake.connector.connect(
            account=account,
            user=username,
            password=password
        )
        conn.cursor().execute("SELECT CURRENT_USER();")

        # Store credentials in session
        session["account"] = account
        session["username"] = username
        session["password"] = password

        return jsonify({"message": "Login successful!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 401


@snowflake_bp.route("/get_User_role", methods=["GET"])
def get_user_role():
    # Check if session variables exist
    if "account" not in session or "username" not in session or "password" not in session:
        return jsonify({"error": "User not logged in! Please log in again."}), 401

    try:
        conn = snowflake.connector.connect(
            account=session["account"],
            user=session["username"],
            password=session["password"]
        )
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_ROLE();")
        role = cursor.fetchone()[0]
        return jsonify({"role": role})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@snowflake_bp.route("/create_role", methods=["POST"])
def create_role():
    data = request.json

    # Retrieve Snowflake credentials from the request
    account = data.get("account")
    username = data.get("username")
    password = data.get("password")

    if not account or not username or not password:
        return jsonify({"error": "User credentials missing! Please log in again."}), 401

    role_name = data.get("role_name")
    privileges = data.get("privileges", [])
    granted_to_role = data.get("granted_to_role")

    if not role_name:
        return jsonify({"error": "Role name is required."}), 400

    if not privileges:
        return jsonify({"error": "At least one privilege is required."}), 400

    try:
        # Connect to Snowflake with the provided credentials
        conn = snowflake.connector.connect(
            account=account,
            user=username,
            password=password
        )
        cursor = conn.cursor()

        # Create the new role
        create_role_query = f"CREATE ROLE {role_name}"
        print(f"Executing: {create_role_query}")  # Debugging log
        cursor.execute(create_role_query)

        # Grant the selected privileges to the role
        for privilege in privileges:
            if privilege:  # Ensure the privilege is valid (non-empty)
                grant_privilege_query = f"GRANT {privilege} TO ROLE {role_name}"
                print(f"Executing: {grant_privilege_query}")  # Debugging log
                cursor.execute(grant_privilege_query)

        # If a parent role is selected, grant the new role to the parent role
        if granted_to_role:
            grant_role_query = f"GRANT ROLE {role_name} TO ROLE {granted_to_role}"
            print(f"Executing: {grant_role_query}")  # Debugging log
            cursor.execute(grant_role_query)

        return jsonify({"message": f"Role '{role_name}' created and privileges granted successfully!"})

    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging log
        return jsonify({"error": str(e)}), 500


@snowflake_bp.route("/get_privileges", methods=["POST"])
def get_privileges():
    data = request.get_json()
    account = data.get("account")
    username = data.get("username")
    password = data.get("password")

    if not account or not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    try:
        # Connect to Snowflake
        conn = snowflake.connector.connect(
            account=account,
            user=username,
            password=password
        )
        cursor = conn.cursor()

        # Execute a valid query to fetch privileges
        cursor.execute("SHOW GRANTS TO USER {}".format(username))
        privileges = [row[0] for row in cursor.fetchall()]

        # Return the privileges
        return jsonify({"privileges": privileges})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@snowflake_bp.route("/get_roles", methods=["POST"])
def get_roles():
    data = request.json
    account = data.get("account")
    username = data.get("username")
    password = data.get("password")

    if not account or not username or not password:
        return jsonify({"error": "Missing required connection parameters"}), 400

    try:
        conn = snowflake.connector.connect(
            account=account,
            user=username,
            password=password
        )
        cursor = conn.cursor()
        cursor.execute("SHOW ROLES")
        roles = [row[1] for row in cursor.fetchall()]
        return jsonify({"roles": roles})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@snowflake_bp.route("/create_user", methods=["POST"])
def create_user():
    data = request.json
    account = data.get("account")
    username = data.get("username")
    password = data.get("password")
    user_name = data.get("user_name")
    user_password = data.get("user_password")
    role_name = data.get("role_name")
    email = data.get("email")

    if not account or not username or not password:
        return jsonify({"error": "User credentials missing!"}), 401

    try:
        # Connect to Snowflake with the provided credentials
        conn = snowflake.connector.connect(
            account=account,
            user=username,
            password=password
        )
        cursor = conn.cursor()

        # Create the user in Snowflake
        cursor.execute(f"""
            CREATE OR REPLACE USER {user_name}
            PASSWORD = '{user_password}'
            DEFAULT_ROLE = {role_name}
            MUST_CHANGE_PASSWORD = TRUE
            EMAIL = '{email}'
        """)
        # Send the email to the newly created user
        send_email(email, user_name, user_password,account)

        return jsonify({"message": f"User '{user_name}' created successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500





@snowflake_bp.route("/test_sf_vw_connection", methods=["POST"])
def test_connection():
    """
    Test connection to Snowflake.
    """
    data = request.json
    account = data.get("account")
    user = data.get("user")
    password = data.get("password")
    warehouse = data.get("warehouse")
    database = data.get("database")
    schema = data.get("schema")

    if not all([account, user, password, warehouse, database, schema]):
        return jsonify({"status": "error", "message": "Missing required connection parameters"}), 400

    result = test_snowflake_connection(account, user, password, warehouse, database, schema)
    return jsonify(result)

@snowflake_bp.route("/get-databases-and-schemas", methods=["POST"])
def get_databases():
    """
    Fetch databases and schemas from Snowflake.
    """
    data = request.json
    account = data.get("account")
    user = data.get("user")
    password = data.get("password")
    warehouse = data.get("warehouse")

    if not all([account, user, password, warehouse]):
        return jsonify({"status": "error", "message": "Missing required connection parameters"}), 400

    result = get_databases_and_schemas(account, user, password, warehouse)
    return jsonify(result)

@snowflake_bp.route("/get-tables-and-views-in-schema", methods=["POST"])
def get_tables_and_views():
    """
    Fetch tables and views from a specific Snowflake schema.
    """
    data = request.json
    account = data.get("account")
    user = data.get("user")
    password = data.get("password")
    warehouse = data.get("warehouse")
    database = data.get("database")
    schema = data.get("schema")

    if not all([account, user, password, warehouse, database, schema]):
        return jsonify({"status": "error", "message": "Missing required connection parameters"}), 400

    result = get_tables_and_views_in_schema(account, user, password, warehouse, database, schema)
    return jsonify(result)

@snowflake_bp.route("/test-ssms-connection", methods=["POST"])
def test_ssms_connection():
    """
    Test connection to SQL Server (SSMS).
    """
    data = request.json
    server = data.get("server")
    database = data.get("database")
    username = data.get("username")
    password = data.get("password")

    if not all([server, database, username, password]):
        return jsonify({"status": "error", "message": "Missing required connection parameters"}), 400

    try:
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password}'
        )
        conn.close()
        return jsonify({"status": "success", "message": "Connection successful!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@snowflake_bp.route("/get-columns", methods=["POST"])
def get_columns():
    data = request.json
    account = data.get("account")
    user = data.get("user")
    password = data.get("password")
    warehouse = data.get("warehouse")
    database = data.get("database")
    schema = data.get("schema")
    object_name = data.get("object_name")

    if not all([account, user, password, warehouse, database, schema, object_name]):
        return jsonify({"status": "error", "message": "Missing required parameters"}), 400

    try:
        connection = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema
        )
        cursor = connection.cursor()
        cursor.execute(f"SHOW COLUMNS IN {database}.{schema}.{object_name};")
        rows = cursor.fetchall()

        # Log the first row to see the structure (optional for debugging)
        # if rows:
        #     print("DEBUG row[0]:", rows[0])

        columns = []
        for row in rows:
            # row[4] = actual column name, row[5] = data type
            col_name = row[2]
            col_type = row[3]
            columns.append({"name": col_name, "type": col_type})

        return jsonify({"status": "success", "columns": columns})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if 'connection' in locals() and connection.is_closed is False:
            connection.close()



@snowflake_bp.route("/create-views-in-ssms", methods=["POST"])
def create_views_in_ssms():
    """
    Create views in SQL Server (SSMS) using data from Snowflake.
    """
    data = request.json
    server = data.get("server")
    database = data.get("database")
    username = data.get("username")
    password = data.get("password")
    linked_server = data.get("linkedServer")
    selected_views = data.get("selectedViews", [])
    selected_tables = data.get("selectedTables", [])
    edited_views = data.get("editedViews", {})
    edited_tables = data.get("editedTables", {})
    source_database = data.get("sourceDatabase")
    source_schema = data.get("sourceSchema")

    if not selected_views and not selected_tables:
        return jsonify({"status": "error", "message": "No views or tables selected. Please select at least one."}), 400

    if not all([server, database, username, password, source_database, source_schema]):
        return jsonify({"status": "error", "message": "Missing required connection parameters"}), 400

    try:
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password}'
        )
        cursor = conn.cursor()

        def quote_identifier(identifier):
            return f'"{identifier}"' if ' ' in identifier else identifier

        def generate_view_or_table_query(object_name, edited_info=None):
            new_object_name = edited_info.get("newName") if edited_info and edited_info.get("newName") else object_name
            new_object_name = quote_identifier(new_object_name)

            column_metadata_query = f"""
                SELECT COLUMN_NAME, DATA_TYPE
                FROM OPENQUERY([{linked_server}],
                    'SELECT CAST(COLUMN_NAME AS VARCHAR(255)) AS COLUMN_NAME, CAST(DATA_TYPE AS VARCHAR(255)) AS DATA_TYPE
                    FROM {source_database}.INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = ''{source_schema}'' AND TABLE_NAME = ''{object_name}''')
            """
            cursor.execute(column_metadata_query)
            columns = cursor.fetchall()

            casting_columns = []
            outside_columns = []
            for column in columns:
                orig_col = column[0]
                data_type = column[1]
                orig_col_quoted = quote_identifier(orig_col)
                col_alias = quote_identifier(edited_info["columns"].get(orig_col, orig_col)) if edited_info else orig_col_quoted

                if data_type.upper() in ['VARCHAR', 'CHAR', 'TEXT']:
                    cast_str = f"CAST({orig_col_quoted} AS VARCHAR(4000)) AS {col_alias}"
                elif data_type.upper() in ['FLOAT', 'REAL', 'DOUBLE', 'NUMERIC', 'DECIMAL','NUMBER']:
                    cast_str = f"CAST({orig_col_quoted} AS FLOAT) AS {col_alias}"
                elif data_type.upper() in ['BIGINT']:
                    cast_str = f"CAST({orig_col_quoted} AS BIGINT) AS {col_alias}"
                elif data_type.upper() in ['INT', 'SMALLINT', 'TINYINT']:
                    cast_str = f"CAST({orig_col_quoted} AS INT) AS {col_alias}"
                elif data_type.upper() in ['BOOLEAN', 'BIT']:
                    cast_str = f"CAST({orig_col_quoted} AS BOOLEAN) AS {col_alias}"
                elif data_type.upper() in ['DATE']:
                    cast_str = f"CAST({orig_col_quoted} AS DATE) AS {col_alias}"
                elif data_type.upper() in ['TIME']:
                    cast_str = f"CAST({orig_col_quoted} AS TIME) AS {col_alias}"
                elif data_type.upper() in ['DATETIME', 'TIMESTAMP', 'TIMESTAMP_NTZ']:
                    cast_str = f"CAST({orig_col_quoted} AS TIMESTAMP) AS {col_alias}"
                elif data_type.upper() in ['BINARY', 'VARBINARY']:
                    cast_str = f"CAST({orig_col_quoted} AS VARBINARY(MAX)) AS {col_alias}"
                elif data_type.upper() in ['JSON']:
                    cast_str = f"CAST({orig_col_quoted} AS NVARCHAR(MAX)) AS {col_alias}"
                else:
                    cast_str = f"CAST({orig_col_quoted} AS NVARCHAR(255)) AS {col_alias}"

                casting_columns.append(cast_str)
                outside_columns.append(col_alias)

            casting_columns_str = ', '.join(casting_columns)
            outside_columns_str = ', '.join(outside_columns)
            return f"""
                CREATE OR ALTER VIEW dbo.{new_object_name} AS
                    SELECT {outside_columns_str}
                    FROM OPENQUERY([{linked_server}],
                        'SELECT {casting_columns_str} FROM {source_database}.{source_schema}.{object_name}'
                    );
            """

        for view in selected_views:
            edited_info = edited_views.get(view)
            try:
                query = generate_view_or_table_query(view, edited_info)
                cursor.execute(query)
            except pyodbc.Error as e:
                return jsonify({"status": "error", "message": f"Error creating view '{view}': {str(e)}"}), 400

        for table in selected_tables:
            edited_info = edited_tables.get(table)
            try:
                query = generate_view_or_table_query(table, edited_info)
                cursor.execute(query)
            except pyodbc.Error as e:
                return jsonify({"status": "error", "message": f"Error creating view for table '{table}': {str(e)}"}), 400

        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Views and tables created successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


    """
    Create views in SQL Server (SSMS) using data from Snowflake.
    """
    data = request.json
    server = data.get("server")
    database = data.get("database")
    username = data.get("username")
    password = data.get("password")
    linked_server = data.get("linkedServer")
    selected_views = data.get("selectedViews", [])
    selected_tables = data.get("selectedTables", [])
    source_database = data.get("sourceDatabase")
    source_schema = data.get("sourceSchema")

    if not selected_views and not selected_tables:
        return jsonify({"status": "error", "message": "No views or tables selected. Please select at least one."}), 400

    if not all([server, database, username, password, source_database, source_schema]):
        return jsonify({"status": "error", "message": "Missing required connection parameters"}), 400

    try:
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password}'
        )
        cursor = conn.cursor()

        # Helper function to generate SQL query for creating views or tables
        def generate_view_or_table_query(object_name):
            # Get column metadata from the Snowflake database using the linked server
            column_metadata_query = f"""
                SELECT COLUMN_NAME, DATA_TYPE
                FROM OPENQUERY([{linked_server}],
                    'SELECT CAST(COLUMN_NAME AS VARCHAR(255)) AS COLUMN_NAME, CAST(DATA_TYPE AS VARCHAR(255)) AS DATA_TYPE
                    FROM {source_database}.INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = ''{source_schema}'' AND TABLE_NAME = ''{object_name}''')
            """

            cursor.execute(column_metadata_query)
            columns = cursor.fetchall()

            # Initialize lists for columns to be used outside and inside OPENQUERY
            outside_columns = []
            casting_columns = []

            # Loop through columns to generate dynamic casting logic
            for column in columns:
                column_name, data_type = column

                # Add cases for various data types
                if data_type in ['VARCHAR', 'CHAR', 'TEXT']:
                    casting_columns.append(f"CAST({column_name} AS VARCHAR(255)) AS {column_name}")
                elif data_type in ['FLOAT', 'REAL', 'DOUBLE', 'NUMERIC', 'DECIMAL','NUMBER']:
                    casting_columns.append(f"CAST({column_name} AS FLOAT) AS {column_name}")
                elif data_type in ['BIGINT']:
                    casting_columns.append(f"CAST({column_name} AS BIGINT) AS {column_name}")
                elif data_type in ['INT', 'SMALLINT', 'TINYINT']:
                    casting_columns.append(f"CAST({column_name} AS INT) AS {column_name}")
                elif data_type in ['BOOLEAN', 'BIT']:
                    casting_columns.append(f"CAST({column_name} AS BOOLEAN) AS {column_name}")
                elif data_type in ['DATE']:
                    casting_columns.append(f"CAST({column_name} AS DATE) AS {column_name}")
                elif data_type in ['TIME']:
                    casting_columns.append(f"CAST({column_name} AS TIME) AS {column_name}")
                elif data_type in ['DATETIME', 'TIMESTAMP', 'TIMESTAMP_NTZ']:
                    casting_columns.append(f"CAST({column_name} AS TIMESTAMP) AS {column_name}")
                elif data_type in ['BINARY', 'VARBINARY']:
                    casting_columns.append(f"CAST({column_name} AS VARBINARY(MAX)) AS {column_name}")
                elif data_type in ['JSON']:
                    casting_columns.append(f"CAST({column_name} AS NVARCHAR(MAX)) AS {column_name}")
                else:
                    # Default case: If data type is not handled, apply a generic cast to VARCHAR
                    casting_columns.append(f"CAST({column_name} AS NVARCHAR(255)) AS {column_name}")

                # Add to outside columns for the final SELECT in the SSMS view
                outside_columns.append(column_name)

            # Join the columns to form the full SELECT clause
            casting_columns_str = ', '.join(casting_columns)
            outside_columns_str = ', '.join(outside_columns)

            # Generate the full query to create the view
            return f"""
                CREATE OR ALTER VIEW [dbo].[{object_name}] AS
                    SELECT {outside_columns_str}
                    FROM OPENQUERY([{linked_server}],
                        'SELECT {casting_columns_str} FROM {source_database}.{source_schema}.{object_name}'
                    );
            """

        # Loop through selected views to create views in SSMS
        for view in selected_views:
            try:
                query = generate_view_or_table_query(view)
                cursor.execute(query)
            except pyodbc.Error as e:
                return jsonify({"status": "error", "message": f"Error creating view '{view}': {str(e)}"}), 400

        # Loop through selected tables to create views in SSMS (same process as views)
        for table in selected_tables:
            try:
                query = generate_view_or_table_query(table)
                cursor.execute(query)
            except pyodbc.Error as e:
                return jsonify({"status": "error", "message": f"Error creating view for table '{table}': {str(e)}"}), 400

        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Views and tables created successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    






@snowflake_bp.route("/create-tables-in-ssms", methods=["POST"])
def create_tables_in_ssms():
    """
    Create tables in SQL Server (SSMS) and insert data from Snowflake.
    """
    data = request.json
    server = data.get("server")
    database = data.get("database")
    username = data.get("username")
    password = data.get("password")
    linked_server = data.get("linkedServer")
    selected_tables = data.get("selectedTables", [])
    source_database = data.get("sourceDatabase")
    source_schema = data.get("sourceSchema")

    if not selected_tables:
        return jsonify({"status": "error", "message": "No tables selected. Please select at least one."}), 400

    if not all([server, database, username, password, source_database, source_schema, linked_server]):
        return jsonify({"status": "error", "message": "Missing required connection parameters"}), 400

    try:
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password}'
        )
        cursor = conn.cursor()

        def quote_identifier(identifier):
            """Quote identifier to handle spaces or special characters."""
            return f'"{identifier}"' if ' ' in identifier else identifier

        def get_snowflake_column_metadata(table_name):
            """Fetch column metadata from Snowflake via linked server."""
            column_metadata_query = f"""
                SELECT COLUMN_NAME, DATA_TYPE
                FROM OPENQUERY([{linked_server}], 
                    'SELECT COLUMN_NAME, DATA_TYPE 
                    FROM {source_database}.INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = ''{source_schema}'' 
                    AND TABLE_NAME = ''{table_name}''')
            """
            cursor.execute(column_metadata_query)
            return cursor.fetchall()

        def snowflake_to_sqlserver_type(data_type):
            """Map Snowflake data types to SQL Server data types."""
            type_mapping = {
                'VARCHAR': 'NVARCHAR(4000)',
                'CHAR': 'CHAR(255)',
                'TEXT': 'NVARCHAR(MAX)',
                'FLOAT': 'FLOAT',
                'REAL': 'REAL',
                'DOUBLE': 'FLOAT',
                'NUMERIC': 'DECIMAL(18,4)',
                'DECIMAL': 'DECIMAL(18,4)',
                'NUMBER': 'DECIMAL(18,4)',
                'BIGINT': 'BIGINT',
                'INT': 'INT',
                'SMALLINT': 'SMALLINT',
                'TINYINT': 'TINYINT',
                'BOOLEAN': 'BIT',
                'BIT': 'BIT',
                'DATE': 'DATE',
                'TIME': 'TIME',
                'DATETIME': 'DATETIME',
                'TIMESTAMP': 'DATETIME',
                'TIMESTAMP_NTZ': 'DATETIME',
                'BINARY': 'VARBINARY(MAX)',
                'VARBINARY': 'VARBINARY(MAX)',
                'JSON': 'NVARCHAR(MAX)',
            }
            return type_mapping.get(data_type.upper(), 'NVARCHAR(255)')

        def generate_create_table_query(table_name, columns):
            """Generate CREATE TABLE SQL for SQL Server."""
            column_definitions = [
                f"{quote_identifier(col[0])} {snowflake_to_sqlserver_type(col[1])}"
                for col in columns
            ]
            columns_str = ",\n    ".join(column_definitions)
            return f"CREATE TABLE dbo.{table_name} (\n    {columns_str}\n);"

        def generate_insert_query(table_name, columns):
            """Generate INSERT INTO query to fetch data from Snowflake."""
            column_names = [quote_identifier(col[0]) for col in columns]
            column_list_str = ", ".join(column_names)
            return f"""
                INSERT INTO dbo.{table_name} ({column_list_str})
                SELECT {column_list_str}
                FROM OPENQUERY([{linked_server}], 
                    'SELECT {column_list_str} 
                    FROM {source_database}.{source_schema}.{table_name}');
            """

        for table in selected_tables:
            try:
                columns = get_snowflake_column_metadata(table)

                # 1. Drop table if exists
                cursor.execute(f"IF OBJECT_ID('dbo.{table}', 'U') IS NOT NULL DROP TABLE dbo.{table};")

                # 2. Create table
                create_table_query = generate_create_table_query(table, columns)
                cursor.execute(create_table_query)

                # 3. Insert data from Snowflake
                insert_query = generate_insert_query(table, columns)
                cursor.execute(insert_query)

            except pyodbc.Error as e:
                return jsonify({"status": "error", "message": f"Error processing table '{table}': {str(e)}"}), 400

        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Tables created and data inserted successfully!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    


@snowflake_bp.route('/get_views', methods=['POST'])
def get_views():
    try:
        data = request.json
        server = data.get("server")
        database = data.get("database")
        username = data.get("username")
        password = data.get("password")

        if not all([server, database, username, password]):
            return jsonify({"success": False, "message": "Missing credentials"}), 400

        connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS")
        views = [row[0] for row in cursor.fetchall()]

        conn.close()
        return jsonify({"success": True, "views": views})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500





@snowflake_bp.route('/alter_views', methods=['POST'])
def alter_views():
    try:
        data = request.json
        server = data.get("server")
        database = data.get("database")
        username = data.get("username")
        password = data.get("password")
        selected_views = data.get("views", [])
        environment = data.get("environment")  # e.g., "TST_UAT" or "TST_PROD"

        # Validate required parameters
        if not all([server, database, username, password, environment]):
            return jsonify({"success": False, "message": "Missing required parameters"}), 400
        if not selected_views:
            return jsonify({"success": False, "message": "No views selected"}), 400

        # Connect to SQL Server
        connection_string = (
            f'DRIVER={{SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password}'
        )
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        altered_views = []
        for view in selected_views:
            # Query the existing view definition using sys.sql_modules and sys.objects
            definition_query = """
                SELECT sm.definition
                FROM sys.sql_modules AS sm
                JOIN sys.objects AS o ON sm.object_id = o.object_id
                WHERE o.name = ? AND o.type = 'V'
            """
            cursor.execute(definition_query, view)
            row = cursor.fetchone()
            if not row:
                # If no definition found, skip this view
                continue

            original_definition = row[0]

            # Replace the environment part dynamically.
            # This regex assumes that the environment is in the format TST_XXXX (e.g., TST_DEV)
            updated_definition = re.sub(
                r'TST_[A-Z]+', 
                environment, 
                original_definition, 
                flags=re.IGNORECASE
            )

            # Change the beginning of the statement from CREATE VIEW to ALTER VIEW if needed.
            # (This assumes the view definition starts with "CREATE   VIEW ...")
            updated_definition = re.sub(
                r'CREATE\s+VIEW', 
                'ALTER VIEW', 
                updated_definition, 
                flags=re.IGNORECASE
            )

            # Execute the altered view definition
            cursor.execute(updated_definition)
            altered_views.append(view)

        conn.commit()
        conn.close()

        return jsonify({
            "success": True, 
            "message": f"Views altered successfully: {', '.join(altered_views)}"
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
