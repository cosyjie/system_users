import subprocess

from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import FormView


from appcommon.helper import subprocess_run, remove_list_blank
from panel.module_system.views import ModuleSystemMixin


from .forms import SystemUserForm, SystemUserDelForm, SystemUserAddForm, SystemUserPwdForm


class UsersAdminMixin(ModuleSystemMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = 'system_users'
        return context


def get_users(username=''):
    user_list = {}
    exec_result = subprocess_run(subprocess, 'cat /etc/passwd')
    if exec_result.returncode == 0:
        run_cmd = exec_result.stdout.strip().split('\n')
        for user in run_cmd:
            user_info = user.split(':')
            if username != '':
                if username == user_info[0]:
                    user_list = {
                        'username': user_info[0], 'uid': user_info[2], 'describe': user_info[4], 'home': user_info[5]
                    }
                    break
            else:
                if '/home/' in user_info[5] or user_info[0] == 'root':
                    user_list[user_info[0]] = {
                        'username': user_info[0], 'uid': user_info[2], 'describe': user_info[4], 'home': user_info[5]
                    }
    return user_list


class UsersAdminView(UsersAdminMixin, TemplateView):
    template_name = 'system_users/users_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '系统用户'
        context['users'] = get_users()
        return context


class UsersAddView(UsersAdminMixin, FormView):
    template_name = 'system_users/users_create.html'
    form_class = SystemUserAddForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '新建用户'
        context['breadcrumb'] = [
            {'title': '用户', 'href': reverse_lazy('module_system:system_users:list'), 'active': False},
            {'title': '新建用户', 'href': '', 'active': True},
        ]
        return context

    def form_valid(self, form):
        real_name = form.cleaned_data.get('real_name')
        user_name = form.cleaned_data.get('user_name')
        pwd = form.cleaned_data.get('pw1')
        run_cmd = 'useradd -c {} {}'.format(real_name, user_name)
        run_end = subprocess.run(run_cmd, shell=True, capture_output=True, encoding='utf-8')
        if run_end.stderr:
            messages.warning(self.request, '服务器执行结果：' + run_end.stderr)
            self.success_url = reverse('module_system:system_users:create')
        else:
            run_cmd = "echo '{}'|passwd --stdin {}".format(pwd, user_name)
            run_end = subprocess.run(run_cmd, shell=True, capture_output=True, encoding='utf-8')
            if run_end.stderr:
                messages.error(self.request, '创建用户完成！但设置密码失败！请尝试重新设置或寻求其他方法设置密码！')
            self.success_url = reverse('module_system:system_users:list')
        return super().form_valid(form)


class UserDetailView(UsersAdminMixin, FormView):
    template_name = 'system_users/users_detail.html'
    form_class = SystemUserForm

    def get_initial(self):
        user = self.kwargs.get('username')
        userinfo = get_users(user)
        run_cmd = subprocess.run('groups {}'.format(user), shell=True, capture_output=True, encoding='utf-8').stdout.split(':')
        self.initial['is_admin'] = 'wheel' in run_cmd[1]
        self.initial['real_name'] = userinfo['describe']
        run_cmd = subprocess.run('passwd -S {}'.format(user), shell=True, capture_output=True, encoding='utf-8').stdout
        self.initial['is_locked'] = ' LK ' in run_cmd
        return self.initial.copy()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '帐号详情'
        context['breadcrumb'] = [
            {'title': '用户', 'href': reverse_lazy('module_system:system_users:list'), 'active': False},
            {'title': '帐号详情', 'href': '', 'active': True},
        ]
        user = self.kwargs.get('username')
        context['current_user'] = user
        return context

    def form_valid(self, form):
        username = self.kwargs.get('username')
        if form.has_changed():
            change_data = form.changed_data
            if 'real_name' in change_data:
                cmd = 'usermod -c {} {}'.format(form.cleaned_data.get('real_name'), username)
                subprocess.run(cmd, shell=True, capture_output=True, encoding='utf-8')
            if 'is_admin' in change_data:
                is_admin = form.cleaned_data.get('is_admin')
                if is_admin:
                    cmd = 'usermod -G wheel {}'.format(username)
                else:
                    cmd = 'gpasswd -d {} wheel'.format(username)
                subprocess.run(cmd, shell=True, capture_output=True, encoding='utf-8')
            if 'is_locked' in change_data:
                is_locked = form.cleaned_data.get('is_locked')
                cmd = 'passwd '
                if is_locked:
                    cmd += '-l '
                else:
                    cmd += '-u '
                cmd = cmd + username
                subprocess.run(cmd, shell=True, capture_output=True, encoding='utf-8')
            messages.success(self.request, '修改用户信息完成！')
        else:
            messages.info(self.request, '您提交的内容没有变化！')
        self.success_url = reverse('module_system:system_users:detail', kwargs={'username': username})
        return super().form_valid(form)


class UserDelView(UsersAdminMixin, FormView):
    form_class = SystemUserDelForm
    template_name = 'system_users/users_del.html'
    success_url = reverse_lazy('module_system:system_users:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '删除用户'
        context['breadcrumb'] = [
            {'title': '用户', 'href': reverse_lazy('module_system:system_users:list'), 'active': False},
            {'title': '删除用户', 'href': '', 'active': True},
        ]
        context['current_user'] = self.kwargs.get('username')
        context['user_home'] = get_users(self.kwargs.get('username'))['home']
        return context

    def form_valid(self, form):
        del_home = form.cleaned_data.get('del_home')
        user = self.kwargs.get('username')
        cmd = 'userdel '
        if del_home: cmd = cmd + '-r '
        cmd = cmd + user
        run_cmd = subprocess_run(subprocess, cmd)
        if run_cmd.returncode == 0:
            messages.success(self.request, f'删除用户信息完成！')
            self.success_url = reverse('module_system:system_users:list')
        else:
            messages.warning(self.request, f'服务器信息：{run_cmd.stderr}')
            self.success_url = reverse('module_system:system_users:list', kwargs={'user': user})
        return super().form_valid(form)


class UserPwdView(UsersAdminMixin, FormView):
    form_class = SystemUserPwdForm
    template_name = 'system_users/users_pwd.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '设置用户密码'
        context['current_user'] = self.kwargs.get('user')
        context['breadcrumb'] = [
            {'title': '用户', 'href': reverse_lazy('module_system:system_users:list'), 'active': False},
            {'title': '帐号详情',
             'href': reverse_lazy('module_system:system_users:detail', kwargs={'username': context['current_user']}),
             'active': False},
            {'title': '设置用户密码', 'href': '', 'active': True},
        ]
        return context

    def form_valid(self, form):
        user_name = self.kwargs.get('user')
        pwd = form.cleaned_data.get('pw1')
        run_cmd = "echo '{}'|passwd --stdin {}".format(pwd, user_name)
        run_end = subprocess.run(run_cmd, shell=True, capture_output=True, encoding='utf-8')
        if run_end.returncode == 0:
            messages.success(self.request, '修改密码操作完成！')
        else:
            messages.warning(self.request, f'修改密码失败！服务器信息：{run_end.stderr}')
        self.success_url = reverse('module_system:system_users:detail', kwargs={'username': user_name})
        return super().form_valid(form)


class LoginUsersListView(UsersAdminMixin, TemplateView):
    template_name = 'system_users/login_users_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '当前登录用户'
        context['breadcrumb'] = [
            {'title': '用户', 'href': reverse_lazy('module_system:system_users:list'), 'active': False},
            {'title': '当前登录用户', 'href': '', 'active': True},
        ]
        cmd = 'who'
        context['wholist'] = []
        run_stdout = subprocess.run(cmd, shell=True, capture_output=True, encoding='utf-8').stdout.strip()
        if run_stdout:
            run_list = run_stdout.split('\n')
            for user_list in run_list:
                tmp_list = remove_list_blank(user_list.split(' '))
                loginfrom = '本地直连'
                if len(tmp_list) == 5:
                    loginfrom = tmp_list[4].replace('(', '').replace(')', '')

                context['wholist'].append({
                    'user': tmp_list[0],
                    'tty': tmp_list[1],
                    'loginat': tmp_list[2] + ' ' + tmp_list[3],
                    'loginfrom': loginfrom
                })
        return context


class UserKillView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse('module_system:system_users:login_users_list')

    def get(self, request, *args, **kwargs):
        tty = request.GET.get('tty')
        cmd = 'pkill -9 -t {}'.format(tty)
        run_end = subprocess.run(cmd, shell=True, capture_output=True, encoding='utf-8')
        if run_end.returncode == 0:
            messages.success(request, f'踢出 {tty} 用户操作完成！')
        else:
            messages.warning(request, f'服务器信息：{run_end.stderr}')

        return super().get(request, *args, **kwargs)