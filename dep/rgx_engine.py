from anytree import Node
from anytree import RenderTree
from dep.NFA import NFA
import copy

class RGXGRMM():
    terminal = {'|', '*', '(', ')', 'a', '$'}
    non_terminal = {'U', 'UP', 'C', 'CP', 'K', 'KP', 'A'}
    ll1_Table = {
        'U' : {
            '|' : None,
            '*' : None,
            '(' : ['C', 'UP'],
            ')' : None,
            'a' : ['C', 'UP'],
            '$' : None
        },
        'UP' : {
            '|' : ['|', 'C', 'UP'],
            '*' : None,
            '(' : None,
            ')' : [''],
            'a' : None,
            '$' : ['']
        },
        'C' : {
            '|' : None,
            '*' : None,
            '(' : ['K', 'CP'],
            ')' : None,
            'a' : ['K', 'CP'],
            '$' : None
        },
        'CP' : {
            '|' : [''],
            '*' : None,
            '(' : ['K', 'CP'],
            ')' : [''],
            'a' : ['K', 'CP'],
            '$' : ['']
        },
        'K' : {
            '|' : None,
            '*' : None,
            '(' : ['A', 'KP'],
            ')' : None,
            'a' : ['A', 'KP'],
            '$' : None
        },
        'KP' : {
            '|' : [''],
            '*' : ['*'],
            '(' : [''],
            ')' : [''],
            'a' : [''],
            '$' : ['']
        },
        'A' : {
            '|' : None,
            '*' : None,
            '(' : ['(', 'U', ')'],
            ')' : None,
            'a' : ['a'],
            '$' : None
        }
    } 
    
    def reco(self, inpt):
        inpt = inpt + '$'
        stack = ['$', 'U']
        p_stack = []
        
        idx = 0
        
        root = Node('U')
        p_stack.append(root)
        
        while True:
            crr = stack.pop()
            
            if crr in self.non_terminal or crr == '':
                if crr != '':
                    if self.ll1_Table[crr][inpt[idx]] is None:
                        return 'error token: ' + str(inpt[idx]) + ' rule: ' + crr
                    stack = stack + self.ll1_Table[crr][inpt[idx]][::-1]
                    ft = p_stack.pop()
                    while ft.name in self.terminal:
                        ft = p_stack.pop()
                    for nt in self.ll1_Table[crr][inpt[idx]][::-1]:
                        if nt not in {'|', '(', ')'}:
                            if nt != '':
                                p_stack.append(Node(nt, parent = ft))
                            else:
                                Node(nt, parent = ft)
                
            elif crr in self.terminal:
                if crr == '$':
                    break
                elif crr == inpt[idx]:
                    idx += 1
                else:
                    return 'error token: ' + str(inpt[idx]) + ' rule: ' + crr
        
            else:
                return 'error token: ' + str(inpt[idx]) + ' rule: ' + crr
        
        if inpt[idx] == '$':
            return root
        else:
            return 'error, final token: ' + str(inpt[idx])
        
        
    def preorder(self, root, vl):
        child = root.children[::-1]
        if root.name == 'a':
            var = vl.pop()
            return NFA({var}, {0, 1}, 0, [{var : 1}], [1])
        elif root.name == 'A':
            return self.preorder(child[0], vl)
        elif root.name == 'K':
            if child[1].children[0].name == '*':
                return kleene(self.preorder(child[0], vl))
            else:
                return self.preorder(child[0], vl) 
        elif root.name == 'C' or root.name == 'CP':
            if len(child) > 1:
                l = self.preorder(child[0], vl)
                r = self.preorder(child[1], vl)
                if l == '':
                    return r
                elif r == '':
                    return l
                else:
                    return conc(l, r)
            else:
                return ''
        elif root.name == 'U' or root.name == 'UP':
            if len(child) > 1:
                l = self.preorder(child[0], vl)
                r = self.preorder(child[1], vl)
                if l == '':
                    return r
                elif r == '':
                    return l
                else:
                    return union(l, r)
            else:
                return ''
        else:
            return ''
        
    def reg_lex(self, expresion):
        fn = ''
        var = []
        for x in expresion:
            if x == ' ':
                continue
            if x == '(' or x == ')' or x == '*'  or x == '|':
                fn += x
            elif x == '$':
                return 'error, unexpected token: ' + x
            else:
                fn += 'a'
                var.append(x)

        return var, fn
    
    def regular_expresion(self, expresion):
        vL, tokens = self.reg_lex(expresion)
        x = self.reco(tokens)
        
        return nfa_dfa(self.preorder(x, vL[::-1]))
    
    def evaluar(self, cadena):
        return self.automata.reco(cadena)

    def export(self):
        return self.automata.export()

    def imprt(self, im):
        self.automata = NFA(
            set(im['sigma']), 
            set(im['Q']), 
            im['q0'],
            im['delta'], 
            set(im['F']),
        )

        self.automata.addtoken(im['token'])

    def __init__(self, expresion, token):
        self.token = token
        if(type(expresion) == type('')):
            self.automata = self.regular_expresion(expresion)
            self.automata.addtoken(token)
        else:
            self.imprt(expresion)
            
