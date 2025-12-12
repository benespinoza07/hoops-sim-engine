from player import Player
from team import Team
from game_sim import GameSim

# Create players
p1 = Player("Alice", {"shooting": 70, "defense": 60, "rebounding": 50, "passing": 55, "iq": 65})
p2 = Player("Bob", {"shooting": 65, "defense": 55, "rebounding": 60, "passing": 50, "iq": 60})

team_a = Team("Team A", [p1, p2])
team_b = Team("Team B", [p1, p2])

game = GameSim(team_a, team_b)
result = game.simulate_game()

print(result)