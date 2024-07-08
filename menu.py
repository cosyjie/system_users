from django.urls import reverse

menu = {
    'module_system': {
        'child': [
            {
                'name': 'system_users',
                'title': '用户帐号',
                'href': reverse('module_system:system_users:list'),
            },
        ]
    }
}
