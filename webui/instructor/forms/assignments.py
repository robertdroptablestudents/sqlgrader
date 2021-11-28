from django import forms

class AssignmentEnvironmentForm(forms.Form):
    initial_code = forms.FileField()
    assignment_environment_id = forms.HiddenInput()