import json
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Playlist
import requests
import base64
import urllib
from django.conf import settings

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

""" Finds the website's show for this playlist """
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def find_show_for_playlist(showName):
    api_url = (
        "https://www.threedradio.com/wp-json/wp/v2/program?search="
        + urllib.parse.quote_plus(showName)
    )
    response = requests.get(api_url, headers=headers)
    response_json = response.json()
    if response_json:
        return response_json[0]


def createPost(title, showId, content, date):
    api_url = "https://www.threedradio.com/wp-json/wp/v2/program-playlist"
    data = {
        "title": title,
        "status": "publish",
        "content": content,
        "date": date,
        "program": [showId],
    }
    pretty_json = json.dumps(data, indent=2)
    logger.info("request:" + pretty_json)
    response = requests.post(api_url, headers=wordpress_header, json=data)
    # Check if the request was successful
    if response.status_code == 200:
        try:
            pretty_resp = json.dumps(response.json(), indent=2)
            logger.info("response:" + pretty_resp)
        except ValueError:
            logger.error("Response is not valid JSON")
    else:
        logger.warning(f"Request failed with status: {response.status_code}")


@receiver(post_save, sender=Playlist)
def playlist_to_wordpress(sender, instance, **kwargs):
    try:
        if not settings.WORDPRESS_USER or not settings.WORDPRESS_API_KEY:
            logger.error("No wordpress auth. Giving up")
            return

        if instance.published or not instance.complete:
            return

        wpShow = find_show_for_playlist(instance.show.name)

        if wpShow:
            logger.info("Found Wordpress Show: " + str(wpShow["slug"]))
        else:
            logger.error(
                f"No Wordpress show found for showId {instance.show.name} (showId={instance.show.id}). Bailing."
            )
            return

        content = "<ol>"
        for track in instance.tracks.all().order_by("index"):
            content += "<li>" + track.artist + " - " + track.title + "</li>\n"
        content += "</ol>"

        timestamp = str(instance.date) + " " + str(instance.show.endTime)

        logger.info(f"Publishing playlist {str(wpShow)} timestamp={timestamp}")
        createPost(
            instance.show.name + ": " + str(instance.date),
            wpShow["id"],
            content,
            timestamp,
        )
        logger.info(f"Published playlist {str(wpShow)} timestamp={timestamp}!")
        instance.published = True
        instance.save()
    except Exception as e:
        logger.error(
            f"Error when publishing playlist {instance.show.name} (showId={instance.show.id}). ",
            e,
        )
