from django import forms
from appcommon.forms import FormBase


class SystemUserAddForm(FormBase):
    real_name = forms.CharField(label='全名*', required=True, widget=forms.TextInput(attrs={
            'class': 'form-control', 'lay-verify': 'required', 'autocomplete': 'off',
            'lay-reqtext': '全名不能为空！',
        }))
    user_name = forms.CharField(label='用户名*', required=True, widget=forms.TextInput(attrs={
            'class': 'form-control', 'lay-verify': 'required', 'autocomplete': 'off',
            'lay-reqtext': '用户名不能为空！',
        }))
    pw1 = forms.CharField(label='密码*', required=True, widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'lay-verify': 'required',
            'lay-reqtext': '密码不能为空！',
        }))
    pw2 = forms.CharField(label='密码确认*', required=True, widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'lay-verify': 'required|confirmPassword',
            'lay-reqtext': '密码确定不能为空！',
        }))


class SystemUserForm(FormBase):
    real_name = forms.CharField(label='全名*', required=True, widget=forms.TextInput(attrs={
            'class': 'form-control col-sm-4', 'lay-verify': 'required', 'autocomplete': 'off',
            'lay-reqtext': '说明不能为空！',
    }))
    is_admin = forms.BooleanField(
        label='角色',  required=False, widget=forms.CheckboxInput(attrs={
        'title':'管理员权限'})
    )
    is_locked = forms.BooleanField(label='锁定帐号', required=False)


class SystemUserDelForm(FormBase):
    del_home = forms.BooleanField(label='同时删除用户主目录数据', required=False)


class SystemUserPwdForm(FormBase):
    pw1 = forms.CharField(label='密码*', required=True, widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'lay-verify': 'required',
            'lay-reqtext': '密码不能为空！',
        }))
    pw2 = forms.CharField(label='密码确认*', required=True, widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'lay-verify': 'required|confirmPassword',
            'lay-reqtext': '密码确认不能为空！',
        }))

