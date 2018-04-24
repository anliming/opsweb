# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
<<<<<<< HEAD

# Register your models here.
=======
from .models import *

admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Publish)

>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
