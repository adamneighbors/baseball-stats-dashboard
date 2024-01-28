from io import StringIO
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from playerstats.models import Player
from datetime import datetime


class Command(BaseCommand):
    help = 'Loads nonexistent players to playerstats_player table'

    def __init__(self, stdout: StringIO | None = ..., stderr: StringIO | None = ...) -> None:
        super().__init__(stdout, stderr)

        self.headers = {
            "X-RapidAPI-Key": settings.API_KEY,
            "X-RapidAPI-Host": settings.API_HOST
        }

    def handle(self, *args, **kwargs):
        self.create_all_missing_players()

    def get_player_list(self):
        url = settings.API_URL + 'getMLBPlayerList'
        querystring = {
        }

        response = requests.get(
            url=url,
            headers=self.headers,
            params=querystring
        )

        if response.status_code == 200:
            return response.json().get('body')
        print('Failed to get list of players.')
        if response.reason:
            print(response.reason)
        return None

    def get_player_info(self, player_id):
        url = settings.API_URL + 'getMLBPlayerInfo'
        querystring = {
            'playerID': player_id
        }

        response = requests.get(
            url=url,
            headers=self.headers,
            params=querystring
        )

        if response.status_code == 200:
            return response.json().get('body')
        print('Failed to get players info.')
        if response.reason:
            print(response.reason)

    def get_all_player_info(self):
        players = []
        player_list = self.get_player_list()
        for player in player_list:
            url = settings.API_URL + 'getMLBPlayerInfo'
            querystring = {
                'playerID': player.get('playerID')
            }

            response = requests.get(
                url=url,
                headers=self.headers,
                params=querystring
            )

            if response.status_code == 200:
                players.append(response.json().get('body'))
                continue
            print('Failed to get players info.')
            if response.reason:
                print(response.reason)
        return players

    def create_missing_player(self, player_id):
        player = self.get_player_info(player_id)

        if not player:
            return None

        feet, inches = player.get('height').split('-')
        height = f"""{feet}' {inches}\""""

        team_id = player.get('teamID', 0)
        if team_id == '': 
            team_id = 0

        player_defaults = {
            'id': player.get('playerID'),
            'name': player.get('longName'),
            'bats': player.get('bat'),
            'throws': player.get('throw'),
            'height': height or 'N/A',
            'weight': player.get('weight'),
            'dob': datetime.strptime(player.get('bDay'), '%m/%d/%Y'),
            'headshot': player.get('mlbHeadshot'),
            'position': player.get('pos'),
            'team_id': team_id
        }

        try:
            player_defaults['jersey_number'] = int(player.get('jerseyNum'))
        except ValueError:
            pass

        Player.objects.get_or_create(id=player_defaults.get('id'), defaults=player_defaults)

    def create_all_missing_players(self):
        player_data = self.get_player_info()

        if not player_data:
            return None
        
        for player in player_data:
            feet, inches = player.get('height').split('-')
            height = f"""{feet}' {inches}\""""

            player_defaults = {
                'id': player.get('playerID'),
                'name': player.get('longName'),
                'bats': player.get('bat'),
                'throws': player.get('throw'),
                'height': height or 'N/A',
                'weight': player.get('weight'),
                'dob': datetime.strptime(player.get('bDay'), '%m/%d/%Y'),
                'headshot': player.get('mlbHeadshot'),
                'position': player.get('pos'),
                'team_id': player.get('teamID')
            }

            try:
                player_defaults['jersey_number'] = int(player.get('jerseyNum'))
            except ValueError:
                pass

            Player.objects.get_or_create(id=player_defaults.get('id'), defaults=player_defaults)
