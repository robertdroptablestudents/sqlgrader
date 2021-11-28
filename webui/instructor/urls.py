from django.urls import path

from . import views

app_name = 'instructor'
urlpatterns = [
    path('', views.index, name='index'),

    path('students', views.studentlist, name='studentlist'),
    path('studentgroup', views.studentgroup, name='studentgroup'),
    path('studentgroup/<int:studentgroup_id>', views.studentgroup, name='studentgroupdetails'),
    path('newstudent', views.newstudent, name='newstudent'),

    path('assignments', views.assignmentlist, name='assignmentlist'),
    path('assignment', views.assignment, name='assignment'),
    path('assignmentedit', views.assignmentedit, name='assignmentedit'),
    path('assignment/<int:assignment_id>', views.assignmentdetails, name='assignmentdetails'),

    path('assignmentenvironmentedit', views.assignmentenvironmentedit, name='assignmentenvironmentedit'),
    path('assignmentenvironmentclear', views.assignmentenvironmentclear, name='assignmentenvironmentclear'),

    path('assignmentitem', views.assignmentitem, name='assignmentitem'),
    path('assignmentitemedit', views.assignmentitemedit, name='assignmentitemedit'),
    path('assignmentitemdetails/<int:assignmentitem_id>', views.assignmentitemdetails, name='assignmentitemdetails'),

    path('environmentinstance', views.environmentinstance, name='environmentinstance'),
    path('environmentinstanceedit', views.environmentinstanceedit, name='environmentinstanceedit'),

    path('grading', views.gradingoverview, name='gradingoverview'),
    path('gradingprocess', views.gradingprocess, name='gradingprocess'),
    path('grading/<int:gradingprocess_id>', views.gradingdetails, name='gradingdetails'),
    path('gradingitem', views.gradingitem, name='gradingitem'),
    path('gradingstart', views.gradingstart, name='gradingstart'),

    # api endpoints
    path('api_updategradingstatus', views.update_gradingstatus.as_view(), name='api_updategradingstatus'),
    # path('api_createcontainer', views.create_container.as_view(), name='api_createcontainer'),
    path('api_getenvironmentinstances/<int:assignmentitem_id>', views.get_environmentinstances.as_view(), name='api_getenvironmentinstances'),
    path('api_getstudentsubmissions/<int:assignmentitem_id>', views.get_studentsubmissions.as_view(), name='api_getstudentsubmissions'),
    path('api_updatestudentsubmissionitem', views.update_studentsubmissionitem.as_view(), name='api_updatestudentsubmissionitem'),
] 