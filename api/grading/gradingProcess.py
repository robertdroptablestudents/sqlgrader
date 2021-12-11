import requests, json

from ..dbManagement import controlplane, dataplane, dbUtilities
from ..queryComparison import dataGen


ADMIN_PORT = 1437
SECONDARY_PORT = 1438


# SECTION
# functions calling back to django instance
APIURL = 'http://localhost:80/instructor/'

# call process to tally all environment instances for a query assignment item
def callUpdateStudentSubmissionQuery(apikey, assignment_item_id):
    payload = {'assignment_item_id': assignment_item_id}
    r = requests.post(APIURL + 'api_updatestudentsubmissionquery', data=json.dumps(payload), headers={'Authorization': 'Token ' + apikey, 'Content-Type': 'application/json'})
    return r.status_code

# update the student submission with grade and status for an environment instance
def callUpdateStudentSubmissionItemQuery(apikey, student_submission_item_id, environment_instance_id, points_possible, points_earned, grading_log):
    payload = {'student_submission_item_id': student_submission_item_id, 'environment_instance_id': environment_instance_id, 'points_possible': points_possible, 'points_earned': points_earned, 'grading_log': grading_log}
    r = requests.post(APIURL + 'api_updatestudentsubmissionitem', data=json.dumps(payload), headers={'Authorization': 'Token ' + apikey, 'Content-Type': 'application/json'})
    return r.status_code

# update the student submission item with the grading results, StudentSubmissionItem only
def callUpdateStudentSubmissionItemSchema(apikey, student_submission_item_id, score_primary, score_secondary, grading_log):
    payload = {'student_submission_item_id': student_submission_item_id, 'score_primary': score_primary, 'score_secondary': score_secondary, 'grading_log': grading_log}
    r = requests.post(APIURL + 'api_updatestudentsubmissionitem', data=json.dumps(payload), headers={'Authorization': 'Token ' + apikey, 'Content-Type': 'application/json'})
    return r.status_code

# update the grading log with status and message
def callUpdateGradingLog(apikey, grading_process_id, new_status, log_message):
    payload = {'grading_process_id': grading_process_id, 'status_message': new_status, 'log_update': log_message }
    r = requests.post(APIURL + 'api_updategradingstatus', data=json.dumps(payload), headers={'Authorization': 'Token ' + apikey, 'Content-Type': 'application/json'})
    return r.status_code

# update the environment instance with completed datagen
def callUpdateEnvironmentInstance(apikey, environment_instance_id, datagen_status):
    if datagen_status == 'completed':
        has_datagen = True
    else:
        has_datagen = False
    payload = {'environment_instance_id': environment_instance_id, 'datagen_status': datagen_status, 'has_datagen': has_datagen}
    r = requests.post(APIURL + 'api_updateenvironmentinstance', data=json.dumps(payload), headers={'Authorization': 'Token ' + apikey, 'Content-Type': 'application/json'})

# get environment instances for a query assignment item
# sample return body
# [{"id": 1, "environment_name": "default", "initial_code": "/media/itemenv_1/sample-data-q1.sql", "item": 1}]
def callGetEnvironmentInstances(apikey, assignment_item_id):
    r = requests.get(APIURL + 'api_getenvironmentinstances/' + str(assignment_item_id), headers={'Authorization': 'Token ' + apikey})
    return r.json()

# get submitted student assignments
# sample return body
# [{"id": 1, "student_submission": {"id": 1, "student": {"id": 1, "first_name": "Henry", "last_name": "Pug", "student_custom_id": "16", "student_group": 1}, "submission_date": "2021-10-31T03:27:58.346970Z", "is_graded": false, "grade": 0, "is_active": true, "assignment": 3}, "is_active": true, "submission_file": "/media/submissions/assign3/item1/student1/student-query.sql", "assignment_item": 1}]
def callGetStudentSubmissions(apikey, assignment_item_id):
    r = requests.get(APIURL + 'api_getstudentsubmissions/' + str(assignment_item_id), headers={'Authorization': 'Token ' + apikey})
    return r.json()



# format rows_missing [] and extra_rows [] into a string
def format_query_output(rows_missing, extra_rows, points_possible, points_earned, environment_name):
    output = 'Test environment ' + environment_name + ' earned score ' + str(points_earned) + ' out of ' + str(points_possible) + '\n'
    output += 'Rows missing: ' + '\n'
    if len(rows_missing) > 0:
        for row in rows_missing:
            output += str(row) + '\n'
    else:
        output += 'None' + '\n'
    output += '\nExtra rows: ' + '\n'
    if len(extra_rows) > 0:
        for row in extra_rows:
            output += str(row) + '\n'
    else:
        output += 'None' + '\n'
    return output


