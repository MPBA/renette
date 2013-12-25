from itertools import combinations
import numpy as np
import os.path
import csv

def write_Sw (Sw, filename='Sw.csv'):
    """
    Write file for edge stability indicator
    """
    try:
        f = open(filename, 'wb')
        fw = csv.writer(f, delimiter='\t', lineterminator='\n')
    except IOError, e:
        print '%s' % e
        return False
    
    fw.writerow(['from', 'to', 'Sw'])
    links = combinations(xrange(Sw.shape[0]),2)
    for j,l in zip(range(Sw.shape[0]),links):
        ll = list(l)
        # Set 1 based index
        ll = [x + 1 for x in ll]
        if (Sw[j,:].mean() != 0.0):
            Swval = (Sw[j,:].max() - Sw[j,:].min()) / Sw[j,:].mean()
        else:
            Swval = 0.0
            ll.append(Swval)
        fw.writerow(ll)
    f.close()
        
    return True

def write_Sd(Sd, filename='Sd.csv'):
    """
    Write degree stability indicator file
    """
    try:
        f = open(filename, 'w')
        fw = csv.writer(f, delimiter='\t', lineterminator='\n')
    except IOError, e:
        print '%s' % e
        return False
    
    fw.writerow(['node', 'Sd'])
    for j in xrange(Sd.shape[1]):
        try:
            Sdval = (Sd[:,j].max() - Sd[:,j].min()) / Sd[:,j].mean()
        except:
            Sdval = 0.0
        # write 1-based index
        fw.writerow([j+1,Sdval])
    
    f.close()
    
    return True



    
