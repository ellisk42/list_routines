from math import log
from collections import Counter

from LOTlib.Hypotheses.RecursiveLOTHypothesis import RecursiveLOTHypothesis
from LOTlib.Eval import primitive
from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
from LOTlib.DataAndObjects import FunctionData
from LOTlib.Grammar import Grammar
from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis


# Define a grammar object
grammar = Grammar(start='START')

grammar.add_rule('START', 'if_', ['PREDICATE','NUMBER','START'],1.0)
grammar.add_rule('START', '%s', ['RECURSIVENUMBER'],1.0)

# Define some operations
if False:
    grammar.add_rule('RECURSIVELIST', 'cdr_', ['RECURSIVELIST'], 1.0)
    grammar.add_rule('RECURSIVELIST', 'cons_', ['NUMBER', 'RECURSIVELIST'], 1.0)
    grammar.add_rule('RECURSIVELIST', '[]', None, 1.0)
    grammar.add_rule('RECURSIVELIST', 'x',None,1.0)
    grammar.add_rule('RECURSIVELIST', 'recurse_', ['RECURSIVELIST'],1.0)


grammar.add_rule('LIST', 'cdr_', ['LIST'], 1.0)
grammar.add_rule('LIST', 'cons_', ['NUMBER', 'LIST'], 1.0)
grammar.add_rule('LIST', '[]', None, 1.0)
grammar.add_rule('LIST', 'x',None,1.0)
#grammar.add_rule('LIST', 'recurse_', ['LIST'],1.0)


#grammar.add_rule('FUNCTION', 'lambda',['LIST'],1.0,bv_type = 'LIST')

grammar.add_rule('NUMBER', 'car_', ['LIST'], 1.0)
#grammar.add_rule('NUMBER', '0', None, 1.)

grammar.add_rule('RECURSIVENUMBER', 'car_', ['LIST'], 1.0)
#grammar.add_rule('RECURSIVENUMBER', 'plus_(%s,1)', ['RECURSIVENUMBER'], 1.)
#grammar.add_rule('RECURSIVENUMBER', 'plus_(%s,-1)', ['RECURSIVENUMBER'], 1.)
#grammar.add_rule('RECURSIVENUMBER', '0', None, 1.)
grammar.add_rule('RECURSIVENUMBER', 'recurse_', ['LIST'],1.0)

# And define some numbers. We'll give them a 1/n^2 probability
if False:
    for n in xrange(1,10):
        grammar.add_rule('NUMBER', str(n), None, 10.0/n**2)
        grammar.add_rule('RECURSIVENUMBER', str(n), None, 10.0/n**2)



grammar.add_rule('PREDICATE', '(%s == [])', ['LIST'],1.0)
# grammar.add_rule('PREDICATE', 'or_', ['PREDICATE','PREDICATE'],1.0)
# grammar.add_rule('PREDICATE', 'not_', ['PREDICATE'],1.0)
# grammar.add_rule('PREDICATE', '(%s < %s)', ['NUMBER','NUMBER'],1.0)
# grammar.add_rule('PREDICATE', '(%s == %s)', ['NUMBER','NUMBER'],1.0)

class MyHypothesis(RecursiveLOTHypothesis):
    def __init__(self, **kwargs):
        RecursiveLOTHypothesis.__init__(self, grammar=grammar, display="lambda recurse_, x: %s", **kwargs)

    def __call__(self,*args):
        try:
            return RecursiveLOTHypothesis.__call__(self,*args)
        except TypeError:
            return None

    def compute_single_likelihood(self, datum):
        try:
            if str(self(*datum.input)) == str(datum.output):
                return log(datum.alpha)
            else:
                return log(1.0-datum.alpha)
        except:
            return float("nan")

def list_(l):
    if l == []: return l
    return cons_(l[0],list_(l[1:]))

lastExamples = [(list_([8]), 8),
                (list_([2,9,1]), 1),
                (list_([2,9,4]), 4),
                (list_([1,3]),3),
                (list_([8,2,9,9,9]),9),
                (list_([2]), 2)
                ]
print lastExamples
data = [ FunctionData(input = [e[0]],output = e[1],alpha = 0.95)
         for e in lastExamples ]
print data


h0 = MyHypothesis()
count = Counter()
for h in MHSampler(h0,data,steps = 1000000):
    count[h] += 1
#    print h.compute_prior(),h.compute_likelihood(data),h
for h in sorted(count.keys(),key = lambda x: count[x]):
    print count[h],h.likelihood,h

