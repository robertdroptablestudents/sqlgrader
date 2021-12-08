from django.db import models

DBTYPES = [('POSTGRES', 'postgres'), ('MYSQL', 'mysql'), ('MSSQL', 'mssql')]

class Assignment(models.Model):
    assignment_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.assignment_name

class AssignmentEnvironment(models.Model):
    db_type = models.CharField(max_length=100, choices=DBTYPES, default='POSTGRES')
    assignment = models.ForeignKey(Assignment, on_delete=models.SET(''), blank=True)
    def get_file_path(self, filename):
        return 'assignmentenv_{0}/{1}'.format(self.id, filename)
    initial_code = models.FileField(upload_to=get_file_path, blank=True, null=True)

class AssignmentItem(models.Model):
    ASSIGNMENT_TYPES = [('QUERY','Query'), ('SCHEMA','Schema')]
    assignment = models.ForeignKey(Assignment, on_delete=models.SET(''), blank=True)
    assignmentenvironment = models.ForeignKey(AssignmentEnvironment, on_delete=models.SET(''), blank=True)
    item_number = models.IntegerField()
    item_type = models.CharField(max_length=25, choices=ASSIGNMENT_TYPES, default='QUERY')
    def get_file_path(self, filename):
        return 'assignmentitem_{0}/{1}'.format(self.id, filename)
    item_solution = models.FileField(upload_to=get_file_path, blank=True, null=True)
    item_name = models.CharField(max_length=100, blank=True)

# an instance of an environment for a specific item and scenario for testing
class EnvironmentInstance(models.Model):
    item = models.ForeignKey(AssignmentItem, on_delete=models.SET(''), blank=True)
    environment_name = models.CharField(max_length=100, default='Default')
    def get_file_path(self, filename):
        return 'itemenv_{0}/{1}'.format(self.id, filename)
    initial_code = models.FileField(upload_to=get_file_path, blank=True, null=True)
    has_datagen = models.BooleanField(default=False)
    datagen_status = models.CharField(max_length=100, blank=True)


# TODO this item is not yet used, could be used for more robust dataset creation
class EnvironmentInstanceDataset(models.Model):
    environmentinstance = models.ForeignKey(EnvironmentInstance, on_delete=models.SET(''), blank=True)
    dataset_table_name = models.CharField(max_length=100)
    def get_file_path(self):
        return 'itemenv_{0}/{1}/'.format(self.itemenvironment.id, self.dataset_table_name)
    dataset_file = models.FileField(upload_to=get_file_path, blank=True, null=True)