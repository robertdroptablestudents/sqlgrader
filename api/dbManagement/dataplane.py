import docker, os, psycopg, mysql.connector, pyodbc
from urllib.parse import quote_plus

from .dbUtilities import get_connectionstring

def runSQLfile(db_type, container_port, sql_file):
    """
    Runs the SQL file on the grading container.
    :param grading_container: The grading container to run the SQL file on.
    :param sql_file: The SQL file to run.
    :return: no return
    """

    # Get the SQL file

    # Run the SQL
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


# compares 2 schemas and returns statistics on the differences
# returns full schemas as an object
def compareSchemas(db_type, admin_port, grading_port):
    rows_mismatched = 0
    rows_missing = []
    extra_rows = []
    primary_score = 0
    secondary_score = 0
    full_schema = {
        'admin_schema': {
            'tables': [],
            'indexes': [],
        },
        'grading_schema': {
            'tables': [],
            'indexes': [],
        }
    }
    tables_query_path = '../schemaComparison/' + db_type.lower() + '/tables.sql'
    indexes_query_path = '../schemaComparison/' + db_type.lower() + '/indexes.sql'

    match db_type.lower():
        case 'postgres':
            try:
                conn1 = psycopg.connect(get_connectionstring(db_type, admin_port, False), autocommit=True)
                conn2 = psycopg.connect(get_connectionstring(db_type, grading_port, False), autocommit=True)

                # open conn1 and conn2 cursors
                with conn1.cursor() as cur1, conn2.cursor() as cur2:
                    cur1.execute(open(tables_query_path,"r").read())
                    cur2.execute(open(tables_query_path,"r").read())

                    # get the tables
                    admin_results = cur1.fetchall()
                    student_results = cur2.fetchall()
                    full_schema['admin_schema']['tables'] = admin_results
                    full_schema['grading_schema']['tables'] = student_results

                    for admin_row in admin_results:
                        if admin_row not in student_results:
                            rows_mismatched += 1
                            rows_missing += [admin_row]
                    if len(student_results) > len(admin_results):
                        for student_row in student_results:
                            if student_row not in admin_results:
                                rows_mismatched += 1
                                extra_rows += [student_row]

                    if len(admin_results) == 0:
                        admin_length = 1
                    primary_score = 100 - ((rows_mismatched / admin_length) * 100)
                    if primary_score < 0:
                        primary_score = 0

                    # match the indexes
                    rows_mismatched = 0
                    cur1.execute(open(indexes_query_path,"r").read())
                    cur2.execute(open(indexes_query_path,"r").read())

                    admin_results = cur1.fetchall()
                    student_results = cur2.fetchall()
                    full_schema['admin_schema']['indexes'] = admin_results
                    full_schema['grading_schema']['indexes'] = student_results

                    for admin_row in admin_results:
                        if admin_row not in student_results:
                            rows_mismatched += 1
                            rows_missing += [admin_row]
                    if len(student_results) > len(admin_results):
                        for student_row in student_results:
                            if student_row not in admin_results:
                                rows_mismatched += 1
                                extra_rows += [student_row]

                    if len(admin_results) == 0:
                        admin_length = 1
                    secondary_score = 100 - ((rows_mismatched / admin_length) * 100)
                    if secondary_score < 0:
                        secondary_score = 0

            
                conn1.close()
                conn2.close()
            except (Exception, psycopg.DatabaseError) as error:
                print('Error connecting to database')
                print(error)

    return {
        'full_schema': full_schema,
        'primary_score': primary_score,
        'secondary_score': secondary_score,
        'rows_missing': rows_missing,
        'extra_rows': extra_rows
    }


