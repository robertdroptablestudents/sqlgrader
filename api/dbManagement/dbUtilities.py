import os
import platform
from urllib.parse import quote_plus

def get_connectionstring(dbType, dbPort, is_initialconnection):
    match dbType.lower():
        case 'postgres':
            if is_initialconnection:
                return 'postgresql://postgres:'+quote_plus(os.environ['DEFAULTPASSWORD'])+'@localhost:'+str(dbPort)+'/postgres'
            else:
                return 'postgresql://postgres:'+quote_plus(os.environ['DEFAULTPASSWORD'])+'@localhost:'+str(dbPort)+'/admindb'
        case 'mysql':
            if is_initialconnection:
                return {
                    'host': 'localhost',
                    'user': 'root',
                    'password': os.environ['DEFAULTPASSWORD'],
                    'port': dbPort
                }
            else:
                return {
                    'host': 'localhost',
                    'user': 'root',
                    'password': os.environ['DEFAULTPASSWORD'],
                    'port': dbPort,
                    'database': 'admindb'
                }
        case 'mssql':
            if is_initialconnection:
                return 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;PORT='+str(dbPort)+';DATABASE=master;UID=sa;PWD='+quote_plus(os.environ['DEFAULTPASSWORD'])+';TDS_Version=8.0;'
            else:
                return 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;PORT='+str(dbPort)+';DATABASE=admindb;UID=sa;PWD='+quote_plus(os.environ['DEFAULTPASSWORD'])+';TDS_Version=8.0;'
        

# any incoming API call that has a DBtype uses this function to check for compatibility
def checkDbCompat(dbType):
    match dbType.lower():
        case 'postgres':
            return True
        case 'mysql':
            return True
        case 'mssql':
            if "arm" in platform.machine() or "aarch" in platform.machine():
                # driver not available for ARM, speculative ETA spring 2022
                return False
            else:
                return True