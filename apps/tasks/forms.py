

from django import forms

from  .models import Tasks


class TaskAddForm(forms.ModelForm):
    class Meta:
        model = Tasks
        fields = ['name','playbook']

class TaskAdd1Form(forms.ModelForm):
    playbook_text = forms.CharField(required=True)

    class Meta:
        model = Tasks
        fields = ['name']

