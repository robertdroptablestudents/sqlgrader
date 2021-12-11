import django_tables2 as tables
from django_tables2.utils import A

from ..models import StudentSubmissionItem, StudentSubmissionItemGrade

# for all grades for an assignment across all students
class AssignmentGradesTable(tables.Table):
    open = tables.TemplateColumn('<a href="{% url "instructor:submissiondetails" record.student_submission.id %}"><i class="fas fa-book"></i></a>', verbose_name='', orderable=False)
    student_first_name = tables.Column(accessor='student_submission.student.first_name', verbose_name='First Name')
    student_last_name = tables.Column(accessor='student_submission.student.last_name', verbose_name='Last Name')
    student_custom_id = tables.Column(accessor='student_submission.student.student_custom_id', verbose_name='Student ID')
    item_number = tables.Column(accessor='assignment_item.item_number', verbose_name='Item #')
    assignment_item = tables.Column(accessor='assignment_item.item_name', verbose_name='Item Name')
    score_primary = tables.Column(accessor='score_primary', verbose_name='Primary Score')

    class Meta:
        model = StudentSubmissionItem
        template_name = 'django_tables2/bootstrap4.html'
        fields = ("open", "student_first_name", "student_last_name", "student_custom_id", "item_number", "assignment_item", "score_primary")

# for specific environment grades on a query item for all students
class StudentSubmissionItemGradeTable(tables.Table):
    student_first_name = tables.Column(accessor='student_submission_item.student_submission.student.first_name', verbose_name='First Name')
    student_last_name = tables.Column(accessor='student_submission_item.student_submission.student.last_name', verbose_name='Last Name')
    student_custom_id = tables.Column(accessor='student_submission_item.student_submission.student.student_custom_id', verbose_name='Student ID')
    assignment_item = tables.Column(accessor='student_submission_item.assignment_item.item_name', verbose_name='Item')

    environment_instance = tables.Column(accessor='environment_instance.environment_name', verbose_name='Instance')

    graded_date = tables.Column(verbose_name='Item Graded Date')

    class Meta:
        model = StudentSubmissionItemGrade
        template_name = 'django_tables2/bootstrap4.html'
        fields = ("student_first_name", "student_last_name", "student_custom_id", "assignment_item", "environment_instance", "graded_date",  "points_possible", "points_earned")