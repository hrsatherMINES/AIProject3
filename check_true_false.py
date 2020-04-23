#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Name:        check_true_false
# Purpose:     Main entry into logic program. Reads input files, creates 
#              base, tests statement, and generates result file.
#
# Created:     09/25/2011
# Last Edited: 07/22/2013     
# Notes:       *Ported by Christopher Conly from C++ code supplied by Dr. 
#               Vassilis Athitsos.
#              *Several integer and string variables are put into lists. This is
#               to make them mutable so each recursive call to a function can
#               alter the same variable instead of a copy. Python won't let us
#               pass the address of the variables, so I put it in a list, which
#               is passed by reference.
#              *Written to be Python 2.4 compliant for omega.uta.edu
#-------------------------------------------------------------------------------

import sys
from logical_expression import *

def contains(sentence, model):
    for element in model:
        if (sentence.symbol == element.symbol
                and sentence.connective == element.connective
                and sentence.subexpressions == element.subexpressions):
            return True
    return False


def pl_true(sentence, model):
    if sentence.symbol != '':
        return contains(sentence.symbol, model)
        #return model[sentence.symbol]

    elif sentence.connective[0] == 'and':
        for child in sentence.subexpressions:
            if pl_true(child, model) == False:
                return False
        return True

    elif sentence.connective[0] == 'or':
        for child in sentence.subexpressions:
            if pl_true(child, model) == True:
                return True
        return False

    elif sentence.connective[0] == 'if':
        left = sentence.subexpressions[0]
        right = sentence.subexpressions[1]
        if pl_true(left, model) == True:
            return False
        if pl_true(right, model) == False:
            return False
        return True

    elif sentence.connective[0] == 'iff':
        left = sentence.subexpressions[0]
        right = sentence.subexpressions[1]
        if pl_true(left, model) == pl_true(right, model):
            return True
        return False

    elif sentence.connective[0] == 'not':
        child = sentence.subexpressions[0]
        return not pl_true(child, model)


def extract_symbols(sentence):
    result = []
    if sentence.symbol == '':
        result.append(sentence.symbol)
    else:
        for child in sentence.subexpressions:
            result += extract_symbols(child)
    return result


def tt_entails(KB, alpha):
    symbols1 = extract_symbols(KB)
    symbols2 = extract_symbols(alpha)
    symbols = symbols1 + symbols2
    return tt_check_all(KB, alpha, symbols, [])


def tt_check_all(KB, alpha, symbols, model):
    if len(symbols) == 0:
        if pl_true(KB, model):
            return pl_true(alpha, model)
        else:
            return True
    else:
        first = symbols[0]
        rest = symbols[1:]
        return (tt_check_all(KB, alpha, rest, extend(first, True, model))
                and tt_check_all(KB, alpha, rest, extend(first, False, model)))

            
def extend(first, boolean, model):
    if boolean == True:
        new_literal = first
    else:
        new_literal = '(not ' + first + ')'
    return model + new_literal


def check_true_false(knowledge_base, statement):

    try:
        output_file = open("result.txt", "w")
    except:
        print('failed to open file results.txt')
        sys.exit(0)

    print("result:", tt_entails(knowledge_base, statement))
    
    output_file.write("results unknown")
    output_file.close()


def main(argv):
    if len(argv) != 4:
        print('Usage: %s [wumpus-rules-file] [additional-knowledge-file] [input_file]' % argv[0])
        sys.exit(0)

    # Read wumpus rules file
    try:
        input_file = open(argv[1], 'r')
    except:
        print('failed to open file %s' % argv[1])
        sys.exit(0)

    # Create the knowledge base with wumpus rules
    print('\nLoading wumpus rules...')
    knowledge_base = logical_expression()
    knowledge_base.connective = ['and']
    for line in input_file:
        # Skip comments and blank lines. Consider all line ending types.
        if line[0] == '#' or line == '\r\n' or line == '\n' or line == '\r':
            continue
        counter = [0]  # A mutable counter so recursive calls don't just make a copy
        subexpression = read_expression(line.rstrip('\r\n'), counter)
        knowledge_base.subexpressions.append(subexpression)
    input_file.close()

    # Read additional knowledge base information file
    try:
        input_file = open(argv[2], 'r')
    except:
        print('failed to open file %s' % argv[2])
        sys.exit(0)

    # Add expressions to knowledge base
    print('Loading additional knowledge...')
    for line in input_file:
        # Skip comments and blank lines. Consider all line ending types.
        if line[0] == '#' or line == '\r\n' or line == '\n' or line == '\r':
            continue
        counter = [0]  # a mutable counter
        subexpression = read_expression(line.rstrip('\r\n'), counter)
        knowledge_base.subexpressions.append(subexpression)
    input_file.close()

    # Verify it is a valid logical expression
    if not valid_expression(knowledge_base):
        sys.exit('invalid knowledge base')

    # I had left this line out of the original code. If things break, comment out.
    print_expression(knowledge_base, '\n')

    # Read statement whose entailment we want to determine
    try:
        input_file = open(argv[3], 'r')
    except:
        print('failed to open file %s' % argv[3])
        sys.exit(0)
    print('\nLoading statement...')
    statement = input_file.readline().rstrip('\r\n')
    input_file.close()
    
    # Convert statement into a logical expression and verify it is valid
    statement = read_expression(statement)
    if not valid_expression(statement):
        sys.exit('invalid statement')

    # Show us what the statement is
    print('\nChecking statement: ')
    print_expression(statement, '')
    print

    # Run the statement through the inference engine
    check_true_false(knowledge_base, statement)

    sys.exit(1)
    

if __name__ == '__main__':
    main(sys.argv)