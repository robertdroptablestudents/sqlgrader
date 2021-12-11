from django.http import HttpResponse, Http404, HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import GradingProcess, GradingAssignment, GradingContainer, Assignment, AssignmentItem, AssignmentEnvironment, StudentSubmissionItem, EnvironmentInstance, StudentSubmissionItemGrade

from ..serializers import GradingAssignmentSerializer, EnvironmentInstanceSerializer, SubmissionItemSerializer

class get_environmentinstances(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, assignmentitem_id):
        try:
            assignment_item = AssignmentItem.objects.get(pk=assignmentitem_id)
            environment_instances =  EnvironmentInstanceSerializer(EnvironmentInstance.objects.filter(item=assignment_item), many=True)
        except AssignmentItem.DoesNotExist:
            raise Http404("assignment item does not exist")
        return Response(environment_instances.data)

class get_studentsubmissions(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, assignmentitem_id):
        try:
            student_submissions = SubmissionItemSerializer(StudentSubmissionItem.objects.filter(assignment_item_id=assignmentitem_id), many=True)
        except AssignmentItem.DoesNotExist:
            raise Http404("assignment item does not exist")
        return Response(student_submissions.data)

class update_gradingstatus(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        # api endpoint to update grading status, returns 200
        try:
            grading_process_id = request.data['grading_process_id']
            grading_process = GradingProcess.objects.get(pk=grading_process_id)
        except GradingProcess.DoesNotExist:
            raise Http404("grading process does not exist")

        # if status_message is not empty, update grading status
        if 'status_message' in request.data and request.data['status_message'] != '':
            grading_process.gradingstatusupdate(request.data['status_message'])
        # if log_update is not empty, add to grading_process log
        if 'log_update' in request.data and request.data['log_update'] != '':
            grading_process.gradinglogupdate(request.data['log_update'])

        return HttpResponse(status=200)

# update the student submission based on individual environment grades
class update_studentsubmissionquery(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        # api endpoint to update student submission, returns 200
        # request.data should contain: assignment_item_id

        try:
            assignment_item = AssignmentItem.objects.get(pk=request.data['assignment_item_id'])
        except AssignmentItem.DoesNotExist:
            raise Http404("assignment item does not exist")

        # get all student submissions for this assignment item
        student_submissions = StudentSubmissionItem.objects.filter(assignment_item=assignment_item)
        
        for student_submission in student_submissions:
            item_grades = StudentSubmissionItemGrade.objects.filter(student_submission_item=student_submission)
            total_points_possible = 0.0
            total_points_earned = 0.0
            for item_grade in item_grades:
                total_points_possible += item_grade.points_possible
                total_points_earned += item_grade.points_earned
            if total_points_possible > 0:
                student_submission.score_primary = total_points_earned / total_points_possible
            else:
                student_submission.score_primary = 0.0
            student_submission.save()

        return HttpResponse(status=200)


# update student submission items - either root item for schema or individual query environments
class update_studentsubmissionitem(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        # api endpoint to update student submission item - grading_log, score_primary, score_secondary, points_possible, points_earned
        try:
            student_submission_item_id = request.data['student_submission_item_id']
            student_submission_item = StudentSubmissionItem.objects.get(pk=student_submission_item_id)
        except StudentSubmissionItem.DoesNotExist:
            raise Http404("student submission item does not exist")
        

        # if grading_log is not empty, add to grading_log
        if 'grading_log' in request.data and request.data['grading_log'] != '':
            student_submission_item.gradinglogupdate(request.data['grading_log'])

        if 'score_primary' in request.data and request.data['score_primary'] != '':
            student_submission_item.score_primary = request.data['score_primary']
            student_submission_item.save()
        if 'score_secondary' in request.data and request.data['score_secondary'] != '':
            student_submission_item.score_secondary = request.data['score_secondary']
            student_submission_item.save()


        if 'environment_instance_id' in request.data:
            environment_instance = EnvironmentInstance.objects.get(pk=request.data['environment_instance_id'])
            # create a new StudentSubmissionItemGrade - points_possible, points_earned - based on the query grade info
            new_grade = StudentSubmissionItemGrade(student_submission_item=student_submission_item, environment_instance=environment_instance, points_possible=environment_instance.points_possible, points_earned= float(environment_instance.points_possible) * ( float(request.data['points_earned'])) /float(request.data['points_possible']) )
            new_grade.save()
        else:
            environment_instance = EnvironmentInstance.objects.get(item=student_submission_item.assignment_item)
            # create a new StudentSubmissionItemGrade - based on the schema score_primary
            new_grade = StudentSubmissionItemGrade(student_submission_item=student_submission_item, environment_instance=environment_instance, points_possible=environment_instance.points_possible, points_earned= float(request.data['score_primary']) )
            new_grade.save()

        return HttpResponse(status=200)

# mark an environment instance for datagen completion
class update_environmentinstance(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        print(request)
        #api endpoint to update environment instance - has_datagen and datagen_status
        try:
            environment_instance_id = request.data['environment_instance_id']
            environment_instance = EnvironmentInstance.objects.get(pk=environment_instance_id)
        except EnvironmentInstance.DoesNotExist:
            raise Http404("environment instance does not exist")
        
        if 'has_datagen' in request.data:
            environment_instance.has_datagen = request.data['has_datagen']
        if 'datagen_status' in request.data and request.data['datagen_status'] != '':
            environment_instance.datagen_status = request.data['datagen_status']

        environment_instance.save()

        return HttpResponse(status=200)