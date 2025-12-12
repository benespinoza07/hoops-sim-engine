import random

class GameSim:
    def __init__(self, team_a, team_b):
        self.team_a = team_a
        self.team_b = team_b

    def simulate_possession(self, offense, defense):
        shooter = random.choice(offense.players)
        shooter.stats["fg_attempts"] += 1

        shot_chance = shooter.ratings["shooting"] + random.randint(-20, 20)
        defense_factor = sum(p.ratings["defense"] for p in defense.players) / len(defense.players)

        if shot_chance > defense_factor:
            shooter.stats["fg_made"] += 1
            shooter.stats["points"] += 2
            offense.score += 2

    def simulate_game(self, possessions=100):
        for _ in range(possessions):
            self.simulate_possession(self.team_a, self.team_b)
            self.simulate_possession(self.team_b, self.team_a)

        return {
            "team_a_score": self.team_a.score,
            "team_b_score": self.team_b.score
        }