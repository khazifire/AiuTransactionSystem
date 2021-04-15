from django.contrib import admin
from .models import UserTransaction,UserAccount,DepositRequest

admin.site.register(UserAccount)
admin.site.register(UserTransaction)
admin.site.register(DepositRequest)