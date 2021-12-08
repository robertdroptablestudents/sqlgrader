from faker import Faker
from faker.providers import python, currency, misc, lorem
from ..dbManagement import controlplane, dataplane, dbUtilities
from ..grading import callGetEnvironmentInstances, ADMIN_PORT
import csv, os

DATASET_SIZE = 200
faker = Faker()

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

def dataStoragePath(assignment_env_id):
    return '/code/webui/media/assignmentenv_{0}/datagen/'.format(assignment_env_id)

# pull int prepending the file name
def fileOrder(filename):
    return int(filename.split('-')[0])

# iterate over insert statements and run them
def loadData(assignment_environment_id, db_type, container_port):
    file_path = dataStoragePath(assignment_environment_id)
    file_list = os.listdir(file_path)
    file_list.sort(key=fileOrder)
    # execute the files in order
    for insert_file in file_list:
        if insert_file.endswith('.sql'):
            dataplane.runSQLfile(db_type, container_port, file_path + insert_file)


# faker utility selector
def fakerData(column_type, isUnique, data_size):
    if column_type in ('string', 'nvarchar', 'varchar', 'text', 'char', 'nchar'):
        if data_size == '-1': # resize (max) columns
            data_size = '500'
        if isUnique == 'YES':
            data_size = int(data_size)
            return faker.unique.pystr(min_chars=1, max_chars=data_size)
        else:
            data_size = int(data_size)
            if data_size > 60: # use lorem generator for long strings
                return faker.text(max_nb_chars=data_size).replace('\n', ' ')
            else:
                return faker.pystr(min_chars=1, max_chars=data_size)
    elif column_type in ('uniqueidentifier'):
        return faker.uuid4()
    elif 'int' in column_type: # encompasses tinyint, smallint, bigint, anyint, int
        # need to set min and max based on data size
        if isUnique == 'YES':
            return faker.unique.pyint(min_value=INT_SETS[column_type]['min'], max_value=INT_SETS[column_type]['max'])
        else:
            return faker.pyint(min_value=INT_SETS[column_type]['min'], max_value=INT_SETS[column_type]['max'])
    elif column_type in ('float'):
        if isUnique == 'YES':
            return faker.unique.pyfloat()
        else:
            return faker.pyfloat()
    elif column_type in ('decimal', 'numeric'):
        right_size = int(data_size.split(',')[1])
        left_size = int(data_size.split(',')[0])-right_size
        if isUnique == 'YES':
            return faker.unique.pydecimal(left_digits=left_size, right_digits=right_size)
        else:
            return faker.pydecimal(left_digits=left_size, right_digits=right_size)
    elif column_type in ('money', 'currency'):
        return faker.pricetag()
    elif 'binary' in column_type:
        if data_size == '-1':
            data_size = '64'
        data_size = int(data_size)
        return faker.binary(length=data_size)
    elif column_type in ('bit'):
        return faker.pybool() 
    elif column_type in ('datetime', 'date', 'time', 'datetime2', 'datetimeoffset'):
        return faker.date_time_this_decade()
    # xml
    else:
        return ''


# generate data values for this table based on existing values in foreign keys
def pullSeedValues(assignment_env_id, source_table, source_column):
    storage_path = dataStoragePath(assignment_env_id)
    seed_values = []

    # list all files in storage_path
    source_files = os.listdir(storage_path)
    for fk_seed in source_files:
        if fk_seed.endswith(source_table+'.csv'):
            fk_seed_file = open(storage_path+fk_seed, 'r')
            fk_seed_reader = csv.DictReader(fk_seed_file)
            for row in fk_seed_reader:
                seed_values.append(row[source_column])

    return seed_values

# generate data values for a specific column in a self-referencing table
def createSeedValues(table_columns, column_name):
    seed_values = []

    # get the data size of the column
    for column in table_columns:

        if column[3] == column_name:
            data_size = column[7]
            isUnique = column[9]
            column_type = column[6]

            # make the seed values for this column
            for i in range(0, DATASET_SIZE):
                # if its an identity column, use i
                if column[8] == 'YES':
                    seed_values.append(i)
                else:
                    seed_values.append(fakerData(column_type, isUnique, data_size))
            
            break
    return seed_values

