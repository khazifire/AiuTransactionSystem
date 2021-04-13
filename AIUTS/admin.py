from django.contrib import admin
from .models import UserTransaction,UserAccount

admin.site.register(UserAccount)
admin.site.register(UserTransaction)