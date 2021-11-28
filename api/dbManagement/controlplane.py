import docker, os, psycopg, mysql.connector, pyodbc
from urllib.parse import quote_plus
from time import sleep
from .dbUtilities import get_connectionstring

databaseOptions = {
    'images' : {
        'mssql': 'mcr.microsoft.com/azure-sql-edge',
        'mysql': 'mysql/mysql-server',
        'postgres': 'postgres',
    },
    'ports' : {
        'mssql': '1433/tcp',
        'mysql': '3306/tcp',
        'postgres': '5432/tcp',
    },
    'environment' : {
        'mssql': {'ACCEPT_EULA': 'Y', 'SA_PASSWORD': os.environ['DEFAULTPASSWORD']},
        'mysql': {'MYSQL_ROOT_PASSWORD': os.environ['DEFAULTPASSWORD'], 'MYSQL_ROOT_HOST': '%'},
        'postgres': {'POSTGRES_PASSWORD': os.environ['DEFAULTPASSWORD']},
    },
    'initialconnstring': {
        'mssql': 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;PORT=1437;DATABASE=master;UID=sa;PWD='+quote_plus(os.environ['DEFAULTPASSWORD'])+';TDS_Version=8.0;',
        'mysql': {
            'host': 'localhost',
            'user': 'root',
            'password': os.environ['DEFAULTPASSWORD'],
            'port': 1437
        },
        'postgres': 'postgresql://postgres:'+quote_plus(os.environ['DEFAULTPASSWORD'])+'@localhost:1437/postgres'
    },
    'adminconnstring': {
        'mssql': '',
        'mysql': '',
        'postgres': 'postgresql://postgres:'+quote_plus(os.environ['DEFAULTPASSWORD'])+'@localhost:1437/admindb'
    }
}

# create a database container, return the container info
def createDB(dbType, dbPort, containerName):
    container_name = 'sqlgrader-'+ containerName
    client = docker.from_env()
    print('Pulling image...')
    client.images.pull(databaseOptions['images'][dbType])
    print('Creating containers...')

    # check for previous container and remove
    existing_containers = client.containers.list(filters={'name': containerName})
    for container in existing_containers:
        container.stop()
        container.remove()

    # Create container
    new_database = client.containers.create(databaseOptions['images'][dbType], detach=True, labels={"sqlgrader": containerName }, name=container_name, environment=databaseOptions['environment'][dbType], ports={databaseOptions['ports'][dbType]: dbPort})

    # Start container
    new_database.start()
    print('Started new container {}'.format(new_database.id))

    return new_database

# remove a container by id
def deleteDB(container_id):
    client = docker.from_env()
    todecommission = client.containers.get(container_id)
    todecommission.stop()
    todecommission.remove()

# run setup scripts on a container by db_type
def setupDB(dbType, dbPort):
    num_retry = 10
    while num_retry > 0:
        print('waiting 2 seconds')
        sleep(2)
        print('done waiting')
        try:
            match dbType.lower():
                case 'postgres':
                    conn = psycopg.connect(get_connectionstring(dbType, dbPort, True), autocommit=True)
                    cur = conn.cursor()
                    cur.execute("CREATE DATABASE admindb")
                    cur.execute("select version()")
                    db_version = cur.fetchone()
                    print(db_version)
                    cur.close()
                    conn.close()

                case 'mysql':
                    conn = mysql.connector.connect(**get_connectionstring(dbType, dbPort, True))
                    with conn.cursor() as cur:
                        cur.execute("CREATE DATABASE admindb")
                        cur.execute("show databases")
                        for db in cur:
                            print(db)
                        cur.close()
                        conn.close()
                case 'mssql':
                    conn = pyodbc.connect(get_connectionstring(dbType, dbPort, True))
                    cur = conn.cursor()
                    cur.execute("CREATE DATABASE admindb")
                    cur.execute("select @@version")
                    db_version = cur.fetchone()
                    print(db_version)
                    cur.close()
                    conn.close()
            break
        except Exception as e:
            print(e)
            num_retry -= 1
            continue
