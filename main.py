import numpy as np
import itertools as it
import shelve

class Puzzle:
    def __init__(self, in_array):
        if in_array.shape == (9,9):
            self.puzzle = in_array
        else:
            Exception('Please enter a 9 x 9 array')
        self.possibilities = np.zeros((9,9), 'object')
        self.si = [[0, 3, 0, 3], [0, 3, 3, 6], [0, 3, 6, 9],
                   [3, 6, 0, 3], [3, 6, 3, 6], [3, 6, 6, 9],
                   [6, 9, 0, 3], [6, 9, 3, 6], [6, 9, 6, 9]]

    def update_possibilities(self):
        for i in range(9):
            for j in range(9):
                if self.possibilities[i,j] == 0:
                    self.possibilities[i, j] = list(range(1,10))
                if self.puzzle[i,j] == 0:
                    # Check row
                    for k in self.puzzle[i,:]:
                        if k in self.possibilities[i,j]:
                            self.possibilities[i,j].remove(k)
                    # Check col
                    for k in self.puzzle[:,j]:
                        if k in self.possibilities[i,j]:
                            self.possibilities[i,j].remove(k)

                    # Check square
                    square_inds = [(i//3)*3, (j//3)*3]
                    square = self.puzzle[square_inds[0]:square_inds[0]+3, square_inds[1]:square_inds[1]+3]
                    for k in square.reshape(1,9)[0]:
                        if k in self.possibilities[i,j]:
                            self.possibilities[i,j].remove(k)
                else:
                    self.possibilities[i,j]  = [int(self.puzzle[i,j])]

    def check_possibilities(self):
        # Check Rows
        for i in range(9):
            counts = dict()
            for k in range(1, 10):
                counts[k] = {'value': 0, 'inds': []}
            for j in range(9):
                # if len(self.possibilities[i,j]) > 1:
                for ii in self.possibilities[i,j]:
                    counts[ii]['value'] += 1
                    counts[ii]['inds'].append(j)
            for (k, v) in counts.items():
                if v['value'] == 1:
                    self.possibilities[i, v['inds'][0]] = [k]
                    self.update_puzzle()
                    self.update_possibilities()
                    self.update_puzzle()

        # Check Cols
        for i in range(9):
            counts = dict()
            for k in range(1, 10):
                counts[k] = {'value': 0, 'inds': []}
            for j in range(9):
                # if len(self.possibilities[j, i]) > 1:
                for ii in self.possibilities[j, i]:
                    counts[ii]['value'] += 1
                    counts[ii]['inds'].append(j)
            for (k,v) in counts.items():
                if v['value'] == 1:
                    self.possibilities[v['inds'][0], i] = [k]
                    self.update_puzzle()
                    self.update_possibilities()
                    self.update_puzzle()

        # Check Squares
        for i in range(9):
            square_poss = self.possibilities[self.si[i][0]:self.si[i][1], self.si[i][2]:self.si[i][3]]
            counts = dict()
            for k in range(1, 10):
                counts[k] = {'value': 0, 'inds': []}
            for j in range(3):
                for jj in range(3):
                    # if len(square_poss[j, jj]) > 1:
                    for ii in square_poss[j, jj]:
                        counts[ii]['value'] += 1
                        counts[ii]['inds'].append([j,jj])
            for (k, v) in counts.items():
                if v['value'] == 1:
                    row = self.si[i][0] + v['inds'][0][0]
                    col = self.si[i][2] + v['inds'][0][1]
                    self.possibilities[row, col] = [k]
                    self.update_puzzle()
                    self.update_possibilities()
                    self.update_puzzle()
                else:
                    relrows_poss = []
                    relcols_poss = []
                    for elem in v['inds']:
                        relrows_poss.append(elem[0])
                        relcols_poss.append(elem[1])
                    relrows_poss = list(set(relrows_poss))
                    relcols_poss = list(set(relcols_poss))
                    if len(relrows_poss) == 1:
                        row = self.si[i][0] + relrows_poss[0]
                        to_remove = list(range(9))
                        to_remove.remove(self.si[i][2])
                        to_remove.remove(self.si[i][2]+1)
                        to_remove.remove(self.si[i][2] + 2)
                        for p in to_remove:
                            if k in self.possibilities[row, p]:
                                self.possibilities[row, p].remove(k)
                                self.update_puzzle()
                                self.update_possibilities()
                                self.update_puzzle()
                    if len(relcols_poss) == 1:
                        col = self.si[i][2] + relcols_poss[0]
                        to_remove = list(range(9))
                        to_remove.remove(self.si[i][0])
                        to_remove.remove(self.si[i][0]+1)
                        to_remove.remove(self.si[i][0] + 2)

                        for p in to_remove:
                            if k in self.possibilities[p, col]:
                                self.possibilities[p, col].remove(k)
                                self.update_puzzle()
                                self.update_possibilities()
                                self.update_puzzle()


    def tile_eliminate(self):
        # Rows of squares
        for i in range(3):
            rowinds = [3*i, 3*i+3]
            square_posses = [self.possibilities[rowinds[0]:rowinds[1], 0:3],
                             self.possibilities[rowinds[0]:rowinds[1], 3:6],
                             self.possibilities[rowinds[0]:rowinds[1], 6:9]]
            combos = [(0, 1), (0, 2), (1, 2)]
            for c in combos:
                counts = dict()
                for ind in range(1, 10):
                    counts[ind] = {'value': 0, 'inds': []}
                square_poss_combo = np.block([square_posses[c[0]], square_posses[c[1]]])
                for j in range(3):
                    for jj in range(6):
                        # if len(square_poss_combo[j, jj]) > 1:
                        for ii in square_poss_combo[j, jj]:
                            counts[ii]['value'] += 1
                            counts[ii]['inds'].append([j, jj])
                for (k,v) in counts.items():
                    if v['value'] > 1:
                        relrows_poss = []
                        for elem in v['inds']:
                            relrows_poss.append(elem[0])
                        relrows_poss = list(set(relrows_poss))
                        if len(relrows_poss) == 2:
                            rowstart = i*3
                            inds_to_elim = [0,1,2]
                            inds_to_elim.remove(c[0])
                            inds_to_elim.remove(c[1])
                            inds_to_elim = inds_to_elim[0]
                            cols_to_elim = list(range(inds_to_elim*3, inds_to_elim*3+3))
                            rows_to_elim = [rowinds[0]+relrows_poss[0], rowinds[0]+relrows_poss[1]]
                            for re in rows_to_elim:
                                for ce in cols_to_elim:
                                    if k in self.possibilities[re, ce]:
                                        self.possibilities[re, ce].remove(k)
                                        # self.check_possibilities()
                                        # self.update_puzzle()
                                        # self.update_possibilities()
                                        # self.update_puzzle()

            colinds = [3*i, 3*i+3]
            square_posses = [self.possibilities[0:3, colinds[0]:colinds[1]],
                             self.possibilities[3:6, colinds[0]:colinds[1]],
                             self.possibilities[6:9, colinds[0]:colinds[1]]]
            for c in combos:
                counts = dict()
                for ind in range(1, 10):
                    counts[ind] = {'value': 0, 'inds': []}
                square_poss_combo = np.block([[square_posses[c[0]]], [square_posses[c[1]]]])
                for j in range(6):
                    for jj in range(3):
                        # if len(square_poss_combo[j, jj]) > 1:
                        for ii in square_poss_combo[j, jj]:
                            counts[ii]['value'] += 1
                            counts[ii]['inds'].append([j, jj])
                for (k, v) in counts.items():
                    if v['value'] > 1:
                        relcols_poss = []
                        for elem in v['inds']:
                            relcols_poss.append(elem[1])
                        relcols_poss = list(set(relcols_poss))
                        if len(relcols_poss) == 2:
                            inds_to_elim = [0,1,2]
                            inds_to_elim.remove(c[0])
                            inds_to_elim.remove(c[1])
                            inds_to_elim = inds_to_elim[0]
                            rows_to_elim = list(range(inds_to_elim*3, inds_to_elim*3+3))
                            cols_to_elim = [colinds[0]+relcols_poss[0], colinds[0]+relcols_poss[1]]
                            for re in rows_to_elim:
                                for ce in cols_to_elim:
                                    if k in self.possibilities[re, ce]:
                                        self.possibilities[re, ce].remove(k)
                                        # self.check_possibilities()
                                        # self.update_puzzle()
                                        # self.update_possibilities()
                                        # self.update_puzzle()

    def regular_pairs(self):
        num_combos = list(it.combinations(list(range(9)), 2))
        for r in range(9):
            row = self.possibilities[r, :]
            for n in num_combos:
                if len(row[n[0]]) == 2 and len(row[n[1]]) == 2:
                    if row[n[0]] == row[n[1]]:
                        to_remove = list(range(9))
                        to_remove.remove(n[0])
                        to_remove.remove(n[1])
                        for cc in row[n[0]]:
                            for rem in to_remove:
                                if cc in self.possibilities[r, rem]:
                                    self.possibilities[r, rem].remove(cc)
        for c in range(9):
            col = self.possibilities[:, c]
            for n in num_combos:
                if len(col[n[0]]) == 2 and len(col[n[1]]) == 2:
                    if col[n[0]] == col[n[1]]:
                        to_remove = list(range(9))
                        to_remove.remove(n[0])
                        to_remove.remove(n[1])
                        for cc in col[n[0]]:
                            for rem in to_remove:
                                if cc in self.possibilities[rem, c]:
                                    self.possibilities[rem, c].remove(cc)

    def hidden_pairs(self):
        num_combos = list(it.combinations(list(range(1,10)), 2))
        for r in range(9):
            row = self.possibilities[r,:]
            poss_count = dict()
            for p in range(1,10):
                poss_count.setdefault(p, [])
            for c in range(9):
                for ii in row[c]:
                    poss_count[ii].append(c)
            for n in num_combos:
                if len(poss_count[n[0]]) == 2 and len(poss_count[n[1]]) == 2:
                    if poss_count[n[0]] == poss_count[n[1]]:
                        for cc in poss_count[n[0]]:
                            self.possibilities[r, cc] = list(n)
        for c in range(9):
            col = self.possibilities[:,c]
            poss_count = dict()
            for p in range(1,10):
                poss_count.setdefault(p, [])
            for r in range(9):
                for ii in col[r]:
                    poss_count[ii].append(r)
            for n in num_combos:
                if len(poss_count[n[0]]) == 2 and len(poss_count[n[1]]) == 2:
                    if poss_count[n[0]] == poss_count[n[1]]:
                        for rr in poss_count[n[0]]:
                            self.possibilities[rr, c] = list(n)
                            # self.update_puzzle()
                            # self.update_possibilities()
                            # self.check_possibilities()


    def update_puzzle(self):
        filled = 0
        for i in range(9):
            for j in range(9):
                if len(self.possibilities[i,j]) == 1:
                    self.puzzle[i,j] = int(self.possibilities[i,j][0])
                    filled += 1
        return filled




if __name__ == '__main__':
    puzzles = shelve.open('puzzles')
    puzzle_arr = puzzles['Level4_Puzzle9']
    puzzle = Puzzle(puzzle_arr)
    puzzle.update_possibilities()
    filled = puzzle.update_puzzle()
    while filled < 81:
        puzzle.update_possibilities()
        puzzle.check_possibilities()
        filled = puzzle.update_puzzle()
        # puzzle.tile_eliminate()
        puzzle.hidden_pairs()
        puzzle.regular_pairs()
        filled = puzzle.update_puzzle()
        print(filled)

    print(puzzle.puzzle)