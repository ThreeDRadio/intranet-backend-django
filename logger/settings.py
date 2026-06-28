from split_settings.tools import optional, include

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'threed',
        'USER': 'test_user',
        'PASSWORD': 'test_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

WORDPRESS_USER=''
WORDPRESS_API_KEY=''

include(
    'settings/base.py',
    'settings/bower.py',
    'settings/installed_apps.py',
    'settings/downloads.py',
    optional('local_settings.py'),

    scope=globals()
)