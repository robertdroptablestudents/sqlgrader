from django.db import models
from .assignments import Assignment, AssignmentItem, DBTYPES

class GradingProcess(models.Model):
    """
    This model is used to keep track of the current grading process.
    """
    PROCESS_STATUS = [('READY', 'Ready'), ('INITIALIZING','Initializing'), ('GRADING','Grading'), ('FINISHED','Finished'), ('ERROR','Error')]
    process_status = models.CharField(max_length=20, choices=PROCESS_STATUS, default='Ready')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    process_start_time = models.DateTimeField(auto_now_add=True)
    process_end_time = models.DateTimeField(null=True)
    process_error = models.TextField(null=True)
    process_log = models.TextField(null=True)

    def __str__(self):
        return self.process_status

    def gradingstatusupdate(self, status):
        self.process_status = status
        print(status)
        self.save()
    
    def gradinglogupdate(self, log_message):
        if self.process_log is None:
            self.process_log = log_message
        else:
            self.process_log = self.process_log + '\n' + log_message
        self.save()

class GradingAssignment(models.Model):
    """
    Tracks the assignments or assignment items associated with a grading process.
    """
    grading_process = models.ForeignKey(GradingProcess, on_delete=models.CASCADE)
    assignment_item = models.ForeignKey(AssignmentItem, on_delete=models.SET_NULL, null=True)

    def get_dbtype(self):
        assignment_environment = self.assignment_item.assignmentenvironment
        return assignment_environment.db_type.lower()


class GradingContainer(models.Model):
    """
    Tracks the containers associated with a grading process.
    """
    container_id = models.CharField(max_length=100)
    container_name = models.CharField(max_length=100)
    container_port = models.IntegerField()
    grading_process = models.ForeignKey(GradingProcess, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    db_type = models.CharField(max_length=100, choices=DBTYPES, default='POSTGRES')