import django_tables2 as tables
from django_tables2.utils import A

from ..models import Student, StudentSubmissionItemGrade

# for group page, lists students in a group
class StudentGroupTable(tables.Table):
    open = tables.TemplateColumn('<a href="{% url "instructor:studentdetails" record.id %}"><i class="fas fa-id-badge"></i></a>', verbose_name='', orderable=False)
    first_name = tables.LinkColumn('instructor:studentdetails', args=[A('pk')], text=lambda record:record.first_name)
    last_name = tables.Column()
    student_custom_id = tables.Column()
    class Meta:
        model = Student
        template_name = 'django_tables2/bootstrap4.html'
        fields = ("open", "first_name", "last_name", "student_custom_id")

# for list of all students
class StudentTable(tables.Table):
    open = tables.TemplateColumn('<a href="{% url "instructor:studentdetails" record.id %}"><i class="fas fa-id-badge"></i></a>', verbose_name='', orderable=False)
    first_name = tables.LinkColumn('instructor:studentdetails', args=[A('pk')], text=lambda record:record.first_name)
    last_name = tables.Column()
    student_custom_id = tables.Column()
    class Meta:
        model = Student
        template_name = 'django_tables2/bootstrap4.html'
        fields = ("open", "first_name", "last_name", "student_custom_id", "student_group")

# for all grades for a student on an assignment
class StudentSubmissionItemGradeTable(tables.Table):
    assignment_name = tables.Column(accessor='student_submission_item.assignment_item.assignment.assignment_name', verbose_name='Assignment')
    assignment_item = tables.Column(accessor='student_submission_item.assignment_item.item_name', verbose_name='Item')
    environment_instance = tables.Column(accessor='environment_instance.environment_name', verbose_name='Instance')
    score_primary = tables.Column(accessor='student_submission_item.score_primary', verbose_name='Primary Score')

    graded_date = tables.Column(verbose_name='Item Graded Date')

    class Meta:
        model = StudentSubmissionItemGrade
        template_name = 'django_tables2/bootstrap4.html'
        fields = ("assignment_name", "assignment_item", "score_primary", "environment_instance", "graded_date",  "points_possible", "points_earned")