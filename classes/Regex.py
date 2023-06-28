from classes.AF import AF
from classes.State import State

class Node:
    def __init__(self, type, label, name=None, left_child=None, right_child=None):
        self.name = name
        self.type = type
        self.left_child = left_child
        self.right_child = right_child
        self.label = label
        self.nullable = False
        self.firstpos = set()
        self.lastpos = set()

    def getId(self):
        return self.name

class Tree:
    def __init__(self, post):
        self.root = Node('cat', '.')
        self.leaves = dict()
        self.id_counter = 1
        self.createTree(post)
        self.followpos = [set() for i in range(self.id_counter)]
        self.postorderNullableFirstposLastposFollowpos(self.root)

    def createTree(self, post):
        stack = []
        for token in post:
            if token == '.':
                left = stack.pop()
                right = stack.pop()
                temp = Node('cat', token, left_child=left, right_child=right)
                stack.append(temp)
            elif token == '+':
                left = stack.pop()
                right = stack.pop()
                temp = Node('or', token, left_child=left, right_child=right)
                stack.append(temp)
            elif token == '*':
                left = stack.pop()  # Star node has only one child.
                temp = Node('star', token, left_child=left)
                stack.append(temp)
            else:  # identifier
                temp = Node('identifier', token, name=self.giveNextId())
                self.leaves[temp.name] = temp.label
                stack.append(temp)

        temp = Node('identifier', '#', name=self.giveNextId())
        self.leaves[temp.name] = temp.label
        self.root.left_child = stack.pop()
        self.root.right_child = temp

    def giveNextId(self):
        name = self.id_counter
        self.id_counter += 1
        return name

    def postorderNullableFirstposLastposFollowpos(self, node):
        if (node):
            self.postorderNullableFirstposLastposFollowpos(node.left_child)
            self.postorderNullableFirstposLastposFollowpos(node.right_child)
            if node.type == 'identifier':
                if node.label == '@':
                    node.nullable = True
                else:
                    node.firstpos.add(node.name)
                    node.lastpos.add(node.name)
            elif node.type == 'or':
                node.nullable = node.left_child.nullable or node.right_child.nullable
                node.firstpos = node.left_child.firstpos.union(node.right_child.firstpos)
                node.lastpos = node.left_child.lastpos.union(node.right_child.lastpos)
            elif node.type == 'star':
                node.nullable = True
                node.firstpos = node.left_child.firstpos
                node.lastpos = node.left_child.lastpos
                self.computeFollows(node)  # Follows is only computed for star and cat nodes
            elif node.type == 'cat':
                node.nullable = node.left_child.nullable and node.right_child.nullable
                if node.left_child.nullable:
                    node.firstpos = node.left_child.firstpos.union(node.right_child.firstpos)
                else:
                    node.firstpos = node.left_child.firstpos
                if node.right_child.nullable:
                    node.lastpos = node.left_child.lastpos.union(node.right_child.lastpos)
                else:
                    node.lastpos = node.right_child.lastpos
                self.computeFollows(node)
        else:
            return

    def computeFollows(self, node):
        if node.type == 'cat':
            for i in node.left_child.lastpos:
                self.followpos[i] = self.followpos[i].union(node.right_child.firstpos)
        elif node.type == 'star':
            for i in node.left_child.lastpos:
                self.followpos[i] = self.followpos[i].union(node.left_child.firstpos)
                
# Classe criada com o proposito de identificarmos o set_id deste estado (na construcao da arvore -> followPos e lastPos)
class StateOfDFAWithTree:
    def __init__(self, alphabet, id_list, name, terminal_id):
        self.name = name
        self.id_set = set(id_list)
        self.transitions = dict()
        self.final = terminal_id in self.id_set
        for a in alphabet:
            self.transitions[a] = {}

    def isFinal(self):
        return self.final

