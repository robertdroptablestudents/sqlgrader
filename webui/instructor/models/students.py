from django.db import models
from django.conf import settings
import os

from .assignments import EnvironmentInstance

class StudentGroup(models.Model):
    group_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.group_name

    def get_student_count(self):
        return 1
        # until I figure that out

class Student(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    student_custom_id = models.CharField(max_length=100)
    student_group = models.ForeignKey(StudentGroup, on_delete=models.SET(''), blank=True)

    def __str__(self):
        return self.first_name + " " + self.last_name + " (" + self.student_custom_id + ")"

class StudentSubmission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET(''))
    assignment = models.ForeignKey('Assignment', on_delete=models.SET(''))
    submission_date = models.DateTimeField(auto_now_add=True)
    is_graded = models.BooleanField(default=False)
    grade = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.student.first_name + " " + self.student.last_name + " (" + self.student.student_custom_id + ")"

class StudentSubmissionItem(models.Model):
    student_submission = models.ForeignKey(StudentSubmission, on_delete=models.SET(''))
    assignment_item = models.ForeignKey('AssignmentItem', on_delete=models.SET(''))
    is_active = models.BooleanField(default=True)
    def get_file_path(self,filename):
        return 'submissions/assign{0}/item{1}/student{2}/{3}'.format(self.assignment_item.assignment.id, self.assignment_item.id, self.student_submission.student.id, filename)
    submission_file = models.FileField(upload_to=get_file_path, blank=True, null=True)
    grading_log = models.TextField(blank=True, null=True)
    score_primary = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    score_secondary = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    def gradinglogupdate(self, log_message):
        if self.grading_log is None:
            self.grading_log = log_message
        else:
            self.grading_log = self.grading_log + '\n' + log_message
        self.save()

class StudentSubmissionItemGrade(models.Model):
    student_submission_item = models.ForeignKey(StudentSubmissionItem, on_delete=models.SET(''))
    environment_instance = models.ForeignKey(EnvironmentInstance, on_delete=models.SET(''))
    graded_date = models.DateTimeField(auto_now_add=True)
    points_possible = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    points_earned = models.DecimalField(max_digits=5, decimal_places=2, default=0)