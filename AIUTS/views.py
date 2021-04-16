from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.views import generic
from django.urls import reverse
from datetime import datetime, timedelta
from .models import UserAccount, UserTransaction, DepositRequest
from .forms import CreateAccount, CreateTransaction, DepositRequestForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F,Q
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
    model = UserTransaction
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
        transactionStatus = 'Pending'
        UserAcc = UserAccount.objects.get(pk=sender)
       
        if amount>UserAcc.accountAmount:
            messages.warning(self.request, "Your transaction was unsuccessfull,please top up")
            return redirect('AIUTS:addTransaction')
        elif sender ==receiver:
            messages.warning(self.request, "Your transaction was unsuccessfull, please Try again")
            return redirect('AIUTS:addTransaction')
  
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
 




class requestList(LoginRequiredMixin,generic.ListView):
    login_url = '/accounts/login/'
    template_name = 'AIUTS/requestList.html'
    context_object_name = 'requestTransactions'
    def get_queryset(self):
        user = UserAccount.objects.get(user=self.request.user)
        return  UserTransaction.objects.filter(Q(transactionSender=user) & Q(transactionStatus="Uncompleted")).order_by('-transactionTime')


class pendingList(LoginRequiredMixin,generic.ListView):
    login_url = '/accounts/login/'
    template_name = 'AIUTS/transactionStatus.html'
    context_object_name = 'Ptransactions'
    def get_queryset(self):
        user = UserAccount.objects.get(user=self.request.user)
        return  UserTransaction.objects.filter(Q(transactionSender=user)  & Q(transactionStatus="Pending") | Q(transactionReceiver=user) & Q(transactionStatus="Pending")).order_by('-transactionTime')

class Approve(LoginRequiredMixin,generic.UpdateView):
    login_url = '/accounts/login/'
    model = UserTransaction
    fields = ['transactionStatus']
    template_name = 'AIUTS/edit.html'
    success_url = '/pendingList/'


class makeDeposit(LoginRequiredMixin,generic.CreateView):
    login_url = '/accounts/login/'
    model = DepositRequest
    template_name = 'AIUTS/requestDeposit.html'    
    form_class = DepositRequestForm
    success_url ="/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        emp = User.objects.filter(groups__name='AIUTS_EMP')
        context["AIUTS_EMP"] = UserAccount.objects.filter(user__in=emp) 
        return context

    def form_valid(self,form):
        self.instance =form.save(commit=False)
        form.instance.user = self.request.user
        RequestAmount = form.cleaned_data['RequestAmount']
        
        RequestReceiver = UserAccount.objects.get(user=self.request.user)

        print(RequestAmount,RequestReceiver)
        deposit =DepositRequest(RequestReceiver=RequestReceiver, RequestAmount =RequestAmount )
        deposit.save()
        return redirect('AIUTS:index')
    
class makeRequest(LoginRequiredMixin,generic.TemplateView):
    login_url = '/accounts/login/'
    template_name = 'AIUTS/requestPayment.html'
    
    def post(self, request):
        requestAmount = self.request.POST.get('depositAmount')
        requestRecipient = self.request.POST.get('requestRecipient')
        requestAmount=  self.request.POST.get('requestAmount')
        requestMessage = self.request.POST.get('transactionMessage')
        sender = UserAccount.objects.get(user=self.request.user).accountId

        if len(requestRecipient) and requestRecipient != sender:
            recipient = UserAccount.objects.get(user=self.request.user)
            sender = UserAccount.objects.get(pk=requestRecipient)
            UserRequest = UserTransaction(transactionSender=sender, transactionReceiver=recipient, transactionAmount=requestAmount,transactionStatus='Pending',transactionMessage=requestMessage,)
            UserRequest.save()
            return redirect('AIUTS:index')
            
        messages.warning(self.request, "Your request was unsuccessfull, please Try again")
        return redirect('AIUTS:paymentRequest')
       