class DFAWithTree:
    # Criou-se uma classe a fim de aplicar a recursão mais facilmente com o armazenamente dos name's
    def __init__(self, alphabet, tree):
        self.states = []
        self.alphabet = alphabet
        self.id_counter = 1
        self.terminal = tree.id_counter - 1
        self.computeStates(tree)

    def computeStates(self, tree):
        D1 = StateOfDFAWithTree(self.alphabet, tree.root.firstpos, self.giveNextId(), self.terminal)
        self.states.append(D1)
        queue = [D1]
        while len(queue) > 0:
            st = queue.pop(0)
            new_states = self.determineTransitions(st, tree)
            for s in new_states:
                state = StateOfDFAWithTree(self.alphabet, s, self.giveNextId(), self.terminal)
                self.states.append(state)
                queue.append(state)

    def determineTransitions(self, state, tree):
        new_states = []
        for i in state.id_set:
            if i == self.terminal:
                continue
            label = tree.leaves[i]
            if state.transitions[label] == {}:
                state.transitions[label] = tree.followpos[i]
            else:
                state.transitions[label] = state.transitions[label].union(tree.followpos[i])
        for a in self.alphabet:
            if state.transitions[a] != {}:
                new = True
                for s in self.states:
                    if s.id_set == state.transitions[a] or state.transitions[a] in new_states:
                        new = False
                if new:
                    new_states.append(state.transitions[a])
        return new_states

    def processingInPostOrder(self):
        has_none_state = False
        for state in self.states:
            for a in self.alphabet:
                if state.transitions[a] == {}:
                    has_none_state = True
                    state.transitions[a] = self.id_counter
                SET = state.transitions[a]
                for state2 in self.states:
                    if state2.id_set == SET:
                        state.transitions[a] = state2.name
        if has_none_state:
            self.states.append(StateOfDFAWithTree(self.alphabet, [], self.id_counter, self.terminal))
            for a in self.alphabet:
                self.states[-1].transitions[a] = self.states[-1].name

    def getFinalStates(self):
        states_final_or_not = []
        for i in self.states:
            states_final_or_not.append(i.isFinal())
        return states_final_or_not

    def giveNextId(self):
        name = self.id_counter
        self.id_counter += 1
        return name
    
def createTokenQueue(inputOfRegex):
    tokens = []
    name = ''
    for letter in inputOfRegex:
        if letter in ['(', ')', '.', '*', '+']:
            if name != '':
                tokens.append(name)
                name = ''
            tokens.append(letter)
        else:
            name = name + letter
    if name != '':
        tokens.append(name)
    return tokens

def createPostfixTokenQueue(tokens):
    output_queue = []
    stack = []
    for token in tokens:
        if token == '(':
            stack.append('(')
        elif token == ')':
            while (len(stack) > 0 and stack[-1] != '('):
                output_queue.append(stack.pop())
            stack.pop()
        elif token == '*':
            stack.append(token)
        elif token == '.':
            while len(stack) > 0 and stack[-1] == '*':
                output_queue.append(stack.pop())
            stack.append(token)
        elif token == '+':
            while len(stack) > 0 and (stack[-1] == '*' or stack[-1] == '.'):
                output_queue.append(stack.pop())
            stack.append(token)
        else:
            output_queue.append(token)
    while (len(stack) > 0):
        output_queue.append(stack.pop())
    return output_queue

def readInputFromTerminal():
    alph = []
    print("Quantidade de letras: ",end='')
    alphabetLenght = int(input())
    for i in range(alphabetLenght):
        print(f"Escreva a letra {i + 1}:",end='')
        letter = str(input())
        alph.append(letter)
    print("Escreva a expressão regular:")
    regex = str(input())
    return alph, regex

def returnAsAFD(dfaWithTree):
    alphabet = dfaWithTree.alphabet
    states = dfaWithTree.states
    finalStates = dfaWithTree.getFinalStates()
    statesForAFD = []
    statesForAFDIds = []
    statesIdsSets = []
    for i in range(len(states)):
        s = State(str(states[i].id_set))
        statesForAFDIds.append((states[i].id_set))
        statesForAFD.append(s)
        statesIdsSets.append(states[i].id_set)
        
    for i in range(len(states)):
        for symbol, to in states[i].transitions.items():
            if to != {}:
                index = statesIdsSets.index(to)
                statesForAFD[i].addTransition(symbol, statesForAFD[index])
    
    initialState = statesForAFD[0]
    finalStatesAFD = []
    for i in range(len(finalStates)):
        if(finalStates[i]):
            finalStatesAFD.append(statesForAFD[i])
    af = AF(alphabet, statesForAFD, initialState, finalStatesAFD)
    print(af)
    return af

def regexIntoAFD():
    alphabet, inputOfRegex = readInputFromTerminal()
    tokens = createTokenQueue(inputOfRegex)
    post = createPostfixTokenQueue(tokens)
    tree = Tree(post)
    d = DFAWithTree(alphabet, tree)
    d = returnAsAFD(d)
