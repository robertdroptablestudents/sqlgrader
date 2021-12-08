import psycopg, mysql.connector, pyodbc, os

from .dbUtilities import get_connectionstring
from ..grading import gradingUtilities

# universal query execution
# does not return results
def runSQLcommand(db_type, container_port, sql_command):
    # Run the SQL
    match db_type.lower():
        case 'postgres':
            try:
                conn = psycopg.connect(get_connectionstring(db_type, container_port, False), autocommit=True)
                with conn.cursor() as cur:
                    cur.execute(sql_command)
                    conn.commit()
                conn.close()
            except (Exception, psycopg.DatabaseError) as error:
                print('Error running script')
                print(error)

        case 'mysql':
            try:
                conn = mysql.connector.connect(**get_connectionstring(db_type, container_port, False))
                with conn.cursor() as cur:
                    cur.execute(sql_command)
                conn.close()
            except Exception as e:
                print('Error creating database')
                print(e)

        case 'mssql':
            try:
                conn = pyodbc.connect(get_connectionstring(db_type, container_port, False))
                with conn.cursor() as cur:
                    cur.execute(sql_command)
                conn.close()
            except Exception as e:
                print('Error creating database')
                print(e)


# query execution wrapper for file input
def runSQLfile(db_type, container_port, sql_file):
    # runSQLcommand(db_type, container_port, open(sql_file,"r").read())
    print('running sql file'+sql_file)
    match db_type.lower():
        case 'postgres':
            try:
                conn = psycopg.connect(get_connectionstring(db_type, container_port, False), autocommit=True)
                with conn.cursor() as cur:
                    cur.execute(open(sql_file,"r").read())
                    conn.commit()
                conn.close()
            except (Exception, psycopg.DatabaseError) as error:
                print('Error running script')
                print(error)

        case 'mysql':
            try:
                conn = mysql.connector.connect(**get_connectionstring(db_type, container_port, False))
                with conn.cursor() as cur:
                    cur.execute(open(sql_file,"r").read())
                conn.close()
            except Exception as e:
                print('Error creating database')
                print(e)

        case 'mssql':
            try:
                conn = pyodbc.connect(get_connectionstring(db_type, container_port, False))
                with conn.cursor() as cur:
                    cur.execute(open(sql_file,"r").read())
                conn.close()
            except Exception as e:
                print('Error creating database')
                print(e)



# universal query execution
# returns results
def runSQLFileReturn(db_type, container_port, sql_file):
    """
    Runs the SQL file on the grading container.
    :param grading_container: The grading container to run the SQL file on.
    :param sql_file: The SQL file to run.
    :return: result set
    """

    # Get the SQL file
    print("Running SQL file: " + sql_file)
    # Run the SQL
    match db_type.lower():
        case 'postgres':
            try:
                conn = psycopg.connect(get_connectionstring(db_type, container_port, False), autocommit=True)
                with conn.cursor() as cur:
                    cur.execute(open(sql_file,"r").read())
                    results = cur.fetchall()
                    conn.commit()
                conn.close()
            except (Exception, psycopg.DatabaseError) as error:
                print('Error running script')
                print(error)

        case 'mysql':
            try:
                conn = mysql.connector.connect(**get_connectionstring(db_type, container_port, False))
                with conn.cursor() as cur:
                    cur.execute(open(sql_file,"r").read())
                    results = cur.fetchall()
                conn.close()
            except Exception as e:
                print('Error running script')
                print(e)

        case 'mssql':
            try:
                conn = pyodbc.connect(get_connectionstring(db_type, container_port, False))
                with conn.cursor() as cur:
                    cur.execute(open(sql_file,"r").read())
                    results = cur.fetchall()
                conn.close()
            except Exception as e:
                print('Error running script')
                print(e)

    return results

# get foreign key constraints
def getForeignKeys(db_type, which_port):
    fk_query_path = 'schemaComparison/' + db_type.lower() + '/foreignkeys.sql'
    fk_results = runSQLFileReturn(db_type, which_port, fk_query_path)
    return fk_results

# gets table schema objects
def getSchemaObjects(db_type, which_port):
    schema_query_path = 'schemaComparison/' + db_type.lower() + '/tables.sql'
    print('getting schema objects')
    schema_objects = runSQLFileReturn(db_type, which_port, schema_query_path)
    return schema_objects


# compares 2 schemas and returns statistics on the differences
def compareSchemas(db_type, admin_port, grading_port):
    return_content = {}
    admin_results = getSchemaObjects(db_type, admin_port)
    student_results = getSchemaObjects(db_type, grading_port)

    return_content = gradingUtilities.schemaObjectComparison(admin_results, student_results)

    # return object
    #  {
    #     'full_schema': full_schema,
    #     'primary_score': primary_score,
    #     'secondary_score': secondary_score,
    #     'rows_missing': rows_missing,
    #     'extra_rows': extra_rows
    # }
    return return_content



# compares 2 queries and returns statistics on the differences
def compareQuery(db_type, admin_port, grading_port, adminsql, studentsql):
    return_content = {}

    admin_results = runSQLFileReturn(db_type, admin_port, adminsql)
    student_results = runSQLFileReturn(db_type, grading_port, studentsql)
    
    return_content = gradingUtilities.queryTupleComparison(admin_results, student_results)

    # return object
    # { 'length_difference': length_difference, 'rows_mismatched': rows_mismatched, 'rows_outoforder': rows_outoforder, 'rows_missing': rows_missing, 'extra_rows': extra_rows, 'points_possible': points_possible, 'points_earned': points_earned, 'specific_feedback': specific_feedback }
    return return_content