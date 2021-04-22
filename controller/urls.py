from django.urls import path
from . import views

app_name = 'controller'
urlpatterns = [
    path('', views.indexViews.as_view(), name='index'),
    path('Approve/<int:pk>', views.Approve.as_view(), name='Approve'),
]

