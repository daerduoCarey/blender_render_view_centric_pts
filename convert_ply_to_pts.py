import os
import sys

for item in os.listdir('.'):
    if item.endswith('.ply'):
        with open(item, 'r') as fin:
            d = fin.readlines()
        with open(item.replace('.ply', '.pts'), 'w') as fout:
            for i in range(7, len(d)):
                fout.write('%s'%d[i])
