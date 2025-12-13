import random

# ============================
# Shooter + Shot Type Helpers
# ============================

def select_shooter(offense):
    """Choose shooter using position, shooting talent, and aggression."""
    position_weights = {
        "PG": 1.25,
        "SG": 1.20,
        "SF": 1.00,
        "PF": 0.85,
        "C": 0.70
    }

    weights = []
    for p in offense.on_floor:
        base = position_weights.get(p.position, 1.0)

        shooting_factor = (p.ratings["shooting"] / 100) * 0.5
        aggression_factor = p.playstyle["aggression"] * 0.3

        weight = base + shooting_factor + aggression_factor
        weights.append(weight)

    return random.choices(offense.on_floor, weights=weights, k=1)[0]


def select_shot_type(shooter):
    """Choose shot type using tendencies + positional influence."""
    base_three = shooter.tendencies["three_point_rate"]

    if shooter.position in ["PG", "SG"]:
        base_three += 0.10

    if shooter.position in ["PF", "C"]:
        base_three -= 0.05

    base_three = max(0, min(1, base_three))

    roll = random.random()
    if roll < base_three:
        return "three"
    elif roll < base_three + shooter.tendencies["mid_range_rate"]:
        return "two"
    else:
        return "drive"


# ============================
# Game Simulation Class
# ============================

