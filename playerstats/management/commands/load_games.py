from io import StringIO
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from playerstats.models import Game, Team
from datetime import datetime
import pytz


class Command(BaseCommand):
    help = 'Loads nonexistent games to playerstats_game table'

    def __init__(self, stdout: StringIO | None = ..., stderr: StringIO | None = ...) -> None:
        super().__init__(stdout, stderr)

        self.headers = {
            "X-RapidAPI-Key": settings.API_KEY,
            "X-RapidAPI-Host": settings.API_HOST
        }

    def handle(self, *args, **kwargs):
        self.create_missing_games()

    def get_team_schedule(self):
        url = settings.API_URL + 'getMLBTeamSchedule'
        querystring = {
            'teamID': 28,
            'season': 2023
        }

        response = requests.get(
            url=url,
            headers=self.headers,
            params=querystring
        )

        if response.status_code == 200:
            return response.json().get('body').get('schedule')
        print('Failed to get team schedule.')
        if response.reason:
            print(response.reason)
        return None

    def create_missing_games(self):
        game_data = self.get_team_schedule()

        if not game_data:
            return None

        for game in game_data:
            game_defaults = {
                'game_id': game.get('gameID'),
                'season': 2023,
                'game_date': pytz.timezone(settings.TIME_ZONE).localize(datetime.utcfromtimestamp(float(game.get('gameTime_epoch')))),
                'home_team': Team.objects.get(id=int(game.get('teamIDHome'))),
                'away_team': Team.objects.get(id=int(game.get('teamIDAway'))),
                'game_type': game.get('gameType')
            }

            Game.objects.get_or_create(game_id=game_defaults.get('game_id'), defaults=game_defaults)
