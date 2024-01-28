from django.db import models


class Season(models.Model):
    opening_day = models.DateField(
        null=False,
        default='1900-01-01'
    )
    closing_day = models.DateField(
        null=False,
        default='1900-01-01'
    )

    def __str__(self):
        return f"The {self.opening_day}/{self.closing_day} season of MLB Baseball."


class Team(models.Model):
    abbreviation = models.CharField(
        null=False,
        default='N/A',
        max_length=3
    )
    city = models.CharField(
        null=False,
        default='N/A',
        max_length=25
    )
    name = models.CharField(
        null=False,
        default='N/A',
        max_length=50
    )
    mlb_logo = models.URLField(
        null=True,
        default='N/A'
    )
    division = models.CharField(
        null=True,
        default='N/A',
        max_length=15
    )
    conference = models.CharField(
        null=True,
        default='N/A',
        max_length=50
    )

    def __str__(self):
        pass


class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='current_team')
    name = models.CharField(
        null=False,
        default='N/A',
        max_length=50
    )
    position = models.CharField(
        max_length=3,
        null=False,
        default='N/A'
    )
    jersey_number = models.IntegerField(
        null=True
    )
    bats = models.CharField(
        null=True,
        max_length=1
    )
    throws = models.CharField(
        null=True,
        max_length=1
    )
    height = models.CharField(
        null=False,
        default="""0' 0\"""",
        max_length=6
        )
    weight = models.IntegerField(
        null=False,
        default=0
    )
    dob = models.DateField(
        null=False,
        default='1900-01-01'
    )
    headshot = models.URLField(
        null=True
    )

    def __str__(self):
        return f"{self.name}"


class Game(models.Model):
    home_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='home_games')
    away_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='away_games')
    mlb_link = models.URLField(
        null=True
    )
    season = models.IntegerField(
        null=True,
        default=1900
    )
    game_date = models.DateField(
        null=False,
        default=0
    )
    game_type = models.CharField(
        null=True,
        max_length=50
    )
    game_id  = models.CharField(
        null=False,
        max_length=25
    )
    mlb_id  = models.IntegerField(
        null=True
    )

    class Meta:
        ordering = ('game_date',)


class GameBoxScore(models.Model):
    game  = models.ForeignKey(Game, on_delete=models.PROTECT, related_name='box_scores')
    game_length  = models.TimeField(
        null=True
    )
    umpires  = models.CharField(
        max_length=255
    )
    attendance  = models.IntegerField(
        null=True
    )
    venue  = models.CharField(
        null=True,
        max_length=50
    )
    home_result  = models.CharField(
        null=True,
        max_length=1
    )
    first_pitch  = models.TimeField(
        null=True
    )
    wind  = models.CharField(
        null=True,
        max_length=25
    )
    away_result  = models.CharField(
        null=True,
        max_length=1
    )
    weather  = models.CharField(
        null=True,
        max_length=50
    )


class PlayerGameStats(models.Model):
    player = models.ForeignKey(Player, on_delete=models.PROTECT, related_name='game_stats')
    game = models.ForeignKey(Game, on_delete=models.PROTECT, related_name='player_stats')
    positions_played = models.CharField(
        null=True,
        max_length=10
    )
    starting_position = models.CharField(
        null=True,
        max_length=2
    )
    started = models.BooleanField(
        default=True
    )


class PlayerGamePitchingStats(models.Model):
    player_game = models.ForeignKey(PlayerGameStats, on_delete=models.PROTECT, related_name='pitching_stats')
    ground_outs = models.IntegerField(
        null=True,
    )
    balk = models.IntegerField(
        null=True,
    )
    wild_pitch = models.IntegerField(
        null=True
    )
    fly_outs = models.IntegerField(
        null=True
    )
    inherited_runners = models.IntegerField(
        null=True
    )
    batters_faced = models.IntegerField(
        null=True
    )
    pitches = models.IntegerField(
        null=True
    )
    strikes = models.IntegerField(
        null=True
    )
    inherited_runners_scored = models.IntegerField(
        null=True
    )


class PlayerGameFieldingStats(models.Model):
    player_game = models.ForeignKey(PlayerGameStats, on_delete=models.PROTECT, related_name='fielding_stats')
    passed_balls = models.IntegerField(
        null=True
    )
    outfield_assists = models.IntegerField(
        null=True
    )
    errors = models.IntegerField(
        null=True
    )
    pick_offs = models.IntegerField(
        null=True
    )


class PlayerGameHittingStats(models.Model):
    player_game = models.ForeignKey(PlayerGameStats, on_delete=models.PROTECT, related_name='hitting_stats')
    walk = models.IntegerField(
        null=True,
    )
    at_bats = models.IntegerField(
        null=True,
    )
    batting_order = models.IntegerField(
        null=True,
    )
    hits = models.IntegerField(
        null=True,
    )
    intentional_walks = models.IntegerField(
        null=True,
    )
    substitution_order = models.IntegerField(
        null=True,
    )
    home_runs = models.IntegerField(
        null=True,
    )
    total_bases = models.IntegerField(
        null=True,
    )
    triples = models.IntegerField(
        null=True,
    )
    grounded_into_double_play = models.IntegerField(
        null=True,
    )
    doubles = models.IntegerField(
        null=True,
    )
    runs = models.IntegerField(
        null=True,
    )
    batting_average = models.FloatField(
        null=True,
    )
    sacrifice_flies = models.IntegerField(
        null=True,
    )
    sacrifice_hits = models.IntegerField(
        null=True,
    )
    hit_by_pitch = models.IntegerField(
        null=True,
    )
    runs_batted_in = models.IntegerField(
        null=True,
    )
    strikeouts = models.IntegerField(
        null=True,
    )
    left_on_base = models.FloatField(
        null=True,
    )


class PlayerGameRunningStats(models.Model):
    player_game = models.ForeignKey(PlayerGameStats, on_delete=models.PROTECT, related_name='running_stats')
    caught_stealing = models.IntegerField(
        null=True,
    )
    stolen_bases = models.IntegerField(
        null=True,
    )
    pick_offs = models.IntegerField(
        null=True,
    )
