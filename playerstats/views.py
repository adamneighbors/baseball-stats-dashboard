from django.shortcuts import HttpResponse, render, get_object_or_404
from django.db.models import Q, Sum, Avg, ExpressionWrapper, FloatField, F
from .models import Player, PlayerGameStats
from playerstats.charts import return_batting_chart, return_pitching_chart

texas_rangers_team_id = 28


def home(request):
    all_players = Player.objects.filter(team_id=texas_rangers_team_id)

    context = {
        'players': all_players ,
    }
    return render(request, "home.html", context)


def player_by_year(request, player_id, year):
    player = get_object_or_404(Player, id=player_id)
    player_game_stats = PlayerGameStats.objects.filter(
        player=player,
        game__season=year,
        game__game_type='REGULAR_SEASON'
    )

    hitting_stats = player_game_stats.prefetch_related('hitting_stats').order_by('hitting_stats__player_game__game__game_date')

    summed_hitting_stats = hitting_stats.annotate(
        at_bats=Sum('hitting_stats__at_bats'),
        runs=Sum('hitting_stats__runs'),
        hits=Sum('hitting_stats__hits'),
        doubles=Sum('hitting_stats__doubles'),
        triples=Sum('hitting_stats__triples'),
        home_runs=Sum('hitting_stats__home_runs'),
        rbi=Sum('hitting_stats__runs_batted_in')
    ).aggregate(
        total_at_bats=Sum('at_bats'),
        total_runs=Sum('runs'),
        total_hits=Sum('hits'),
        total_doubles=Sum('doubles'),
        total_triples=Sum('triples'),
        total_home_runs=Sum('home_runs'),
        total_rbi=Sum('rbi')
    )

    pitching_stats = player_game_stats.prefetch_related('pitching_stats').order_by('pitching_stats__player_game__game__game_date')

    summed_pitching_stats = pitching_stats.annotate(
        pitches=Sum('pitching_stats__pitches'),
        strikes=Sum('pitching_stats__strikes'),
        ground_outs=Sum('pitching_stats__ground_outs'),
        fly_outs=Sum('pitching_stats__fly_outs'),
        batters_faced=Sum('pitching_stats__batters_faced'),
    ).aggregate(
        total_pitches=Sum('pitches'),
        total_strikes=Sum('strikes'),
        total_ground_outs=Sum('ground_outs'),
        total_fly_outs=Sum('fly_outs'),
        total_batters_faced=Sum('batters_faced'),
    )

    ba_chart = return_batting_chart(hitting_stats)
    pitching_chart = return_pitching_chart(pitching_stats)

    if ba_chart:
        ba_chart = ba_chart.to_html()
    if pitching_chart:
        pitching_chart = pitching_chart.to_html()

    if summed_hitting_stats.get('total_hits') and summed_hitting_stats.get('total_at_bats'):
        summed_hitting_stats['total_batting_average'] = f"{round(summed_hitting_stats.get('total_hits') / summed_hitting_stats.get('total_at_bats'), 3):.3f}"

    summed_pitching_stats.update(summed_hitting_stats)
    context = {
        'player': player,
        'player_stats': summed_pitching_stats,
        'year': year,
        'ba_chart': ba_chart,
        'pitch_chart': pitching_chart
    }

    return render(request, "player.html", context)


def search_players(request):
    query = request.GET.get('q', '')

    players = []

    if query:
        players = Player.objects.filter(
            Q(name__icontains=query), Q(team_id=texas_rangers_team_id)
        )

    return render(request, 'search_results_ajax.html', {'players': players})
