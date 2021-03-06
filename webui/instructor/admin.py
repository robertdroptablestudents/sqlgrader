from django.contrib import admin

from .models import Student, StudentGroup, Assignment, AssignmentEnvironment, AssignmentItem, EnvironmentInstance, EnvironmentInstanceDataset, StudentSubmission, StudentSubmissionItem, StudentSubmissionItemGrade, GradingProcess, GradingAssignment, GradingContainer

admin.site.register([Student, StudentGroup, Assignment, AssignmentEnvironment, AssignmentItem, EnvironmentInstance, EnvironmentInstanceDataset, StudentSubmission, StudentSubmissionItem, StudentSubmissionItemGrade, GradingProcess, GradingAssignment, GradingContainer])
