from player import Player
from team import Team
from game_sim import GameSim

# Create simple players
p1 = Player("Alice", {"shooting": 70, "defense": 60})
p2 = Player("Bob", {"shooting": 65, "defense": 55})
p3 = Player("Cara", {"shooting": 75, "defense": 50})

team_a = Team("Team A", [p1, p2, p3])
team_b = Team("Team B", [p1, p2, p3])

game = GameSim(team_a, team_b)
box = game.simulate_game()

print(box)