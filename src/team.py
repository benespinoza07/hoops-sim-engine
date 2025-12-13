class Team:
    def __init__(self, name, players):
        self.name = name
        self.players = players  # full roster
        self.score = 0

        # For future: lineup + rotations
        # Right now, small rosters → everyone is on the floor
        self.on_floor = list(players)
        self.bench = []

        # Optional: quick lookup by position (useful later for 5-man lineups and subs)
        self.players_by_position = {}
        for p in players:
            self.players_by_position.setdefault(p.position, []).append(p)