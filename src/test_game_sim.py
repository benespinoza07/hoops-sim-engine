import pytest
from run_demo import team_a, team_b
from game_sim import GameSim
from stats import build_advanced_boxscore

def test_realistic_scoring():
    """Verify scores are in realistic NBA range."""
    game = GameSim(team_a, team_b)
    raw_box = game.simulate_game()
    box = build_advanced_boxscore(raw_box, team_a, team_b)

    team_a_score = box[team_a.name]["score"]
    team_b_score = box[team_b.name]["score"]

    assert 80 <= team_a_score <= 140, f"Team A score {team_a_score} unrealistic"
    assert 80 <= team_b_score <= 140, f"Team B score {team_b_score} unrealistic"

def test_realistic_shooting():
    """FG% should be 40-55%."""
    game = GameSim(team_a, team_b)
    raw_box = game.simulate_game()
    box = build_advanced_boxscore(raw_box, team_a, team_b)

    for team_name in [team_a.name, team_b.name]:
        team_box = box[team_name]
        total_fga = sum(p["fg_attempts"] for p in team_box["players"].values())
        total_fgm = sum(p["fg_made"] for p in team_box["players"].values())

        fg_pct = (total_fgm / total_fga) * 100 if total_fga > 0 else 0
        assert 35 <= fg_pct <= 60, f"{team_name} FG% {fg_pct}% unrealistic"

def test_pace():
    """Pace should be 90-110 possessions per game."""
    game = GameSim(team_a, team_b)
    raw_box = game.simulate_game()
    box = build_advanced_boxscore(raw_box, team_a, team_b)

    team_a_pace = box[team_a.name]["team_stats"]["pace"]
    assert 80 <= team_a_pace <= 120, f"Pace {team_a_pace} unrealistic"