import os
import sys
import argparse
from collections import Counter
import numpy as np

class HMM:
    '''Hidden Markov Model class to store relevent matrices and function sequences'''
    def __init__(self):
        observations = []
        hiddenStates = []
        initialProb = np.array([])
        transitionProb = np.array([])
        observationProb = np.array([])
        orderPOS = []

    def parseTraining(self, training_list):
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

        self.observations = words
        self.hiddenStates = posTags

    def sentenceSeperation(self, symbol):
        '''Create matrices of words and POS tags using symbol of choice (i.e. periods, colons etc) to split sentences'''
        
        sentences = []
        sentence = []
        posTagSentence = []
        posTagSentences = []
        for i, word in enumerate(self.observations):
            if word == symbol:
                sentences.append(sentence)
                sentence = []
                posTagSentences.append(posTagSentence)
                posTagSentence = []
            else:
                sentence.append(word)
                posTagSentence.append(self.hiddenStates[i])
        sentences.append(sentence)
        posTagSentences.append(posTagSentence)

        # Remove empty list at the end of each matrix, sentences and posTagSentences
        sentences.pop()
        posTagSentences.pop()
        
        # Overwrite observations array with sentences array and hiddenStates array with posTagSentences array
        self.observations = sentences
        self.hiddenStates = posTagSentences

    def initialProbCounting(self):
        '''Create matrix for the initial probabilities for each POS tag - P(S0)'''
        
        numSentences = len(self.hiddenStates)
        initProb = np.array([])
        initStates = []

        # Get first column of hiddenStates matrix
        for sentence in self.hiddenStates:
            initStates.append(sentence[0])

        initCount = Counter(initStates)
        orderingTags = list(initCount.keys())

        # Using initCount, create initProb array of initial probabilities for each POS tag
        for tag in initCount:
            initProb = np.append(initProb, initCount[tag]/numSentences)
        
        # Normalize initProb array
        initProb = initProb/np.sum(initProb)

        # Set class variables for future use
        self.initialProb = initProb
        self.orderPOS = orderingTags

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
    hmm.parseTraining(training_list)
    hmm.sentenceSeperation('.')
    hmm.initialProbCounting()
    print(hmm.initialProb)