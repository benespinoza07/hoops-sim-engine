class Player:
    def __init__(self, name, ratings):
        """
        ratings = {
            "shooting": int,
            "defense": int,
            "rebounding": int,
            "passing": int,
            "iq": int
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
            "fg_attempts": 0,
            "fg_made": 0
        }