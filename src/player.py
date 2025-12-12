class Player:
    def __init__(self, name, ratings):
        """
        ratings = {
            "shooting": int,
            "finishing": int,   
            "defense": int,
            "steal": int,
            "rebounding": int,
            "passing": int,
            "block": int,
            "iq": int
            "discipline": int   # affects fouls
        }
        """
        self.name = name
        self.ratings = ratings
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
            "ft_made": 0
        }
        