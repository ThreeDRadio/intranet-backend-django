import base64
import json
import logging
import urllib

import requests
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Playlist

wordpress_user = settings.WORDPRESS_USER
wordpress_password = settings.WORDPRESS_API_KEY
wordpress_credentials = wordpress_user + ":" + wordpress_password
wordpress_token = base64.b64encode(wordpress_credentials.encode())

wordpress_header = {
    "Authorization": "Basic " + wordpress_token.decode("utf-8"),
    "user-agent": "threedradio-api",
    "accept": "application/json",
}

headers = {"user-agent": "threedradio-api", "accept": "application/json"}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

""" Finds the website's show for this playlist """


def find_show_for_playlist(showName):
    api_url = f"{settings.WORDPRESS_URL}/program?search=" + urllib.parse.quote_plus(
        showName
    )
    response = requests.get(api_url, headers=headers)

    if response.status_code != 200:
        logger.error(
            f"Find show request failed with status:{response.status_code}. Show={showName}"
        )
        return None

    response_json = response.json()
    if len(response_json) == 0:
        return None
    return response_json[0]


def createPost(title, showId, content, date):
    api_url = f"{settings.WORDPRESS_URL}/program-playlist"
    data = {
        "title": title,
        "status": "publish",
        "content": content,
        "date": date,
        "program": [showId],
    }

    response = requests.post(api_url, headers=wordpress_header, json=data)

    # Check if the request was successful and we receive 201 Created. If not then drop an error in logs.
    if response.status_code != 201:
        logger.error(
            f"Create Wordpress playlist request failed with status:{response.status_code}. Body:{json.dumps(data, indent=2)}"
        )

    return response.status_code == 201


@receiver(post_save, sender=Playlist)
def playlist_to_wordpress(sender, instance, **kwargs):
    try:
        if not settings.WORDPRESS_USER or not settings.WORDPRESS_API_KEY:
            logger.error("No wordpress auth. Giving up")
            return

        if instance.published or not instance.complete:
            return

        wpShow = find_show_for_playlist(instance.show.name)

        if not wpShow:
            logger.error(
                f"No Wordpress show found for showId {instance.show.name} (showId={instance.show.id}). Bailing."
            )
            return

        content = "<ol>"
        for track in instance.tracks.all().order_by("index"):
            content += "<li>" + track.artist + " - " + track.title + "</li>\n"
        content += "</ol>"

        timestamp = str(instance.date) + " " + str(instance.show.endTime)

        created = createPost(
            instance.show.name + ": " + str(instance.date),
            wpShow["id"],
            content,
            timestamp,
        )

        if created:
            instance.published = True
            instance.save()
        else:
            logger.error(
                f"Playlist {instance.show.name} {timestamp} (showId={instance.show.id}) was not published.",
            )
    except Exception as e:
        logger.error(
            f"Exception when publishing playlist {instance.show.name} (showId={instance.show.id}). ",
            e,
        )
