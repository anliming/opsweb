# _*_ coding: utf-8 _*_

from django.forms import ModelForm
from dashboard.models import UserProfile
from books.models import Publish, Author, Book
from django.contrib.auth.models import Permission,Group
from dashboard.models import UserProfile

class PublishForm(ModelForm):
    class Meta:
        model = Publish
        fields = "__all__"
class AuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = "__all__"

class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = "__all__"

class PowerForm(ModelForm):
    class Meta:
        model = Permission
        fields = "__all__"
class PowerUpdateForm(ModelForm):
    class Meta:
        model =Permission
        fields = ["name","codename"]

class UserForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ["username","name_cn","email","phone"]

class UserUpdataForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ["name_cn","phone","email"]

class GroupUpdateForm(ModelForm):
    class Meta:
        model = Group
        fields = ["name"]
class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = "__all__"
