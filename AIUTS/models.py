from django.db import models
from django.contrib.auth.models import User

class UserAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accountId = models.CharField(primary_key=True,max_length=255,)
    accountAmount = models.IntegerField(default=100)

class UserTransaction(models.Model):
    transactionId = models.AutoField(primary_key=True)
    transactionTime = models.DateTimeField(auto_now_add=True)
    transactionSender = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="Sender")
    transactionReceiver = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="Receiver")
    transactionAmount = models.IntegerField(default=0)
    transactionMessage = models.CharField(max_length=100, null=True)
    transactionStatus =  models.CharField(choices=[('Completed', 'C'), ('Uncompleted', 'U')], default='Completed', max_length=20)
    transactionType = models.CharField(choices=[('Deposit', 'TU'), ('Request', 'R'), ('Transfer', 'T')], default='Transfer', max_length=20)
    
    def __str__ (self):
        return "{}".format(self.transactionTime)
        
   
