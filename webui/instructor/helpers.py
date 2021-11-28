
# converts a dict to a return object with value and label
def convert_dict_select(somedict):
    return [{'value': k, 'label': v} for k, v in somedict.items()]
