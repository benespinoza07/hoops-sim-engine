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
    for p in offense.on_floor:  # now uses on_floor
        base = position_weights.get(p.position, 1.0)

        shooting_factor = (p.ratings["shooting"] / 100) * 0.5
        aggression_factor = p.playstyle["aggression"] * 0.3

        weight = base + shooting_factor + aggression_factor
        weights.append(weight)

    return random.choices(offense.on_floor, weights=weights, k=1)[0]


def select_shot_type(shooter):
    """Choose shot type using tendencies + positional influence."""
    base_three = shooter.tendencies["three_point_rate"]

    # Guards shoot more threes
    if shooter.position in ["PG", "SG"]:
        base_three += 0.10

    # Bigs shoot fewer threes
    if shooter.position in ["PF", "C"]:
        base_three -= 0.05

    # Clamp
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

        # Substitution thresholds (you can tune these)
        self.sub_stamina_threshold = 35      # below this, try to sub out
        self.max_fouls_before_sub = 4        # simple foul trouble rule

    # ---------- Substitution logic ----------

    def check_substitutions(self, team):
        """
        Check on_floor players for low stamina or foul trouble.
        Try to sub them out for a same-position bench player.
        """
        for player in list(team.on_floor):  # copy to avoid modifying while iterating
            needs_sub = False

            # Stamina-based subs
            if player.stamina < self.sub_stamina_threshold:
                needs_sub = True

            # Simple foul-trouble logic
            if player.stats["fouls"] >= self.max_fouls_before_sub:
                needs_sub = True

            if not needs_sub:
                continue

            # Try to find same-position replacement on bench
            bench_candidates = team.get_bench_by_position(player.position)

            if not bench_candidates:
                # Fallback: any bench player, pick the one with highest stamina
                if not team.bench:
                    continue  # no subs available at all
                bench_candidates = sorted(team.bench, key=lambda p: p.stamina, reverse=True)

            # Choose bench player with highest stamina among candidates
            sub_in = max(bench_candidates, key=lambda p: p.stamina)

            # Execute substitution
            team.swap_players(out_player=player, in_player=sub_in)

    # ---------- Possession logic ----------

    def simulate_possession(self, offense, defense):

        shooter = select_shooter(offense)

        # Stamina drain for shooter
        shooter.stamina = max(0, shooter.stamina - random.randint(3, 6))

        # Light stamina drain for all other players on the floor
        for p in offense.on_floor + defense.on_floor:
            if p != shooter:
                p.stamina = max(0, p.stamina - random.randint(1, 2))

        # Fatigue load for being on the floor
        for p in offense.on_floor + defense.on_floor:
            p.stats["fatigue_load"] += 1

        # Turnover chance (fatigue increases turnovers)
        turnover_roll = random.random()
        fatigue_turnover_bonus = (100 - shooter.stamina) * 0.0015
        shooter.stats["fatigue_turnover_penalty"] += fatigue_turnover_bonus

        turnover_chance = (
            0.08
            + (0.02 * (50 - shooter.ratings["iq"]) / 50)
            + fatigue_turnover_bonus
        )

        if turnover_roll < turnover_chance:
            shooter.stats["turnovers"] += 1
            if random.random() < 0.4:
                defender = random.choice(defense.on_floor)
                defender.stats["steals"] += 1
            return

        # Shot type selection
        shot_type = select_shot_type(shooter)

        # Attempt shot (fatigue penalties applied)
        if shot_type == "three":
            shooter.stats["three_attempts"] += 1
            shooter.stats["fg_attempts"] += 1
            shooter.stats["fatigue_load"] += 3
            shot_value = 3

            fatigue_penalty = (100 - shooter.stamina) * 0.15
            shooter.stats["fatigue_shooting_penalty"] += fatigue_penalty

            shot_rating = shooter.ratings["three_point"] - fatigue_penalty

        elif shot_type == "two":
            shooter.stats["fg_attempts"] += 1
            shooter.stats["fatigue_load"] += 3
            shot_value = 2

            fatigue_penalty = (100 - shooter.stamina) * 0.15
            shooter.stats["fatigue_shooting_penalty"] += fatigue_penalty

            shot_rating = shooter.ratings["shooting"] - fatigue_penalty

        else:  # Drive logic
            shooter.stats["fg_attempts"] += 1
            shooter.stats["fatigue_load"] += 5
            shot_value = 2

            fatigue_penalty = (100 - shooter.stamina) * 0.20
            shooter.stats["fatigue_shooting_penalty"] += fatigue_penalty

            shot_rating = shooter.ratings["finishing"] - fatigue_penalty + random.randint(-15, 10)

        # Defense contest (fatigue penalties applied)
        defender = random.choice(defense.on_floor)
        defense_fatigue_penalty = (100 - defender.stamina) * 0.15

        defender.stats["fatigue_defense_penalty"] += defense_fatigue_penalty
        defender.stats["fatigue_load"] += 2

        contest = (defender.ratings["defense"] - defense_fatigue_penalty) + random.randint(-10, 10)

        # Block chance
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

            if random.random() < 0.35:
                passer = random.choice([p for p in offense.on_floor if p != shooter])
                passer.stats["assists"] += 1
            return

        # Missed shot → rebound (still basic for now)
        off_reb_weight = sum(p.playstyle["rebound_focus"] for p in offense.on_floor)
        def_reb_weight = sum(p.playstyle["rebound_focus"] for p in defense.on_floor)
        total_weight = off_reb_weight + def_reb_weight
        off_reb_prob = off_reb_weight / total_weight if total_weight > 0 else 0.5

        if random.random() < off_reb_prob * 0.75:
            rebounder = random.choice(offense.on_floor)
        else:
            rebounder = random.choice(defense.on_floor)

        rebounder.stats["rebounds"] += 1

        # Foul chance
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

        for i in range(pace):

            # Halftime recovery
            if i == pace // 2:
                for p in self.team_a.players + self.team_b.players:
                    p.stamina = min(p.max_stamina, p.stamina + 20)

            self.simulate_possession(self.team_a, self.team_b)
            self.simulate_possession(self.team_b, self.team_a)

            # Light recovery between possessions
            for p in self.team_a.players + self.team_b.players:
                p.stamina = min(p.max_stamina, p.stamina + 0.5)

            # Substitution checks after each pair of possessions
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