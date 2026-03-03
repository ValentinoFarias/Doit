from django.contrib import admin

from .models import FocusItem, Note, Task


admin.site.register(Task)
admin.site.register(FocusItem)
admin.site.register(Note)
