from player import Player
from team import Team
from game_sim import GameSim

# Create players with full ratings + archetypes
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
    archetype="Sharpshooter"
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
    archetype="Slasher"
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
    archetype="Playmaker"
)

# Create DIFFERENT players for Team B
q1 = Player("Derek", p1.ratings, archetype="Two-Way")
q2 = Player("Evan", p2.ratings, archetype="Big Man")
q3 = Player("Fiona", p3.ratings, archetype="Sharpshooter")

team_a = Team("Team A", [p1, p2, p3])
team_b = Team("Team B", [q1, q2, q3])

# Run the game
game = GameSim(team_a, team_b)
box = game.simulate_game()

# Print results
import pprint
pprint.pprint(box)