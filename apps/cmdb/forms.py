# _*_ coding: utf-8 _*_

from django import forms
from cmdb.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def clean_module_letter(self):
        '''
            自定义字段验证  clean_字段名称
            获取name，转换为小写
        '''
        module_letter = self.cleaned_data.get("module_letter").strip().lower()
        print module_letter
        return module_letter

