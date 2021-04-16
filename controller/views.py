from django.shortcuts import render
from django.views import generic
from AIUTS.models import DepositRequest



class indexViews(generic.ListView):
    template_name = 'controller/index.html'
    context_object_name = 'requests'

    def get_queryset(self):
        return DepositRequest.objects.filter(RequestStatus="Pending").order_by('RequestTime')

class Approve(generic.UpdateView):
    model = DepositRequest
    fields = ['RequestStatus']
    template_name = 'controller/edit.html'
    success_url = '/controller/'