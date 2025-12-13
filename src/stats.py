from copy import deepcopy

def calculate_possessions(team_box):
    """
    Estimate possessions from box score.
    Formula: (FGA - OREB) + TOV + (0.4 * FTA)
    NOTE: Using total rebounds as a rough proxy for OREB.
    """
    return (
        team_box["fg_attempts"]
        - team_box["rebounds"]  # TODO: replace with offensive rebounds later
        + team_box["turnovers"]
        + 0.4 * team_box["ft_attempts"]
    )

def calculate_offensive_rating(points, possessions):
    if possessions == 0:
        return 0
    return (points / possessions) * 100

def calculate_defensive_rating(opp_points, possessions):
    if possessions == 0:
        return 0
    return (opp_points / possessions) * 100

def calculate_true_shooting_pct(points, fga, fta):
    denom = (fga + 0.44 * fta)
    if denom == 0:
        return 0
    return points / (2 * denom)

def calculate_player_stats(player, team_points, team_possessions):
    stats = player.stats.copy()

    # Shooting accuracy
    stats["fg_pct"] = (
        player.stats["fg_made"] / player.stats["fg_attempts"]
        if player.stats["fg_attempts"] > 0 else 0
    )
    stats["three_pct"] = (
        player.stats["three_made"] / player.stats["three_attempts"]
        if player.stats["three_attempts"] > 0 else 0
    )
    stats["ft_pct"] = (
        player.stats["ft_made"] / player.stats["ft_attempts"]
        if player.stats["ft_attempts"] > 0 else 0
    )

    # True shooting
    stats["ts_pct"] = calculate_true_shooting_pct(
        player.stats["points"],
        player.stats["fg_attempts"],
        player.stats["ft_attempts"]
    )

    # Usage rate
    player_poss = (
        player.stats["fg_attempts"]
        + player.stats["turnovers"]
        + 0.4 * player.stats["ft_attempts"]
    )
    stats["usage_rate"] = (
        (player_poss / team_possessions) * 100
        if team_possessions > 0 else 0
    )

    return stats

def build_advanced_boxscore(game_result, team_a, team_b):
    enhanced = deepcopy(game_result)

    # Team A possessions
    team_a_poss = calculate_possessions({
        "fg_attempts": sum(p.stats["fg_attempts"] for p in team_a.players),
        "rebounds": sum(p.stats["rebounds"] for p in team_a.players),
        "turnovers": sum(p.stats["turnovers"] for p in team_a.players),
        "ft_attempts": sum(p.stats["ft_attempts"] for p in team_a.players)
    })

    # Team B possessions
    team_b_poss = calculate_possessions({
        "fg_attempts": sum(p.stats["fg_attempts"] for p in team_b.players),
        "rebounds": sum(p.stats["rebounds"] for p in team_b.players),
        "turnovers": sum(p.stats["turnovers"] for p in team_b.players),
        "ft_attempts": sum(p.stats["ft_attempts"] for p in team_b.players)
    })

    # Team-level advanced stats
    enhanced[team_a.name]["team_stats"] = {
        "possessions": team_a_poss,
        "pace": team_a_poss,  # TODO: refine later
        "offensive_rating": calculate_offensive_rating(team_a.score, team_a_poss),
        "defensive_rating": calculate_defensive_rating(team_b.score, team_a_poss)
    }

    enhanced[team_b.name]["team_stats"] = {
        "possessions": team_b_poss,
        "pace": team_b_poss,
        "offensive_rating": calculate_offensive_rating(team_b.score, team_b_poss),
        "defensive_rating": calculate_defensive_rating(team_a.score, team_b_poss)
    }

    # Player-level advanced stats
    for p in team_a.players:
        enhanced[team_a.name]["players"][p.name].update(
            calculate_player_stats(p, team_a.score, team_a_poss)
        )

    for p in team_b.players:
        enhanced[team_b.name]["players"][p.name].update(
            calculate_player_stats(p, team_b.score, team_b_poss)
        )

    return enhanced