# #   'primary_score': primary_score, 'secondary_score': secondary_score, 'rows_missing': rows_missing, 'extra_rows': extra_rows
def format_schema_output(rows_missing, extra_rows, primary_score, secondary_score):
    output = 'Tables/columns score: ' + str(primary_score) + '\n'
    output += 'Indexes score: ' + str(secondary_score) + '\n'
    output += 'Tables/columns missing: ' + '\n'
    if len(rows_missing) > 0:
        for row in rows_missing:
            output += str(row) + '\n'
    else:
        output += 'None' + '\n'
    output += '\nExtra tables/columns: ' + '\n'
    if len(extra_rows) > 0:
        for row in extra_rows:
            output += str(row) + '\n'
    else:
        output += 'None' + '\n'
    return output

# grading process for a query assignment item
def runGraderQuery(apikey, grading_process_id, db_type, initial_code_path, item_number, assignment_item_id, query_solution):
    student_submissions = callGetStudentSubmissions(apikey, assignment_item_id)
    environment_instances = callGetEnvironmentInstances(apikey, assignment_item_id)
    # for each environment instance, run grading process
    for environment_instance in environment_instances:

        # update the grading log
        log_string = 'Initializing admin container for ' + str(item_number) + ' with a ' + db_type + ' database'
        callUpdateGradingLog(apikey, grading_process_id, 'Initializing', log_string)

        # initialize the admin container
        admin_container = controlplane.createDB(db_type, ADMIN_PORT, 'admin-'+str(grading_process_id))
        controlplane.setupDB(db_type, ADMIN_PORT)
        dataplane.runSQLfile(db_type, ADMIN_PORT, initial_code_path)

        # run individual assignment item setup code (eg adding data to tables)
        more_code = dataplane.FILEPREFIX + environment_instance['initial_code']
        dataplane.runSQLfile(db_type, ADMIN_PORT, more_code)

        # check for generated data
        if environment_instance['has_datagen'] is not None and environment_instance['has_datagen'] == True:
            dataGen.loadData(environment_instance['id'], db_type, ADMIN_PORT)

        # create an image from the admin container
        image_name = 'sqlgraderimage/assignmentitem-' + str(item_number) + '-env-' + str(environment_instance['id'])
        controlplane.createImage(admin_container.id, image_name)

        # for each student submission, run grading process
        for student_submission in student_submissions:
            callUpdateGradingLog(apikey, grading_process_id, 'Grading', 'Grading ' + str(item_number) + ' for ' + str(student_submission['student_submission']['student']['student_custom_id']))
            studentcontainerid = 'student'+str(student_submission['student_submission']['student']['id'])
            # create student_container from image
            student_container = controlplane.createClonedDB(image_name, db_type, SECONDARY_PORT, studentcontainerid)

            # { 'length_difference': length_difference, 'rows_mismatched': rows_mismatched, 'rows_missing': rows_missing, 'extra_rows': extra_rows }
            studentgradeinfo = dataplane.compareQuery(db_type, ADMIN_PORT, SECONDARY_PORT, query_solution, student_submission['submission_file'])

            callUpdateGradingLog(apikey, grading_process_id, '', 'Graded ' + student_submission['student_submission']['student']['student_custom_id'])

            # update the student submission
            student_log = format_query_output(studentgradeinfo['rows_missing'], studentgradeinfo['extra_rows'], studentgradeinfo['points_possible'], studentgradeinfo['points_earned'], environment_instance['environment_name'])
            callUpdateStudentSubmissionItemQuery(apikey, student_submission['id'], environment_instance['id'], studentgradeinfo['points_possible'], studentgradeinfo['points_earned'], student_log)

            # delete the student container
            controlplane.deleteDB(student_container.id)

        # delete the admin container
        controlplane.deleteDB(admin_container.id)
    
    # call an API to tally the query points for each student
    callUpdateStudentSubmissionQuery(apikey, assignment_item_id)

