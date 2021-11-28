from django.shortcuts import render
# from django.template import loader
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse

from ..models import Student, StudentGroup, Assignment, AssignmentEnvironment, AssignmentItem, EnvironmentInstance, DBTYPES

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
    new_environment = EnvironmentInstance.objects.create(item=AssignmentItem.objects.get(pk=request.POST['assignment_item_id']), environment_name=request.POST['environment_name'])
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
    except Assignment.DoesNotExist:
        raise Http404("assignment does not exist")
    context = {
        'assignment': assignment,
        'assignment_environments': assignment_environments,
        'assignmenttypes': AssignmentItem.ASSIGNMENT_TYPES,
        'assignment_items': assignment_items,
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
