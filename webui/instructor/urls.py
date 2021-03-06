from django.urls import path

from . import views

app_name = 'instructor'
urlpatterns = [
    path('', views.index, name='index'),

    path('students', views.studentlist, name='studentlist'),
    path('studentgroup', views.studentgroup, name='studentgroup'),
    path('studentgroup/<int:studentgroup_id>', views.studentgroupdetails, name='studentgroupdetails'),
    path('student/<int:student_id>', views.studentdetails, name='studentdetails'),
    path('newstudent', views.newstudent, name='newstudent'),
    path('studentgroupedit', views.studentgroupedit, name='studentgroupedit'),
    path('studentedit', views.studentedit, name='studentedit'),

    path('student/submission/<int:submission_id>', views.submissiondetails, name='submissiondetails'),

    path('assignments', views.assignmentlist, name='assignmentlist'),
    path('assignment', views.assignment, name='assignment'),
    path('assignmentedit', views.assignmentedit, name='assignmentedit'),
    path('assignment/<int:assignment_id>', views.assignmentdetails, name='assignmentdetails'),

    path('assignmentenvironmentedit', views.assignmentenvironmentedit, name='assignmentenvironmentedit'),
    path('assignmentenvironmentclear', views.assignmentenvironmentclear, name='assignmentenvironmentclear'),

    path('assignmentitem', views.assignmentitem, name='assignmentitem'),
    path('assignmentitemedit', views.assignmentitemedit, name='assignmentitemedit'),
    path('assignmentitemdetails/<int:assignmentitem_id>', views.assignmentitemdetails, name='assignmentitemdetails'),
    path('environmentinstancedatagen', views.datagenstart, name='environmentinstancedatagen'),

    path('environmentinstance', views.environmentinstance, name='environmentinstance'),
    path('environmentinstanceedit', views.environmentinstanceedit, name='environmentinstanceedit'),

    path('grading', views.gradingoverview, name='gradingoverview'),
    path('gradingprocess', views.gradingprocess, name='gradingprocess'),
    path('grading/<int:gradingprocess_id>', views.gradingdetails, name='gradingdetails'),
    path('gradingitem', views.gradingitem, name='gradingitem'),
    path('gradingstart', views.gradingstart, name='gradingstart'),
    path('gradingitemdetails/<int:gradingprocess_id>/<int:assignmentitem_id>', views.gradingitemdetails, name='gradingitemdetails'),

    # api endpoints
    path('api_updategradingstatus', views.update_gradingstatus.as_view(), name='api_updategradingstatus'),
    path('api_getenvironmentinstances/<int:assignmentitem_id>', views.get_environmentinstances.as_view(), name='api_getenvironmentinstances'),
    path('api_getstudentsubmissions/<int:assignmentitem_id>', views.get_studentsubmissions.as_view(), name='api_getstudentsubmissions'),
    path('api_updatestudentsubmissionitem', views.update_studentsubmissionitem.as_view(), name='api_updatestudentsubmissionitem'),
    path('api_updateenvironmentinstance', views.update_environmentinstance.as_view(), name='api_updateenvironmentinstance'),
    path('api_updatestudentsubmissionquery', views.update_studentsubmissionquery.as_view(), name='api_updatestudentsubmissionquery'),


    # bulk import actions
    path('studentimport', views.import_students_togroup, name='studentimport'),
] 