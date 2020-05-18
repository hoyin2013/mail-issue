# coding: utf-8
import datetime

from django.contrib.auth import login as auth_login, logout as auth_logout,authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, View, FormView
from common.utils import TimeUtils

from . import models
from django.db.models import Q

import logging

from .forms import LoginForm

logger = logging.getLogger('__name__')


class IndexView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'app1/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mail_lists = models.Emails.objects.filter(~Q(attaches='') & ~Q(sender='operation@xdjk.com'))\
            .order_by('-send_date')[:100]
        # print(mail_lists)
        logger.error(mail_lists)

        for m in mail_lists:
            m.attachs = m.attaches.split(',')

        context['emails'] = mail_lists
        # for m in mail_lists:
        #     print(m.attaches)

        return context


class ShowSQLView(TemplateView):
    # login_url = '/login/'
    template_name = 'app1/showsql.html'

    def get_context_data(self, sqltext, **kwargs):
        context = super().get_context_data(**kwargs)
        print(sqltext)

        # 尝试读取脚本
        try:
            fpath = '/usr/src/app/data/attaches/' + sqltext
            print(fpath)
            f = open(fpath)
            sql_content = [x.rstrip('\n').strip() for x in f.readlines()]
        except Exception as e:
            print(e)
            sql_content = ''

        context['sql_content'] = sql_content

        return context


def showsql(request, sqltext):
    print('sqltext')
    _sqltext =sqltext.strip()
    dpath = _sqltext[1:11]
    sqltext = dpath + '/' + _sqltext[12:]

    # 尝试读取脚本
    try:
        fpath = '/usr/src/app/data/attaches/' + sqltext
        print(fpath)
        f = open(fpath)
        sql_content = [x.rstrip('\n').strip() for x in f.readlines()]
    except Exception as e:
        print(e)
        sql_content = ''

    return render(request, 'app1/showsql.html', {'sql_content': sql_content})


def update_view(request, mail_id):
    try:
        mail_id = int(mail_id)
        mail = models.Emails.objects.get(id=mail_id)
        mail.is_execute = True
        mail.operator = str(request.user)
        mail.execute_time = datetime.datetime.now()
        mail.save()
        return JsonResponse({"status": "success"})
    except Exception as e:
        print(e)
        return JsonResponse({"status": "failed"})


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/login/')


class LoginView(FormView):
    template_name = 'app1/login.html'
    form_class = LoginForm
    redirect_field_name = 'next'
    success_url = '/index/'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        print(username,password)
        user = authenticate(username=username,password=password)
        if user:
            request = self.request
            auth_login(request,user)
            return HttpResponseRedirect('/index/')

        return super().form_valid(form)




class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'app1/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        attach_email = models.Emails.objects.filter(~Q(attaches='') & ~Q(sender='operation@xdjk.com'))

        # 总计
        thisweek = TimeUtils().get_this_week_start()

        context['totals'] = attach_email.filter(attaches__isnull=False).count()

        # 本周统计
        thisweek = TimeUtils().get_this_week_start()
        context['thisweek'] = attach_email.filter(send_date__gte=thisweek).count()

        # 本周统计
        thismonth = TimeUtils().get_this_month_start()
        context['thismonth'] = attach_email.filter(send_date__gte=thismonth).count()

        return context

