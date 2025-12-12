import random

class GameSim:
    def __init__(self, team_a, team_b):
        self.team_a = team_a
        self.team_b = team_b

    def simulate_possession(self, offense, defense):
        shooter = random.choice(offense.players)

        # Turnover chance
        turnover_roll = random.random()
        turnover_chance = 0.08 + (0.02 * (50 - shooter.ratings["iq"]) / 50)

        if turnover_roll < turnover_chance:
            shooter.stats["turnovers"] += 1

            # Steal chance
            if random.random() < 0.4:
                defender = random.choice(defense.players)
                defender.stats["steals"] += 1
            return

        # Decide shot type
        shot_type_roll = random.random()
        if shot_type_roll < 0.35:
            shot_type = "three"
        else:
            shot_type = "two"

        # Attempt shot
        if shot_type == "three":
            shooter.stats["three_attempts"] += 1
            shooter.stats["fg_attempts"] += 1

            shot_value = 3
            shot_rating = shooter.ratings["three_point"]
        else:
            shooter.stats["fg_attempts"] += 1
            shot_value = 2
            shot_rating = shooter.ratings["shooting"]

        # Defense contest
        defender = random.choice(defense.players)
        contest = defender.ratings["defense"] + random.randint(-10, 10)

        # Block chance
        if random.random() < (defender.ratings["block"] / 200):
            defender.stats["blocks"] += 1
            return

        # Make or miss
        shot_roll = shot_rating + random.randint(-25, 25)
        if shot_roll > contest:
            shooter.stats["fg_made"] += 1
            shooter.stats["points"] += shot_value
            offense.score += shot_value

            if shot_type == "three":
                shooter.stats["three_made"] += 1

            # Assist chance
            if random.random() < 0.35:
                passer = random.choice([p for p in offense.players if p != shooter])
                passer.stats["assists"] += 1
            return

        # Missed shot → rebound
        if random.random() < 0.55:
            rebounder = random.choice(offense.players)
        else:
            rebounder = random.choice(defense.players)

        rebounder.stats["rebounds"] += 1

        # Foul chance on shot
        foul_roll = random.random()
        foul_chance = 0.07 + (0.02 * (50 - defender.ratings["discipline"]) / 50)

        if foul_roll < foul_chance:
            defender.stats["fouls"] += 1
            self.shoot_free_throws(shooter, 2 if shot_type == "two" else 3)

    def shoot_free_throws(self, shooter, attempts):
        for _ in range(attempts):
            shooter.stats["ft_attempts"] += 1
            ft_roll = shooter.ratings["shooting"] + random.randint(-20, 20)

            if ft_roll > 50:
                shooter.stats["ft_made"] += 1
                shooter.stats["points"] += 1

                # Add to team score
                if shooter in self.team_a.players:
                    self.team_a.score += 1
                else:
                    self.team_b.score += 1

def simulate_game(self, possessions=100):
    # Reset stats
    for p in self.team_a.players + self.team_b.players:
        p.reset_stats()

    # Pace variation
    pace = random.randint(85, 105)

    for _ in range(pace):
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