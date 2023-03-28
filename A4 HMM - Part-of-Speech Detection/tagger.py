import os
import sys
import argparse
from collections import Counter

class HMM:
    '''Hidden Markov Model class to store relevent matrices and sequences'''
    def __init__(self):
        pass

def sentenceSeperation():
    '''Seperate input text file by text symbol of choice (i.e. periods, colons etc)'''
    pass

def initialProbCounting():
    '''Create matrix for the initial probabilities of each POS tag - P(S0)'''
    pass

def transitionProbCounting():
    '''Create matrix for transition probabilities between POS tags - P(Sk+1|Sk)'''
    pass

def observationProbCounting():
    '''Create matrix for observation probabilities of word observation, given POS tag - P(ek|Sk)'''
    pass

def viterbi():
    '''Use Viterbi algorithm to determine the most likely sequence of POS tags'''
    pass

def trackSequence():
    '''With Viterbi algorithm complete, track most likely sequence and print results to output file'''
    pass

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--trainingfiles",
        action="append",
        nargs="+",
        required=True,
        help="The training files."
    )
    parser.add_argument(
        "--testfile",
        type=str,
        required=True,
        help="One test file."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file."
    )
    args = parser.parse_args()

    training_list = args.trainingfiles[0]
    print("training files are {}".format(training_list))

    print("test file is {}".format(args.testfile))

    print("output file is {}".format(args.outputfile))


    print("Starting the tagging process.")
