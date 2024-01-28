import plotly.express as px
from playerstats.templatetags.custom_filters import remove_leading_zero


def return_batting_chart(hitting_stats):
    chart_data = []
    # Create chart data for each game
    for game_stats in hitting_stats:
        hitting_stats_first = game_stats.hitting_stats.first()

        if not hitting_stats_first:
            continue

        if hitting_stats_first and hitting_stats_first.at_bats != 0:
            batting_average = round(hitting_stats_first.hits / hitting_stats_first.at_bats, 3)
            batting_average_visual = remove_leading_zero(f"{batting_average:.3f}")
        else:
            continue

        chart_data.append({
            'Game Day': game_stats.game.game_date,
            'Hits/At Bats': batting_average,
            'batting_average_visual': batting_average_visual,
            'Hits': hitting_stats_first.hits,
            'At Bats': hitting_stats_first.at_bats
        })

    # Just a check in case player didn't play that season
    if not chart_data:
        return None

    # Setup Hoverdata info
    hits_visual_values = [item['Hits'] for item in chart_data]
    at_bats_values = [item['At Bats'] for item in chart_data]
    batting_average_visual_values = [item['batting_average_visual'] for item in chart_data]

    # Create figure for BA chart
    fig = px.line(
        data_frame=chart_data,
        x='Game Day',
        y='Hits/At Bats',
        title='Batting Average Per Game',
        custom_data=(hits_visual_values, at_bats_values, batting_average_visual_values)
    ).update_layout(
        title={
            'font_size': 22,
            'x': 0.5
        }
    )

    # Update hoverdata with wanted format
    fig.update_traces(
        hovertemplate='Date: %{x}<br>'+
        'Hits: %{customdata[0]}<br>'+
        'At Bats: %{customdata[1]}<br>'+
        'Hits/At Bats: %{customdata[2]}'
    )

    return fig


def return_pitching_chart(pitching_stats):
    chart_data = []
    # Create chart data for each game
    for game_stats in pitching_stats:
        pitching_stats_first = game_stats.pitching_stats.first()
        if not pitching_stats_first:
            continue
        if not pitching_stats_first.pitches:
            continue
        
        chart_data.append({
            'Game Day': game_stats.game.game_date,
            'Strikes/Pitches': round(pitching_stats_first.strikes / pitching_stats_first.pitches, 3),
        })

    # Just a check in case player didn't play that season
    if not chart_data:
        return None

    # Create figure for pitching chart
    fig = px.line(
        data_frame=chart_data,
        x='Game Day',
        y='Strikes/Pitches',
        title='Strikes/Pitches Per Game',
    ).update_layout(
        title={
            'font_size': 22,
            'x': 0.5
        }
    )

    return fig
