from django.contrib.auth.models import User
from django.urls import resolve, reverse
from rest_framework.test import (
    APIClient,
    APIRequestFactory,
    APITestCase,
    force_authenticate,
)

from playlist.models import Playlist, PlaylistEntry, Show
from session.models import Whitelist


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


class PlaylistEntryViewsetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", "password", "fake1@user.com")
        self.whitelist = Whitelist.objects.create(
            ip="127.198.1.1", name="test whitelist"
        )
        # Index testing
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
        self.playlist_entry_1 = PlaylistEntry.objects.create(
            playlist=self.playlist_instance,
            artist="test artist",
            title="test title",
            local=False,
            female=False,
            australian=False,
            newRelease=False,
            index=1,
            id=99,
        )
        self.playlist_entry_2 = PlaylistEntry.objects.create(
            playlist=self.playlist_instance,
            artist="test artist 2",
            title="test title 2",
            local=False,
            female=False,
            australian=False,
            newRelease=False,
            index=2,
            id=100,
        )
        self.playlist_entry_3 = PlaylistEntry.objects.create(
            playlist=self.playlist_instance,
            artist="test artist 3",
            title="test title 3",
            local=False,
            female=False,
            australian=False,
            newRelease=False,
            index=3,
            id=103,
        )
        self.playlist_entry_4 = PlaylistEntry.objects.create(
            playlist=self.playlist_instance,
            artist="test artist 4",
            title="test title 4",
            local=False,
            female=False,
            australian=False,
            newRelease=False,
            index=4,
            id=108,
        )

    def test_grant_access_for_unauthenticated_unwhitelisted(self):
        """Makes sure a non-authenticated, non-whitelisted request fails with forbidden"""
        factory = APIRequestFactory()
        url = reverse("PlaylistEntry-list")
        view = resolve(url).func
        request = factory.get(url)
        response = view(request)
        self.assertEqual(response.status_code, 403)

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

    # Move semantics for index
    def test_move_no_to_throws_400(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("PlaylistEntry-move", kwargs={"pk": 100})
        response = client.post(url, {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_move_to_lt_1_throws_400(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("PlaylistEntry-move", kwargs={"pk": 100})
        response = client.post(url, {"to": 0}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_move_to_gt_largest_throws_400(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("PlaylistEntry-move", kwargs={"pk": 100})
        response = client.post(url, {"to": 5}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_move_to_null_throws_400(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("PlaylistEntry-move", kwargs={"pk": 100})
        response = client.post(url, {"to": None}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_move_with_unindexed_entry_present(self):
        # Regression test for #92: an entry without an index must not break
        # moving the indexed entries (on Postgres the old largest-index
        # lookup could return the unindexed entry and crash).
        PlaylistEntry.objects.create(
            playlist=self.playlist_instance,
            artist="unindexed artist",
            title="unindexed title",
            local=False,
            female=False,
            australian=False,
            newRelease=False,
            index=None,
            id=110,
        )
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("PlaylistEntry-move", kwargs={"pk": 99})
        response = client.post(url, {"to": 2}, format="json")
        self.assertEqual(response.status_code, 204)
        indexed_order = list(
            PlaylistEntry.objects.filter(
                playlist=self.playlist_instance, index__isnull=False
            )
            .order_by("index")
            .values_list("id", flat=True)
        )
        self.assertEqual(
            indexed_order,
            [
                self.playlist_entry_2.id,
                self.playlist_entry_1.id,
                self.playlist_entry_3.id,
                self.playlist_entry_4.id,
            ],
        )

    def test_move_entry_without_index_throws_400(self):
        unindexed = PlaylistEntry.objects.create(
            playlist=self.playlist_instance,
            artist="unindexed artist",
            title="unindexed title",
            local=False,
            female=False,
            australian=False,
            newRelease=False,
            index=None,
            id=110,
        )
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("PlaylistEntry-move", kwargs={"pk": unindexed.id})
        response = client.post(url, {"to": 1}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_move_in_playlist_with_no_indexes_throws_400(self):
        # Regression test for #92: with no indexed entries at all there is
        # no valid move target; this used to crash with
        # TypeError: '>' not supported between 'int' and 'NoneType'.
        playlist = Playlist.objects.create(
            id=1000,
            show=self.show,
            date="2026-01-02",
            australianQuota=20,
            localQuota=20,
            femaleQuota=40,
        )
        entry = PlaylistEntry.objects.create(
            playlist=playlist,
            artist="unindexed artist",
            title="unindexed title",
            local=False,
            female=False,
            australian=False,
            newRelease=False,
            index=None,
            id=111,
        )
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("PlaylistEntry-move", kwargs={"pk": entry.id})
        response = client.post(url, {"to": 1}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_move_forward_1(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("PlaylistEntry-move", kwargs={"pk": 99})
        response = client.post(url, {"to": 2}, format="json")
        self.assertEqual(response.status_code, 204)
        current_order = list(
            PlaylistEntry.objects.filter(playlist=self.playlist_instance)
            .order_by("index")
            .values_list("id", flat=True)
        )

        # Assert the exact expected sequence of IDs
        self.assertEqual(
            current_order,
            [
                self.playlist_entry_2.id,
                self.playlist_entry_1.id,
                self.playlist_entry_3.id,
                self.playlist_entry_4.id,
            ],
        )

    def test_move_back_1(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("PlaylistEntry-move", kwargs={"pk": 103})
        response = client.post(url, {"to": 2}, format="json")
        self.assertEqual(response.status_code, 204)
        current_order = list(
            PlaylistEntry.objects.filter(playlist=self.playlist_instance)
            .order_by("index")
            .values_list("id", flat=True)
        )

        # Assert the exact expected sequence of IDs
        self.assertEqual(
            current_order,
            [
                self.playlist_entry_1.id,
                self.playlist_entry_3.id,
                self.playlist_entry_2.id,
                self.playlist_entry_4.id,
            ],
        )

    def test_move_first_to_last(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("PlaylistEntry-move", kwargs={"pk": 99})
        response = client.post(url, {"to": 4}, format="json")
        self.assertEqual(response.status_code, 204)
        current_order = list(
            PlaylistEntry.objects.filter(playlist=self.playlist_instance)
            .order_by("index")
            .values_list("id", flat=True)
        )

        # Assert the exact expected sequence of IDs
        self.assertEqual(
            current_order,
            [
                self.playlist_entry_2.id,
                self.playlist_entry_3.id,
                self.playlist_entry_4.id,
                self.playlist_entry_1.id,
            ],
        )

    def test_move_last_to_first(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("PlaylistEntry-move", kwargs={"pk": 108})
        response = client.post(url, {"to": 1}, format="json")
        self.assertEqual(response.status_code, 204)
        current_order = list(
            PlaylistEntry.objects.filter(playlist=self.playlist_instance)
            .order_by("index")
            .values_list("id", flat=True)
        )

        # Assert the exact expected sequence of IDs
        self.assertEqual(
            current_order,
            [
                self.playlist_entry_4.id,
                self.playlist_entry_1.id,
                self.playlist_entry_2.id,
                self.playlist_entry_3.id,
            ],
        )
