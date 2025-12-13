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

        self.sub_stamina_threshold = 50
        self.max_fouls_before_sub = 4

        # team fouls hooks (per game for now, can become per-quarter later)
        self.team_fouls = {
            self.team_a.name: 0,
            self.team_b.name: 0
        }

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

    # ---------- Helper: fastbreak after steal ----------

    def simulate_fastbreak(self, offense, defense):
        """
        Simple fastbreak: higher chance of an easy 2, low contest.
        """
        scorer = select_shooter(offense)  # usually guard/wing, but keep it simple for now
        scorer.stats["fg_attempts"] += 1
        scorer.stats["fatigue_load"] += 1

        # Fastbreak is usually a 2 at the rim
        shot_value = 2
        fatigue_penalty = (100 - scorer.stamina) * 0.04  # lighter than halfcourt
        scorer.stats["fatigue_shooting_penalty"] += fatigue_penalty

        shot_rating = scorer.ratings["finishing"] - fatigue_penalty + random.randint(-5, 10)

        defender = random.choice(defense.on_floor)
        defense_fatigue_penalty = (100 - defender.stamina) * 0.05  # slightly lower impact
        defender.stats["fatigue_defense_penalty"] += defense_fatigue_penalty
        defender.stats["fatigue_load"] += 1

        contest = (defender.ratings["defense"] - defense_fatigue_penalty) + random.randint(-5, 5)

        shot_roll = shot_rating + random.randint(-10, 10)
        if shot_roll > contest:
            scorer.stats["fg_made"] += 1
            scorer.stats["points"] += shot_value
            offense.score += shot_value

            # Occasional fastbreak assist
            if random.random() < 0.35:
                passer = random.choice([p for p in offense.on_floor if p != scorer])
                passer.stats["assists"] += 1

    # ---------- Helper: record team foul ----------

    def _add_team_foul(self, defense_team):
        self.team_fouls[defense_team.name] += 1

    # ---------- Possession logic ----------

    def simulate_possession(self, offense, defense):

        shooter = select_shooter(offense)

        shooter.stamina = max(0, shooter.stamina - random.randint(2, 4))

        for p in offense.on_floor + defense.on_floor:
            if p != shooter:
                p.stamina = max(0, p.stamina - random.randint(1, 2))

        for p in offense.on_floor + defense.on_floor:
            p.stats["fatigue_load"] += 1

        # ---------- REALISTIC TURNOVER SYSTEM ----------
        turnover_roll = random.random()
        fatigue_turnover_bonus = (100 - shooter.stamina) * 0.0012
        shooter.stats["fatigue_turnover_penalty"] += fatigue_turnover_bonus

        turnover_chance = (
            0.12
            + (0.015 * (50 - shooter.ratings["iq"]) / 50)
            + fatigue_turnover_bonus
        )

        if turnover_roll < turnover_chance:
            shooter.stats["turnovers"] += 1

            # some of these are steals → potential fastbreak
            if random.random() < 0.35:
                defender = random.choice(defense.on_floor)
                defender.stats["steals"] += 1

                # chance of a fastbreak after the steal
                if random.random() < 0.40:
                    self.simulate_fastbreak(defense, offense)
            return

        shot_type = select_shot_type(shooter)

        # ---------- Offensive foul on drive ----------

        if shot_type == "drive":
            offensive_foul_base = 0.03
            discipline_penalty = (50 - shooter.ratings["discipline"]) / 100  # worse discipline = more charges
            offensive_foul_chance = offensive_foul_base + discipline_penalty

            if random.random() < offensive_foul_chance:
                shooter.stats["fouls"] += 1
                shooter.stats["turnovers"] += 1
                return

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

        else:  # drive
            shooter.stats["fg_attempts"] += 1
            shooter.stats["fatigue_load"] += 4
            shot_value = 2

            fatigue_penalty = (100 - shooter.stamina) * 0.12
            shooter.stats["fatigue_shooting_penalty"] += fatigue_penalty

            shot_rating = shooter.ratings["finishing"] - fatigue_penalty + random.randint(-10, 10)

        # ---------- Contest logic ----------

        defender = random.choice(defense.on_floor)
        defense_fatigue_penalty = (100 - defender.stamina) * 0.10

        defender.stats["fatigue_defense_penalty"] += defense_fatigue_penalty
        defender.stats["fatigue_load"] += 1

        contest = (defender.ratings["defense"] - defense_fatigue_penalty) + random.randint(-5, 8)

        # ---------- REALISTIC BLOCK SYSTEM ----------

        base_block = 0.03
        drive_bonus = 0.02 if shot_type == "drive" else 0.0
        rating_multiplier = defender.ratings["block"] / 100
        block_chance = base_block + (rating_multiplier * 0.05) + drive_bonus
        block_chance = min(block_chance, 0.12)

        if random.random() < block_chance:
            defender.stats["blocks"] += 1
            return

        # ---------- Make or miss + AND-1 logic ----------

        shot_roll = shot_rating + random.randint(-15, 15)
        if shot_roll > contest:
            shooter.stats["fg_made"] += 1
            shooter.stats["points"] += shot_value
            offense.score += shot_value

            if shot_type == "three":
                shooter.stats["three_made"] += 1

            # Assist chance on made basket
            if random.random() < 0.28:
                passer = random.choice([p for p in offense.on_floor if p != shooter])
                passer.stats["assists"] += 1

            # AND-1 chance on made shot (higher for drives)
            and1_base = 0.04
            if shot_type == "drive":
                and1_base += 0.03
            and1_chance = and1_base

            if random.random() < and1_chance:
                defender.stats["fouls"] += 1
                self._add_team_foul(defense)
                self.shoot_free_throws(shooter, 1, offense)

            return

        # ---------- REALISTIC REBOUNDING (POSITION‑WEIGHTED) ----------

        off_reb_weight = sum(p.playstyle["rebound_focus"] for p in offense.on_floor)
        def_reb_weight = sum(p.playstyle["rebound_focus"] for p in defense.on_floor)
        total_weight = off_reb_weight + def_reb_weight
        off_reb_prob = off_reb_weight / total_weight if total_weight > 0 else 0.5

        position_reb_bonus = {
            "PG": 0.3,
            "SG": 0.5,
            "SF": 0.8,
            "PF": 1.5,
            "C": 2.0
        }

        off_weights = [
            p.playstyle["rebound_focus"] * position_reb_bonus.get(p.position, 1.0)
            for p in offense.on_floor
        ]

        def_weights = [
            p.playstyle["rebound_focus"] * position_reb_bonus.get(p.position, 1.0)
            for p in defense.on_floor
        ]

        if random.random() < off_reb_prob * 0.70:
            rebounder = random.choices(offense.on_floor, weights=off_weights, k=1)[0]
            rebounder.stats["off_rebounds"] += 1
        else:
            rebounder = random.choices(defense.on_floor, weights=def_weights, k=1)[0]
            rebounder.stats["def_rebounds"] += 1

        rebounder.stats["rebounds"] += 1

        # ---------- REALISTIC FOUL / FREE THROW LOGIC (MISSED SHOT FOULS) ----------

        foul_roll = random.random()
        base_foul = 0.18
        discipline_factor = (50 - defender.ratings["discipline"]) / 50
        aggression_factor = shooter.playstyle["aggression"] * 0.015

        foul_chance = base_foul + discipline_factor + aggression_factor

        if foul_roll < foul_chance:
            defender.stats["fouls"] += 1
            self._add_team_foul(defense)

            # Only shooting fouls award free throws (non-bonus, for now)
            if random.random() < 0.70:
                if shot_type == "three":
                    self.shoot_free_throws(shooter, 3, offense)
                else:
                    self.shoot_free_throws(shooter, 2, offense)

    # ---------- FREE THROWS ----------

    def shoot_free_throws(self, shooter, attempts, offense):
        for _ in range(attempts):
            shooter.stats["ft_attempts"] += 1
            ft_roll = shooter.ratings["shooting"] + random.randint(-15, 15)
            if ft_roll > 50:
                shooter.stats["ft_made"] += 1
                shooter.stats["points"] += 1
                offense.score += 1

    # ---------- GAME LOOP (FIXED PACE) ----------

    def simulate_game(self):
        for p in self.team_a.players + self.team_b.players:
            p.reset_stats()

        # reset team fouls for this game
        self.team_fouls[self.team_a.name] = 0
        self.team_fouls[self.team_b.name] = 0

        possessions_per_team = random.randint(90, 110)

        for i in range(possessions_per_team // 2):

            if i == (possessions_per_team // 4):
                for p in self.team_a.players + self.team_b.players:
                    p.stamina = min(p.max_stamina, p.stamina + 20)

            self.simulate_possession(self.team_a, self.team_b)
            self.simulate_possession(self.team_b, self.team_a)

            for p in self.team_a.players + self.team_b.players:
                p.stamina = min(p.max_stamina, p.stamina + 1.5)

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