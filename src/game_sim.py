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

        # Archetype-based shot selection
        shot_roll = random.random()

        if shot_roll < shooter.tendencies["three_point_rate"]:
            shot_type = "three"
        elif shot_roll < shooter.tendencies["three_point_rate"] + shooter.tendencies["mid_range_rate"]:
            shot_type = "two"
        else:
            shot_type = "drive"

        # Attempt shot
        if shot_type == "three":
            shooter.stats["three_attempts"] += 1
            shooter.stats["fg_attempts"] += 1
            shot_value = 3
            shot_rating = shooter.ratings["three_point"]

        elif shot_type == "two":
            shooter.stats["fg_attempts"] += 1
            shot_value = 2
            shot_rating = shooter.ratings["shooting"]

        else:  # Drive logic
            shooter.stats["fg_attempts"] += 1
            shot_value = 2
            shot_rating = shooter.ratings["finishing"] + random.randint(-15, 10)

        # Defense contest
        defender = random.choice(defense.players)
        contest = defender.ratings["defense"] + random.randint(-10, 10)

        # Block chance (higher on drives)
        block_factor = 200 if shot_type != "drive" else 150
        if random.random() < (defender.ratings["block"] / block_factor):
            defender.stats["blocks"] += 1
            return

        # Make or miss
        shot_roll = shot_rating + random.randint(-25, 20)
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
        off_reb_weight = sum(p.playstyle["rebound_focus"] for p in offense.players)
        def_reb_weight = sum(p.playstyle["rebound_focus"] for p in defense.players)

        total_weight = off_reb_weight + def_reb_weight
        off_reb_prob = off_reb_weight / total_weight

        # Decide which team gets the rebound
        if random.random() < off_reb_prob * 0.75:
            rebounder = random.choice(offense.players)
        else:
            rebounder = random.choice(defense.players)

        rebounder.stats["rebounds"] += 1


        # Foul chance (archetype-influenced)
        foul_roll = random.random()
        base_foul = 0.07
        discipline_factor = (50 - defender.ratings["discipline"]) / 50
        aggression_factor = shooter.playstyle["aggression"] * 0.02

        foul_chance = base_foul + discipline_factor + aggression_factor

        if foul_roll < foul_chance:
            defender.stats["fouls"] += 1
            self.shoot_free_throws(shooter, 2 if shot_type != "three" else 3)

    def shoot_free_throws(self, shooter, attempts):
        for _ in range(attempts):
            shooter.stats["ft_attempts"] += 1
            ft_roll = shooter.ratings["shooting"] + random.randint(-20, 20)

            if ft_roll > 50:
                shooter.stats["ft_made"] += 1
                shooter.stats["points"] += 1

                if shooter in self.team_a.players:
                    self.team_a.score += 1
                else:
                    self.team_b.score += 1

    def simulate_game(self):
        # Reset stats
        for p in self.team_a.players + self.team_b.players:
            p.reset_stats()

        # Pace variation
        pace = random.randint(60, 75)

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