from django.forms import ModelForm
from .models import UserTransaction, UserAccount, DepositRequest
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class CreateAccount(UserCreationForm):
    # password = forms.CharField(widget = forms.PasswordInput, error_messages = {'required':"Please create a password"})
    # # accountAmount =forms.IntegerField(error_messages = {'required':"Please provide a starting amount for your account"})
    # username = forms.CharField(error_messages = {'required':"Please enter your username"})
    class Meta:
        model = User
        fields = ['username','password1','password2'] 

class CreateTransaction(forms.ModelForm):
    class Meta:
        model = UserTransaction
        fields =['transactionReceiver','transactionAmount','transactionMessage'] 

class DepositRequestForm(forms.ModelForm):
    class Meta:
        model = DepositRequest
        fields =['RequestAmount']