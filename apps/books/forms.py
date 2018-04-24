<<<<<<< HEAD
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
=======
# _*_ coding: utf-8 _*_

from django.forms import ModelForm
from dashboard.models import UserProfile
from books.models import Publish, Author, Book 


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

>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
