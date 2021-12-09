import django_tables2 as tables
from django_tables2.utils import A
from ..models import Student

class StudentGroupTable(tables.Table):
    open = tables.TemplateColumn('<a href="{% url "instructor:studentdetails" record.id %}"><i class="fas fa-id-badge"></i></a>', verbose_name='', orderable=False)
    first_name = tables.LinkColumn('instructor:studentdetails', args=[A('pk')], text=lambda record:record.first_name)
    last_name = tables.Column()
    student_custom_id = tables.Column()
    class Meta:
        model = Student
        template_name = 'django_tables2/bootstrap4.html'
        fields = ("open", "first_name", "last_name", "student_custom_id")


class StudentTable(tables.Table):
    open = tables.TemplateColumn('<a href="{% url "instructor:studentdetails" record.id %}"><i class="fas fa-id-badge"></i></a>', verbose_name='', orderable=False)
    first_name = tables.LinkColumn('instructor:studentdetails', args=[A('pk')], text=lambda record:record.first_name)
    last_name = tables.Column()
    student_custom_id = tables.Column()
    class Meta:
        model = Student
        template_name = 'django_tables2/bootstrap4.html'
        fields = ("open", "first_name", "last_name", "student_custom_id", "student_group")