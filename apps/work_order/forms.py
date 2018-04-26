# _*_ coding: utf-8 _*_

from django import forms
from work_order.models import WorkOrder
from dashboard.models import UserProfile


class WorkOrderApplyForm(forms.Form):
    assign_to_sa = UserProfile.objects.filter(groups__name='sa').values_list('id', 'name_cn')

    type = forms.IntegerField(widget=forms.Select(attrs={'class': 'type form-control'}, choices=WorkOrder.ORDER_TYPE))
    title = forms.CharField(required=True,
                           max_length=10,
                           error_messages={'required': '标题不能为空', 'max_length': '最多10个字符'},
                           widget=forms.TextInput(attrs={'class': 'form-control','placeholder': '工单标题'}))
    order_contents = forms.CharField(required=True,
                                    error_messages={'required': '工单内容不能为空',},
                                    widget=forms.Textarea(attrs={'class': 'form-control',
                                                                  'rows': 8, 'placeholder': '工单详细内容'}))
    assign_to = forms.ChoiceField(widget=forms.Select(attrs={'class': 'assign-to form-control'}, choices=assign_to_sa))
    # assign_to = forms.MultipleChoiceField(widget=forms.SelectMultiple(attrs={'class': 'assign-to form-control'}, choices=assign_to_sa))

    # 知识点 指派给用户的时候，如果用户更新了 指派的下拉列表也得更新
    def __init__(self, *args, **kwargs):
        super(WorkOrderApplyForm, self).__init__(*args, **kwargs)
        self.fields['assign_to'].choices = UserProfile.objects.filter(groups__name='sa').values_list('id', 'name_cn')


class WorkOrderResultForm(forms.Form):
    result_desc = forms.CharField(widget=forms.Textarea(), required=True)
