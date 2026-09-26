from unittest import mock

from django.contrib.auth.models import User
from django.urls import resolve, reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from playlist.models import Playlist, PlaylistEntry, Show
from playlist.views import (
    ShowViewSet,
)
from session.models import Whitelist


class ShowViewsetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", "password", "fake1@user.com")
        self.whitelist = Whitelist.objects.create(ip="127.0.1.1", name="test whitelist")
        self.show = Show.objects.create(
            id=1, name="radio", startTime="17:00", endTime="19:00", active=True
        )
        self.show2 = Show.objects.create(
            id=2, name="radio2", startTime="14:00", endTime="15:00", active=False
        )

    def test_filter_active_shows(self):
        with mock.patch.object(ShowViewSet, "permission_classes", []):
            factory = APIRequestFactory()
            request = factory.get("/api/shows/active")
            view = ShowViewSet.as_view({"get": "active"})
            response = view(request)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Verify only the active show is returned
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]["id"], self.show.id)

    def test_no_filter_returns_all_shows(self):
        with mock.patch.object(ShowViewSet, "permission_classes", []):
            factory = APIRequestFactory()
            request = factory.get("/api/shows")
            view = ShowViewSet.as_view({"get": "list"})
            response = view(request)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Verify both shows are returned
            self.assertEqual(len(response.data), 2)

    def test_grant_access_for_unauthenticated_unwhitelisted(self):
        """Makes sure a non-authenticated, non-whitelisted request fails with forbidden"""
        factory = APIRequestFactory()
        url = reverse("Show-list")
        view = resolve(url).func
        request = factory.get(url)
        response = view(request)
        self.assertEqual(response.status_code, 403)

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


class ShowViewSetActionTests(APITestCase):
    def setUp(self):
        # Create a sample show
        self.show = Show.objects.create(
            id=1, name="Morning Mix", active=True, startTime="8:00", endTime="9:00"
        )

        # Create a playlist for the show
        self.playlist = Playlist.objects.create(
            id=100,
            show=self.show,
            showname="Episode 1",
            date="2026-09-01",
            australianQuota=20,
            localQuota=20,
            femaleQuota=40,
        )

        # Create sample playlist entries to test statistics and top artists
        PlaylistEntry.objects.create(
            playlist=self.playlist,
            artist="Artist A",
            local=True,
            australian=True,
            female=True,
            newRelease=False,
        )
        PlaylistEntry.objects.create(
            playlist=self.playlist,
            artist="Artist A",
            local=True,
            australian=False,
            female=True,
            newRelease=False,
        )
        PlaylistEntry.objects.create(
            playlist=self.playlist,
            artist="Artist B",
            local=False,
            australian=True,
            female=False,
            newRelease=True,
        )

    def test_topartists_action(self):
        """Test that topartists returns correctly aggregated and ordered artist counts."""
        with mock.patch.object(ShowViewSet, "permission_classes", []):
            url = reverse("Show-topartists", kwargs={"pk": self.show.pk})
            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Artist A has 2 plays, Artist B has 1 play
            self.assertEqual(len(response.data), 2)
            self.assertEqual(response.data[0]["artist"], "Artist A")
            self.assertEqual(response.data[0]["plays"], 2)
            self.assertEqual(response.data[1]["artist"], "Artist B")
            self.assertEqual(response.data[1]["plays"], 1)

    def test_statistics_action(self):
        """Test that statistics action returns accurate counts for the specific show."""
        with mock.patch.object(ShowViewSet, "permission_classes", []):
            url = reverse("Show-statistics", kwargs={"pk": self.show.pk})
            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Map response list into a dictionary for clean assertions
            stats_dict = {item["name"]: item["value"] for item in response.data}

            self.assertEqual(stats_dict["Total tracks"], 3)
            self.assertEqual(stats_dict["Unique artists"], 2)
            self.assertEqual(stats_dict["Local"], 2)
            self.assertEqual(stats_dict["Australian"], 2)
            self.assertEqual(stats_dict["Female"], 2)

    def test_playlists_action(self):
        """Test that playlists action returns the correct playlist data for the show."""
        with mock.patch.object(ShowViewSet, "permission_classes", []):
            url = reverse("Show-playlists", kwargs={"pk": self.show.pk})
            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Validates that the list contains the playlist created in setup
            self.assertTrue(len(response.data) >= 1)

    def test_action_returns_404_for_invalid_show(self):
        """Test that actions correctly return 404 if the show instance does not exist."""
        with mock.patch.object(ShowViewSet, "permission_classes", []):
            invalid_url = reverse("Show-statistics", kwargs={"pk": 9999})
            response = self.client.get(invalid_url)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_shows_success(self):
        """Test searching for shows with a valid list of IDs."""
        # Create an extra show to verify filtering works correctly
        extra_show = Show.objects.create(
            id=2, name="Evening Beats", active=True, startTime="18:00", endTime="19:00"
        )

        with mock.patch.object(ShowViewSet, "permission_classes", []):
            url = reverse("Show-search")
            data = {"ids": [1, 2]}

            response = self.client.post(url, data, format="json")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 2)
            self.assertEqual(response.data[0]["id"], 1)
            self.assertEqual(response.data[1]["id"], 2)

    def test_search_shows_missing_ids_key(self):
        """Test that a 400 error is returned when 'ids' key is missing from payload."""
        with mock.patch.object(ShowViewSet, "permission_classes", []):
            url = reverse("Show-search")
            data = {"wrong_key": ""}

            response = self.client.post(url, data, format="json")

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", response.data)
            self.assertEqual(response.data["error"], "No search parameters provided.")

    def test_search_shows_empty_ids_list(self):
        """Test that searching with an empty list returns an empty response."""
        with mock.patch.object(ShowViewSet, "permission_classes", []):
            url = reverse("Show-search")
            data = {"ids": []}

            response = self.client.post(url, data, format="json")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 0)

    def test_search_shows_non_existent_ids(self):
        """Test that searching for IDs that do not exist returns an empty response."""
        with mock.patch.object(ShowViewSet, "permission_classes", []):
            url = reverse("Show-search")
            data = {"ids": [999]}

            response = self.client.post(url, data, format="json")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 0)
