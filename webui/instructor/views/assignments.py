from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User

import requests, os
from rest_framework.authtoken.models import Token

from ..models import Student, StudentGroup, Assignment, AssignmentEnvironment, AssignmentItem, EnvironmentInstance, GradingProcess, DBTYPES
from .grading import APIURL

# return full assignment list view
def assignmentlist(request):
    full_assignment_list = Assignment.objects.all()
    context = {
        'full_assignment_list': full_assignment_list,
        'dbtypes': DBTYPES,
    }
    return render(request, 'instructor/assignmentlist.html', context)

# create new assignment with a default environment
def assignment(request):
    try:
        new_assignment = Assignment.objects.create(assignment_name=request.POST['assignment_name'])
        new_assignment.save()
        print(new_assignment.assignment_name)
        new_environment = AssignmentEnvironment.objects.create(assignment=new_assignment, db_type=request.POST['db_type'])
        new_environment.save()
    except:
        raise Http404("error creating assignment")
    return HttpResponseRedirect(reverse('instructor:assignmentdetails', args=(new_assignment.id,)))

# create new assignment item on an assignment
def assignmentitem(request):
    try:
        assignment = Assignment.objects.get(pk=request.POST['assignment_id'])
        new_item = AssignmentItem.objects.create(assignment=assignment, item_number=request.POST['item_number'], item_type=request.POST['assignment_type'], assignmentenvironment=AssignmentEnvironment.objects.filter(assignment=assignment).first())
        new_item.save()
        default_environment = EnvironmentInstance.objects.create(item=new_item, environment_name='default')
        default_environment.save()
    except Assignment.DoesNotExist:
        raise Http404("assignment does not exist")
    return HttpResponseRedirect(reverse('instructor:assignmentdetails', args=(assignment.id,)))

def assignmentitemdetails(request, assignmentitem_id):
    try:
        assignment_item = AssignmentItem.objects.get(pk=assignmentitem_id)
        environment_instance = EnvironmentInstance.objects.filter(item=assignment_item)
        # for each environment instance, check the instance folder for files
        for instance in environment_instance:
            datagenpath = settings.MEDIA_ROOT + '/'+ instance.get_file_path(filename='')+'datagen/'
            # check if datagen folder exists
            if os.path.isdir(datagenpath):
                datagenfiles = os.listdir(settings.MEDIA_ROOT + '/'+ instance.get_file_path(filename='')+'datagen/')
            else:
                datagenfiles = []

            if instance.initial_code:
                instance.allfiles = [instance.initial_code.name] + datagenfiles
            else:
                instance.allfiles = datagenfiles

    except AssignmentItem.DoesNotExist:
        raise Http404("assignment item does not exist")
    context = {
        'assignment_item': assignment_item,
        'environment_instance': environment_instance,
    }
    return render(request, 'instructor/assignmentitem.html', context)

def assignmentitemedit(request):
    try:
        assignment_item = AssignmentItem.objects.get(pk=request.POST['assignment_item_id'])
        assignment_item.item_name = request.POST['item_name']
        # make sure file upload wasn't sent as a blank item
        if 'item_code' not in request.POST:
            assignment_item.item_solution = request.FILES['item_code']
        assignment_item.save()
    except AssignmentItem.DoesNotExist:
        raise Http404("assignment item does not exist")
    return HttpResponseRedirect(reverse('instructor:assignmentitemdetails', args=(assignment_item.id,)))


# creates new EnvironmentInstance
# form elements: assignment_item_id, environment_name, initial_code
def environmentinstance(request):
    new_environment = EnvironmentInstance.objects.create(item=AssignmentItem.objects.get(pk=request.POST['assignment_item_id']), environment_name=request.POST['environment_name'], points_possible=request.POST['points_possible'])
    new_environment.save()
    if 'initial_code' in request.FILES:
        new_environment.initial_code = request.FILES['initial_code']
        new_environment.save()
    return HttpResponseRedirect(reverse('instructor:assignmentitemdetails', args=(request.POST['assignment_item_id'],)))

# edits an EnvironmentInstance
# form elements: environment_instance_id, environment_name, initial_code
def environmentinstanceedit(request):
    try:
        environment_instance = EnvironmentInstance.objects.get(pk=request.POST['environment_instance_id'])
        environment_instance.environment_name = request.POST['environment_name']
        if 'initial_code' in request.FILES:
            environment_instance.initial_code = request.FILES['initial_code']
        if 'points_possible' in request.POST:
            environment_instance.points_possible = request.POST['points_possible']
        environment_instance.save()
    except EnvironmentInstance.DoesNotExist:
        raise Http404("environment instance does not exist")
    return HttpResponseRedirect(reverse('instructor:assignmentitemdetails', args=(environment_instance.item.id,)))


