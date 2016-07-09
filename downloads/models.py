from django.db import models
import uuid
# Create your models here.
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

class DownloadLink(models.Model):
    
    id = models.UUIDField(primary_key=True, 
                          default=uuid.uuid4, 
                          editable=False)

    name = models.CharField(max_length=100)

    path = models.FilePathField(path=settings.DOWNLOAD_BASE_PATH, recursive=True)
    
    createdAt = models.DateTimeField(auto_now_add=True)

    def getExpiry(self):
        return self.createdAt + timedelta(seconds=int(settings.DOWNLOAD_LIFETIME))

    def isCurrent(self):
        now = timezone.now()
        return now < self.getExpiry()

