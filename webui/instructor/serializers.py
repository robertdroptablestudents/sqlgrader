from rest_framework import serializers
from . import models


# chained serializers to GradingAssignmentSerializer
class AssignmentEnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssignmentEnvironment
        fields = ['db_type', 'initial_code']

class AssignmentItemSerializer(serializers.ModelSerializer):
    assignmentenvironment = AssignmentEnvironmentSerializer(read_only=True)
    class Meta:
        model = models.AssignmentItem
        fields = '__all__'

class GradingAssignmentSerializer(serializers.ModelSerializer):
    assignment_item = AssignmentItemSerializer(many=False)
    class Meta:
        model = models.GradingAssignment
        fields = '__all__'


# single serializer for EnvrionmentInstances
class EnvironmentInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EnvironmentInstance
        fields = '__all__'

# chained serializers to StudentSubmissionItems
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Student
        fields = '__all__'

class StudentSubmissionSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    class Meta:
        model = models.StudentSubmission
        fields = '__all__'

class SubmissionItemSerializer(serializers.ModelSerializer):
    student_submission = StudentSubmissionSerializer(many=False, read_only=True)
    class Meta:
        model = models.StudentSubmissionItem
        fields = '__all__'
