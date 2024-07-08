from django.apps import AppConfig


class SystemUsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.system_users'
    dependent_modules = ['module_system']
    version = '0.0.1-Alpha'
    description = '管理操作系统里的用户帐号'
