from faker import Faker
from faker.providers import python, currency, misc, lorem
from ..dbManagement import controlplane, dataplane, dbUtilities
from ..grading import callGetEnvironmentInstances, ADMIN_PORT

DATASET_SIZE = 100
fake = Faker()

INT_SETS = {
    'int': {
        'min': -2147483648,
        'max': 2147483647
    },
    'smallint': {
        'min': -32768,
        'max': -32768
    },
    'tinyint': {
        'min': 0,
        'max': 255
    },
    'bigint': {
        'min': -9223372036854775808,
        'max': -9223372036854775807
    },
}

# faker utility selector
def fakerData(column_type, isUnique, data_size):
    if column_type in ('string', 'nvarchar', 'varchar', 'text', 'char', 'nchar'):
        if data_size == '-1': # resize (max) columns
            data_size = '500'
        if isUnique == 'YES':
            return fake.unique.pystr(min_chars=1, max_chars=data_size)
        else:
            if data_size > 60: # use lorem generator for long strings
                return fake.text(max_nb_chars=data_size)
            else:
                return fake.pystr(min_chars=1, max_chars=data_size)
    elif column_type in ('uniqueidentifier'):
        return fake.uuid4()
    elif 'int' in column_type: # encompasses tinyint, smallint, bigint, anyint, int
        # need to set min and max based on data size
        if isUnique == 'YES':
            return fake.unique.pyint(min_value=INT_SETS[column_type]['min'], max_value=INT_SETS[column_type]['max'])
        else:
            return fake.pyint(min_value=INT_SETS[column_type]['min'], max_value=INT_SETS[column_type]['max'])
    elif column_type in ('float'):
        if isUnique == 'YES':
            return fake.unique.pyfloat()
        else:
            return fake.pyfloat()
    elif column_type in ('decimal', 'numeric'):
        right_size = int(data_size.split(',')[1])
        left_size = int(data_size.split(',')[0])-right_size
        if isUnique == 'YES':
            return fake.unique.pydecimal(left_digits=left_size, right_digits=right_size)
        else:
            return fake.pydecimal(left_digits=left_size, right_digits=right_size)
    elif column_type in ('money', 'currency'):
        return fake.pricetag()
    elif 'binary' in column_type:
        if data_size == '-1':
            data_size = '64'
        return fake.binary(length=data_size)
    elif column_type in ('bit'):
        return fake.pybool() 
    elif column_type in ('datetime', 'date', 'time', 'datetime2', 'datetimeoffset'):
        return fake.date_time_this_decade()
    # xml
    else:
        return ''

def dataStoragePath(assignment_env_id):
    return '/code/webui/media/assignmentenv_{0}/'.format(assignment_env_id)

# generate data for this table based on data types only
def basicDataGen(assignment_env_id, tableName, all_columns, file_number):
    # get the schema of the table, excluding identity columns
    table_columns = []
    for row in all_columns:
        if row[0]+'-'+row[1] == tableName and row[8] == 'NO':
            table_columns.append(row)

    # open a new csv file
    csv_file_name = str(file_number)+'-'+tableName+'.csv'
    sql_file_name = str(file_number)+'-'+tableName+'.sql'
    # 'assignmentenv_{0}/{1}'.format(self.id, filename)
    csv_file_path = dataStoragePath(assignment_env_id)+csv_file_name
    csv_file = open(csv_file_path, 'w')
    sql_file_path = dataStoragePath(assignment_env_id)+sql_file_name
    sql_file = open(sql_file_path, 'w')

    insert_statement = 'INSERT INTO '+tableName+' ('
    firstColumn = True
    for column in table_columns:
        if firstColumn:
            insert_statement += ', '
            firstColumn = False
        insert_statement += column[3]
    insert_statement += ') VALUES '

    for i in range(0, DATASET_SIZE):
        # create a new row
        row = []
        for column in table_columns:
            new_data = fakerData(column[6], column[9], column[7])
            row.append(new_data)
            insert_statement += '\''+new_data+'\''
            # check for guids, identifiers

        # store the data in a csv file
        csv_file.write(','.join(row))

        # write the sql insert statement to file
        if i == DATASET_SIZE-1:
            sql_file.write(insert_statement+' );')
        else:
            sql_file.write(insert_statement+' ), ( ')

    # close the files
    csv_file.close()
    sql_file.close()

    return

