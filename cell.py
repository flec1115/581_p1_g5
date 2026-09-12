class Cell:
    def __init__(self):
        self.has_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0
