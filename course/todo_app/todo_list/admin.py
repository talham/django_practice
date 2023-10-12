from django.contrib import admin
from .models import todo_list

# Register your models here.
# @admin.register(todo_list)
class todoAdmin(admin.ModelAdmin):
    list_display = ['task','status']

admin.site.register(todo_list,todoAdmin)