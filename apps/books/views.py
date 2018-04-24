# -*- coding: utf-8 -*-
from __future__ import unicode_literals
<<<<<<< HEAD
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from pure_pagination.mixins import PaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from django.conf import settings
from books.models import Publish, Author, Book
from books.forms import BookForm


# Create your views here.


=======

from django.shortcuts import render

# Create your views here.
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
