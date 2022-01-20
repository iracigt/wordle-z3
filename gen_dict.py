from z3 import *

def letters2word(l):
    return ''.join([chr(0x40 + c) if c else ' ' for c in l])

def word2letters(w):
    return [ord(c) - 0x40 for c in w.upper()]

with open('wordle_complete_dictionary.txt', 'r') as f:
    wordle_dict = f.readlines()

wd = {}

for w in wordle_dict:
    wd[w.upper()] = True

with open('dict_stripped.txt', 'r') as f:
    my_dict = f.readlines()

letters_dict = []

for word in my_dict:
    if word.upper() in wd:
        letters_dict.append(word2letters(word))


with open('solns.txt', 'r') as f:
    solns = f.readlines()

soln_dict = [word2letters(s) for s in solns]

grid = [[Int('l_{}_{}'.format(i+1, j+1)) for j in range(5)] for i in range(6)]
ans = [Int('a_{}'.format(i+1)) for i in range(5)]


s = Solver()
# Every row is valid word
row_dict = [[0,0,0,0,0]] + letters_dict

for i, row in enumerate(grid):
    print('row', i+1)
    s.add(Or(*(And(*(a == b for a,b in zip(row, word))) for word in row_dict)))

with open('dict_stripped.z3', 'w') as f:
    f.write(s.sexpr())

# Every solution is a real, recent solution
s = Solver() 
print('soln')
s.add(Or(*(And(*(a == b for a,b in zip(ans, word))) for word in soln_dict)))

with open('solns.z3', 'w') as f:
    f.write(s.sexpr())