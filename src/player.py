class Player:
    def __init__(self, name, ratings):
        self.name = name
        self.ratings = ratings

        # Basic box score stats
        self.stats = {
            "points": 0,
            "rebounds": 0,
            "assists": 0,
            "steals": 0,
            "blocks": 0,
            "turnovers": 0,
            "fg_attempts": 0,
            "fg_made": 0,
            "three_attempts": 0,
            "three_made": 0,
            "ft_attempts": 0,
            "ft_made": 0,
        }

    def reset_stats(self):
        for key in self.stats:
            self.stats[key] = 0