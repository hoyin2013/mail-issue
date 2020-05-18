from django.contrib import admin
from .models import Emails


class EmailsAdmin(admin.ModelAdmin):
    list_display = ['subjects', 'sender', 'send_date', 'status', 'is_execute', 'operator',
                    'execute_time', 'update_time', 'attaches']
    search_fields =list_display
    ordering = ['-send_date']

admin.site.register(Emails, EmailsAdmin)


