from django.db import models
from django.contrib.auth.models import User

class UserAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accountId = models.CharField(primary_key=True,max_length=255,)
    accountAmount = models.IntegerField(default=100)


   
  

class UserTransaction(models.Model):
    transactionTime = models.DateTimeField(auto_now_add=True, primary_key=True)
    transactionSender = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="Sender")
    transactionReceiver = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="Receiver")
    transactionAmount = models.IntegerField(default=0)
    transactionMessage = models.CharField(max_length=100, null=True)
    def __str__ (self):
        return "{}".format(self.transactionTime)
        
    def save(self,*args,**kwargs):
        if self.transactionAmount >self.transactionSender.accountAmount:
            return False
        elif self.transactionReceiver ==self.transactionSender:
            return False
        else:
            self.transactionSender.accountAmount -=self.transactionAmount
            self.transactionSender.save()
            self.transactionReceiver.accountAmount +=self.transactionAmount
            self.transactionReceiver.save()
            super(UserTransaction,self).save(*args,**kwargs)