def queryTupleComparison(admin_results, student_results):
    length_difference = 0
    rows_mismatched = 0
    rows_outoforder = 0
    rows_missing = []
    extra_rows = []
    specific_feedback = ""
    points_possible = 100
    points_earned = 0

    # compare the result set lengths
    if len(admin_results) != len(student_results):
        length_difference = abs(len(admin_results) - len(student_results))
        specific_feedback = "The number of rows returned by the query differs from the expected number of rows by " + length_difference + " row(s)."
    else:
        specific_feedback = "The number of rows returned by the query matches the expected number of rows."

    # compare the result set widths (number of columns)
    if len(admin_results[0]) != len(student_results[0]):
        specific_feedback += "\nThe number of columns returned by the query differs from the expected number of columns by " + str(abs(len(admin_results[0]) - len(student_results[0]))) + " column(s)."
        rows_mismatched = len(admin_results)
    else:
        # number of columns matches, compare the contents of each row
        specific_feedback += "\nThe number of columns returned by the query matches the expected number of columns."

        # look for a matching row from the admin_results in the student_results
        for i in range(0, len(admin_results)):
            if i < len(student_results) and admin_results[i] != student_results[i]:
                rows_outoforder += 1
            if admin_results[i] not in student_results:
                rows_mismatched += 1
                rows_missing += [admin_results[i]]
        # if everything wasn't matching so far, check for extra rows
        if length_difference > 0 or rows_mismatched > 0:
            for i in range(0, len(student_results)):
                if student_results[i] not in admin_results:
                    rows_mismatched += 1
                    extra_rows += [student_results[i]]


    # for each row in the admin_results, convert to points possible scale and reduce by mismatched rows
    if len(admin_results) == 0:
        admin_length = 1
    else:
        admin_length = len(admin_results)*2
    points_earned = points_possible - ( ( points_possible / admin_length ) * (rows_mismatched + rows_outoforder) )
    if points_earned < 0:
        points_earned = 0

    # return length_difference, rows_mismatched as an object
    return { 'length_difference': length_difference, 'rows_mismatched': rows_mismatched, 'rows_outoforder': rows_outoforder, 'rows_missing': rows_missing, 'extra_rows': extra_rows, 'points_possible': points_possible, 'points_earned': points_earned, 'specific_feedback': specific_feedback }


# compares 2 queries and returns statistics on the differences
def compareQuery(db_type, admin_port, grading_port, adminsql, studentsql):
    return_content = {}
    match db_type.lower():
        case 'postgres':
            try:
                conn1 = psycopg.connect(get_connectionstring(db_type, admin_port, False), autocommit=True)
                conn2 = psycopg.connect(get_connectionstring(db_type, grading_port, False), autocommit=True)

                # open conn1 and conn2 cursors
                with conn1.cursor() as cur1, conn2.cursor() as cur2:
                    cur1.execute(open(adminsql,"r").read())
                    cur2.execute(open(studentsql,"r").read())

                    # get the results
                    admin_results = cur1.fetchall()
                    student_results = cur2.fetchall()

                    return_content = queryTupleComparison(admin_results, student_results)

                conn1.close()
                conn2.close()
            except (Exception, psycopg.DatabaseError) as error:
                print('Error running queries')
                print(error)

        case 'mysql':
            try:
                conn1 = mysql.connector.connect(**get_connectionstring(db_type, admin_port, False))
                conn2 = mysql.connector.connect(**get_connectionstring(db_type, grading_port, False))

                with conn1.cursor() as cur1, conn2.cursor() as cur2:
                    cur1.execute(open(adminsql,"r").read())
                    cur2.execute(open(studentsql,"r").read())

                    admin_results = cur1.fetchall()
                    student_results = cur2.fetchall()

                    return_content = queryTupleComparison(admin_results, student_results)
                    
                conn1.close()
                conn2.close()
            except Exception as e:
                print('Error running queries')
                print(e)

        case 'mssql':
            try:
                conn1 = pyodbc.connect(get_connectionstring(db_type, admin_port, False))
                conn2 = pyodbc.connect(get_connectionstring(db_type, grading_port, False))

                with conn1.cursor() as cur1, conn2.cursor() as cur2:
                    cur1.execute(open(adminsql,"r").read())
                    cur2.execute(open(studentsql,"r").read())

                    admin_results = cur1.fetchall()
                    student_results = cur2.fetchall()

                    return_content = queryTupleComparison(admin_results, student_results)

                conn1.close()
                conn2.close()
            except Exception as e:
                print('Error running queries')
                print(e)

    # return object
    # { 'length_difference': length_difference, 'rows_mismatched': rows_mismatched, 'rows_outoforder': rows_outoforder, 'rows_missing': rows_missing, 'extra_rows': extra_rows, 'points_possible': points_possible, 'points_earned': points_earned, 'specific_feedback': specific_feedback }
    return return_content