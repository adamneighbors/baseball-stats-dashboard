from datetime import datetime
from io import StringIO
import json
from pathlib import Path
import pytz
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from playerstats.models import Game, GameBoxScore, Player, \
    PlayerGameStats, PlayerGamePitchingStats, PlayerGameHittingStats, PlayerGameFieldingStats, \
    PlayerGameRunningStats
from playerstats.management.commands.load_players import Command as PlayerCommand


class Command(BaseCommand):
    help = 'Loads nonexistent box_scores to playerstats_gameboxscore table'

    def __init__(self, stdout: StringIO | None = ..., stderr: StringIO | None = ...) -> None:
        super().__init__(stdout, stderr)

        self.headers = {
            "X-RapidAPI-Key": settings.API_KEY,
            "X-RapidAPI-Host": settings.API_HOST
        }

    def handle(self, *args, **kwargs):
        # self.get_box_scores()
        # self.create_missing_box_scores()
        self.create_missing_player_stats()

    def get_box_scores(self):
        games = Game.objects.all()
        box_scores = []
        for game in games:
            if game.season != 2023:
                continue
            url = settings.API_URL + 'getMLBBoxScore'
            querystring = {
                'gameID': game.game_id
            }

            response = requests.get(
                url=url,
                headers=self.headers,
                params=querystring
            )

            if response.status_code == 200:
                box_scores.append(response.json().get('body'))
                with open(f'data/{game.game_id}.json', "w") as outfile:
                    outfile.write(json.dumps(response.json(), indent=4))
                continue
            print('Failed to get team schedule.')
            if response.reason:
                print(response.reason)

    def read_json_files(self):
        box_score_data = []
        for json_file in settings.JSON_DATA_DIR.iterdir():
            if not json_file.is_file():
                continue
            with open(json_file, 'r') as file:
                box_score_data.append(json.load(file).get('body'))

        return box_score_data

    def create_missing_player_stats(self):
        box_score_data = self.read_json_files()
        existing_players_id = [x.id for x in Player.objects.all()]

        if not box_score_data:
            return None

        for box_score in box_score_data:
            for player_id, stats in box_score.get('playerStats').items():
                player_id = int(player_id)
                pitching_stats = stats.get('Pitching')
                fielding_stats = stats.get('Fielding')
                hitting_stats = stats.get('Hitting')
                running_stats = stats.get('BaseRunning')

                if player_id not in existing_players_id:
                    PlayerCommand().create_missing_player(player_id)
                    existing_players_id.append(player_id)
                game = Game.objects.get(game_id=box_score.get('gameID'))
                player = Player.objects.get(id=player_id)
                player_game_defaults = {
                    'player': player,
                    'game': game,
                    'positions_played': stats.get('allPositionsPlayed'),
                    'starting_position': stats.get('startingPosition'),
                    'started': stats.get('started')
                }

                player_game_stats = PlayerGameStats.objects.get_or_create(game_id=game.id, player_id=player_id, defaults=player_game_defaults)[0]

                if int(pitching_stats.get('Pitches', 0)) > 0:
                    pitching_defaults = {
                        'player_game': player_game_stats,
                        'ground_outs': pitching_stats.get('Groundouts'),
                        'balk': pitching_stats.get('Balk'),
                        'wild_pitch': pitching_stats.get('Wild Pitch'),
                        'fly_outs': pitching_stats.get('Flyouts'),
                        'inherited_runners': pitching_stats.get('Inherited Runners'),
                        'batters_faced': pitching_stats.get('Batters Faced'),
                        'pitches': pitching_stats.get('Pitches'),
                        'strikes': pitching_stats.get('Strikes'),
                        'inherited_runners_scored': pitching_stats.get('Inherited Runners Scored')
                    }

                    PlayerGamePitchingStats.objects.get_or_create(player_game=player_game_stats.id, defaults=pitching_defaults)

                if int(pitching_stats.get('Pitches', 0)) > 0:
                    fielding_defaults = {
                        'player_game': player_game_stats,
                        'passed_balls': fielding_stats.get('Passed Ball'),
                        'outfield_assists': fielding_stats.get('Outfield assists'),
                        'errors': fielding_stats.get('E'),
                        'pick_offs': fielding_stats.get('Pickoffs')
                    }

                    PlayerGameFieldingStats.objects.get_or_create(player_game=player_game_stats.id, defaults=fielding_defaults)


                if int(hitting_stats.get('AB', 0)) > 0:
                    hitting_defaults = {
                        'player_game': player_game_stats,
                        'walk': hitting_stats.get('BB'),
                        'at_bats': hitting_stats.get('AB'),
                        'batting_order': hitting_stats.get('battingOrder'),
                        'hits': hitting_stats.get('H'),
                        'intentional_walks': hitting_stats.get('IBB'),
                        'substitution_order': hitting_stats.get('substitutionOrder'),
                        'home_runs': hitting_stats.get('HR'),
                        'total_bases': hitting_stats.get('TB'),
                        'triples': hitting_stats.get('3B'),
                        'grounded_into_double_play': hitting_stats.get('GIDP'),
                        'doubles': hitting_stats.get('2B'),
                        'runs': hitting_stats.get('R'),
                        'batting_average': hitting_stats.get('AVG'),
                        'sacrifice_flies': hitting_stats.get('SF'),
                        'sacrifice_hits': hitting_stats.get('SAC'),
                        'hit_by_pitch': hitting_stats.get('HBP'),
                        'runs_batted_in': hitting_stats.get('RBI'),
                        'strikeouts': hitting_stats.get('SO'),
                        'left_on_base': hitting_stats.get('LOB')
                    }

                    PlayerGameHittingStats.objects.get_or_create(player_game=player_game_stats.id, defaults=hitting_defaults)

                if int(running_stats.get('CS', 0)) > 0 or int(running_stats.get('SB', 0)) > 0  or int(running_stats.get('PO', 0)) > 0:
                    running_defaults = {
                        'player_game': player_game_stats,
                        'caught_stealing': running_stats.get('CS'),
                        'stolen_bases': running_stats.get('SB'),
                        'pick_offs': running_stats.get('PO')
                    }

                    PlayerGameRunningStats.objects.get_or_create(player_game=player_game_stats.id, defaults=running_defaults)

    def create_missing_box_scores(self):
        box_score_data = self.read_json_files()
        if not box_score_data:
            return None

        for box_score in box_score_data:
            first_pitch = datetime.strptime(box_score.get('FirstPitch'), '%I:%M %p').time()
            game_length = box_score.get('GameLength')
            if ' ' in game_length:
                game_length = datetime.strptime(box_score.get('GameLength').split(' ')[0], '%I:%M').time()
            else:
                game_length = datetime.strptime(box_score.get('GameLength'), '%I:%M').time()

            game_defaults = {
                'game': Game.objects.get(game_id=box_score.get('gameID')),
                'game_length': game_length,
                'umpires': box_score.get('Umpires'),
                'attendance': box_score.get('Attendance').replace(',', ''),
                'venue': box_score.get('Venue'),
                'home_result': box_score.get('homeResult'),
                'first_pitch': first_pitch,
                'wind': box_score.get('Wind'),
                'away_result': box_score.get('awayResult'),
                'weather': box_score.get('Weather')
            }

            GameBoxScore.objects.get_or_create(game_id=game_defaults.get('game').id, defaults=game_defaults)
