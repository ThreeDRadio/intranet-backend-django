from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from playlist.models import Playlist, Setting, Show


class PlaylistQuotaInheritanceTests(APITestCase):
    def setUp(self):
        # Create global fallback settings required when customQuotas is False
        self.global_female = Setting.objects.create(
            id="female_quota", value="25", description="Global female quota"
        )
        self.global_local = Setting.objects.create(
            id="local_quota", value="15", description="Global local quota"
        )
        self.global_australian = Setting.objects.create(
            id="australian_quota", value="40", description="Global Aus quota"
        )

        # Create a show with custom quotas active
        self.custom_show = Show.objects.create(
            name="Custom Quota Show",
            defaultHost="Host Custom",
            startTime="14:00:00",
            endTime="16:00:00",
            customQuotas=True,
            femaleQuota=35,
            localQuota=20,
            australianQuota=50,
        )

        # Create a show using standard system-wide quotas
        self.standard_show = Show.objects.create(
            name="Standard Quota Show",
            defaultHost="Host Standard",
            startTime="16:00:00",
            endTime="18:00:00",
            customQuotas=False,
        )

    def test_playlist_inherits_custom_show_quotas(self):
        """Verify playlist copies quotas directly from its parent show when customQuotas is True."""
        playlist = Playlist.objects.create(
            show=self.custom_show, host="Host Custom", date=date.today()
        )

        # Must reflect the parent show configuration properties
        self.assertEqual(playlist.femaleQuota, 35)
        self.assertEqual(playlist.localQuota, 20)
        self.assertEqual(playlist.australianQuota, 50)

    def test_playlist_inherits_global_settings_quotas(self):
        """Verify playlist falls back to Setting table parameters when customQuotas is False."""
        playlist = Playlist.objects.create(
            show=self.standard_show, host="Host Standard", date=date.today()
        )

        # Must parse and map string inputs directly into instance quota variables
        self.assertEqual(playlist.femaleQuota, 25)
        self.assertEqual(playlist.localQuota, 15)
        self.assertEqual(playlist.australianQuota, 40)

    def test_api_creates_playlist_with_correct_quotas(self):
        """Verify the API endpoint payload leverages the model signal to assign correct values on creation."""
        url = reverse("Playlist-list")
        payload = {
            "show": self.custom_show.id,
            "showname": "Morning Live",
            "host": "Host Custom",
            "date": str(date.today()),
            "notes": "Testing programmatic assignment",
        }

        response = self.client.post(url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check that the assigned values are returned in the response metadata fields
        self.assertEqual(response.data["femaleQuota"], 35)
        self.assertEqual(response.data["localQuota"], 20)
        self.assertEqual(response.data["australianQuota"], 50)
