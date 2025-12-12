from archetypes import ARCHETYPES

class Player:
    def __init__(self, name, ratings, archetype="Two-Way"):
        """
        ratings = {
            "shooting": int,
            "finishing": int,
            "defense": int,
            "steal": int,
            "rebounding": int,
            "passing": int,
            "block": int,
            "iq": int,
            "discipline": int   # affects fouls
        }
        """
        self.name = name
        self.ratings = ratings

        # Add archetype system here
        self.archetype = archetype
        self.tendencies = ARCHETYPES[archetype]["tendencies"]
        self.playstyle = ARCHETYPES[archetype]["playstyle"]

        # Add stamina system
        self.max_stamina = 100
        self.stamina = 100

        # Stats come after identity attributes
        self.stats = {
            "points": 0,
            "rebounds": 0,
            "assists": 0,
            "steals": 0,
            "blocks": 0,
            "turnovers": 0,
            "fouls": 0,
            "fg_attempts": 0,
            "fg_made": 0,
            "three_attempts": 0,
            "three_made": 0,
            "ft_attempts": 0,
            "ft_made": 0,
            "fatigue_load": 0,
            "fatigue_shooting_penalty": 0,
            "fatigue_defense_penalty": 0,
            "fatigue_turnover_penalty": 0
        }

    def reset_stats(self):
        for key in self.stats:
            self.stats[key] = 0

        # Reset stamina each game
        self.stamina = self.max_stamina