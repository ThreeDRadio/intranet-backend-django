from split_settings.tools import optional, include

include(
    'settings/base.py',
    'settings/bower.py',
    'settings/installed_apps.py',
    'settings/database.py',
    optional('local_settings.py'),

    scope=globals()
)
