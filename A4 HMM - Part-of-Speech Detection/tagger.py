import os
import sys
import argparse
from collections import Counter

class HMM:
    '''Hidden Markov Model class to store relevent matrices and sequences'''
    def __init__(self):
        observations = []
        hiddenStates = []

def parseTraining(hmm, training_list):
    '''Parse training data and create two lists, one for the words (observations) and one for the POS tags (hidden states)'''
    words = []
    posTags = []

    for training_file in training_list:
        # Open training file, for each line split on colon, appending first element to words list and second element to posTags list
        with open(training_file, 'r') as f:
            for line in f:
                line = line.split(':')
                words.append(line[0].strip())
                posTags.append(line[1].strip())
    
    hmm.observations = words
    hmm.hiddenStates = posTags

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
        required=False,
        help="One test file."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=False,
        help="The output file."
    )
    args = parser.parse_args()

    training_list = args.trainingfiles[0]

    # Initialize HMM class and parse training data
    hmm = HMM()
    parseTraining(hmm, training_list)