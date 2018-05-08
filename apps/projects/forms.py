# _*_ coding: utf-8 _*_
from django import forms


class ProjectAddForm(forms.Form):
    LEVEL = (
        (0, '私有'),
        (10, '内部'),
        (20, '公开'),
    )
    group = forms.CharField(widget=forms.Select(attrs={}))
    name = forms.CharField(required=True)
    description = forms.CharField(widget=forms.Textarea)
    visibility_level = forms.ChoiceField(label=u'可见等级', choices=LEVEL, widget=forms.RadioSelect)
