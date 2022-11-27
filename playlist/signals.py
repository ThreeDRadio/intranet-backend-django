from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Playlist 
import requests
import base64
from django.conf import settings

base_category = 167

wordpress_user = settings.WORDPRESS_USER
wordpress_password = settings.WORDPRESS_API_KEY
wordpress_credentials = wordpress_user + ":" + wordpress_password
wordpress_token = base64.b64encode(wordpress_credentials.encode())
wordpress_header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8')}

''' Finds the category for this show, nil otherwise '''
def find_category_for_show(showName):
  api_url = 'https://www.threedradio.com/wp-json/wp/v2/categories?parent=' + str(base_category) + '&search=' + showName
  response = requests.get(api_url)
  response_json = response.json()
  if response_json:
    return response_json[0]

def create_category_for_show(showName):
  api_url = 'https://www.threedradio.com/wp-json/wp/v2/categories'
  data = {
    'name' : showName,
    'description': 'Show playlists for ' + showName,
    'parent': base_category
  }
  response = requests.post(api_url,headers=wordpress_header, json=data)
  return response.json()

def createPost(title, categoryId, content):
  api_url = 'https://www.threedradio.com/wp-json/wp/v2/posts'
  data = {
    'title' : title,
    'status': 'publish',
    'content': content,
    'categories': [categoryId]
  }
  response = requests.post(api_url,headers=wordpress_header, json=data)

  
@receiver(post_save, sender=Playlist)
def playlist_to_wordpress(sender, instance, **kwargs):

  try:
    if settings.WORDPRESS_USER == False or settings.WORDPRESS_API_KEY == False:
      print('No wordpress auth. Giving up')
      return

    if instance.published:
      print('Already published')
    elif instance.complete == False:
      print('Playlist not complete yet')
    else:
      category = find_category_for_show(instance.show.name)

      if category:
        print('Found category ' + str(category['id']))
      else:
        print('No category found, creating')
        category = create_category_for_show(instance.show.name)

      print(instance.show.name)
      print(instance.date)

      content = '<ol>\n'
      for track in instance.tracks.all().order_by('index'):
        content += '  <li>' + track.artist + ' - ' + track.title + '</li>\n'
      content += '</ol>\n'

      print(content)
      createPost(instance.show.name + ': ' + str(instance.date), category['id'], content)
      instance.published = True
      instance.save()
  except Exception as e:
    print('Could not upload playlist')
    print(e)
    