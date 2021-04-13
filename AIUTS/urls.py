from django.urls import path
from . import views

app_name = 'AIUTS'
urlpatterns = [
    path('', views.userAccountList.as_view(), name='index'),
    path('acc/<str:pk>/', views.userbalanceView.as_view(), name='userbalance'),
    path('transactionList/', views.transactionList.as_view(), name='transactionList'),
    path('addAccount/', views.CreateAccountView.as_view(), name='addAccount'),
    path('addTransaction/', views.CreateTransactionView.as_view(), name='addTransaction'),
    
    
]