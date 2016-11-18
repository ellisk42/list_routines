from math import log
from collections import Counter
import editdistance

from LOTlib.Hypotheses.RecursiveLOTHypothesis import RecursiveLOTHypothesis
from LOTlib.Eval import primitive
from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
from LOTlib.DataAndObjects import FunctionData
from LOTlib.Grammar import Grammar
from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis

@primitive
def myFirst_(xs):
    if type(xs) is list and len(xs) == 2:
        return xs[0]
    else:
        raise Exception('FIRST')

@primitive
def myRest_(xs):
    if type(xs) is list and len(xs) == 2:
        return xs[1]
    else:
        raise Exception('REST')

# Define a grammar object
grammar = Grammar(start='START')

grammar.add_rule('START', '(%s if (myRest_(x) != []) else %s)', ['NUMBER','NUMBER'],1.0)

# Define some operations
grammar.add_rule('LIST', 'myRest_', ['LIST'], 1.0)
grammar.add_rule('LIST', 'cons_', ['NUMBER', 'LIST'], 1.0)
# grammar.add_rule('LIST', '[]', None, 1.0)
grammar.add_rule('LIST', 'x',None,1.0)

grammar.add_rule('NUMBER', 'myFirst_', ['LIST'], 1.0)
grammar.add_rule('NUMBER', 'recurse_', ['LIST'],1.0)

#grammar.add_rule('PREDICATE', '(%s == [])', ['LIST'],1.0)

class MyHypothesis(RecursiveLOTHypothesis):
    def __init__(self, **kwargs):
        RecursiveLOTHypothesis.__init__(self, grammar=grammar, display="lambda recurse_, x: %s", **kwargs)

#    def __call__(self,*args):
#        try:
#            return RecursiveLOTHypothesis.__call__(self,*args)
#        except TypeError:
#            return None

    def compute_single_likelihood(self, datum):
        try:
            # print 'program: ', str(self)
            # print 'input: ', datum.input
            # print 'our output: ', datum.output
            # print 'their output: ', self(*datum.input)
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
data = [ FunctionData(input = [e[0]],output = e[1],alpha = 0.95)
         for e in lastExamples ]


h0 = MyHypothesis()
count = Counter()
for h in MHSampler(h0,data,steps = 10000,likelihood_temperature=0.001):
    count[h] += 1
for h in sorted(count.keys(),key = lambda x: count[x]):
    print count[h],h.likelihood,h.prior,h