def conc(nfa1, nfa2):
    last = len(nfa1.Q)

    d1 = copy.deepcopy(nfa1.delta)
    d2 = copy.deepcopy(nfa2.delta)
    
    d1.append({'$': nfa2.q0 + last})
    
    for k, elm in enumerate(d2):
        for key in elm:
            if type(d2[k][key]) == type(1):
                d2[k][key] = d2[k][key] + last
            else:
                d2[k][key] = [nm + last for nm in d2[k][key]]
    d3 = d1 + d2

    nfa3 = NFA(nfa1.sigma.union(nfa2.sigma), 
               nfa1.Q.union([elm + last for elm in nfa2.Q]), 
               nfa1.q0, 
               d3,
               set([elm + last for elm in nfa2.F])
              )
    
    return nfa3

def union(nfa1, nfa2):
    last1 = len(nfa1.Q) - 1
    last2 = len(nfa1.Q) + len(nfa2.Q) - 1
    
    d1 = copy.deepcopy(nfa1.delta)
    d1.append({'$': last2 + 2})
    
    d2 = copy.deepcopy(nfa2.delta)
    for k, elm in enumerate(d2):
        for key in elm:
            if type(d2[k][key]) == type(1):
                d2[k][key] = d2[k][key] + last1 + 1
            else:
                d2[k][key] = [elem + last1 + 1 for elem in d2[k][key]]
            
    d2.append({'$': last2 + 2})
            
    d3 = d1 + d2
    d3.append({
        '$': [nfa1.q0, nfa2.q0 + last1 + 1]
    })
    
    sigma = nfa1.sigma.union(nfa2.sigma)
    Q = nfa1.Q.union([elem + last1 + 1 for elem in nfa2.Q])
    Q = Q.union({last2 + 1, last2 + 2})
    q0 = last2 + 1
    F = {last2 + 2}
    
    nfa3 = NFA(sigma, Q, q0, d3, F)
    return nfa3
    
def kleene(nfa1):
    last = len(nfa1.Q) - 1
    
    d1 = copy.deepcopy(nfa1.delta)
    d1.append({'$': [nfa1.q0, last + 2]})
    d1.append({'$': [nfa1.q0, last + 2]})
    
    sigma = copy.deepcopy(nfa1.sigma)
    Q = nfa1.Q.union([last + 1, last + 2])
    q0 = last + 1
    F = {last + 2}
    
    nfa3 = NFA(sigma, Q, q0, d1, F)
    return nfa3

# nfa a dfa
def nfa_dfa(nfa):
    dn = copy.deepcopy(nfa.delta)
      
    Q = set({})
    d = {}
    
    start = e_cl(nfa, nfa.q0)
    xtr = {str(start)}
    visited = set({})
    
    q0 = str(start)
    
    F = set({})
    f1 = nfa.F
    
    while len(xtr):
        xtr.remove(str(start))
        
        for fnl in f1:
            if fnl in start:
                F.add(str(start))
        
        if str(start) not in visited:
            visited.add(str(start))
            if len(start):
                Q.add(str(start))

            for k in nfa.sigma:
                e = set({})
                
                for elm in start:
                    if elm < len(nfa.delta) and k in nfa.delta[elm]:
                        dlt = nfa.delta[elm][k]
                        if type(dlt) == type(1):
                            e = e.union(e_cl(nfa, dlt))
                        else:
                            for itm in dlt:
                                e = e.union(e_cl(nfa, itm))
                            
                if len(e):
                    if str(start) not in d:
                        d[str(start)] = {}
                    d[str(start)][k] = str(e)
                
                xtr.add(str(e))
        
        start = '' if len(xtr) < 1 else eval(list(xtr)[0])
        
    dfa = NFA(nfa.sigma, Q, q0, d, F)
    return dfa
    
# lambda clausura
def e_cl(nfa, state):
    res = {state}
    
    if state < len(nfa.delta) and '$' in nfa.delta[state]:
        nxt = nfa.delta[state]['$']
        
        if type(nxt) == type(1):
            res = res.union(e_cl(nfa, nxt))
        else:
            for x in nxt:
                res = res.union(e_cl(nfa, x))    
    
    return res

def parser(expresion, nfa):
    c = expresion[0]
    c1 = expresion[1]
    
    op = {'(', '*', '|'}
    
    if c not in op:
        ax = NFA({c}, {0, 1}, 0, [{c : 1}], [1])
        
        if len(nfa.Q):
            nfa = conc(nfa, ax)
            
            if len(expresion) > 1:
                return parser(expresion[1::], nfa)
    
        else:
            return ax
    
    return nfa
        