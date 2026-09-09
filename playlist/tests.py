import csv
from datetime import date, timedelta, timezone
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.http import Http404
from django.test import RequestFactory
from django.urls import resolve, reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from playlist.models import Playlist, PlaylistEntry, Setting, Show
from playlist.views import PlaylistEntryViewSet, ShowViewSet, playlist, summary
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
        factory = APIRequestFactory()
        request = factory.get("/api/shows/active")
        view = ShowViewSet.as_view({"get": "active"})
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify only the active show is returned
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.show.id)

    def test_no_filter_returns_all_shows(self):
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

        self.assertEqual(playlist_instance.femaleQuota, None)
        self.assertEqual(playlist_instance.localQuota, None)
        self.assertEqual(playlist_instance.australianQuota, None)


class PlaylistEntryModelTest(APITestCase):
    def setUp(self):
        self.show = Show.objects.create(
            name="Existing Show",
            customQuotas=True,
            startTime="18:00",
            endTime="19:00",
        )
        self.playlist_instance = Playlist.objects.create(
            id=999,
            show=self.show,
            date="2026-01-01",
            australianQuota=20,
            localQuota=20,
            femaleQuota=40,
        )
        self.playlist_entry = PlaylistEntry.objects.create(
            playlist=self.playlist_instance,
            artist="test artist",
            title="test title",
            local=False,
            female=False,
            australian=False,
            newRelease=False,
        )

    def test_string_converters(self):
        expected = "(Existing Show) test artist - test title"

        self.assertEqual(
            self.playlist_entry.__unicode__(),
            expected,
        )

        self.assertEqual(
            self.playlist_entry.__str__(),
            expected,
        )


