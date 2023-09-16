from django.core.management.base import BaseCommand
from Directory.models import Gang, Character, Streamer, CharacterGangLink
import requests, json, time, os
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    help = 'Updates the database with gang information via web scraping'

    current_dir = os.path.dirname(os.path.abspath(__file__))
    TOKEN_FILE = os.path.join(current_dir, '..', '..', '..', 'config', 'twitch_token.json')
    ID_AND_SECRET_FILE = os.path.join(current_dir, '..', '..', '..', 'config', 'secret_and_id.json')

    def get_id_and_secret(self):

        with open(self.ID_AND_SECRET_FILE, 'r') as file:
            return json.load(file)

    
    def get_oauth_token(self, id, secret):

        url = "https://id.twitch.tv/oauth2/token"
        payload = {
            'client_id': id,
            'client_secret': secret,
            'grant_type': 'client_credentials'
        }
        response = requests.post(url, params=payload)
        return response.json()
    

    def save_token_to_file(self, response):
        data = {
            'token': response.get('access_token'),
            'expires_at': time.time() + response.get('expires_in'),
            'token_type': response.get('token_type')
        }
        with open(self.TOKEN_FILE, 'w') as file:
            json.dump(data, file)


    def get_token_from_file(self):

        id_and_secret = self.get_id_and_secret()

        try:
            with open(self.TOKEN_FILE, 'r') as file:
                
                data = json.load(file)
                if data['expires_at'] > time.time() + 60:
                    return data
                else:
                    self.save_token_to_file(self.get_oauth_token(id_and_secret.get("client_id"),id_and_secret.get("client_secret")))
                    return self.get_token_from_file()
        except:
            return None
    

    def are_channels_live(self, channel_names):

        id_and_secret = self.get_id_and_secret()
        oauth_token = self.get_token_from_file().get("token")

        if(len(channel_names) == 0):
            return[]
        
        url = "https://api.twitch.tv/helix/streams"

        headers = {
            'Client-ID': id_and_secret.get('client_id'),
            'Authorization': f'Bearer {oauth_token}'
        }
        params = [("user_login", channel) for channel in channel_names]
        response = requests.get(url, headers=headers, params=params)

        data = response.json().get('data', [])

        final_data = [{'name': streamer_data.get('user_login').lower(), 'live': len(streamer_data) > 0, 'gta': streamer_data.get('game_name').lower() == "grand theft auto v",
                        'title': streamer_data.get('title'),'viewcount': streamer_data.get('viewer_count')} for streamer_data in data]
        return final_data


    def check_rate_limit(self):

        id_and_secret = self.get_id_and_secret()
        oauth_token = self.get_oauth_token(id_and_secret.get('client_id'), id_and_secret.get('secret_id')).get('token')

        url = "https://api.twitch.tv/helix/streams"

        headers = {
            'Client-ID': id_and_secret.get('client_id'),
            'Authorization': f'Bearer {oauth_token}'
        }

        response = requests.get(url, headers=headers)
        
        limit = response.headers.get('Ratelimit-Limit')
        remaining = response.headers.get('Ratelimit-Remaining')
        reset = int(response.headers.get('Ratelimit-Reset')) - time.time()
        
        return {
            "Limit": limit,
            "Remaining": remaining,
            "Reset": reset
        }

    def handle(self, *args, **kwargs):
        
        Streamer.objects.update(streamer_is_live = False, streamer_on_gta = False, streamer_title = "", streamer_viewcount = 0)

        all_groups = Gang.objects.all()

        for group in all_groups:

            logger.info(f"Checking {group.name}")

            characterlinks = CharacterGangLink.objects.filter(member_gang_id=group.id)
            streamers = [link.member_character.character_streamer for link in characterlinks]

            channel_data = self.are_channels_live([bloke.streamer_name for bloke in streamers])

            people_live = False
            people_on_gta = False

            for result in channel_data:
                people_live += 1
                people_on_gta += result.get('gta')

                Streamer.objects.filter(streamer_name__iexact = result.get('name')).update(
                    streamer_on_gta = result.get('gta'),
                    streamer_is_live = True,
                    streamer_title = result.get('title'),
                    streamer_viewcount = result.get('viewcount') if result.get('viewcount') else 0
                )
            
            group.people_live = people_live
            group.people_on_gta = people_on_gta
            group.save()