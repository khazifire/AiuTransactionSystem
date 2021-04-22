from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from AIUTS.models import DepositRequest
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class indexViews(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    permission_required = 'depositrequest.view_depositrequest'
    template_name = 'controller/index.html'
    context_object_name = 'requests'

    def get_queryset(self):
        return DepositRequest.objects.filter(RequestStatus="Pending").order_by('RequestTime')

class Approve(PermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    permission_required = 'depositrequest.change_depositrequest'
    model = DepositRequest
    fields = ['RequestStatus']
    template_name = 'controller/edit.html'
    success_url = '/controller/'

