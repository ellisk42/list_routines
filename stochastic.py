from math import log
from collections import Counter
import editdistance
from random import random

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

grammar.add_rule('START', '(%s if %s else %s)', ['NUMBER','PREDICATE','START'],1.0)
grammar.add_rule('START', '%s', ['NUMBER'],2.0)

# Define some operations
grammar.add_rule('LIST', 'myRest_', ['LIST'], 1.0)
grammar.add_rule('LIST', 'cons_', ['NUMBER', 'LIST'], 1.0)
grammar.add_rule('LIST', '[]', None, 2.)
grammar.add_rule('LIST', 'x',None, 2.)

grammar.add_rule('NUMBER', 'myFirst_', ['LIST'], 1.0)
grammar.add_rule('NUMBER', 'recurse_', ['NUMBER','LIST'],1.0)
grammar.add_rule('NUMBER', '(%s + 1)', ['NUMBER'],0.5)
grammar.add_rule('NUMBER', '(%s - 1)', ['NUMBER'],0.5)
grammar.add_rule('NUMBER', '0', None,1.5)
grammar.add_rule('NUMBER', '1', None,1.5)
grammar.add_rule('NUMBER', 'i', None,1.5)

grammar.add_rule('PREDICATE', '(%s == [])', ['LIST'],1.0)
grammar.add_rule('PREDICATE', '(%s %s %s)', ['NUMBER', 'COMPARISON', 'NUMBER'],1.)
#grammar.add_rule('PREDICATE', '(not (%s and %s))', ['PREDICATE','PREDICATE'],1.)

grammar.add_rule('COMPARISON', ' < ', None, 1.)
grammar.add_rule('COMPARISON', ' <= ', None, 1.)
grammar.add_rule('COMPARISON', ' == ', None, 1.)


class MyHypothesis(RecursiveLOTHypothesis):
    def __init__(self, **kwargs):
        RecursiveLOTHypothesis.__init__(self, grammar=grammar, display="lambda recurse_, i, x: %s", **kwargs)

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
def insert(x,ys):
    if ys == []: return [x]
    if x < ys[0]: return [x] + ys
    return [ys[0]] + insert(x,ys[1:])

lastExamples = [(list_([8]), 8),
                (list_([2,9,1]), 1),
                (list_([2,9,4]), 4),
                (list_([1,3]),3),
                (list_([8,2,9,9,9]),9),
                (list_([2]), 2)
                ]
getExamples = [[input[0], list_(input[1:]), input[input[0]]]
               for input in [[1,9],
                             [2,2,8],
                             [2,3,3,5],
                             [3,1,0,8,4],
                             [3,4,0,7,1,47]] ]
insertExamples = [[input[0], list_(input[1:]), list_(insert(input[0],input[1:]))]
                  for input in [[2],
                                [1],
                                [5,1,2,3],
                                [1,2,3],
                                [3,4]] ]
data = [ FunctionData(input = e[:-1], output = e[-1], alpha = 0.95)
         for e in insertExamples ]
print data

raise Exception('test')

h0 = MyHypothesis()
count = Counter()
for h in MHSampler(h0,data,steps = 100000,prior_temperature=1):
    count[h] += 1
for h in sorted(count.keys(),key = lambda x: x.likelihood + x.prior):
    print count[h],h.likelihood,h.prior,h