# grading process for a schema assignment item
def runGraderSchema(apikey, grading_process_id, db_type, initial_code_path, item_number, assignment_item_id):
    student_submissions = callGetStudentSubmissions(apikey, assignment_item_id)
    # update the grading log
    log_string = 'Initializing admin container for ' + str(item_number) + ' with a ' + db_type + ' database'
    callUpdateGradingLog(apikey, grading_process_id, 'Initializing', log_string)

    # initialize the admin container
    admin_container = controlplane.createDB(db_type, ADMIN_PORT, 'admin')
    controlplane.setupDB(db_type, ADMIN_PORT)
    dataplane.runSQLfile(db_type, ADMIN_PORT, initial_code_path)

    # for each student submission, run grading process
    for student_submission in student_submissions:
        callUpdateGradingLog(apikey, grading_process_id, 'Grading', 'Grading ' + str(item_number) + ' for ' + str(student_submission['student_submission']['student']['student_custom_id']))
        studentcontainerid = 'student'+str(student_submission.student_submission.student.id)
        student_container = controlplane.createDB(db_type, SECONDARY_PORT, studentcontainerid)
        controlplane.setupDB(db_type, SECONDARY_PORT)
        dataplane.runSQLfile(db_type, SECONDARY_PORT, initial_code_path)

        studentgradeinfo = dataplane.compareSchemas(db_type, ADMIN_PORT, SECONDARY_PORT)
        callUpdateGradingLog(apikey, grading_process_id, '', 'Graded ' + student_submission['student_submission']['student']['student_custom_id'])
        #   'primary_score': primary_score, 'secondary_score': secondary_score, 'rows_missing': rows_missing, 'extra_rows': extra_rows
        student_log = format_schema_output(studentgradeinfo['rows_missing'], studentgradeinfo['extra_rows'], studentgradeinfo['primary_score'], studentgradeinfo['secondary_score'])
        callUpdateStudentSubmissionItemSchema(apikey, student_submission['id'], studentgradeinfo['primary_score'], studentgradeinfo['secondary_score'], student_log)

        controlplane.deleteDB(student_container.id)

    # delete the admin container
    controlplane.deleteDB(admin_container.id)

# 
# sample post_body:
# [
#     {'id': 10, 'assignment_item': {'id': 1, 'assignmentenvironment': {'db_type': 'POSTGRES', 'initial_code': '/media/assignmentenv_3/sample-table.sql'
#             }, 'item_number': 1, 'item_type': 'QUERY', 'item_solution': '/media/assignmentitem_1/sample-query_CWOZKc4.sql', 'item_name': 'test query', 'assignment': 3
#         }, 'grading_process': 6
#     },
#     {'id': 11, 'assignment_item': {'id': 3, 'assignmentenvironment': {'db_type': 'POSTGRES', 'initial_code': '/media/assignmentenv_3/sample-table.sql'
#             }, 'item_number': 2, 'item_type': 'SCHEMA', 'item_solution': None, 'item_name': '', 'assignment': 3
#         }, 'grading_process': 6
#     }
# ]
# 
def rungradingprocess(**kwargs):
    post_body = kwargs.get('post_body')
    grading_process_id = kwargs.get('grading_process_id')
    apikey = kwargs.get('apikey')

    # for each assignment_environment, initialize the admin container
    for assignment_item in post_body:
        initial_code_path = dataplane.FILEPREFIX + assignment_item['assignment_item']['assignmentenvironment']['initial_code']
        db_type = assignment_item['assignment_item']['assignmentenvironment']['db_type'].lower()
        item_number = assignment_item['assignment_item']['item_number']
        item_type = assignment_item['assignment_item']['item_type']
        assignment_item_id = assignment_item['assignment_item']['id']

        # break if db_type is not supported
        if not dbUtilities.checkDbCompat(db_type):
            callUpdateGradingLog(apikey, grading_process_id, 'Grading', 'DB type not compatible with CPU running SQLGrader for assignment item ' + str(item_number) + '.')
            break

        student_submissions = callGetStudentSubmissions(apikey, assignment_item_id)

        # if a QUERY item_type, get the environment instances
        if item_type == 'QUERY':
            query_solution = assignment_item['assignment_item']['item_solution']
            runGraderQuery(apikey, grading_process_id, db_type, initial_code_path, item_number, assignment_item_id, query_solution)

        # if a SCHEMA item_type run grader once
        if item_type == 'SCHEMA':
            runGraderSchema(apikey, grading_process_id, db_type, initial_code_path, item_number, assignment_item_id)

    # update the grading process for completion
    callUpdateGradingLog(apikey, grading_process_id, 'Finished', 'Grading process completed.')
