from classes.GR import GR

def readRightSide(gr):
    map = gr.productions.copy()
    for key,value in map.items() :
        if '&' in value :
            value.remove('&')
            for key1,value1 in map.items() :
                for info in value1 :
                    if key.strip() in info.strip() :
                        newstr = info.replace(key, '')
                        value1.append(newstr)
    return map

def eliminateIndirect(map):
    x = 0
    y = 0
    for key, value in map.items() :
        for key1, value1 in map.items() :
            if y > x :
                for v in value1 :
                    if v[0] == key :
                        vv = v[1:]
                        new_values = []
                        for v1 in value :
                            new_values.append(v1+vv)
                        value1 += new_values
                        value1.remove(v)            
            y+=1
        x+=1
        y=0                                  
    return map

def eliminateDirect(map):
    newProductions = {}
    newNonTerminals = []
    belongToMap = False
    for key,value in map.items():
        for v in value :
            if v[0] == key :
                belongToMap = True
        if belongToMap==False:
            newProductions[key] = value 
        else :
            key1 = key
            key2 = key+'\''
            value1 = []
            value2 = []
            for v in value :
                if v[0] != key:
                    value1.append(v+key2)
                else :
                    value2.append(v[1:]+key2)    
            value2.append('&')
            newProductions[key1] = value1
            newProductions[key2] = value2
            newNonTerminals.append(key2)
        belongToMap = False          
    return (newProductions, set(newNonTerminals))
    
def removeLeftRecursion(gr):
    map = readRightSide(gr)
    eliminateIndirectRecursion = eliminateIndirect(map)
    leftRecursionRemoved, newNonTerminals = eliminateDirect(eliminateIndirectRecursion)
    newNonTerminals = list(newNonTerminals.union(gr.nTerminals.copy()))
    newGR = GR(gr.terminals.copy(), newNonTerminals, list(leftRecursionRemoved.keys())[0], leftRecursionRemoved)
    return newGR

# exemplo
inicial = 'A'
naoTerminais = ['A','B','C']
terminais = ['a','b','c']
producoes = {'A':['AB','C'], 'B': ['Bc', 'BCc']}
gr = GR(terminais, naoTerminais, inicial, producoes)
newgr = removeLeftRecursion(gr)
print(newgr)
