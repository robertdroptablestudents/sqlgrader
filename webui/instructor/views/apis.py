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

class update_studentsubmissionitem(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        # api endpoint to update student submission item - grading_log, score_primary, score_secondary, points_possible, points_earned
        try:
            student_submission_item_id = request.data['student_submission_item_id']
            student_submission_item = StudentSubmissionItem.objects.get(pk=student_submission_item_id)
        except StudentSubmissionItem.DoesNotExist:
            raise Http404("student submission item does not exist")
        
        try:
            environment_instance = EnvironmentInstance.objects.get(pk=request.data['environment_instance_id'])
        except EnvironmentInstance.DoesNotExist:
            raise Http404("environment instance does not exist")

        # if grading_log is not empty, add to grading_log
        if 'grading_log' in request.data and request.data['grading_log'] != '':
            student_submission_item.gradinglogupdate(request.data['grading_log'])

        if 'score_primary' in request.data and request.data['score_primary'] != '':
            student_submission_item.score_primary = request.data['score_primary']
            student_submission_item.save()
        if 'score_secondary' in request.data and request.data['score_secondary'] != '':
            student_submission_item.score_secondary = request.data['score_secondary']
            student_submission_item.save()

        if 'points_possible' in request.data and request.data['points_possible'] != '':
            # create a new StudentSubmissionItemGrade - points_possible, points_earned
            new_grade = StudentSubmissionItemGrade(student_submission_item=student_submission_item, environment_instance=environment_instance, points_possible=request.data['points_possible'], points_earned=request.data['points_earned'])
            new_grade.save()

        return HttpResponse(status=200)

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
        # if 'has_datagen' in request.data and request.data['has_datagen'] == "False":
        #     environment_instance.has_datagen = False
        if 'datagen_status' in request.data and request.data['datagen_status'] != '':
            environment_instance.datagen_status = request.data['datagen_status']

        environment_instance.save()

        return HttpResponse(status=200)