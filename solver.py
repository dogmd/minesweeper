import sys
from constraint import *
from collections import defaultdict
import time
from cell import Cell
from cell import bcolors
import random

def main(args):
    board = []
    visualize = False if 'visualize' not in args else args['visualize'] != "False"
    print(visualize, args)
    width = 8 if 'width' not in args else int(args['width'])
    height = 8 if 'height' not in args else int(args['height'])

    init_guess_x = width // 2
    init_guess_y = height // 2
    for i in range(height):
        row = []
        for j in range(width):
            cell = Cell(j, i)
            if j == init_guess_x and i == init_guess_y:
                cell.is_revealed = True
            row.append(cell)
        board.append(row)

    for neighbor in get_neighbors(board, init_guess_x, init_guess_y):
        neighbor.is_revealed = True

    mine_count = 10 if 'mine_count' not in args else int(args['mine_count'])
    set_mines(board, mine_count)

    for neighbor in get_neighbors(board, init_guess_x, init_guess_y):
        neighbor.is_revealed = False

    solve(board, visualize)
    print_board(board)

def solve(board, visualize=False):
    height = len(board)
    width = len(board[0])
    cells = [board[height // 2][width // 2]]
    incomplete_count = width * height
    while len(cells) > 0:
        cell = cells.pop()

        if not cell.is_solved and not cell.is_flagged:
            if visualize and not cell.is_revealed:
                highlight_set(board, [cell])
                time.sleep(0.2)

            reveal(cell)

            neighbors = get_neighbors(board, cell.x, cell.y)
            hidden = []
            flagged = []
            for n in neighbors: 
                if not n.is_revealed:
                    hidden.append(n)
                    if n.is_flagged:
                        flagged.append(n)

            if cell.adj_mines == 0:
                cell.is_solved = True
                cells.extend(neighbors)
            elif cell.adj_mines == len(hidden):
                for c in hidden:
                    if visualize and not c.is_flagged:
                        highlight_set(board, [c])
                        time.sleep(0.1)
                    c.is_flagged = True
                    for n in get_neighbors(board, c.x, c.y):
                        if n.is_revealed and n != cell and n not in cells:
                            cells.append(n)
                cell.is_solved = True
            elif cell.adj_mines == len(flagged):
                cell.is_solved = True
                cells.extend(neighbors)

        if len(cells) == 0:
            incomplete = []
            for row in board:
                for c in row:
                    if not c.is_revealed and not c.is_flagged:
                        incomplete.append(c)

            if len(incomplete) != incomplete_count:
                incomplete_count = len(incomplete)
                adj = []
                for c in incomplete:
                    for n in get_neighbors(board, c.x, c.y):
                        if n.is_revealed:
                            adj.append(n)

                if len(incomplete) > 0:
                    print("Using CSP...")
                    probabilities = solve_csp(board, adj)
                    min_prob = 1
                    min_cell = None
                    for c, prob in probabilities.items():
                        if min_prob >= prob:
                            min_prob = prob
                            min_cell = c
                        if prob == 1:
                            if visualize and not c.is_flagged:
                                highlight_set(board, [c])
                                time.sleep(0.1)
                            c.is_flagged = True
                            for n in get_neighbors(board, c.x, c.y):
                                if n.is_revealed and n != cell and n not in cells and not n.is_flagged:
                                    cells.append(n)
                        elif prob == 0:
                            cells.append(c)

                    if len(cells) == 0:
                        print("GUESSING ", min_cell.x, min_cell.y, min_prob)
                        cells.append(min_cell)

    solved = []
    for row in board:
        for cell in row:
            if cell.is_solved:
                solved.append(cell)
    highlight_set(board, solved)
                
def solve_csp(board, known):
    problem = Problem()
    cell_ids = {}
    unknown = []
    for cell in known:
        for n in get_neighbors(board, cell.x, cell.y):
            if n not in unknown and not n.is_revealed and not n.is_flagged:
                unknown.append(n)

    highlight_set(board, unknown)

    for cell in unknown:
        problem.addVariable(cell.id, [0, 1])
        cell_ids[cell.id] = cell

    for cell in known:
        constraint_vars = []
        flag_count = 0
        for n in get_neighbors(board, cell.x, cell.y):
            if n in unknown:
                constraint_vars.append(n.id)
            if n.is_flagged:
                flag_count += 1
        problem.addConstraint(ExactSumConstraint(cell.adj_mines - flag_count), constraint_vars)

    solutions = problem.getSolutions()
    vals = defaultdict(int)
    for solution in solutions:
        for id, val in solution.items():
            vals[cell_ids[id]] += val
    for cell, val in vals.items():
        vals[cell] = val / len(solutions)
    return vals


def push_neighbors(board, cell, stack):
    for n in get_neighbors(board, cell.x, cell.y):
        if not cell.is_solved and not cell.is_flagged:
            stack.append(n)


def highlight_set(board, cells):
    for row in board:
        out = ''
        for cell in row:
            if cell in cells:
                out += f'{bcolors.OKCYAN} # {bcolors.ENDC}'
            else:
                out += str(cell)
        print(out)
    print()

def reveal(cell):
    cell.is_revealed = True
    if cell.is_mine:
        raise Exception("BOOM!")

def set_mines(board, mine_count):
    height = len(board)
    width = len(board[0])

    for i in range(mine_count):
        while True:        
            x = random.randrange(width)
            y = random.randrange(height)
            cell = board[y][x]

            if not cell.is_mine and not cell.is_revealed:
                cell.is_mine = True
                for neighbor in get_neighbors(board, x, y):
                    neighbor.adj_mines += 1
                break

def print_board(board, highlight=None, lowlight=None):
    out = ''
    for row in board:
        for cell in row:
            if cell == highlight:
                out += f'{bcolors.OKCYAN} # {Cell.bcolors.ENDC}'
            elif lowlight and cell in lowlight and not (cell.is_solved or cell.is_flagged):
                out += str(cell).strip() + '. '
            else:
                out += str(cell)
        out += "\n"
    print(out)
    print()

def get_neighbors(board, x, y):
    neighbors = []
    max_y = len(board) - 1
    max_x = len(board[0]) - 1

    if x != 0:
        neighbors.append(board[y][x - 1])
    if y != 0:
        neighbors.append(board[y - 1][x])
    if x != max_x:
        neighbors.append(board[y][x + 1])
    if y != max_y:
        neighbors.append(board[y + 1][x])
    if x != 0 and y != 0:
        neighbors.append(board[y - 1][x - 1])
    if x != 0 and y != max_y:
        neighbors.append(board[y + 1][x - 1])
    if x != max_x and y != 0:
        neighbors.append(board[y - 1][x + 1])
    if x != max_x and y != max_y:
        neighbors.append(board[y + 1][x + 1])

    return neighbors

if __name__ == "__main__":
    d=defaultdict(list)
    for k, v in ((k.lstrip('-'), v) for k,v in (a.split('=') for a in sys.argv[1:])):
        d[k].append(v)

    for k in (k for k in d if len(d[k])==1):
        d[k] = d[k][0]

    main(d)
