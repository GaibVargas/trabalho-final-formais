from classes.State import State
from classes.AF import AF

class Node:
    def __init__(self, left=None,right=None,data=None,father=None,first=None,fulfilled=None):
        self.father = father
        self.left = left
        self.right = right
        self.data = data
        self.lastpos = None
        self.firstpos = None
        self.nullable = None
        self.is_first_of_chain = first
        self.fulfilled = fulfilled

    def set_left(self, left):
        self.left = left

    def get_left(self):
        return self.left
    
    def set_right(self, right):
        self.right = right

    def get_right(self):
        return self.right
    
    def set_father(self, father):
        self.father = father

    def get_father(self):
        return self.father
    
    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def post_order(self, root):
        res = []
        if root:
            res = self.post_order(root.left)
            res = res + self.post_order(root.right)
            res.append(root)
        return res

def render_tree(regex):
    string = regex.replace(' ','')[::-1]
    tree = Node()
    last = tree
    index = 0
    while(index < len(string)):
        char = string[index]
        if char == '#':
            last.data = '#'
            last.father = Node(left=last)
            last.is_first_of_chain = True
            tree = last
        else:
            last, index = add_node(index,string,last)
        index = index + 1
    return tree.father.left

def add_node(index, string, node):
    char = string[index]
    if char == ')':
        index = index+1
        char = string[index]
        new_node = Node(data=char, first=True)
        new_node.father = Node(left=new_node)
        while(not string[index] == '('):
            new_node, index = add_node(index+1, string, new_node)
        n = new_node
        while(n.data):
            n = n.father
        n = n.left
        if not node.data == '*':
            new = concatenation(n,node)
            new.left.fulfilled = True
            return new.left, index
        else:
            node.left = n
            node.father.fulfilled = True
            return node.father, index
    elif char == '(':
        return node, index
    elif char == '|':
        n = node
        while(not n.is_first_of_chain):
            n = node.father
        new = Node(right=n,data='|', father=n.father)
        n.father.left = new
        n.father = new
        return new, index
    elif node.fulfilled:
        new = concatenation(Node(data=char),node)
        return new.left, index
    elif node.data == '|':
        node.left = Node(data=char, first=True, father=node)
        return node.left, index
    elif node.data == '*':
        node.left = Node(data=char,father=node)
        node.fulfilled = True
        return node, index
    else:
        new = concatenation(Node(data=char),node)
        return new.left, index
    
def def_nodes_function(tree):
    nodes = tree.post_order(tree)
    count = 1
    nodes_index = dict()
    for no in nodes:
        if no.data == '|':
                no.nullable = no.left.nullable or no.right.nullable
                no.firstpos = no.left.firstpos | no.right.firstpos
                no.lastpos = no.left.lastpos | no.right.lastpos
        elif no.data == 'concatenation':
            no.nullable = no.left.nullable and no.right.nullable
            if no.left.nullable:
                no.firstpos = no.left.firstpos | no.right.firstpos
            else:
                no.firstpos = no.left.firstpos
            if no.right.nullable:
                no.lastpos = no.left.lastpos | no.right.lastpos
            else:
                no.lastpos = no.right.lastpos
        elif no.data == '*':
            no.nullable = True
            no.firstpos = no.left.firstpos
            no.lastpos = no.left.lastpos
        else:
            if no.data != '&':
                no.nullable = False
                no.firstpos = set([count])
                no.lastpos = set([count])
                nodes_index[f'{count}'] = no.data
                count = count + 1
            else:
                no.nullable = True
                no.firstpos = set()
                no.lastpos = set()
    return count-1, nodes_index
    
def concatenation(node1,node2):
    if node2.is_first_of_chain:
        is_first = True
        node2.is_first_of_chain = False
    else:
        is_first = False
    newNode = Node(right=node2, data='concatenation', father=node2.father, first=is_first)
    node1.father = newNode
    node2.father.left = newNode
    newNode.left = node1
    return newNode

def define_followpos(tree, n_nodes):
    nodes = tree.post_order(tree)
    followpos = dict()
    for index in range(n_nodes):
        followpos[f'{index+1}'] = set()
    for no in nodes:
        if no.data == 'concatenation':
            for lastpos_node in no.left.lastpos:
                followpos[str(lastpos_node)] = followpos[str(lastpos_node)] | no.right.firstpos
        if no.data == '*':
            for firstpos_node in no.lastpos:
                followpos[str(firstpos_node)] = followpos[str(firstpos_node)] | no.firstpos
    return followpos, tree.firstpos

def dfa(followpos, nodes_index, initial_state):
    union = dict()
    states = list()
    states.append(initial_state)
    visited_states = list()
    automata = dict()
    while(not len(states) == 0):
        state = states.pop()
        visited_states.append(state)
        for pos in state:
            node = nodes_index.get(str(pos))
            if not node == '#':
                if not union.__contains__(node):
                    union[node] = set(followpos.get(str(pos)))
                else:
                    union[node] = union.get(node) | set(followpos.get(str(pos)))
        for s in union.items():
            if visited_states.count(s[1]) == 0:
                states.append(s[1])
        automata[str(state)] = union.copy()
        union.clear()
    return automata

def format_dfa(automata, initial_state, final, alphabet):
    dfa = dict()
    dfa['n_estados'] = len(automata)
    dfa['inicial'] = initial_state
    dfa['aceitacao'] = list()
    dfa['alfabeto'] = list(alphabet)
    dfa['transicoes'] = dict()
    estados = []
    for transiction in automata:
        if transiction.find(final):
            dfa.get('aceitacao').append(transiction)
        t = dict()
        for a in alphabet:
            tr = automata.get(transiction).get(a)
            if (tr):
                t[a] = [str(tr)]
            else:
                t[a] = []
        dfa.get('transicoes')[transiction] = t
    nomes_estados = list(dfa['transicoes'].keys())
    estado_inicial = dfa['inicial']
    estados_finais = []
    for i in range(len(nomes_estados)):
        estado_a_criar = State(nomes_estados[i])
        estados.append(estado_a_criar)
        if str(estado_inicial) == str(estado_a_criar.getId()):
            estado_inicial = estado_a_criar
        if (str(estado_a_criar.getId in dfa['aceitacao'])):
            estados_finais.append(estado_a_criar)
    transictions = dfa['transicoes']
    for k, v in transictions.items():
        index = nomes_estados.index(str(k))
        for k2, v2 in v.items():
            if v2 != []:
               indexForTarget = nomes_estados.index(str(v2[0]))
               estados[index].addTransition(k2, estados[indexForTarget]) 
    dfamin = AF(dfa['alfabeto'], estados, estado_inicial, estados_finais)
    return dfamin

def er_to_dfa(string):
    tree = render_tree(string)
    n_nodes, nodes_index = def_nodes_function(tree)
    followpos, initial_state = define_followpos(tree, n_nodes)
    automata = dfa(followpos,nodes_index,initial_state)
    final = [item[0] for item in list(nodes_index.items()) if item[1] == '#'][0]
    alphabet = set([item[1] for item in list(nodes_index.items()) if not item[1] == '#'])
    return format_dfa(automata, initial_state, final, alphabet)
