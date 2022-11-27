from django.apps import AppConfig
from django.core.signals import request_finished

class PlaylistConfig(AppConfig):
  name = 'playlist'
  verbose_name = 'Online Logging Sheets'
  def ready(self):
      # Implicitly connect signal handlers decorated with @receiver.
      from . import signals