class GameSim:
    def __init__(self, team_a, team_b):
        self.team_a = team_a
        self.team_b = team_b

        # Earlier subs for realism
        self.sub_stamina_threshold = 50
        self.max_fouls_before_sub = 4

    # ---------- Substitution logic ----------

    def check_substitutions(self, team):
        for player in list(team.on_floor):
            needs_sub = False

            if player.stamina < self.sub_stamina_threshold:
                needs_sub = True

            if player.stats["fouls"] >= self.max_fouls_before_sub:
                needs_sub = True

            if not needs_sub:
                continue

            bench_candidates = team.get_bench_by_position(player.position)

            if not bench_candidates:
                if not team.bench:
                    continue
                bench_candidates = sorted(team.bench, key=lambda p: p.stamina, reverse=True)

            sub_in = max(bench_candidates, key=lambda p: p.stamina)
            team.swap_players(out_player=player, in_player=sub_in)

    # ---------- Possession logic ----------

    def simulate_possession(self, offense, defense):

        shooter = select_shooter(offense)

        shooter.stamina = max(0, shooter.stamina - random.randint(2, 4))

        for p in offense.on_floor + defense.on_floor:
            if p != shooter:
                p.stamina = max(0, p.stamina - random.randint(1, 2))

        for p in offense.on_floor + defense.on_floor:
            p.stats["fatigue_load"] += 1

        turnover_roll = random.random()
        fatigue_turnover_bonus = (100 - shooter.stamina) * 0.0012
        shooter.stats["fatigue_turnover_penalty"] += fatigue_turnover_bonus

        turnover_chance = (
            0.07
            + (0.02 * (50 - shooter.ratings["iq"]) / 50)
            + fatigue_turnover_bonus
        )

        if turnover_roll < turnover_chance:
            shooter.stats["turnovers"] += 1
            if random.random() < 0.35:
                defender = random.choice(defense.on_floor)
                defender.stats["steals"] += 1
            return

        shot_type = select_shot_type(shooter)

        # ---------- Shot logic with tuned fatigue penalties ----------

        if shot_type == "three":
            shooter.stats["three_attempts"] += 1
            shooter.stats["fg_attempts"] += 1
            shooter.stats["fatigue_load"] += 2
            shot_value = 3

            fatigue_penalty = (100 - shooter.stamina) * 0.08
            shooter.stats["fatigue_shooting_penalty"] += fatigue_penalty

            shot_rating = shooter.ratings["three_point"] - fatigue_penalty

        elif shot_type == "two":
            shooter.stats["fg_attempts"] += 1
            shooter.stats["fatigue_load"] += 2
            shot_value = 2

            fatigue_penalty = (100 - shooter.stamina) * 0.08
            shooter.stats["fatigue_shooting_penalty"] += fatigue_penalty

            shot_rating = shooter.ratings["shooting"] - fatigue_penalty

        else:
            shooter.stats["fg_attempts"] += 1
            shooter.stats["fatigue_load"] += 4
            shot_value = 2

            fatigue_penalty = (100 - shooter.stamina) * 0.12
            shooter.stats["fatigue_shooting_penalty"] += fatigue_penalty

            shot_rating = shooter.ratings["finishing"] - fatigue_penalty + random.randint(-10, 10)

        # ---------- Contest logic (tuned randomness) ----------

        defender = random.choice(defense.on_floor)
        defense_fatigue_penalty = (100 - defender.stamina) * 0.10

        defender.stats["fatigue_defense_penalty"] += defense_fatigue_penalty
        defender.stats["fatigue_load"] += 1

        contest = (defender.ratings["defense"] - defense_fatigue_penalty) + random.randint(-5, 8)

        # ---------- Block chance ----------

        block_factor = 200 if shot_type != "drive" else 150
        if random.random() < (defender.ratings["block"] / block_factor):
            defender.stats["blocks"] += 1
            return

        # ---------- Make or miss (tuned randomness) ----------

        shot_roll = shot_rating + random.randint(-15, 15)
        if shot_roll > contest:
            shooter.stats["fg_made"] += 1
            shooter.stats["points"] += shot_value
            offense.score += shot_value

            if shot_type == "three":
                shooter.stats["three_made"] += 1

            if random.random() < 0.40:
                passer = random.choice([p for p in offense.on_floor if p != shooter])
                passer.stats["assists"] += 1
            return

        # ---------- Missed shot → rebound ----------

        off_reb_weight = sum(p.playstyle["rebound_focus"] for p in offense.on_floor)
        def_reb_weight = sum(p.playstyle["rebound_focus"] for p in defense.on_floor)
        total_weight = off_reb_weight + def_reb_weight
        off_reb_prob = off_reb_weight / total_weight if total_weight > 0 else 0.5

        if random.random() < off_reb_prob * 0.70:
            rebounder = random.choice(offense.on_floor)
        else:
            rebounder = random.choice(defense.on_floor)

        rebounder.stats["rebounds"] += 1

        # ---------- Foul chance ----------

        foul_roll = random.random()
        base_foul = 0.06
        discipline_factor = (50 - defender.ratings["discipline"]) / 50
        aggression_factor = shooter.playstyle["aggression"] * 0.015

        foul_chance = base_foul + discipline_factor + aggression_factor

        if foul_roll < foul_chance:
            defender.stats["fouls"] += 1
            self.shoot_free_throws(shooter, 2 if shot_type != "three" else 3, offense)

    # ---------- FIXED FREE THROW FUNCTION ----------

    def shoot_free_throws(self, shooter, attempts, offense):
        for _ in range(attempts):
            shooter.stats["ft_attempts"] += 1
            ft_roll = shooter.ratings["shooting"] + random.randint(-15, 15)
            if ft_roll > 50:
                shooter.stats["ft_made"] += 1
                shooter.stats["points"] += 1
                offense.score += 1

    def simulate_game(self):
        for p in self.team_a.players + self.team_b.players:
            p.reset_stats()

        # NBA pace
        pace = random.randint(90, 110)

        for i in range(pace):

            if i == pace // 2:
                for p in self.team_a.players + self.team_b.players:
                    p.stamina = min(p.max_stamina, p.stamina + 20)

            self.simulate_possession(self.team_a, self.team_b)
            self.simulate_possession(self.team_b, self.team_a)

            for p in self.team_a.players + self.team_b.players:
                p.stamina = min(p.max_stamina, p.stamina + 0.5)

            self.check_substitutions(self.team_a)
            self.check_substitutions(self.team_b)

        return self.generate_box_score()

    def generate_box_score(self):
        return {
            self.team_a.name: {
                "score": self.team_a.score,
                "players": {
                    p.name: {
                        **p.stats,
                        "stamina": p.stamina,
                        "position": p.position
                    }
                    for p in self.team_a.players
                }
            },
            self.team_b.name: {
                "score": self.team_b.score,
                "players": {
                    p.name: {
                        **p.stats,
                        "stamina": p.stamina,
                        "position": p.position
                    }
                    for p in self.team_b.players
                }
            }
        }