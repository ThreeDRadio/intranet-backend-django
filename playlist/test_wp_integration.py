from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.db.models.signals import post_save
from django.test import TestCase, override_settings

# Import your exact models and the signal function
from .models import Playlist, PlaylistEntry, Setting, Show
from .signals import createPost, find_show_for_playlist, playlist_to_wordpress


class WordPressSignalTests(TestCase):
    def setUp(self):
        """Set up database entries and manage signal connection states."""
        # 1. Create global quota settings needed for the Playlist pre_save method
        Setting.objects.get_or_create(id="female_quota", defaults={"value": "25"})
        Setting.objects.get_or_create(id="local_quota", defaults={"value": "15"})
        Setting.objects.get_or_create(id="australian_quota", defaults={"value": "40"})

        # 2. Temporarily disconnect the post_save signal to prevent it firing during creation
        post_save.disconnect(playlist_to_wordpress, sender=Playlist)

        # 3. Build valid model instances based on your schema fields
        self.show = Show.objects.create(
            name="Drive Time", startTime="16:00:00", endTime="18:00:00"
        )
        self.playlist = Playlist.objects.create(
            show=self.show,
            host="DJ Tester",
            date="2026-03-01",
            complete=True,
            published=False,
        )
        self.track = PlaylistEntry.objects.create(
            playlist=self.playlist,
            index=1,
            artist="The Tester",
            title="Unit Track",
            album="Test Album",
            duration=timedelta(minutes=3, seconds=45),
            local=True,
            australian=True,
            female=False,
            newRelease=False,
        )

        # 4. Reconnect the post_save signal for the actual test runs
        post_save.connect(playlist_to_wordpress, sender=Playlist)

    @patch("requests.get")
    @override_settings(WORDPRESS_USER="FakeUser", WORDPRESS_API_KEY="Fake-Key")
    def test_find_show_for_playlist_success(self, mock_get):
        """Verify standard API response processing when a show match is found."""
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": 42, "slug": "drive-time"}]
        mock_get.return_value = mock_response

        result = find_show_for_playlist("Drive Time")

        self.assertEqual(result["id"], 42)
        mock_get.assert_called_once_with(
            "https://www.threedradio.com/wp-json/wp/v2/program?search=Drive+Time",
            headers={"user-agent": "threedradio-api", "accept": "application/json"},
        )

    @patch("requests.get")
    @override_settings(WORDPRESS_USER="FakeUser", WORDPRESS_API_KEY="Fake-Key")
    def test_find_show_for_playlist_empty(self, mock_get):
        """Verify None is returned safely when the external API returns no records."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = find_show_for_playlist("Unknown Show")
        self.assertIsNone(result)

    @patch("requests.post")
    @override_settings(WORDPRESS_USER="FakeUser", WORDPRESS_API_KEY="Fake-Key")
    def test_create_post(self, mock_post):
        """Verify createPost executes a payload containing the correct WordPress parameters."""
        createPost("Title", 42, "<p>Content</p>", "2026-03-01 18:00:00")

        mock_post.assert_called_once()
        kwargs = mock_post.call_args[1]  # Get keyword arguments from calls
        self.assertEqual(kwargs["json"]["title"], "Title")
        self.assertEqual(kwargs["json"]["program"], [42])

    @override_settings(WORDPRESS_USER=None, WORDPRESS_API_KEY=None)
    def test_signal_aborts_if_no_settings_keys(self):
        """Signal must abort immediately if authentication details are missing."""
        with patch("requests.get") as mock_get:
            self.playlist.save()
            mock_get.assert_not_called()

    @override_settings(WORDPRESS_USER="FakeUser", WORDPRESS_API_KEY="Fake-Key")
    def test_signal_aborts_if_already_published(self):
        """Signal must abort gracefully if the playlist is marked as published."""
        self.playlist.published = True
        with patch("requests.get") as mock_get:
            self.playlist.save()
            mock_get.assert_not_called()

    @override_settings(WORDPRESS_USER="FakeUser", WORDPRESS_API_KEY="Fake-Key")
    def test_signal_aborts_if_playlist_not_complete(self):
        """Signal must abort if the complete boolean evaluates to False."""
        self.playlist.complete = False
        with patch("requests.get") as mock_get:
            self.playlist.save()
            mock_get.assert_not_called()

    @patch("requests.get")
    def test_signal_aborts_if_show_not_found(self, mock_get):
        """Signal must abort if no show is found in WordPress."""
        # Mock finding the WordPress program id
        mock_get_resp = MagicMock()
        mock_get_resp.json.return_value = [{}]
        mock_get.return_value = mock_get_resp

        # Force save to evaluate the post_save logic
        self.playlist.save()

        mock_get.assert_called_once()

        # Confirm the instance mutated state and saved back to our mock DB
        self.playlist.refresh_from_db()
        self.assertFalse(self.playlist.published)

    @patch("playlist.signals.find_show_for_playlist")
    def test_signal_aborts_if_exception_occurs(self, mock_fs4p):
        """Signal must abort if no show is found in WordPress."""
        # Mock finding the WordPress program id
        mock_fs4p.side_effect = ConnectionError("Failed to connect")

        # Force save to evaluate the post_save logic
        self.playlist.save()
        mock_fs4p.assert_called_once()

        # Confirm the instance mutated state and saved back to our mock DB
        self.playlist.refresh_from_db()
        self.assertFalse(self.playlist.published)

    @patch("requests.post")
    @patch("requests.get")
    def test_signal_publishes_successfully(self, mock_get, mock_post):
        """Validates playlist content assembly and state mutation upon success."""
        # Mock finding the WordPress program id
        mock_get_resp = MagicMock()
        mock_get_resp.json.return_value = [{"id": 99, "slug": "drive-time"}]
        mock_get.return_value = mock_get_resp

        # Mock posting the generated content
        mock_post_resp = MagicMock()
        mock_post.return_value = mock_post_resp

        # Force save to evaluate the post_save logic
        self.playlist.save()

        # Check payload dictionary attributes
        mock_post.assert_called_once()
        posted_json = mock_post.call_args[1]["json"]
        self.assertIn("<li>The Tester - Unit Track</li>", posted_json["content"])
        self.assertEqual(posted_json["date"], "2026-03-01 18:00:00")

        # Confirm the instance mutated state and saved back to our mock DB
        self.playlist.refresh_from_db()
        self.assertTrue(self.playlist.published)
