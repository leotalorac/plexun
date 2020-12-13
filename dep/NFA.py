import json

class NFA():
    sigma = {}
    Q = {}
    q0 = 0
    delta = [{}]
    F = {}
    token = ''
    
    def __init__(self, sigma, Q, q0, delta, F):
        self.sigma = sigma
        self.Q = Q
        self.q0 = q0
        self.delta = delta
        self.F = F
        
    def reco(self, cadena):
        curr = self.q0
        for char in cadena:
            if char in self.sigma:
                if char in self.delta[str(curr)]:
                    curr = self.delta[str(curr)][char]
                else:
                    if str(curr) in self.F:
                        return True
                    else:
                        return False
                    
            else:
                return False
        
        if str(curr) in self.F:
            return True
        else:
            return False

    def addtoken(self, token):
        self.token = token
    
    def export(self):
        exp = {
            'token': self.token,
            'sigma': list(self.sigma),
            'Q': list(self.Q),
            'q0': self.q0,
            'delta': dict(self.delta),
            'F': list(self.F)
        }

        return exp

    def __str__(self):
        q = str(self.q0) if type(self.q0) == type(1) else self.q0
        
        res = (
            "sigma: " + str(self.sigma) + 
            " Q: " + str(self.Q) + 
            " q0: " + q + 
            " delta: " + str(self.delta) + 
            " F: " + str(self.F)
        )
        return res