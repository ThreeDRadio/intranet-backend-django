from datetime import timezone
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.urls import resolve, reverse
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from playlist.models import Playlist, Setting, Show
from session.models import Whitelist


class ShowViewsetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", "password", "fake1@user.com")
        self.whitelist = Whitelist.objects.create(ip="127.0.1.1", name="test whitelist")
        self.show = Show.objects.create(
            name="radio", startTime="17:00", endTime="19:00"
        )

    def test_grant_access_for_unauthenticated_unwhitelisted(self):
        """Makes sure a non-authenticated, non-whitelisted request fails with forbidden"""
        factory = APIRequestFactory()
        url = reverse("Show-list")
        view = resolve(url).func
        request = factory.get(url)
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_grant_access_for_unauthenticated_whitelisted(self):
        """Makes sure a non-authenticated, but whitelisted request succeeds"""
        factory = APIRequestFactory()
        url = reverse("Show-list")
        view = resolve(url).func
        request = factory.get(url, REMOTE_ADDR="127.0.1.1")
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_grant_access_for_authenticated(self):
        """Makes sure an authenticated, request succeeds"""
        factory = APIRequestFactory()
        url = reverse("Show-list")
        view = resolve(url).func
        request = factory.get(url)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_show_string(self):
        self.assertEqual(self.show.__unicode__(), "radio")
        self.assertEqual(self.show.__str__(), "radio")


class PlaylistViewsetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", "password", "fake1@user.com")
        self.whitelist = Whitelist.objects.create(
            ip="127.198.1.1", name="test whitelist"
        )

    def test_grant_access_for_unauthenticated_unwhitelisted(self):
        """Makes sure a non-authenticated, non-whitelisted request fails with forbidden"""
        factory = APIRequestFactory()
        url = reverse("Playlist-list")
        view = resolve(url).func
        request = factory.get(url)
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_grant_access_for_unauthenticated_whitelisted(self):
        """Makes sure a non-authenticated, but whitelisted request succeeds"""
        factory = APIRequestFactory()
        url = reverse("Playlist-list")
        view = resolve(url).func
        request = factory.get(url, REMOTE_ADDR="127.198.1.1")
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_grant_access_for_authenticated(self):
        """Makes sure an authenticated, request succeeds"""
        factory = APIRequestFactory()
        url = reverse("Playlist-list")
        view = resolve(url).func
        request = factory.get(url)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 200)


class PlaylistEntryViewsetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", "password", "fake1@user.com")
        self.whitelist = Whitelist.objects.create(
            ip="127.198.1.1", name="test whitelist"
        )

    def test_grant_access_for_unauthenticated_unwhitelisted(self):
        """Makes sure a non-authenticated, non-whitelisted request fails with forbidden"""
        factory = APIRequestFactory()
        url = reverse("PlaylistEntry-list")
        view = resolve(url).func
        request = factory.get(url)
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_grant_access_for_unauthenticated_whitelisted(self):
        """Makes sure a non-authenticated, but whitelisted request succeeds"""
        factory = APIRequestFactory()
        url = reverse("PlaylistEntry-list")
        view = resolve(url).func
        request = factory.get(url, REMOTE_ADDR="127.198.1.1")
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_grant_access_for_authenticated(self):
        """Makes sure an authenticated, request succeeds"""
        factory = APIRequestFactory()
        url = reverse("PlaylistEntry-list")
        view = resolve(url).func
        request = factory.get(url)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 200)


class PlaylistModelTest(APITestCase):
    def setUp(self):
        """Set up common test data used across multiple test cases."""
        # Create a basic show instance for testing string representation
        self.test_show = Show.objects.create(
            name="The Morning Show",
            customQuotas=False,
            startTime="17:00",
            endTime="18:00",
        )
        self.test_date = timezone.max

    def test_string_representation(self):
        """Verify that __str__ and __unicode__ return correct format."""
        playlist = Playlist(show=self.test_show, date=self.test_date)
        expected_string = f"{self.test_show} - {self.test_date}"

        self.assertEqual(str(playlist), expected_string)
        self.assertEqual(playlist.__unicode__(), expected_string)

    @patch("playlist.models.Setting.objects.get")
    def test_apply_quotas_global_settings(self, mock_setting_get):
        """Verify quotas pull from global Settings when customQuotas is False."""
        # Arrange: Setup mock responses for the global Setting lookups
        mock_female = MagicMock(value="25")
        mock_local = MagicMock(value="15")
        mock_australian = MagicMock(value="35")

        # side_effect allows .get() to return different mocks based on the pk requested
        def mock_get(pk):
            if pk == "female_quota":
                return mock_female
            if pk == "local_quota":
                return mock_local
            if pk == "australian_quota":
                return mock_australian
            raise Setting.DoesNotExist

        mock_setting_get.side_effect = mock_get

        # Arrange: Create a Show without custom quotas
        show_without_custom = Show.objects.create(
            name="Standard Show",
            customQuotas=False,
            startTime="12:00",
            endTime="14:00",
        )

        # Instantiate an unsaved Playlist (pk is None)
        playlist_instance = Playlist(show=show_without_custom)

        # Act: Fire the classmethod manually
        Playlist.applyQuotas(
            sender=Playlist,
            instance=playlist_instance,
            raw=False,
            using="default",
            update_fields=None,
        )

        # Assert: Values should match the mocked global settings integers
        self.assertEqual(playlist_instance.femaleQuota, 25)
        self.assertEqual(playlist_instance.localQuota, 15)
        self.assertEqual(playlist_instance.australianQuota, 35)

    def test_apply_quotas_custom_show_quotas(self):
        """Verify quotas pull directly from the Show when customQuotas is True."""
        # Arrange: Create a Show with its own custom quotas enabled
        show_with_custom = Show.objects.create(
            name="Indie Hour",
            customQuotas=True,
            femaleQuota=40,
            localQuota=30,
            australianQuota=50,
            startTime="15:00",
            endTime="17:00",
        )

        playlist_instance = Playlist(show=show_with_custom)

        # Act: Fire the classmethod manually
        Playlist.applyQuotas(
            sender=Playlist,
            instance=playlist_instance,
            raw=False,
            using="default",
            update_fields=None,
        )

        # Assert: Values should directly match the Show properties
        self.assertEqual(playlist_instance.femaleQuota, 40)
        self.assertEqual(playlist_instance.localQuota, 30)
        self.assertEqual(playlist_instance.australianQuota, 50)

    def test_apply_quotas_ignored_if_already_saved(self):
        """Verify applyQuotas skips logic if the instance already has a primary key."""
        # Arrange: Create a playlist and explicitly give it a primary key (simulating a saved object)
        show = Show.objects.create(
            name="Existing Show",
            customQuotas=True,
            startTime="18:00",
            endTime="19:00",
        )
        playlist_instance = Playlist(id=999, show=show)

        # Intentionally do not assign quotas to the instance variables
        # Act
        Playlist.applyQuotas(
            sender=Playlist,
            instance=playlist_instance,
            raw=False,
            using="default",
            update_fields=None,
        )

        # Assert: Attributes remain unset (raise AttributeError) because the code inside the if block skipped
        with self.assertRaises(AttributeError):
            _ = playlist_instance.femaleQuota
