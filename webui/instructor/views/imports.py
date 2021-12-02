import csv, io
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse

from ..models import Student, StudentGroup


# imports a csv file with students for a specific group
def import_students_togroup(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        group = StudentGroup.objects.get(id=group_id)
        csvfile = request.FILES['csvfile']
        if csvfile.name.endswith('.csv'):
            csvdata = csvfile.read().decode('utf-8')
            datastream = io.StringIO(csvdata)

            reader = csv.reader(datastream, delimiter=',', quotechar='"')
            student_list = []
            for row in reader:
                student = Student(
                    first_name = row[0],
                    last_name = row[1],
                    student_custom_id = row[2],
                    student_group = group
                )
                student_list.append(student)
            if len(student_list) > 0:
                Student.objects.bulk_create(student_list)
            return HttpResponseRedirect(reverse('instructor:studentgroupdetails', args=(group_id,)))
        else:
            return HttpResponse('Only csv files are supported')
    else:
        raise Http404
