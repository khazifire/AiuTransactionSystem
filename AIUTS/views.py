from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.views import generic
from django.urls import reverse
from datetime import datetime, timedelta
from .models import UserAccount, UserTransaction
from .forms import CreateAccount, CreateTransaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.contrib.auth.models import User
from django.template import loader
import hashlib

class CreateAccountView(generic.CreateView):
    template_name = 'AIUTS/account_form.html'    
    form_class = CreateAccount
  
    def form_valid(self, form):
        self.instance =form.save(commit=False)
        username = form.cleaned_data['username']
        accountId= hashlib.md5(str.encode(username)).hexdigest()
        user = User.objects.create_user(username=username,password=form.cleaned_data['password1'])
        user.save()
        acct = UserAccount(user=user, accountId =accountId, accountAmount=100 )
        acct.save()

        return redirect('AIUTS:index')

class CreateTransactionView(LoginRequiredMixin,generic.CreateView):
    login_url = '/accounts/login/'
    template_name = 'AIUTS/transaction_form.html'    
    form_class = CreateTransaction
    success_url ="/"
    def form_valid(self,form):
        self.instance =form.save(commit=False)
        form.instance.user = self.request.user
        amount = form.cleaned_data['transactionAmount']
        receiver = self.request.POST.get('transactionReceiver')
        sender =self.request.POST.get('transactionSender')
        message =self.request.POST.get('transactionMessage')
        UserAcc = UserAccount.objects.get(pk=sender)
       
        if amount>UserAcc.accountAmount:
            messages.warning(self.request, "Your transaction was unsuccessfull,please top up")
            return redirect('AIUTS:addTransaction')
        elif sender ==receiver:
            messages.warning(self.request, "Your transaction was unsuccessfull, please Try again")
            return redirect('AIUTS:addTransaction')
        else:
            UserAccount.objects.filter(pk=sender).update(accountAmount = F('accountAmount')- amount)
            UserAccount.objects.filter(pk=receiver).update(accountAmount = F('accountAmount')+ amount)
            form.save()
            messages.success(self.request, "Your transaction was successfull")
            
        return super().form_valid(form)
    
class userAccountList(LoginRequiredMixin,generic.ListView):
    login_url = '/accounts/login/'
    template_name = 'AIUTS/index.html'
    context_object_name = 'users'
    def get_queryset(self):
        return UserAccount.objects.filter(user=self.request.user)

class userbalanceView(LoginRequiredMixin,generic.DetailView):
    login_url = '/accounts/login/'
    model = UserAccount
    template_name = 'AIUTS/balance.html'

class transactionList(LoginRequiredMixin,generic.ListView):
    login_url = '/accounts/login/'
    template_name = 'AIUTS/transactionList.html'
    context_object_name = 'transactions'
    
    
    def post(self, request):
        user = UserAccount.objects.get(user=request.user)
        from_date = self.request.POST['from_date']
        to_date = self.request.POST['to_date']
        template = loader.get_template(self.template_name)

        transactions = set(UserTransaction.objects.filter(transactionSender=user).order_by('-transactionTime')).union(set(UserTransaction.objects.filter(transactionReceiver=user).order_by('-transactionTime')))

        if len(from_date) and len(to_date):
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
            to_date = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)
            transactions =set(UserTransaction.objects.filter(transactionSender=user).filter(transactionTime__range=(from_date,to_date)).order_by('-transactionTime')).union(set(UserTransaction.objects.filter(transactionSender=user).filter(transactionTime__range=(from_date, to_date)).order_by('-transactionTime')))

        context = {"transactions": transactions, "Reset":True,'requestTransactions':requestTransactions}
        return HttpResponse(template.render(context, request))
    def get_queryset(self):
        user = UserAccount.objects.get(user=self.request.user)
        return set(UserTransaction.objects.filter(transactionSender=user).order_by('-transactionTime')).union(set(UserTransaction.objects.filter(transactionReceiver=user).order_by('-transactionTime')))
 

class makeRequest(LoginRequiredMixin,generic.TemplateView):
    login_url = '/accounts/login/'
    template_name = 'AIUTS/request_Form.html'

    def post(self, request):
        requestAmount = self.request.POST.get('depositAmount')
        requestRecipient = self.request.POST.get('requestRecipient')
        requestAmount=  self.request.POST.get('requestAmount')

        if len(requestRecipient):
            recipient = UserAccount.objects.get(user=self.request.user)
            sender = UserAccount.objects.get(pk=requestRecipient)
            UserRequest = UserTransaction(
                transactionSender=sender, 
                transactionReceiver=recipient, 
                transactionAmount=requestAmount,
                transactionStatus='Uncompleted',
                transactionMessage="Requesting for payment",
                transactionType="Request")
            UserRequest.save()
            return redirect('AIUTS:transactionList')

# def approveTransaction(request, tid):
#     if userTransaction.objects.filter(id=tid).exists():
#        record = userTransaction.objects.get(id=tid)
#        recipient = record.recipient
#        recipient.balance += record.amount
#        sender = record.sender
#        if sender.balance < record.amount:
#            messages.info(request, "Please make sure you have enough balance")
#            return redirect(request.META['HTTP_REFERER'])
#        sender.balance -= record.amount
#        sender.save()
#        recipient.save()
#        record.complete = True
#        record.remark = "Approved at {}".format(timezone.now())
#        record.save()
#     messages.info(request, "Transaction ID: {} is approved".format(tid))
#     return redirect(request.META['HTTP_REFERER'])

class requestList(LoginRequiredMixin,generic.ListView):
    login_url = '/accounts/login/'
    template_name = 'AIUTS/requestList.html'
    context_object_name = 'requestTransactions'
    def get_queryset(self):
        user = UserAccount.objects.get(user=self.request.user)
     
        return  UserTransaction.objects.filter(transactionReceiver=user and transactionStatus="Uncomplete").order_by('-transactionTime')