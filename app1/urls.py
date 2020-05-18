# coding:utf-8

from django.urls import path, re_path
from app1 import views

app_name = 'app1'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('index/', views.IndexView.as_view(), name='index'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('update_status/<int:mail_id>/', views.update_view, name='update_status'),
    path('showsql/<sqltext>/', views.ShowSQLView.as_view(), name='showsql'),
    path('showsql1/<sqltext>/', views.showsql, name='showsql1'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
]