# generate data for this table based on existing values in foreign keys
def linkedDataGen(assignment_env_id, tableName, all_columns, file_number, foreign_keys):
    # get the schema of the table
    table_columns = []
    for row in all_columns:
        if row[0]+'-'+row[1] == tableName:
            table_columns.append(row)

    # pick out which columns are foreign keys

    return



# sample post body
# {'db_type': 'POSTGRES', 'initial_code': '/media/assignmentenv_3/sample-table.sql'
#             }
def startdatagen(**kwargs):
    post_body = kwargs.get('post_body')
    assignment_item_id = kwargs.get('assignment_item_id')
    apikey = kwargs.get('apikey')

    db_type = post_body['db_type']

    if not dbUtilities.checkDbCompat(db_type):
        print("Database type not supported")
        # cannot datagen, bail out
        return

    # setup an admin instance for the assignment
    initial_code_path = post_body['initial_code']
    admin_container = controlplane.createDB(db_type, ADMIN_PORT, 'datagen-'+str(assignment_item_id))
    controlplane.setupDB(db_type, ADMIN_PORT)
    dataplane.runSQLfile(db_type, ADMIN_PORT, initial_code_path)

    # get any existing environment instances
    environment_instances = callGetEnvironmentInstances(apikey, assignment_item_id)
    if environment_instances.length > 0:
        # run this script in the environment
        more_code = environment_instances[0]['initial_code']
        dataplane.runSQLfile(db_type, ADMIN_PORT, more_code)


    assignment_env_id = 0 
    # need to make an API on django side to make a new assignment environment

    # get the schema of the database
    schema_tables = dataplane.getSchemaObjects(db_type, ADMIN_PORT)

    # create list of table names
    foreign_keys_map = {}
    for row in schema_tables:
        tableName = row[0]+'-'+row[1]
        if not tableName in foreign_keys_map:
            foreign_keys_map[tableName] = 0

    # check for foreign keys
    foreign_keys = dataplane.getForeignKeys(db_type, ADMIN_PORT)
    for row in foreign_keys:
        foreign_keys_map[row[0]+'-'+row[1]] += 1

    # start datagen
    tables_completed = []
    file_number = 0

    # for any table that does not have a foreign key, do data generation
    for tableName in foreign_keys_map:
        if foreign_keys_map[tableName] == 0:
            # generate data for this table based on data types only
            basicDataGen(assignment_env_id, tableName, schema_tables, file_number)
            # add table to completed list
            tables_completed.append(tableName)
            file_number += 1
            
    # for any table that has a foreign key, do data generation
    while len(tables_completed) < len(foreign_keys_map):
        for tableName in foreign_keys_map:
            if not tableName in tables_completed:
                # if not already completed, check if foreign keys are completed
                dependencies_met = True
                table_dependencies = [] # list of foreign key tuples on this table
                for row in foreign_keys:
                    if row[0]+'-'+row[1] == tableName:
                        table_dependencies.append(row) # add this FK to the dependency list
                        if tables_completed.count(row[3]+'-'+row[4]) == 0:
                            # if the FK's table isn't completed, keep iterating
                            dependencies_met = False
                            break
                if dependencies_met:
                    # generate data for this table based on dependent columns
                    linkedDataGen(assignment_env_id, tableName, schema_tables, file_number, table_dependencies)
                    # add table to completed list
                    tables_completed.append(tableName)
                    file_number += 1

    # delete the admin container
    controlplane.deleteDB(admin_container.id)