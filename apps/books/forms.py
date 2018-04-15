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

