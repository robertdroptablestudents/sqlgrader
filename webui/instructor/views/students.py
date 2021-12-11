from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse


from ..models import Student, StudentGroup, Assignment, AssignmentEnvironment, AssignmentItem, StudentSubmission, StudentSubmissionItem, StudentSubmissionItemGrade
from ..tables import studenttables

def index(request):
    return render(request, 'instructor/index.html')

def studentlist(request):
    full_student_list = Student.objects.all()
    student_table = studenttables.StudentTable(full_student_list)
    student_table.paginate(page=request.GET.get('page', 1), per_page=15)
    active_groups = StudentGroup.objects.filter(is_active=True)
    groups_for_newstudent = StudentGroup.objects.filter(is_active=True).values()
    context = {
        'full_student_list': student_table,
        'active_groups': active_groups,
        'groups_for_newstudent': groups_for_newstudent,
    }
    return render(request, 'instructor/studentlist.html', context)

def studentdetails(request, student_id):
    try:
        student = Student.objects.get(pk=student_id)
        student_submissions = StudentSubmission.objects.filter(student=student)
        student_group_options = StudentGroup.objects.filter(is_active=True).values()
        context = {
            'student': student,
            'student_submissions': student_submissions,
            'student_group_options': student_group_options,
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

def studentedit(request):
    try:
        student = Student.objects.get(pk=request.POST['student_id'])
        student.first_name = request.POST['first_name']
        student.last_name = request.POST['last_name']
        student.student_custom_id = request.POST['student_custom_id']
        student.student_group = StudentGroup.objects.get(pk=request.POST['student_group_id'])
        if 'is_active' in request.POST:
            student.is_active = True
        else:
            student.is_active = False
        student.save()
    except:
        raise Http404("error editing student")
    return HttpResponseRedirect(reverse('instructor:studentdetails', args=(student.id,)))

def studentgroupdetails(request, studentgroup_id):
    try:
        group = StudentGroup.objects.get(pk=studentgroup_id)
        students = Student.objects.filter(student_group=group)
        student_table = studenttables.StudentGroupTable(students)
        student_table.paginate(page=request.GET.get('page', 1), per_page=15)
    except StudentGroup.DoesNotExist:
        raise Http404("group does not exist")

    return render(request, 'instructor/studentgroupdetails.html', {'group': group, 'student_table': student_table})

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


def submissiondetails(request, submission_id):
    submission = StudentSubmission.objects.get(pk=submission_id)
    assignment_items = AssignmentItem.objects.filter(assignment=submission.assignment)
    submission_items = StudentSubmissionItem.objects.filter(student_submission=submission)
    submission_grades = StudentSubmissionItemGrade.objects.filter(student_submission_item__in=submission_items)
    grade_table = studenttables.StudentSubmissionItemGradeTable(submission_grades)
    
    context = {
        'submission': submission,
        'submission_items': submission_items,
        'submission_grades': submission_grades,
        'assignment_items': assignment_items,
        'grade_table': grade_table,
    }

    return render(request, 'instructor/studentsubmission.html', context)