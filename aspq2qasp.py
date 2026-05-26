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
        if "(" in bh[i][j]:
            j += 1
        else:
            bh[i].pop(j)

dom = copy.deepcopy(bh)
for i in range(n):
    j = 0
    while j < len(dom[i]):
        if not (any(char.isupper() for char in dom[i][j])): #removes variables (uppercase characters or strings beginning with uppercase characters)
            dom[i][j] = dom[i][j].split(")")[0].split("(")[1]
            j += 1
        else:
            dom[i].pop(j)

for i in range(n): #replaces variables with all the possible values of the domain 
    j = 0
    while j < len(bh[i]):
        if any(char.isupper() for char in bh[i][j]):
            for k in range(len(dom[i])):
                bh[i].append(bh[i][j].split("(")[0] + "(" + dom[i][k] + ")")
            bh[i].pop(j)
        else:
            j += 1

prefix = [[] for _ in range(n)]
for i in range(n): #removes duplicates
    for x in bh[i]:
        if x not in prefix[i]:
            prefix[i].append(x) 

for i in range(n): #renames the atoms so contradicting facts won't be added to the program during the evaluation of the quantifiers
    for j in range(len(prefix[i])):
        prefix[i][j] = prefix[i][j].split("(")[0] + ("'" * (i+1)) + "(" + prefix[i][j].split("(")[1]

#translation

translation = ""

#translation of the programs

for i in range(n):
    translation += subp[i][1]
translation += "\n"

#add new atoms and check rules to avoid contradicting facts

translation += "{"
if len(prefix[n-1]) > 0:
    for i in range(n-1):
        for j in range(len(prefix[i])):
            translation += prefix[i][j] + ";"
    for j in range(len(prefix[n-1])-1):
        translation += prefix[n-1][j] + ";"
    translation += prefix[n-1][len(prefix[n-1])-1] + "}.\n"
else:
    for i in range(n-2):
        for j in range(len(prefix[i])):
            translation += prefix[i][j] + ";"
    for j in range(len(prefix[n-2])-1):
        translation += prefix[n-2][j] + ";"
    translation += prefix[n-2][len(prefix[n-2])-1] + "}.\n"

for i in range(n):
    for j in range(len(prefix[i])):
        translation += ":- " + prefix[i][j] + ", not " + re.split(r'\'+', prefix[i][j])[0] + re.split(r'\'+', prefix[i][j])[1] + ".\n"
        translation += ":- " + re.split(r'\'+', prefix[i][j])[0] + re.split(r'\'+', prefix[i][j])[1] + ", not " + prefix[i][j] + ".\n"
translation += "\n"

#translation of the prefix
#ex: @exists P
#becomes _exists(n, Bp). (expanded)

for i in range(n):
    for j in range(len(prefix[i])):
        if "exists" in subp[i][0]:
            translation += "_exists(" + str(i+1) + "," + prefix[i][j] + ").\n"
        else:
            translation += "_forall(" + str(i+1) + "," + prefix[i][j] + ").\n"

#output

print(translation)
