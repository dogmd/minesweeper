class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Cell:
    id = 0
    def __init__(self, x, y):
        self.is_mine = False
        self.adj_mines = 0
        self.is_flagged = False
        self.adj_flags = 0
        self.is_revealed = False
        self.x = x
        self.y = y
        self.is_solved = False
        self.id = Cell.id
        Cell.id += 1

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if type(other) is Cell:
            return self.id == other.id
        else:
            return False

    def __str__(self):
        if self.is_flagged:
            return f'{bcolors.BOLD}{bcolors.UNDERLINE} F {bcolors.ENDC * 2}'
        if not self.is_revealed:
            return f' - '
        elif self.is_mine:
            return f'{bcolors.FAIL}{bcolors.UNDERLINE}{bcolors.BOLD} * {bcolors.ENDC * 3}'
        else:
            if self.adj_mines == 0:
                return '   '
            if self.adj_mines == 1:
                return f'{bcolors.OKGREEN} {self.adj_mines} {bcolors.ENDC}'
            if self.adj_mines == 2:
                return f'{bcolors.OKCYAN} {self.adj_mines} {bcolors.ENDC}'
            if self.adj_mines == 3:
                return f'{bcolors.HEADER} {self.adj_mines} {bcolors.ENDC}'
            if self.adj_mines == 4:
                return f'{bcolors.WARNING} {self.adj_mines} {bcolors.ENDC}'
            if self.adj_mines == 5:
                return f'{bcolors.FAIL} {self.adj_mines} {bcolors.ENDC * 2}'
            if self.adj_mines > 5:
                return f'{bcolors.FAIL}{bcolors.BOLD} {self.adj_mines} {bcolors.ENDC}'
