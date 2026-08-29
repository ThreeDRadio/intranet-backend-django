from django.apps import AppConfig

class PlaylistConfig(AppConfig):
    name = "playlist"
    verbose_name = "Online Logging Sheets"

    def ready(self):
        from . import signals
