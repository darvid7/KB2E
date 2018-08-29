import os, sys
import math
import random
import time


def map_add(mp, key1, key2, value):
    if (key1 not in mp):
        mp[key1] = {}
    if (key2 not in mp[key1]):
        mp[key1][key2] = 0.0
    mp[key1][key2] += value


def map_add1(mp, key):
    if (key not in mp):
        mp[key] = 0
    mp[key] += 1


f = open("data/relation2id.txt", "r")
relation2id = {}
id2relation = {}
relation_num = 0
for line in f:
    seg = line.strip().split()
    relation2id[seg[0]] = int(seg[1])
    id2relation[int(seg[1])] = seg[0]
    relation_num += 1
    print("There")

for line in f:
    print("HERE")
    seg = line.strip().split()
    id2relation[int(seg[1]) + relation_num] = "~" + seg[0]
f.close()

print id2relation
ok = {}
a = {}