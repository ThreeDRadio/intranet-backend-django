import hashlib
import json
import os
import tempfile
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from downloads.models import DownloadLink

from .models import Comment, Release, Track
from .serializers import (
    ProfileSerializer,
)


class TrackPropertiesTest(TestCase):
    def setUp(self):
        """Set up a mock object structure to mimic the release relation."""
        # We construct a basic instance manually without saving to DB
        # to keep the tests incredibly fast.
        self.track = Track(tracknum=4)  # Target format: 04
        self.track.release = Release(id=123)

    @override_settings(DOWNLOAD_BASE_PATH="/var/media/")
    def test_path_construction_and_padding(self):
        """Verify that paths pad IDs with zeros and concatenate correctly."""
        expected_hi = "/var/media/music/hi/0000123/0000123-04.mp3"
        expected_lo = "/var/media/music/lo/0000123/0000123-04.mp3"

        self.assertEqual(self.track.hiPath, expected_hi)
        self.assertEqual(self.track.loPath, expected_lo)

    @patch(
        "catalogue.models.os.path.exists"
    )  # Path to where 'os' is imported in models.py
    def test_availability_properties(self, mock_exists):
        """Verify availability returns correctly based on file existence."""
        # Use patch.object to shortcut the path logic to simple strings
        with (
            patch.object(Track, "hiPath", "/fake/hi.mp3"),
            patch.object(Track, "loPath", "/fake/lo.mp3"),
        ):
            # Scenario A: Files exist on the system
            mock_exists.return_value = True
            self.assertTrue(self.track.hiAvailable)
            self.assertTrue(self.track.loAvailable)
            mock_exists.assert_any_call("/fake/hi.mp3")
            mock_exists.assert_any_call("/fake/lo.mp3")
            # Scenario B: Files are missing from the system
            mock_exists.return_value = False
            self.assertFalse(self.track.hiAvailable)
            self.assertFalse(self.track.loAvailable)


class UnicodeStringTest(TestCase):
    def setUp(self):
        self.release = Release(id=123, artist="test artist", title="test title")
        self.comment = Comment(id=1, comment="test comment")

    def test_release_to_unicode(self):
        self.assertTrue(self.release.__unicode__() == "test artist - test title")

    def test_comment_to_unicode(self):
        self.assertTrue(self.comment.__unicode__() == "test comment")


class ProfileSerializerTest(TestCase):
    def setUp(self):
        # Create a user with both username and email
        self.user_with_email = User.objects.create_user(
            username="JohnDoe",
            email="John.Doe@Example.com",  # Mixed case to test lowercase handling
            first_name="John",
            last_name="Doe",
        )

        # Create a user with only a username (email is empty string)
        self.user_without_email = User.objects.create_user(
            username="JaneDoe",
            email="",
            first_name="Jane",
            last_name="Doe",
        )

    def test_serializer_fields(self):
        """Verify the serializer includes the correct defined fields."""
        serializer = ProfileSerializer(instance=self.user_with_email)
        expected_fields = {"first_name", "last_name", "gravatar", "id"}
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_gravatar_with_email(self):
        """Verify Gravatar URL generation using a lowercase MD5 hash of the email."""
        serializer = ProfileSerializer(instance=self.user_with_email)

        # Expected hash calculations
        expected_email = "john.doe@example.com"
        expected_hash = hashlib.md5(expected_email.encode("utf-8")).hexdigest()
        expected_url = f"https://www.gravatar.com/avatar/{expected_hash}"

        self.assertEqual(serializer.data["gravatar"], expected_url)

    def test_gravatar_fallback_to_username(self):
        """Verify Gravatar URL falls back to username if email is empty."""
        serializer = ProfileSerializer(instance=self.user_without_email)

        # Expected hash calculations using username
        expected_username = "janedoe"
        expected_hash = hashlib.md5(expected_username.encode("utf-8")).hexdigest()
        expected_url = f"https://www.gravatar.com/avatar/{expected_hash}"

        self.assertEqual(serializer.data["gravatar"], expected_url)


class ArtistViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user for authentication
        cls.user = User.objects.create_user(username="testuser", password="password123")
        # URL for the list route (assumes registered as 'artist-list' in your router)
        cls.url = reverse("Artist-list")
        # Create sample releases with duplicate/mixed-case artists to test distinct & sorting
        Release.objects.create(artist="Nirvana", title="Nevermind")
        Release.objects.create(artist="Beatles", title="Abbey Road")
        Release.objects.create(artist="Nirvana", title="In Utero")  # Duplicate artist
        Release.objects.create(artist="Radiohead", title="OK Computer")

    def setUp(self):
        # Authenticate the client by default for endpoint logic tests
        self.client.force_authenticate(user=self.user)

    def test_list_artists_unauthenticated_fails(self):
        """Verify that unauthenticated requests are blocked (403 Forbidden)."""
        self.client.force_authenticate(user=None)  # Clear authentication
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_all_artists_distinct_and_sorted(self):
        """Verify list returns unique artists sorted alphabetically when no term is passed."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Expected: Unique items sorted alphabetically -> ['Beatles', 'Nirvana', 'Radiohead']
        expected_data = ["Beatles", "Nirvana", "Radiohead"]
        self.assertEqual(response.data, expected_data)

    def test_list_artists_filtered_by_term(self):
        """Verify list filters artists using case-insensitive partial matching on 'term'."""
        # Querying 'va' should match 'Nirvana' case-insensitively
        response = self.client.get(self.url, {"term": "va"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ["Nirvana"])

    def test_list_artists_filtered_by_term_case_insensitive(self):
        """Verify that the search term ignores casing rules."""
        # Querying uppercase 'BEAT' should match 'Beatles'
        response = self.client.get(self.url, {"term": "BEAT"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ["Beatles"])

    def test_list_artists_no_match_returns_empty_list(self):
        """Verify that an unmatched term returns a 200 OK with an empty array."""
        response = self.client.get(self.url, {"term": "NonExistentArtist"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class ReleaseViewSetTest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )

        # Create sample data
        self.release1 = Release.objects.create(
            id=123,
            artist="Radiohead",
            title="Kid A",
            year=2000,
            arrivaldate="2026-01-01",
        )
        self.release2 = Release.objects.create(
            artist="Daft Punk", title="Discovery", year=2001, arrivaldate="2026-02-01"
        )

        # Create nested relationships
        self.track1 = Track.objects.create(
            id=1,
            release=self.release1,
            tracktitle="Everything in Its Right Place",
            tracknum=1,
        )

        self.track2 = Track.objects.create(
            id=2, release=self.release1, tracktitle="Kid A", tracknum=2
        )

        self.track3 = Track.objects.create(
            id=3, release=self.release2, tracktitle="Kid Z", tracknum=1
        )

        self.comment1 = Comment.objects.create(
            id=1,
            cdtrackid=1,
            release=self.release1,
            comment="Masterpiece",
            author=self.user,
            createwhen=100,
            modifywho=0,
            modifywhen=0,
        )

        self.bad_comment = Comment.objects.create(
            id=2,
            cdtrackid=3,
            release=self.release2,
            comment="I am a bad person and need to shut up",
            author=self.user,
            createwhen=100,
            modifywho=0,
            modifywhen=0,
            visible=False,
        )

        self.good_comment = Comment.objects.create(
            id=3,
            cdtrackid=3,
            release=self.release2,
            comment="I am a good person and am ok to speak :)",
            author=self.user,
            createwhen=100,
            modifywho=0,
            modifywhen=0,
            visible=True,
        )

        # URL Helpers
        self.list_url = reverse("release-list")
        self.detail_url = reverse("release-detail", kwargs={"pk": self.release1.pk})
        self.tracks_url = reverse("release-tracks", kwargs={"pk": self.release1.pk})
        self.comments_url = reverse("release-comments", kwargs={"pk": self.release1.pk})
        self.comments_url_2 = reverse(
            "release-comments", kwargs={"pk": self.release2.pk}
        )

    # --- PERMISSION TESTS ---
    def test_unauthenticated_user_is_forbidden(self):
        """Verify that anonymous requests are rejected."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- STANDARD CRUD TESTS ---
    def test_list_releases_authenticated(self):
        """Verify authenticated users can fetch the release list with pagination."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)  # LimitOffsetPagination format

    def test_retrieve_single_release(self):
        """Verify fetching a specific release by ID."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Kid A")

    # --- FILTERING, SEARCHING, & ORDERING TESTS ---
    def test_search_by_artist(self):
        """Verify filtering results via the search query parameter."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"search": "Radiohead"})
        self.assertEqual(len(response.data["results"]), 1)

    def test_search_by_nested_track_title(self):
        """Verify search works across the track title relation."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"search": "Everything"})
        self.assertEqual(len(response.data["results"]), 1)

    def test_ordering_by_year_ascending(self):
        """Verify ordering parameter sorts results chronologically."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"ordering": "year"})
        self.assertEqual(response.data["results"][0]["title"], "Kid A")

    # --- CUSTOM ACTION TESTS ---
    def test_get_tracks_ordered_by_tracknum(self):
        """Verify custom tracks action returns nested tracks sorted by track number."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.tracks_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["tracknum"], 1)

    def test_get_comments_ordered_by_pk(self):
        """Verify custom comments action returns nested comments sorted by primary key."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.comments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["comment"], "Masterpiece")

    def test_get_comments_does_not_return_invisible(self):
        """Verify custom comments action does NOT return hidden comments."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.comments_url_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["comment"], "I am a good person and am ok to speak :)"
        )


# Create a temporary directory for file path testing
TEMP_DIR = tempfile.mkdtemp()


