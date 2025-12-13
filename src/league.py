import random
from game_sim import GameSim
from stats import build_advanced_boxscore

class League:
    def __init__(self, teams):
        self.teams = teams
        self.schedule = []
        self.standings = {
            team.name: {"W": 0, "L": 0}
            for team in teams
        }

    # -------------------------
    # CONFERENCE + DIVISION HELPERS
    # -------------------------

    def get_conference_teams(self, conference):
        return [t for t in self.teams if t.conference == conference]

    def get_division_teams(self, division):
        return [t for t in self.teams if t.division == division]

    # -------------------------
    # NBA‑STYLE SCHEDULE GENERATION
    # -------------------------

    def generate_schedule(self):
        self.schedule = []

        # 1. Division games (4 each)
        divisions = set(t.division for t in self.teams)
        for div in divisions:
            div_teams = self.get_division_teams(div)
            for i, a in enumerate(div_teams):
                for j, b in enumerate(div_teams):
                    if i < j:
                        for _ in range(4):
                            self.schedule.append((a, b))

        # 2. Same‑conference, different division (3 each)
        conferences = set(t.conference for t in self.teams)
        for conf in conferences:
            conf_teams = self.get_conference_teams(conf)
            div_groups = {}
            for t in conf_teams:
                div_groups.setdefault(t.division, []).append(t)

            div_list = list(div_groups.values())
            for group_a in div_list:
                for group_b in div_list:
                    if group_a is group_b:
                        continue
                    for team_a in group_a:
                        for team_b in group_b:
                            for _ in range(3):
                                self.schedule.append((team_a, team_b))

        # 3. Opposite conference (2 each)
        east = self.get_conference_teams("East")
        west = self.get_conference_teams("West")

        for e in east:
            for w in west:
                self.schedule.append((e, w))
                self.schedule.append((w, e))

        random.shuffle(self.schedule)

    # -------------------------
    # SEASON SIMULATION
    # -------------------------

    def simulate_season(self):
        """Simulate all scheduled games and update standings."""
        self.season_boxscores = []

        for team_a, team_b in self.schedule:

            game = GameSim(team_a, team_b)
            raw_box = game.simulate_game()

            box = build_advanced_boxscore(raw_box, team_a, team_b)
            self.season_boxscores.append(box)

            a_score = box[team_a.name]["score"]
            b_score = box[team_b.name]["score"]

            # Handle ties (NBA cannot end tied)
            while a_score == b_score:
                game.simulate_possession(team_a, team_b)
                game.simulate_possession(team_b, team_a)
                a_score = team_a.score
                b_score = team_b.score

            if a_score > b_score:
                self.update_standings(team_a.name, team_b.name)
            else:
                self.update_standings(team_b.name, team_a.name)

        return self.season_boxscores

    # -------------------------
    # STANDINGS
    # -------------------------

    def update_standings(self, winner, loser):
        self.standings[winner]["W"] += 1
        self.standings[loser]["L"] += 1

    def print_standings(self):
        print("\n=== EASTERN CONFERENCE ===")
        east = [t for t in self.standings if self._team_obj(t).conference == "East"]
        self._print_sorted(east)

        print("\n=== WESTERN CONFERENCE ===")
        west = [t for t in self.standings if self._team_obj(t).conference == "West"]
        self._print_sorted(west)

    def _print_sorted(self, team_names):
        sorted_teams = sorted(team_names, key=lambda t: self.standings[t]["W"], reverse=True)
        for t in sorted_teams:
            rec = self.standings[t]
            print(f"{t}: {rec['W']} - {rec['L']}")

    def _team_obj(self, name):
        return next(t for t in self.teams if t.name == name)