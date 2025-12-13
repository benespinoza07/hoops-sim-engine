from player import Player
from team import Team
from game_sim import GameSim

# ===== Team A: 5 players =====

p1 = Player(
    "Alice",
    {
        "shooting": 70,
        "three_point": 75,
        "finishing": 65,
        "defense": 60,
        "steal": 55,
        "rebounding": 40,
        "passing": 60,
        "block": 30,
        "iq": 70,
        "discipline": 80
    },
    archetype="Sharpshooter",
    position="PG"
)

p2 = Player(
    "Bob",
    {
        "shooting": 65,
        "three_point": 60,
        "finishing": 70,
        "defense": 55,
        "steal": 50,
        "rebounding": 45,
        "passing": 55,
        "block": 25,
        "iq": 65,
        "discipline": 75
    },
    archetype="Slasher",
    position="SG"
)

p3 = Player(
    "Cara",
    {
        "shooting": 75,
        "three_point": 72,
        "finishing": 68,
        "defense": 50,
        "steal": 45,
        "rebounding": 35,
        "passing": 50,
        "block": 20,
        "iq": 60,
        "discipline": 70
    },
    archetype="Playmaker",
    position="SF"
)

p4 = Player(
    "Dylan",
    {
        "shooting": 60,
        "three_point": 50,
        "finishing": 72,
        "defense": 65,
        "steal": 55,
        "rebounding": 70,
        "passing": 45,
        "block": 65,
        "iq": 68,
        "discipline": 75
    },
    archetype="Two-Way",
    position="PF"
)

p5 = Player(
    "Eli",
    {
        "shooting": 55,
        "three_point": 40,
        "finishing": 75,
        "defense": 68,
        "steal": 50,
        "rebounding": 80,
        "passing": 40,
        "block": 72,
        "iq": 65,
        "discipline": 70
    },
    archetype="Big Man",
    position="C"
)

team_a = Team("Team A", [p1, p2, p3, p4, p5])

# ===== Team B: 5 players =====

q1 = Player(
    "Frank",
    {
        "shooting": 68,
        "three_point": 70,
        "finishing": 62,
        "defense": 58,
        "steal": 52,
        "rebounding": 38,
        "passing": 62,
        "block": 28,
        "iq": 72,
        "discipline": 82
    },
    archetype="Sharpshooter",
    position="PG"
)

q2 = Player(
    "Grace",
    {
        "shooting": 64,
        "three_point": 58,
        "finishing": 72,
        "defense": 57,
        "steal": 53,
        "rebounding": 48,
        "passing": 54,
        "block": 26,
        "iq": 66,
        "discipline": 76
    },
    archetype="Slasher",
    position="SG"
)

q3 = Player(
    "Hank",
    {
        "shooting": 73,
        "three_point": 70,
        "finishing": 69,
        "defense": 52,
        "steal": 46,
        "rebounding": 37,
        "passing": 52,
        "block": 22,
        "iq": 61,
        "discipline": 71
    },
    archetype="Playmaker",
    position="SF"
)

q4 = Player(
    "Ivan",
    {
        "shooting": 59,
        "three_point": 48,
        "finishing": 73,
        "defense": 67,
        "steal": 56,
        "rebounding": 72,
        "passing": 43,
        "block": 67,
        "iq": 69,
        "discipline": 74
    },
    archetype="Two-Way",
    position="PF"
)

q5 = Player(
    "Jake",
    {
        "shooting": 54,
        "three_point": 38,
        "finishing": 76,
        "defense": 70,
        "steal": 51,
        "rebounding": 82,
        "passing": 41,
        "block": 75,
        "iq": 64,
        "discipline": 69
    },
    archetype="Big Man",
    position="C"
)

team_b = Team("Team B", [q1, q2, q3, q4, q5])

# Run the game
game = GameSim(team_a, team_b)
box = game.simulate_game()

# Print results
import pprint
pprint.pprint(box)