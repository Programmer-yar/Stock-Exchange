from django.contrib import admin
from .models import File, Company, Inputs, Result, MailUserInput

admin.site.register(File)
admin.site.register(Company)
admin.site.register(Inputs)
admin.site.register(Result)
admin.site.register(MailUserInput)