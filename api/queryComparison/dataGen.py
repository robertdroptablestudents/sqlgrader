from faker import Faker
from ..dbManagement import controlplane, dataplane, dbUtilities
from ..grading import gradingProcess
import csv, os

faker = Faker()

INT_SETS = {
    'int': {
        'min': -2147483648,
        'max': 2147483647
    },
    'integer': {
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
    # return '/code/webui/media/assignmentenv_{0}/datagen/'.format(assignment_env_id)
    # check if '../webui/media/assignmentenv_{0}/datagen/' exists
    if not os.path.exists('../webui/media/itemenv_{0}/'.format(assignment_env_id)):
        os.makedirs('../webui/media/itemenv_{0}/'.format(assignment_env_id))
    if not os.path.exists('../webui/media/itemenv_{0}/datagen/'.format(assignment_env_id)):
        os.makedirs('../webui/media/itemenv_{0}/datagen/'.format(assignment_env_id))
    return '../webui/media/itemenv_{0}/datagen/'.format(assignment_env_id)

def initialCodePath(filename):
    return '../webui/media/' + filename

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
    if column_type in ('string', 'nvarchar', 'varchar', 'text', 'char', 'nchar','char varying', 'nchar varying', 'character varying', 'character'):
        if data_size == '-1': # resize (max) columns
            data_size = '500'
        if data_size == ',': # resize flex columns
            data_size = '50'
        if isUnique == 'YES':
            data_size = int(data_size)
            return faker.unique.pystr(min_chars=1, max_chars=data_size)
        else:
            data_size = int(data_size)
            if data_size > 60: # use lorem generator for long strings
                return faker.text(max_nb_chars=data_size).replace('\n', ' ')
            else:
                return faker.pystr(min_chars=1, max_chars=data_size)
    elif column_type in ('uniqueidentifier', 'uuid'):
        return faker.uuid4()
    elif 'int' in column_type: # encompasses tinyint, smallint, bigint, anyint, int
        # need to set min and max based on data size
        if isUnique == 'YES':
            return faker.unique.pyint(min_value=INT_SETS[column_type]['min'], max_value=INT_SETS[column_type]['max'])
        else:
            return faker.pyint(min_value=INT_SETS[column_type]['min'], max_value=INT_SETS[column_type]['max'])
    elif column_type in ('float', 'real', 'double precision'):
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
    elif 'binary' in column_type or column_type in ('varbinary', 'image', 'bytea'):
        if data_size == '-1' or data_size == ',':
            data_size = '64'
        data_size = int(data_size)
        return faker.binary(length=data_size)
    elif column_type in ('bit', 'boolean'):
        return faker.pybool() 
    elif column_type.split(' ')[0] in ('datetime', 'date', 'time', 'datetime2', 'datetimeoffset'): # includes with and without timezone
        return faker.date_time_this_decade()
    elif column_type in ('inet','cidr'):
        return faker.ipv4()
    elif column_type in ('macaddr'):
        return faker.mac_address()
    # xml, anyarray, array, time interval
    else:
        return ''


# faker special column name executor
def fakerSpecialData(column_type, isUnique, data_size):
    # start with the non-string options
    match column_type:
        case 'latitude':
            return faker.latitude()
        case 'longitude':
            return faker.longitude()
    
    # string options
    if data_size == '-1': # resize (max) columns
        data_size = 500
    elif data_size == ',': # resize flex columns
        data_size = 50
    else:
        data_size = int(data_size)-1

    match column_type:
        case 'city':
            if isUnique == 'YES':
                return faker.unique.city()[:data_size]
            else:
                return faker.city()[:data_size]
        case 'country':
            if int(data_size) < 5:
                if isUnique == 'YES':
                    return faker.unique.country_code()[:data_size]
                else:
                    return faker.country_code()[:data_size]
            else:
                if isUnique == 'YES':
                    return faker.unique.country()[:data_size]
                else:
                    return faker.country()[:data_size]
        case 'zip':
            if isUnique == 'YES':
                return faker.unique.postcode()[:data_size]
            else:
                return faker.postcode()[:data_size]
        case 'address':
            if isUnique == 'YES':
                return faker.unique.street_address()[:data_size]
            else:
                return faker.street_address()[:data_size]
        case 'phone':
            if isUnique == 'YES':
                return faker.unique.phone_number()[:data_size]
            else:
                return faker.phone_number()[:data_size]
        case 'company':
            if isUnique == 'YES':
                return faker.unique.company()[:data_size]
            else:
                return faker.company()[:data_size]
        case 'color':
            if isUnique == 'YES':
                return faker.unique.color_name()[:data_size]
            else:
                return faker.color_name()[:data_size]
        case 'email':
            if isUnique == 'YES':
                return faker.unique.email()[:data_size]
            else:
                return faker.email()[:data_size]
        case 'url':
            if isUnique == 'YES':
                return faker.unique.url()[:data_size]
            else:
                return faker.url()[:data_size]
        case 'first_name':
            if isUnique == 'YES':
                return faker.unique.first_name()[:data_size]
            else:
                return faker.first_name()[:data_size]
        case 'last_name':
            if isUnique == 'YES':
                return faker.unique.last_name()[:data_size]
            else:
                return faker.last_name()[:data_size]
        case 'account':
            if isUnique == 'YES':
                return faker.unique.bban()[:data_size]
            else:
                return faker.bban()[:data_size]
    
    # no types have matched, return empty string
    return ''


# faker special column name selector
def fakerSpecialDataType(column_name, orig_column_type):
    new_column_type = ''

    # types only strings
    if orig_column_type in ('string', 'nvarchar', 'varchar', 'text', 'char', 'nchar','char varying', 'nchar varying', 'character varying', 'character'):
        # city, country, zip, postal, address, company, phone
        if 'city' in column_name:
            new_column_type = 'city'
        if 'country' in column_name:
            new_column_type = 'country'
        if 'zip' in column_name or 'postal' in column_name:
            new_column_type = 'postcode'
        if 'address' in column_name:
            new_column_type = 'address'
        if 'phone' in column_name:
            new_column_type = 'phone_number'
        if 'company' in column_name:
            new_column_type = 'company'

        # color (color_name)
        if 'color' in column_name:
            new_column_type = 'color_name'
        # email, url
        if 'email' in column_name:
            new_column_type = 'email'
        if 'url' in column_name or 'website' in column_name:
            new_column_type = 'url'

        # first name, last name
        if 'first_name' in column_name:
            new_column_type = 'first_name'
        if 'last_name' in column_name:
            new_column_type = 'last_name'

        # account (bank account)
        if 'account' in column_name:
            new_column_type = 'bank_account'
    
    # not necessarily strings
    # latitude, longitude
    if 'latitude' in column_name:
        new_column_type = 'latitude'
    if 'longitude' in column_name:
        new_column_type = 'longitude'

    return new_column_type


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
def createSeedValues(row_count, table_columns, column_name):
    seed_values = []

    # get the data size of the column
    for column in table_columns:

        if column[3] == column_name:
            data_size = column[7]
            isUnique = column[9]
            column_type = column[6]

            # make the seed values for this column
            for i in range(0, row_count):
                # if its an identity column, use i
                if column[8] == 'YES':
                    seed_values.append(i)
                else:
                    seed_values.append(fakerData(column_type.lower(), isUnique, data_size))
            
            break
    return seed_values

# generate data for this table based on data types only
def basicDataGen(assignment_env_id, row_count, tableName, all_columns, file_number, foreign_keys, db_type):
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
    if foreign_keys and len(foreign_keys) > 0:
        for fk in foreign_keys:
            # if this foreign key references this table only once, we can use the seed values
            if fk[0]+'-'+fk[1] == tableName and fk[3]+'-'+fk[4] != tableName:
                foreign_key_columns.append(fk[2])
                foreign_key_seeds[fk[2]] = pullSeedValues(assignment_env_id, fk[3]+'-'+fk[4], fk[5])
            
            # if this references this table multiple times, we need to generate new values
            elif fk[0]+'-'+fk[1] == tableName and fk[3]+'-'+fk[4] == tableName:
                self_referencing_columns.append(fk[2])
                self_referencing_columns.append(fk[5])
                foreign_key_seeds[fk[5]] = createSeedValues(row_count, table_columns, fk[5])
                # start the self referencing column with its first value
                foreign_key_seeds[fk[2]] = [ foreign_key_seeds[fk[5]][0] ] + foreign_key_seeds[fk[5]]

    # check column names for special data shapes (eg address, color)
    special_columns = {}
    for column in table_columns:
        if column[3] not in foreign_key_columns and column[3] not in self_referencing_columns and column[8] != 'YES':
            new_column_type = fakerSpecialDataType(column[3], column[6].lower())
            if new_column_type != '':
                special_columns[column[3]] = new_column_type

    # open a new csv file filenumber-schema-tablename.csv
    csv_file_name = str(file_number)+'-'+tableName+'.csv'
    sql_file_name = str(file_number)+'-'+tableName+'.sql'
    # 'assignmentenv_{0}/{1}'.format(self.id, filename)
    csv_file_path = dataStoragePath(assignment_env_id)+csv_file_name
    csv_file = open(csv_file_path, 'w')
    csv_writer = csv.writer(csv_file, delimiter=',')
    sql_file_path = dataStoragePath(assignment_env_id)+sql_file_name
    sql_file = open(sql_file_path, 'w')

    insert_statement = ''
    # if table has an identity column, we need to set identity insert on for mssql
    # not required for postgres
    if table_has_id and db_type == 'mssql':
        insert_statement += 'SET IDENTITY_INSERT {0} ON;\n'.format(tableName.replace('-','.'))

    insert_statement += 'INSERT INTO '+tableName.replace('-','.')+' ('
    insert_columns = []
    for column in table_columns:
        insert_columns.append(column[3])
    #print(insert_columns)
    insert_statement += ', '.join(insert_columns)
    insert_statement += ') VALUES '
    sql_file.write(insert_statement+'\n(')
    csv_writer.writerow(insert_columns)

    # generate data for each row
    for i in range(0, row_count):
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
            # column is a special data type, retrieve for special faker data function
            elif column[3] in special_columns:
                new_data = fakerSpecialData(special_columns[column[3]], column[9], column[7])
            # not linked to another column, generate data
            else:
                new_data = fakerData(column[6].lower(), column[9], column[7])
            row.append(str(new_data))
            

        insert_statement = '\'' + '\', \''.join(row) + '\''

        # store the data in a csv file
        csv_writer.writerow(row)

        # write the sql insert statement to file
        if i == row_count-1:
            sql_file.write(insert_statement+' );')
        else:
            sql_file.write(insert_statement+' ),\n( ')

    # close the files
    csv_file.close()
    sql_file.close()
    #print('datagen finished')

    return


# from external datagen module, generate a fake data set
def createDataCsvSQL(assignment_env_id, row_count, schema_tables, foreign_keys, db_type):
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
    #print('starting data generation')
    tables_completed = []
    file_number = 0

    # for any table that does not have a foreign key, do data generation
    for tableName in foreign_keys_map:
        if foreign_keys_map[tableName] == 0:
            # generate data for this table based on data types only
            #print('generating data for table: '+tableName)
            basicDataGen(assignment_env_id, row_count, tableName, schema_tables, file_number, foreign_keys, db_type)
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
                    #print('generating data for table: '+tableName)
                    basicDataGen(assignment_env_id, row_count, tableName, schema_tables, file_number, foreign_keys, db_type)
                    # add table to completed list
                    tables_completed.append(tableName)
                    file_number += 1


# sample post body
# {'db_type': 'POSTGRES', 'initial_code': '/media/assignmentenv_3/sample-table.sql'
#             }
def startdatagen(**kwargs):
    apikey = kwargs.get('apikey')
    try:
        post_body = kwargs.get('post_body')
        assignment_env_id = kwargs.get('environment_instance_id')

        db_type = post_body['db_type'].lower()
        assignment_item_id = post_body['assignment_item_id']
        env_code_path = post_body['env_code']
        initial_code_path = post_body['initial_code']
        row_count = int(post_body['row_count'])

        # to generate seed values
        if post_body['query_text']:
            query_text = post_body['query_text']
        seed_array = []

        if not dbUtilities.checkDbCompat(db_type):
            #print("Database type not supported")
            # cannot datagen, bail out
            raise Exception("Database type not supported")

        # setup an admin instance for the assignment
        admin_container = controlplane.createDB(db_type, gradingProcess.ADMIN_PORT, 'datagen-'+str(assignment_item_id))
        controlplane.setupDB(db_type, gradingProcess.ADMIN_PORT)

        # run environment setup
        #print(env_code_path)
        dataplane.runSQLfile(db_type, gradingProcess.ADMIN_PORT, initialCodePath(env_code_path))
        if initial_code_path != '':
            dataplane.runSQLfile(db_type, gradingProcess.ADMIN_PORT, initialCodePath(initial_code_path))

        # get the schema of the database
        schema_tables = dataplane.getSchemaObjects(db_type, gradingProcess.ADMIN_PORT)
        #print(schema_tables)

        # check for foreign keys
        foreign_keys = dataplane.getForeignKeys(db_type, gradingProcess.ADMIN_PORT)
        #print(foreign_keys)
        
        # run datageneration
        createDataCsvSQL(assignment_env_id, row_count, schema_tables, foreign_keys, db_type)

        # delete the admin container
        controlplane.deleteDB(admin_container.id)

        # call api to set datagen_status to complete
        gradingProcess.callUpdateEnvironmentInstance(apikey, assignment_env_id, 'completed')
    
    except Exception as e:
        gradingProcess.callUpdateEnvironmentInstance(apikey, assignment_env_id, 'failed '+str(e)[0:90])
        # delete the admin container
        controlplane.deleteDB(admin_container.id)