# generate data for this table based on data types only
def basicDataGen(assignment_env_id, tableName, all_columns, file_number, foreign_keys):
    # get the schema of the table, excluding identity columns
    table_columns = []
    table_has_id = False
    for row in all_columns:
        if row[0]+'-'+row[1] == tableName:
            table_columns.append(row)
        if row[8] == 'YES':
            # set flag to generate IDs and allow identity insert
            table_has_id = True

    # pick out which columns are foreign keys
    foreign_key_columns = []
    foreign_key_seeds = {}
    self_referencing_columns = []
    for fk in foreign_keys:
        # if this foreign key references this table only once, we can use the seed values
        if fk[0]+'-'+fk[1] == tableName and fk[3]+'-'+fk[4] != tableName:
            foreign_key_columns.append(fk[2])
            foreign_key_seeds[fk[2]] = pullSeedValues(assignment_env_id, fk[3]+'-'+fk[4], fk[5])
        
        # if this references this table multiple times, we need to generate new values
        elif fk[0]+'-'+fk[1] == tableName and fk[3]+'-'+fk[4] == tableName:
            self_referencing_columns.append(fk[2])
            self_referencing_columns.append(fk[5])
            foreign_key_seeds[fk[5]] = createSeedValues(table_columns, fk[5])
            # start the self referencing column with its first value
            foreign_key_seeds[fk[2]] = [ foreign_key_seeds[fk[5]][0] ] + foreign_key_seeds[fk[5]]


    # open a new csv file filenumber-schema-tablename.csv
    csv_file_name = str(file_number)+'-'+tableName+'.csv'
    sql_file_name = str(file_number)+'-'+tableName+'.sql'
    # 'assignmentenv_{0}/{1}'.format(self.id, filename)
    csv_file_path = dataStoragePath(assignment_env_id)+csv_file_name
    csv_file = open(csv_file_path, 'w')
    csv_writer = csv.writer(csv_file, delimiter=',')
    sql_file_path = dataStoragePath(assignment_env_id)+sql_file_name
    sql_file = open(sql_file_path, 'w')

    # if table has an identity column, we need to set identity insert on
    if table_has_id:
        insert_statement = 'SET IDENTITY_INSERT {0} ON;\n'.format(tableName.replace('-','.'))

    insert_statement += 'INSERT INTO '+tableName.replace('-','.')+' ('
    insert_columns = []
    for column in table_columns:
        insert_columns.append(column[3])
    insert_statement += ', '.join(insert_columns)
    insert_statement += ') VALUES '
    sql_file.write(insert_statement+'\n(')
    csv_writer.writerow(insert_columns)

    # generate data for each row
    for i in range(0, DATASET_SIZE):
        # create a new row
        row = []
        for column in table_columns:
            # linked foreign key, pull data from seed data
            if column[3] in foreign_key_columns:
                data_options = foreign_key_seeds[column[3]]
                new_data = faker.random_element(elements=data_options)
            # foreign key referencing this table (self reference)
            elif column[3] in self_referencing_columns:
                new_data = foreign_key_seeds[column[3]][i]
            # column is an ID
            elif column[8] == 'YES':
                new_data = i
            # not linked to another column, generate data
            else:
                new_data = fakerData(column[6], column[9], column[7])
            row.append(str(new_data))
            
            # check for guids, identifiers

        insert_statement = '\'' + '\', \''.join(row) + '\''

        # store the data in a csv file
        csv_writer.writerow(row)

        # write the sql insert statement to file
        if i == DATASET_SIZE-1:
            sql_file.write(insert_statement+' );')
        else:
            sql_file.write(insert_statement+' ),\n( ')

    # close the files
    csv_file.close()
    sql_file.close()

    return


# from external datagen module, generate a fake data set
def createDataCsvSQL(assignment_env_id, schema_tables, foreign_keys):
    # create list of table names
    foreign_keys_map = {}
    for row in schema_tables:
        tableName = row[0]+'-'+row[1]
        if not tableName in foreign_keys_map:
            foreign_keys_map[tableName] = 0

    # check for foreign keys
    for row in foreign_keys:
        if row[0]+'-'+row[1] != row[3]+'-'+row[4]:
            foreign_keys_map[row[0]+'-'+row[1]] += 1

    # start datagen
    tables_completed = []
    file_number = 0

    # for any table that does not have a foreign key, do data generation
    for tableName in foreign_keys_map:
        if foreign_keys_map[tableName] == 0:
            # generate data for this table based on data types only
            basicDataGen(assignment_env_id, tableName, schema_tables, file_number, foreign_keys)
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
                    basicDataGen(assignment_env_id, tableName, schema_tables, file_number, foreign_keys)
                    # add table to completed list
                    tables_completed.append(tableName)
                    file_number += 1


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

    # check for foreign keys
    foreign_keys = dataplane.getForeignKeys(db_type, ADMIN_PORT)
    
    # run datageneration
    createDataCsvSQL(assignment_env_id, schema_tables, foreign_keys)

    # delete the admin container
    controlplane.deleteDB(admin_container.id)