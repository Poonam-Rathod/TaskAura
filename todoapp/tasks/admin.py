from django.contrib import admin #builtin admin panel
from .models import Task

# Register your models here.
admin.site.register(Task)
