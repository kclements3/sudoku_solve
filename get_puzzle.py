from bs4 import BeautifulSoup
import numpy as np
import requests
import shelve

s_out = shelve.open('puzzles')
url_base = 'https://nine.websudoku.com/?'
levels = range(1, 5)
puzzle_ids = range(10)

for level in levels:
    for puzzle_id in puzzle_ids:
        print(level, puzzle_id)
        url = url_base + 'level=%i&set_id=%i' % (level, puzzle_id)
        request = requests.get(url)
        if request.status_code == 200:
            puzzle_out = np.zeros((9,9))
            soup = BeautifulSoup(request.text, 'html.parser')
            pg = soup.find(id='puzzle_grid')
            for r in range(9):
                for c in range(9):
                    elem = pg.find(id='f%i%i' % (c, r))
                    if elem.get('value') is not None:
                        puzzle_out[r,c] = int(elem.get('value'))
            s_out['Level%i_Puzzle%i' % (level, puzzle_id)] = puzzle_out

s_out.close()