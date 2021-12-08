import pyodbc

from faker import Faker
from faker.providers import python

dataset_size = 10
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

def generate_data(column_type, isUnique, data_size):
    if column_type == 'string':
        if isUnique:
            return fake.unique.pystr(min_chars=1, max_chars=data_size)
        else:
            return fake.pystr(min_chars=1, max_chars=data_size)
    elif column_type in ('int', 'smallint', 'tinyint', 'bigint'):
        if isUnique:
            return fake.unique.pyint(min_value=INT_SETS[column_type]['min'], max_value=INT_SETS[column_type]['max'])
        else:
            return fake.pyint(min_value=INT_SETS[column_type]['min'], max_value=INT_SETS[column_type]['max'])
    elif column_type == 'float':
        if isUnique:
            return fake.unique.pyfloat()
        else:
            return fake.pyfloat()
    else:
        return ''


def main():
    current_columns = [
        { 'name': 'firstcolumn', 'type': 'tinyint', 'isUnique': False, 'length': 3 },
        { 'name': 'secondcolumn', 'type': 'int', 'isUnique': True, 'length': 5 },
        { 'name': 'thirdcolumn', 'type': 'smallint',  'isUnique': False, 'length': 10 },
    ]


    for i in range(dataset_size):
        for column in current_columns:
            print(generate_data(column['type'], column['isUnique'], column['length']),end=',')
        print('\n')


main()