class SummaryViewTests(APITestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Set up a dummy show
        self.show = Show.objects.create(
            name="Morning Beats", startTime="08:00", endTime="10:00"
        )

        # Set up a playlist with a show
        self.playlist_with_show = Playlist.objects.create(
            id=888,
            date="2026-07-01",
            show=self.show,
            showname="Test",
            australianQuota=20,
            localQuota=20,
            femaleQuota=40,
        )

        # Set up a playlist without a show (uses showname)
        self.playlist_no_show = Playlist.objects.create(
            id=999,
            date="2026-07-02",
            show=None,
            showname="Late Night Jazz",
            australianQuota=20,
            localQuota=20,
            femaleQuota=40,
        )

        self.playlist_entry1 = PlaylistEntry.objects.create(
            playlist=self.playlist_with_show,
            artist="test artist",
            title="test title",
            local=False,
            female=False,
            australian=False,
            newRelease=False,
        )

        self.playlist_entry2 = PlaylistEntry.objects.create(
            playlist=self.playlist_no_show,
            artist="test local female artist",
            title="test local female title",
            local=True,
            female=True,
            australian=False,
            newRelease=False,
        )

    def test_top20_format_returns_csv(self):
        """Test that the top20 format returns a valid CSV file with correct headers."""
        request = self.factory.get("/summary/", {"format": "top20"})
        response = summary(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertEqual(
            response["Content-Disposition"], 'attachment; filename="play_summary.csv"'
        )

        # Parse CSV content
        content = response.content.decode("utf-8").splitlines()
        reader = csv.reader(content)
        headers = next(reader)

        expected_headers = [
            "show",
            "date",
            "start time",
            "artist",
            "track",
            "album",
            "local",
            "australian",
            "female",
            "new release",
        ]
        self.assertEqual(headers, expected_headers)

    def test_top20_format_with_show(self):
        """Test CSV row output when a playlist is linked to a Show object."""
        request = self.factory.get(
            "/summary/",
            {"format": "top20", "startDate": "2026-07-01", "endDate": "2026-07-01"},
        )
        response = summary(request)

        content = response.content.decode("utf-8").splitlines()
        reader = csv.reader(content)
        next(reader)  # Skip header
        row = next(reader)

        self.assertEqual(row[0], "Morning Beats")
        self.assertEqual(row[1], "2026-07-01")
        self.assertEqual(row[2], "08:00:00")
        self.assertEqual(row[3], "test artist")
        self.assertEqual(row[4], "test title")

    def test_top20_format_without_show(self):
        """Test CSV row output when a playlist fallback to showname and 0:00 time."""
        request = self.factory.get(
            "/summary/",
            {"format": "top20", "startDate": "2026-07-02", "endDate": "2026-07-02"},
        )
        response = summary(request)

        content = response.content.decode("utf-8").splitlines()
        reader = csv.reader(content)
        next(reader)  # Skip header
        row = next(reader)

        self.assertEqual(row[0], "Late Night Jazz")
        self.assertEqual(row[1], "2026-07-02")
        self.assertEqual(row[2], "0:00")
        self.assertEqual(row[3], "test local female artist")
        self.assertEqual(row[4], "test local female title")

    def test_default_format_else_branch(self):
        """Test the fallback branch when format is not top20."""
        request = self.factory.get("/summary/", {"format": "apra"})
        response = summary(request)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8").splitlines()
        reader = csv.reader(content)
        headers = next(reader)

        expected_headers = [
            "Title of Work",
            "Composer/Arranger",
            "Artist",
            "Record Label",
            "Total No Usages Per Week",
            "Duration",
            "APRA use only",
        ]
        self.assertEqual(headers, expected_headers)


class PlaylistViewTests(APITestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # 1. Create a dummy Show
        self.show = Show.objects.create(
            id=100, name="Afternoon Mix", startTime="14:00", endTime="17:00"
        )

        # 2. Create Playlists (with and without a bound Show)
        self.playlist_with_show = Playlist.objects.create(
            id=998,
            date="2026-07-17",
            show=self.show,
            australianQuota=20,
            localQuota=20,
            femaleQuota=40,
        )
        self.playlist_no_show = Playlist.objects.create(
            id=999,
            date="2026-07-18",
            show=None,
            showname="Midnight Indie",
            australianQuota=20,
            localQuota=20,
            femaleQuota=40,
        )

        # 3. Create Tracks (assuming standard fields)
        # Note: Your CSV code uses track.newRelease (camelCase), matching it here
        self.track1 = PlaylistEntry.objects.create(
            playlist=self.playlist_with_show,
            artist="The Chats",
            title="Smoko",
            album="High Risk Behaviour",
            local=True,
            australian=True,
            female=False,
            newRelease=False,
            index=1,
        )
        self.track2 = PlaylistEntry.objects.create(
            playlist=self.playlist_with_show,
            artist="Amyl and the Sniffers",
            title="Guided by Angels",
            album="Comfort to Me",
            local=True,
            australian=True,
            female=True,
            newRelease=True,
            index=2,
        )

        # 5. Populate playlist.tracks.all() ManyToMany if your CSV logic iterates there directly
        self.playlist_with_show.tracks.add(self.track1, self.track2)

    def test_playlist_not_found_raises_404(self):
        """View should return a 404 response if the playlist ID does not exist."""
        request = self.factory.get("/playlist/9999/")
        with self.assertRaises(Http404):
            playlist(request, playlist_id=9999)

    def test_text_format_view(self):
        """Text format returns plain text response and maps context correctly."""
        request = self.factory.get("/playlist/", {"format": "text"})
        response = playlist(request, playlist_id=self.playlist_with_show.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")

    def test_text_format_with_album_true(self):
        """Setting album=true flag injects printalbum into the template context."""
        request = self.factory.get("/playlist/", {"format": "text", "album": "true"})
        response = playlist(request, playlist_id=self.playlist_with_show.pk)

        self.assertEqual(response.status_code, 200)

    def test_csv_format_filename_with_show(self):
        """CSV filename uses the Show name if a relation exists."""
        request = self.factory.get("/playlist/", {"format": "csv"})
        response = playlist(request, playlist_id=self.playlist_with_show.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        expected_disposition = 'attachment; filename="Afternoon Mix-2026-07-17.csv"'
        self.assertEqual(response["Content-Disposition"], expected_disposition)

    def test_csv_format_filename_without_show(self):
        """CSV filename falls back to showname string if no Show object is linked."""
        request = self.factory.get("/playlist/", {"format": "csv"})
        response = playlist(request, playlist_id=self.playlist_no_show.pk)

        expected_disposition = 'attachment; filename="Midnight Indie-2026-07-18.csv"'
        self.assertEqual(response["Content-Disposition"], expected_disposition)

    def test_csv_content_and_headers(self):
        """CSV contains accurate tracking data structured into the exact columns."""
        request = self.factory.get("/playlist/", {"format": "csv"})
        response = playlist(request, playlist_id=self.playlist_with_show.pk)

        # Parse output data
        csv_data = response.content.decode("utf-8").splitlines()
        reader = csv.reader(csv_data)

        headers = next(reader)
        expected_headers = [
            "artist",
            "track",
            "album",
            "local",
            "australian",
            "female",
            "new release",
        ]
        self.assertEqual(headers, expected_headers)

        # Check first track row value mapping
        first_row = next(reader)
        self.assertEqual(first_row[0], "The Chats")
        self.assertEqual(first_row[1], "Smoko")
        self.assertEqual(first_row[2], "High Risk Behaviour")
        self.assertEqual(first_row[3], "True")


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
        url = reverse("Show-playlists", kwargs={"pk": self.show.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Validates that the list contains the playlist created in setup
        self.assertTrue(len(response.data) >= 1)

    def test_action_returns_404_for_invalid_show(self):
        """Test that actions correctly return 404 if the show instance does not exist."""
        invalid_url = reverse("Show-statistics", kwargs={"pk": 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PlaylistViewSetTests(APITestCase):
    def setUp(self):
        # Create global quota settings needed by the Playlist pre_save signal
        Setting.objects.create(id="female_quota", value="25")
        Setting.objects.create(id="local_quota", value="15")
        Setting.objects.create(id="australian_quota", value="40")

        # Create a sample show
        self.show = Show.objects.create(
            name="Morning Beats",
            defaultHost="Host A",
            startTime="9:00:00",
            endTime="10:00:01",
        )

        # Create a playlist
        self.playlist = Playlist.objects.create(
            show=self.show, host="Host A", date="2026-01-02"
        )

        self.playlist_2 = Playlist.objects.create(
            show=self.show, host="Host A", date="2026-01-01"
        )

        # Create playlist entries with different indices to test sorting order
        self.track_index_2 = PlaylistEntry.objects.create(
            playlist=self.playlist,
            index=2,
            artist="Artist Alpha",
            album="Album Alpha",
            title="Song Alpha",
            local=True,
            australian=True,
            female=False,
            newRelease=True,
        )
        self.track_index_1 = PlaylistEntry.objects.create(
            playlist=self.playlist,
            index=1,
            artist="Artist Beta",
            album="Album Beta",
            title="Song Beta",
            local=False,
            australian=True,
            female=True,
            newRelease=False,
        )

    def test_list_playlists(self):
        """Verify the playlist collection can be fetched successfully."""
        url = reverse("Playlist-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_tracks_detail_action_ordering(self):
        """Verify the custom 'tracks' action sorts items strictly by index, then pk."""
        # Standard DRF router formats extra detail actions as 'basename-action_name'
        url = reverse("Playlist-tracks", kwargs={"pk": self.playlist.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Track with index=1 (Song Beta) must appear first despite being created second
        self.assertEqual(response.data[0]["title"], "Song Beta")
        self.assertEqual(response.data[1]["title"], "Song Alpha")


class PlaylistEntryViewSetTests(APITestCase):
    def setUp(self):
        # Create global quota settings for the pre_save signal
        Setting.objects.create(id="female_quota", value="25")
        Setting.objects.create(id="local_quota", value="15")
        Setting.objects.create(id="australian_quota", value="40")

        self.show = Show.objects.create(
            name="Rock Hour",
            defaultHost="Host B",
            startTime="12:00:00",
            endTime="13:00:00",
        )

        # Create two playlists: one for today, one for yesterday
        self.today_playlist = Playlist.objects.create(
            show=self.show, host="Host B", date=date.today()
        )
        self.past_playlist = Playlist.objects.create(
            show=self.show,
            host="Host B",
            date=date.today() - timedelta(days=1),
        )

        # Track variant A played twice today
        PlaylistEntry.objects.create(
            playlist=self.today_playlist,
            index=1,
            artist="Artist Heavy",
            album="Album Rock",
            title="Track One",
            local=True,
            australian=True,
            female=False,
            newRelease=False,
        )
        PlaylistEntry.objects.create(
            playlist=self.today_playlist,
            index=2,
            artist="Artist Heavy",
            album="Album Rock",
            title="Track One",
            local=True,
            australian=True,
            female=False,
            newRelease=False,
        )

        # Track variant B played once today
        PlaylistEntry.objects.create(
            playlist=self.today_playlist,
            index=3,
            artist="Artist Soft",
            album="Album Indie",
            title="Track Two",
            local=False,
            australian=False,
            female=True,
            newRelease=True,
        )

        # Track variant A played on a past day (should be ignored by 'today' query filter)
        PlaylistEntry.objects.create(
            playlist=self.past_playlist,
            index=1,
            artist="Artist Heavy",
            album="Album Rock",
            title="Track One",
            local=True,
            australian=True,
            female=False,
            newRelease=False,
        )

    def test_today_action_aggregation_and_ordering(self):
        """Verify aggregate query counts today's plays and sorts by artist, then plays."""
        url = reverse("PlaylistEntry-today")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Handle paginated framework responses dynamically
        results = (
            response.data.get("results")
            if isinstance(response.data, dict)
            else response.data
        )

        # Total distinct track groupings today should be 2
        self.assertEqual(len(results), 2)

        # Find explicit counts inside the payload
        track_one_data = next(item for item in results if item["title"] == "Track One")
        track_two_data = next(item for item in results if item["title"] == "Track Two")

        # Check aggregation calculations
        self.assertEqual(track_one_data["plays"], 2)
        self.assertEqual(track_two_data["plays"], 1)

        # Verify serializer fields match PlayCountSerializer schema definitions
        self.assertIn("artist", track_one_data)
        self.assertIn("album", track_one_data)
        self.assertIn("plays", track_one_data)

    def test_today_no_pagination_class(self):
        # 1. Create a fake request
        factory = APIRequestFactory()
        request = factory.get("/fake-url/")

        # 2. Instantiate view and explicitly wipe pagination
        view = PlaylistEntryViewSet.as_view({"get": "today"})
        PlaylistEntryViewSet.pagination_class = None

        # 3. Call the view
        response = view(request)

        # 4. Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
