from configparser import Error
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse

import requests
from rest_framework.authtoken.models import Token
import os

from ..models import GradingProcess, GradingAssignment, GradingContainer, Assignment, AssignmentItem, AssignmentEnvironment, StudentSubmissionItem, EnvironmentInstance

from ..serializers import GradingAssignmentSerializer, EnvironmentInstanceSerializer, SubmissionItemSerializer

APIURL = "http://localhost:5000/"

def gradingoverview(request):
    full_grading_list = GradingProcess.objects.all()
    assignments_tograde = Assignment.objects.filter(is_active=True).values()
    context = {
        'full_grading_list': full_grading_list,
        'assignments_tograde': assignments_tograde,
    }
    return render(request, 'instructor/gradingoverview.html', context)

# creates a new grading process
# form element default_assignment
def gradingprocess(request):
    try:
        new_gradingprocess = GradingProcess.objects.create(assignment=Assignment.objects.get(id=request.POST['default_assignment']))
        new_gradingprocess.save()
        for new_assignment_item in AssignmentItem.objects.filter(assignment__is_active=True):
            new_gradingassignment = GradingAssignment.objects.create(assignment_item=new_assignment_item, grading_process=new_gradingprocess)
            new_gradingassignment.save()
    except:
        raise Http404("Error creating grading process")
    return HttpResponseRedirect(reverse('instructor:gradingoverview'))


# grading process detail view
def gradingdetails(request, gradingprocess_id):
    grading_process = GradingProcess.objects.get(pk=gradingprocess_id)
    grading_assignments = GradingAssignment.objects.filter(grading_process=grading_process)
    grading_containers = GradingContainer.objects.filter(grading_process=grading_process)
    assignment_items = AssignmentItem.objects.filter(assignment=grading_process.assignment)
    context = {
        'grading_process': grading_process,
        'grading_assignments': grading_assignments,
        'grading_containers': grading_containers,
        'assignment_items': assignment_items,
    }
    return render(request, 'instructor/gradingdetails.html', context)

# create new gradingassignment
# form elements grading_process_id, assignment_item
def gradingitem(request):
    try:
        new_gradingassignment = GradingAssignment.objects.create(grading_process=GradingProcess.objects.get(id=request.POST['grading_process_id']), assignment_item=AssignmentItem.objects.get(id=request.POST['assignment_item']))
        new_gradingassignment.save()
    except:
        raise Http404("Error creating grading assignment")
    return HttpResponseRedirect(reverse('instructor:gradingdetails', args=(request.POST['grading_process_id'],)))


def gradingstart(request):
    """
    request contains gradingprocess_id
    for each gradingassignment, initialize and grade
    """
    grading_process_id = request.POST['grading_process_id']
    grading_process = GradingProcess.objects.get(pk=grading_process_id)
    grading_process.gradingstatusupdate('Initializing')
    grading_assignmentitem = GradingAssignmentSerializer(GradingAssignment.objects.filter(grading_process=grading_process), many=True)

    # put token in an env variable
    token = Token.objects.get(user=request.user)

    # make a post request to APIURL /gradingrunprocess/<grading_process_id>
    # with grading_assignmentitem as json
    # token.key in header
    callURL = APIURL+'grading/'+grading_process_id
    headers = {'apikey': token.key}
    startGrading = requests.post(callURL, json=grading_assignmentitem.data, headers=headers)

    if startGrading.status_code != 200:
        grading_process.gradingstatusupdate('Error initializing grading service')

    return HttpResponseRedirect(reverse('instructor:gradingdetails', args=(request.POST['grading_process_id'],)))
