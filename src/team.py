class Team:
    def __init__(self, name, players):
        """
        players: list[Player]
        For NBA-accurate usage, expect up to 12 players:
        - 5 starters
        - 7 bench
        We'll treat the first 5 as starters by default.
        """
        self.name = name
        self.players = players          # full roster
        self.score = 0

        # First 5 = starters (on_floor), rest = bench
        self.on_floor = list(players[:5])
        self.bench = list(players[5:])

        # Quick lookup by position (for subs, matchups later)
        self.players_by_position = {}
        for p in self.players:
            self.players_by_position.setdefault(p.position, []).append(p)

    def get_bench_by_position(self, position):
        """Return list of bench players who can play the given position."""
        return [p for p in self.bench if p.position == position]

    def swap_players(self, out_player, in_player):
        """
        Substitution: move out_player to bench, in_player to floor.
        Assumes in_player is currently on bench and out_player is on_floor.
        """
        if out_player in self.on_floor:
            self.on_floor.remove(out_player)
            self.bench.append(out_player)

        if in_player in self.bench:
            self.bench.remove(in_player)
            self.on_floor.append(in_player)

    # -------------------------
    # GAME RESET FIX
    # -------------------------

    def reset_game_state(self):
        """Reset team-specific game state before a new game."""
        self.score = 0