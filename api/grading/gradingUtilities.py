
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
        rows_outoforder = len(admin_results)
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

def schemaObjectComparison(admin_objects, student_objects):
    length_difference = 0
    rows_mismatched = 0
    rows_missing = []
    extra_rows = []
    specific_feedback = ""
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

    # sanitize the schema objects
    for i in range(0, len(admin_objects)):
        # set 1st, 2nd, and 4th columns to lowercase
        admin_objects[i][0] = admin_objects[i][0].lower() # schema name
        admin_objects[i][1] = admin_objects[i][1].lower() # table name
        admin_objects[i][3] = admin_objects[i][3].lower() # column name
    for i in range(0, len(student_objects)):
        # set 1st, 2nd, and 4th columns to lowercase
        student_objects[i][0] = student_objects[i][0].lower()
        student_objects[i][1] = student_objects[i][1].lower()
        student_objects[i][3] = student_objects[i][3].lower()

    # compare the number of schema objects
    if len(admin_objects) != len(student_objects):
        length_difference = abs(len(admin_objects) - len(student_objects))
        specific_feedback = "The number of schema objects differs from the expected number of schema objects by " + length_difference + " schema object(s)."
    else:
        specific_feedback = "The number of schema objects matches the expected number of schema objects."



    # full_schema['admin_schema']['tables'] = admin_results
    # full_schema['grading_schema']['tables'] = student_results
 
    # for admin_row in admin_results:
    #     if admin_row not in student_results:
    #         rows_mismatched += 1
    #         rows_missing += [admin_row]
    # if len(student_results) > len(admin_results):
    #     for student_row in student_results:
    #         if student_row not in admin_results:
    #             rows_mismatched += 1
    #             extra_rows += [student_row]

    # if len(admin_results) == 0:
    #     admin_length = 1
    # primary_score = 100 - ((rows_mismatched / admin_length) * 100)
    # if primary_score < 0:
    #     primary_score = 0


    # # match the indexes
    # rows_mismatched = 0
    # cur1.execute(open(indexes_query_path,"r").read())
    # cur2.execute(open(indexes_query_path,"r").read())

    # admin_results = cur1.fetchall()
    # student_results = cur2.fetchall()
    # full_schema['admin_schema']['indexes'] = admin_results
    # full_schema['grading_schema']['indexes'] = student_results

    # for admin_row in admin_results:
    #     if admin_row not in student_results:
    #         rows_mismatched += 1
    #         rows_missing += [admin_row]
    # if len(student_results) > len(admin_results):
    #     for student_row in student_results:
    #         if student_row not in admin_results:
    #             rows_mismatched += 1
    #             extra_rows += [student_row]

    # if len(admin_results) == 0:
    #     admin_length = 1
    # secondary_score = 100 - ((rows_mismatched / admin_length) * 100)
    # if secondary_score < 0:
    #     secondary_score = 0

    return {
        'full_schema': full_schema,
        'primary_score': primary_score,
        'secondary_score': secondary_score,
        'rows_missing': rows_missing,
        'extra_rows': extra_rows,
        'specific_feedback': specific_feedback
    }