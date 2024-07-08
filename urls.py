from django.urls import path, include
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'system_users'

urlpatterns = [
    path('index/', login_required(views.UsersAdminView.as_view()), name='list'),
    path('create/', login_required(views.UsersAddView.as_view()), name='create'),
    path('detail/<str:username>/', login_required(views.UserDetailView.as_view()), name='detail'),
    path('delete/<str:username>/', login_required(views.UserDelView.as_view()), name='delete'),
    path('password/<str:user>/', login_required(views.UserPwdView.as_view()), name='pwd'),
    path('loginusers/list/', login_required(views.LoginUsersListView.as_view()), name='login_users_list'),
    path('loginusers/list/kill/', login_required(views.UserKillView.as_view()), name='login_users_kill'),
]
