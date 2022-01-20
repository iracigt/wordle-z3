answer = 'POINT'

board = r"""
⬜⬜⬜⬜⬜
⬜⬜⬜🟨⬜
⬜🟨🟨⬜⬜
⬜🟩⬜🟨🟩
⬜🟩🟩🟩🟩
🟩🟩🟩🟩🟩
"""

hard_mode = True
extras = True

from z3 import *

def letters2word(l):
    return ''.join([chr(0x40 + c) if c else ' ' for c in l])

def word2letters(w):
    return [ord(c) - 0x40 for c in w.upper()]

def ltr(l):
    return ord(l.upper()) - 0x40

s = Solver()


grid = [[Int('l_{}_{}'.format(i+1, j+1)) for j in range(5)] for i in range(6)]
ans = [Int('a_{}'.format(i+1)) for i in range(5)]
all_letters = [l for row in grid for l in row] + ans

grays = [] # for "hard mode" / perfect play
must_use_gold = []
must_use_green = []


def green(i,j):
    must_use_green.extend([row[j-1] == ans[j-1] for row in grid[i:]])
    s.add(grid[i-1][j-1] == ans[j-1])

def gray(i,j):
    grays.append(grid[i-1][j-1])
    s.add(And(*(grid[i-1][j-1] != l for l in ans)))

def gold(i, j):
    must_use_gold.extend([And(Or(*[a == grid[i-1][j-1] for a in row]), row[j-1] != grid[i-1][j-1]) for row in grid[i:]])
    s.add(And(Or(*(grid[i-1][j-1] == l for l in ans)), Not(grid[i-1][j-1] == ans[j-1])))

def used(r):
    s.add(And(*(l != 0 for l in grid[r-1])))

def unused(r):
    s.add(And(*(l == 0 for l in grid[r-1])))

def set_row(r, w):
    s.add([a == b for a,b in zip(grid[r-1], word2letters(w))])

def not_row(r, w):
    s.add(Or(*[a != b for a,b in zip(grid[r-1], word2letters(w))]))

def ltr_in(r, l):
    s.add(Or(*[a == ltr(l) for a in grid[r-1]]))

def not_in(r, l):
    s.add([a != ltr(l) for a in grid[r-1]])


# Is letter
s.add([And(l >= 0, l < 27) for l in all_letters]) 

# Every guess is a (common) allowed word
s.from_file('dict_stripped.z3')

all_diff = [Or(*(Or(a != b, a == 0) for a,b in zip(x,y))) for i in range(5) for x,y in zip(grid[:-i], grid[i:])]
s.add(all_diff)


# Answer is given or recent
if answer:
    s.add([a == b for a,b in zip(ans, word2letters(answer))])
else:
    s.from_file('solns.z3')

board = board.strip().splitlines()

for i, guess in enumerate(board):
    used(i)
    for j, l in enumerate(guess):
        if l == '⬜':
            gray(i+1, j+1)
        if l == '🟨':
            gold(i+1, j+1)
        if l == '🟩':
            green(i+1, j+1)

for i in range(len(board), len(grid)):
    unused(i+1)


if extras:
    ltr_in(1, 'A')
    ltr_in(1, 'E')

    not_in(1, 'Q')
    not_in(1, 'X')
    not_in(1, 'Z')

    not_in(2, 'Q')
    not_in(2, 'X')
    not_in(2, 'Z')

if hard_mode:
    s.add(Distinct(*grays))
    s.add(must_use_gold)
    s.add(must_use_green)

if s.check() != sat:
    print('no solution')
else:
    model = s.model()
    soln = [[model[l].as_long() for l in row] for row in grid]
    print('\n'.join([letters2word(guess) for guess in soln]))