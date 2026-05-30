from split_settings.tools import optional, include

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