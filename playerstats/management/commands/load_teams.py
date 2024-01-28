from io import StringIO
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from playerstats.models import Team


class Command(BaseCommand):
    help = 'Loads nonexistent teams to playerstats_team table'

    def __init__(self, stdout: StringIO | None = ..., stderr: StringIO | None = ...) -> None:
        super().__init__(stdout, stderr)

        self.headers = {
            "X-RapidAPI-Key": settings.API_KEY,
            "X-RapidAPI-Host": settings.API_HOST
        }
    
    def handle(self, *args, **kwargs):
        self.create_missing_teams()

    def get_mlb_teams(self):
        url = settings.API_URL + 'getMLBTeams'
        querystring = {
            "teamStats":"false",
            "topPerformers":"false"
        }

        response = requests.get(
            url=url,
            headers=self.headers,
            params=querystring
        )

        if response.status_code == 200:
            return response.json().get('body')
        print('Failed to get list of MLB teams.')
        if response.reason:
            print(response.reason)
        return None

    def create_missing_teams(self):
        team_data = self.get_mlb_teams()

        if not team_data:
            return None
        
        for team in team_data:
            team_defaults = {
                'id': team.get('teamID'),
                'abbreviation': team.get('teamAbv'),
                'city': team.get('teamCity'),
                'name': team.get('teamName'),
                'mlb_logo': team.get('mlbLogo1'),
                'division': team.get('division'),
                'conference': team.get('conference')
            }

            Team.objects.get_or_create(id=team_defaults.get('id'), defaults=team_defaults)
