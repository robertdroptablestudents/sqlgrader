from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse

from ..models import Student, StudentGroup, Assignment, AssignmentEnvironment, AssignmentItem, StudentSubmission, StudentSubmissionItem


def index(request):
    return render(request, 'instructor/index.html')

def studentlist(request):
    full_student_list = Student.objects.all()
    active_groups = StudentGroup.objects.filter(is_active=True)
    groups_for_newstudent = StudentGroup.objects.filter(is_active=True).values()
    context = {
        'full_student_list': full_student_list,
        'active_groups': active_groups,
        'groups_for_newstudent': groups_for_newstudent,
    }
    return render(request, 'instructor/studentlist.html', context)

def studentdetails(request, student_id):
    try:
        student = Student.objects.get(pk=student_id)
        student_submissions = StudentSubmission.objects.filter(student=student)
        context = {
            'student': student,
            'student_submissions': student_submissions,
        }
    except Student.DoesNotExist:
        raise Http404("student does not exist")

    return render(request, 'instructor/studentinfo.html', context)

def newstudent(request):
    try:
        student_group = StudentGroup.objects.get(pk=request.POST['student_group_id'])
        new_student = Student.objects.create(first_name=request.POST['first_name'], last_name=request.POST['last_name'], student_custom_id=request.POST['student_custom_id'], student_group=student_group)
        new_student.save()
    except Exception as e:
        print(e)
        raise Http404("error creating student")
    return HttpResponseRedirect(reverse('instructor:studentlist'))

def studentgroupdetails(request, studentgroup_id):
    try:
        group = StudentGroup.objects.get(pk=studentgroup_id)
        students = Student.objects.filter(student_group=group)
    except StudentGroup.DoesNotExist:
        raise Http404("group does not exist")

    return render(request, 'instructor/studentgroupdetails.html', {'group': group, 'students': students})

def studentgroup(request):
    try:
        new_group = StudentGroup.objects.create(group_name=request.POST['group_name'], is_active=True)
        new_group.save()
    except:
        raise Http404("error creating group")
    return HttpResponseRedirect(reverse('instructor:studentlist'))

def studentgroupedit(request):
    try:
        group = StudentGroup.objects.get(pk=request.POST['studentgroup_id'])
        group.group_name = request.POST['group_name']
        if 'is_active' in request.POST:
            group.is_active = True
        else:
            group.is_active = False
        group.save()
    except:
        raise Http404("error editing group")
    return HttpResponseRedirect(reverse('instructor:studentgroupdetails', args=(group.id,)))
