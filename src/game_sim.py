import random

class GameSim:
    def __init__(self, team_a, team_b):
        self.team_a = team_a
        self.team_b = team_b

    def simulate_possession(self, offense, defense):
        shooter = random.choice(offense.players)
        shooter.stats["fg_attempts"] += 1

        # Shot quality vs defense
        shot_chance = shooter.ratings["shooting"] + random.randint(-20, 20)
        defense_factor = sum(p.ratings["defense"] for p in defense.players) / len(defense.players)

        # Make or miss
        if shot_chance > defense_factor:
            shooter.stats["fg_made"] += 1
            shooter.stats["points"] += 2
            offense.score += 2

            # Chance of assist
            if random.random() < 0.35:
                passer = random.choice([p for p in offense.players if p != shooter])
                passer.stats["assists"] += 1
        else:
            # Rebound battle
            if random.random() < 0.55:
                rebounder = random.choice(offense.players)
            else:
                rebounder = random.choice(defense.players)

            rebounder.stats["rebounds"] += 1

    def simulate_game(self, possessions=100):
        # Reset stats
        for p in self.team_a.players + self.team_b.players:
            p.reset_stats()

        for _ in range(possessions):
            self.simulate_possession(self.team_a, self.team_b)
            self.simulate_possession(self.team_b, self.team_a)

        return self.generate_box_score()

    def generate_box_score(self):
        return {
            self.team_a.name: {
                "score": self.team_a.score,
                "players": {p.name: p.stats for p in self.team_a.players}
            },
            self.team_b.name: {
                "score": self.team_b.score,
                "players": {p.name: p.stats for p in self.team_b.players}
            }
        }