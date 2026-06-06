#TODO: add an exists that doesn't do anything to deal with forall exists ... programs

import fileinput
import re
import copy

#input management

source = []
n = 0 #number of subprograms
pos = [] #to track the lines at which each subprogram starts

i = 0
for line in fileinput.input(encoding="utf-8"):
    if "@" in line:
        n += 1
        pos.append(i)
    source.append(line)
    i += 1

#breaking down the program into the subprograms

subp = [['' for _ in range(2)] for _ in range(n)]

i = 1
j = 0
while i < n:
    while j < pos[i]:
        if "@" in source[j]:
            subp[i-1][0] += source[j] 
        else:
            subp[i-1][1] += source[j] 
        j += 1
    i += 1    
while j < len(source):
    if "@" in source[j]:
        subp[n-1][0] += source[j] 
    else:
        subp[n-1][1] += source[j] 
    j += 1   

for i in range(n):
    if "exists" in subp[i][0] and (i+1) % 2 == 0:
        raise ValueError("exists quantifier at even level is not accepted by qasp")
    if "forall" in subp[i][0] and (i+1) % 2 != 0:
        raise ValueError("forall quantifier at odd level is not accepted by qasp")
    
#finding the herbrand base of each subprogram 

bh = []
for i in range(n): 
    temp = re.split(r'[.,\|:\-\s]+', subp[i][1])
    bh.append(temp)

for i in range(n): #keeps only the atoms
    j = 0
    while j < len(bh[i]):
        if "(" in bh[i][j] and not "{" in bh[i][j]:
            j += 1
        else:
            bh[i].pop(j)

dom = []
for i in range(n):
    for j in range (len(bh[i])):
        if not (any(char.isupper() for char in bh[i][j])): 
            dom.append(bh[i][j].split(")")[0].split("(")[1])
        else:
            hasVariables = True

for i in range(n): #renames the atoms so contradicting facts won't be added to the program during the evaluation of the quantifiers
    for j in range(len(bh[i])):
        bh[i][j] = bh[i][j].split("(")[0] + ("'" * (i+1)) + "(" + bh[i][j].split("(")[1]

for i in range(n): #removes duplicates
    j = 0
    while j < len(bh[i]):
        if bh[i][j] in bh[i][0:j]:
            bh[i].pop(j)
        else:
            j+=1

#translation

translation = ""

#translation of the programs

for i in range(n):
    translation += subp[i][1]
translation += "\n"

#add new atoms and check rules to avoid contradicting facts

#if there's variables defines a domain for them
if hasVariables:
    translation += "dom(" + min(dom) + ".." + max(dom) + ").\n"
    
for i in range(n):
    for j in range(len(bh[i])):
        if any(char.isupper() for char in bh[i][j]):
            translation += "{" + bh[i][j] + "}" + " :- dom(" + bh[i][j].split("(")[1].split(")")[0] + ").\n"  
        else:
            translation += "{" + bh[i][j] + "}.\n"
translation += "\n"

for i in range(n):
    for j in range(len(bh[i])):
        translation += ":- " + bh[i][j] + ", not " + re.split(r'\'+', bh[i][j])[0] + re.split(r'\'+', bh[i][j])[1] + ".\n"
        translation += ":- " + re.split(r'\'+', bh[i][j])[0] + re.split(r'\'+', bh[i][j])[1] + ", not " + bh[i][j] + ".\n"
translation += "\n"

#translation of the quantifiers 
#ex: @exists P
#becomes _exists(n, Bp). (expanded)

for i in range(n):
    for j in range(len(bh[i])):
        if "exists" in subp[i][0]:
            if any(char.isupper() for char in bh[i][j]):
                translation += "_exists(" + str(i+1) + "," + bh[i][j] + ") :- dom(" + bh[i][j].split("(")[1].split(")")[0] + ").\n"
            else:
                translation += "_exists(" + str(i+1) + "," + bh[i][j] + ").\n"
        else: 
            if any(char.isupper() for char in bh[i][j]):
                translation += "_forall(" + str(i+1) + "," + bh[i][j] + ") :- dom(" + bh[i][j].split("(")[1].split(")")[0] + ").\n"
            else:
                translation += "_forall(" + str(i+1) + "," + bh[i][j] + ").\n"

#output

print(translation)