@override_settings(
    DOWNLOAD_BASE_PATH=os.path.join(TEMP_DIR, "downloads/"), API_PREFIX="/api/v1/"
)
class TrackViewSetTest(APITestCase):
    def setUp(self):
        # Create user and authenticate
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.client.force_authenticate(user=self.user)

        # Setup mock entities
        self.release = Release.objects.create(
            id=42, artist="Daft Punk", title="Discovery"
        )

        # Construct a track path pointing into our temp testing directory
        self.test_audio_path = os.path.join(
            TEMP_DIR, "downloads", "music", "hi", "0000042", "0000042-01.mp3"
        )
        self.track = Track.objects.create(
            release=self.release,
            tracktitle="One More Time",
            id=1,
            tracknum=1,
        )

        # URL helpers
        self.audio_url = reverse("track-audio", kwargs={"pk": self.track.pk})
        self.download_base_url = f"/api/tracks/{self.track.pk}/download/"

    def tearDown(self):
        # Clean up files created during the tests
        if os.path.exists(self.test_audio_path):
            os.remove(self.test_audio_path)
        # Clean up dynamically created directories
        try:
            os.removedirs(os.path.dirname(self.test_audio_path))
        except OSError:
            pass

    # --- AUDIO UPLOAD TESTS ---
    def test_audio_upload_creates_directory_and_writes_file(self):
        """Verify audio action saves the uploaded file chunks to track.hiPath."""
        # Ensure destination folder does not exist before test runs
        if os.path.exists(os.path.dirname(self.test_audio_path)):
            os.removedirs(os.path.dirname(self.test_audio_path))

        # Mock an uploaded audio file
        uploaded_file = SimpleUploadedFile(
            name="test_track.mp3",
            content=b"fake_mp3_binary_data_stream_chunks",
            content_type="audio/mp3",
        )

        response = self.client.post(
            self.audio_url, {"file": uploaded_file}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(os.path.exists(self.test_audio_path))

        with open(self.test_audio_path, "rb") as f:
            self.assertEqual(f.read(), b"fake_mp3_binary_data_stream_chunks")

    def test_audio_upload_missing_file_raises_key_error(self):
        """Verify uploading without a 'file' payload triggers a bad request or server error."""
        # This will raise a KeyError in the view due to request.FILES['file']
        with self.assertRaises(KeyError):
            self.client.post(self.audio_url, {}, format="multipart")

    # --- DOWNLOAD LINK TESTS ---
    def test_download_high_quality_generates_correct_path_and_url(self):
        """Verify 'hi' quality generates the correct absolute URL and saves DownloadLink."""
        response = self.client.get(f"{self.download_base_url}hi/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify the database entry
        link = DownloadLink.objects.latest("id")
        self.assertEqual(link.name, "One More Time")
        # Format checks for 7-digit zero-padded release ID and 2-digit tracknum
        expected_path = os.path.join(
            TEMP_DIR, "downloads/", "music/hi/0000042/0000042-01.mp3"
        )
        self.assertEqual(link.path, expected_path)

        # Verify absolute URI format in json response
        expected_json_url = f"http://testserver/api/v1/download/{link.id}/"
        self.assertJSONEqual(response.content.decode(), {"url": expected_json_url})

    def test_download_low_quality_uses_lo_folder(self):
        """Verify 'lo' quality configuration paths correctly."""
        response = self.client.get(f"{self.download_base_url}lo/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        link = DownloadLink.objects.latest("id")
        self.assertIn("music/lo/", link.path)

    def test_download_invalid_quality_returns_404(self):
        """Verify string qualities other than hi/lo trigger an explicit Http404."""
        response = self.client.get(f"{self.download_base_url}medium/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_download_invalid_track_id_returns_404(self):
        """Verify get_object_or_404 handles non-existent track records safely."""
        invalid_url = "/api/v1/tracks/99999/download/hi/"
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommentViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.client.force_authenticate(user=self.user)

        self.release = Release.objects.create(
            artist="Daft Punk", title="Discovery", year=2001, arrivaldate="2026-02-01"
        )

        self.bad_comment = Comment.objects.create(
            id=1,
            cdtrackid=1,
            release=self.release,
            comment="I am a bad person and need to shut up",
            author=self.user,
            createwhen=100,
            modifywho=0,
            modifywhen=0,
            visible=True,
        )

        self.good_comment = Comment.objects.create(
            id=2,
            cdtrackid=1,
            release=self.release,
            comment="I am a good person and am ok to speak :)",
            author=self.user,
            createwhen=100,
            modifywho=0,
            modifywhen=0,
            visible=True,
        )

        self.comment_1_url = "/api/comments/1/"
        self.comment_2_url = "/api/comments/2/"

    def test_patch_visible_hides_comment(self):
        response1 = self.client.get(self.comment_1_url)
        response2 = self.client.get(self.comment_2_url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        patch_data = {"visible": "false"}
        _ = self.client.patch(
            self.comment_1_url,
            data=json.dumps(patch_data),
            content_type="application/json",
        )
        # Comment 1 should no longer be accessible via the comments API
        response_404 = self.client.get(self.comment_1_url)
        response_200 = self.client.get(self.comment_2_url)
        self.assertEqual(response_404.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