# return detals for a single assignment
def assignmentdetails(request, assignment_id):
    try:
        assignment = Assignment.objects.get(pk=assignment_id)
        assignment_environments = AssignmentEnvironment.objects.filter(assignment=assignment)
        assignment_items = AssignmentItem.objects.filter(assignment=assignment).order_by('item_number')
        grading_processes = GradingProcess.objects.filter(assignment=assignment)
    except Assignment.DoesNotExist:
        raise Http404("assignment does not exist")
    context = {
        'assignment': assignment,
        'assignment_environments': assignment_environments,
        'assignmenttypes': AssignmentItem.ASSIGNMENT_TYPES,
        'assignment_items': assignment_items,
        'grading_processes': grading_processes,
    }
    return render(request, 'instructor/assignment.html', context)

# edit a single assignment
def assignmentedit(request):
    try:
        assignment = Assignment.objects.get(pk=request.POST['assignment_id'])
        assignment.assignment_name = request.POST['assignment_name']
        if 'is_active' in request.POST:
            assignment.is_active = True
        else:
            assignment.is_active = False
        assignment.save()
    except Assignment.DoesNotExist:
        raise Http404("assignment does not exist")
    return HttpResponseRedirect(reverse('instructor:assignmentdetails', args=(assignment.id,)))

# upload initial_code file in request for assignmentenvironment
def assignmentenvironmentedit(request):
    try:
        assignment_environment = AssignmentEnvironment.objects.get(pk=request.POST['assignment_environment_id'])
        assignment_environment.initial_code = request.FILES['initial_code']
        assignment_environment.save()
    except AssignmentEnvironment.DoesNotExist:
        raise Http404("assignment environment does not exist")
    return HttpResponseRedirect(reverse('instructor:assignmentdetails', args=(assignment_environment.assignment.id,)))

# remove an initial_code file from assignmentenvironment
def assignmentenvironmentclear(request):
    try:
        assignment_environment = AssignmentEnvironment.objects.get(pk=request.POST['assignment_environment_id'])
        assignment_environment.initial_code = None
        assignment_environment.save()
    except AssignmentEnvironment.DoesNotExist:
        raise Http404("assignment environment does not exist")
    return HttpResponseRedirect(reverse('instructor:assignmentdetails', args=(assignment_environment.assignment.id,)))


def datagenstart(request):
    """
    request contains environment_instance_id
    starts datagen API
    sends POST body with db_type, assignment_item_id, initial_code
    """
    environment_instance_id = request.POST['environment_instance_id']
    assignment_item_id = request.POST['assignment_item_id']
    initial_code = request.POST['initial_code']
    row_count = request.POST['row_count']


    # get assignmentenvironment
    assignment_item = AssignmentItem.objects.get(pk=assignment_item_id)
    assignment_environment = AssignmentEnvironment.objects.get(pk=assignment_item.assignmentenvironment.id)
    db_type = assignment_environment.db_type
    env_code = assignment_environment.initial_code.name

    postbody = {
        'db_type': db_type,
        'assignment_item_id': assignment_item_id,
        'env_code': env_code,
        'initial_code': initial_code,
        'row_count': row_count,
    }

    # get token to pass to API
    adminuser = User.objects.get(username='admin')
    token = Token.objects.get(user=adminuser.id)

    # make a post request to APIURL /datagen/<grading_process_id>
    # with grading_assignmentitem as json
    # token.key in header
    callURL = APIURL+'datagen/'+environment_instance_id
    headers = {'apikey': token.key}
    startGrading = requests.post(callURL, json=postbody, headers=headers)
    print(postbody)

    environmentinstance = EnvironmentInstance.objects.get(pk=environment_instance_id)
    if startGrading.status_code != 200:
        # set datagen_status to error
        environmentinstance.datagen_status = 'error'
    else:
        # set datagen_status to running
        environmentinstance.has_datagen = True
        environmentinstance.datagen_status = 'running'
    environmentinstance.save()

    return HttpResponseRedirect(reverse('instructor:assignmentitemdetails', args=(request.POST['assignment_item_id'],)))