
## v tabelo igre se je dodal še en stolpec z (naključnimi) ocenami. 
## Program zamenja vrstni red zadnjega in predzadnjega stolpca.

import re

def p():
    b = []
    with open('tabele\igre.csv', 'r',errors = 'ignore') as f:
        for line in f:
            line = re.sub(r'(\'[7-9]),([0-9][0-9]\')',r'\1.\2',line)
            line = re.sub('\n','',line)
            line = line.split(',')
            line[8] = line[8].replace('\'','')
            line = line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[8],line[7]
            line= ','.join(line).replace('\'','')
            b.append(line)
    with open('tabele\igre.csv','w') as f:
        for elt in b:
            f.write(elt+'\n')



