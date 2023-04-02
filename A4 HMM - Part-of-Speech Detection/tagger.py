import os
import sys
import argparse
from collections import Counter
from collections import defaultdict
from itertools import chain
import numpy as np

class HMM:
    '''Hidden Markov Model class to store relevent matrices and function sequences
    Note that N = number of POS tags and M = number of words in the data set'''
    def __init__(self):
        self.observations = []
        self.hiddenStates = []
        self.initialProb = np.array([])
        self.transitionProb = np.array([])
        self.observationProb = np.array([])
        self.initPOS = []
        self.tags = ["AJ0", "AJC", "AJS", "AT0", "AV0", "AVP", "AVQ", "CJC", "CJS", "CJT", "CRD",
        "DPS", "DT0", "DTQ", "EX0", "ITJ", "NN0", "NN1", "NN2", "NP0", "ORD", "PNI",
        "PNP", "PNQ", "PNX", "POS", "PRF", "PRP", "PUL", "PUN", "PUQ", "PUR", "TO0",
        "UNC", 'VBB', 'VBD', 'VBG', 'VBI', 'VBN', 'VBZ', 'VDB', 'VDD', 'VDG', 'VDI',
        'VDN', 'VDZ', 'VHB', 'VHD', 'VHG', 'VHI', 'VHN', 'VHZ', 'VM0', 'VVB', 'VVD',
        'VVG', 'VVI', 'VVN', 'VVZ', 'XX0', 'ZZ0', 'AJ0-AV0', 'AJ0-VVN', 'AJ0-VVD',
        'AJ0-NN1', 'AJ0-VVG', 'AVP-PRP', 'AVQ-CJS', 'CJS-PRP', 'CJT-DT0', 'CRD-PNI', 'NN1-NP0', 'NN1-VVB',
        'NN1-VVG', 'NN2-VVZ', 'VVD-VVN', 'AV0-AJ0', 'VVN-AJ0', 'VVD-AJ0', 'NN1-AJ0', 'VVG-AJ0', 'PRP-AVP',
        'CJS-AVQ', 'PRP-CJS', 'DT0-CJT', 'PNI-CRD', 'NP0-NN1', 'VVB-NN1', 'VVG-NN1', 'VVZ-NN2', 'VVN-VVD']

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

        # TODO: Do this for test data as well

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
        
        # For each POS tag not seen in tags, append 0 to initProb array
        for tag in self.tags:
            if tag not in orderingTags:
                initProb = np.append(initProb, 0)
                orderingTags.append(tag)

        # Reshape initProb array into matrix (1 x N)
        initProb = np.reshape(initProb, (1, len(initProb)))

        # Set class variables for future use
        self.initialProb = initProb
        self.initPOS = orderingTags

    def transitionProbCounting(self):
        '''Create matrix for transition probabilities between POS tags - P(Sk+1|Sk).
        Each starting POS tag has a probability distribution over the next POS tag.'''
        
        tagCount = dict()
        tranProb = np.array([])

        # Get number of times each tag appears in dataset (aside from last tag in each sentence since no transition occurs)
        for tag in self.tags:
            count = 0
            for sentence in self.hiddenStates:
                for i in range(len(sentence)-1):
                    if sentence[i] == tag:
                        count += 1
            tagCount = {**tagCount, **{tag: count}}

        # Get number of times each tag appears after another tag
        for tag1 in self.tags:
            for tag2 in self.tags:
                count = 0
                for sentence in self.hiddenStates:
                    for i in range(len(sentence)-1):
                        if sentence[i] == tag1 and sentence[i+1] == tag2:
                            count += 1
                if tagCount[tag1] == 0:
                    tranProb = np.append(tranProb, 0)
                else:
                    tranProb = np.append(tranProb, count/tagCount[tag1])

        # Reshape tranProb array into matrix (N x N)
        tranProb = np.reshape(tranProb, (len(self.tags), len(self.tags)))

        self.transitionProb = tranProb

    def observationProbCounting(self):
        '''Create matrix for observation probabilities of word observation, given POS tag - P(ek|Sk).
        Each POS tag has a probability distribution over observed words.'''
        
        tagCount = dict()
        flat_obs = list(chain.from_iterable(self.observations))
        flat_obs_set = set(flat_obs)

        # Get number of times each tag appears in dataset
        flat_pos = list(chain.from_iterable(self.hiddenStates))
        tagTotal = Counter(flat_pos)

        # Join observations and hiddenStates into one list of tuples
        obs_pos = list(zip(flat_obs, flat_pos))
        while ('', '') in obs_pos:
            obs_pos.remove(('', ''))
        obsProb = np.zeros((len(self.tags), (len(flat_obs_set))))

        # Get count of word given POS tag using obs_pos list and tagCount dictionary
        for obs in obs_pos:
            if obs in tagCount:
                tagCount[obs] += 1
            elif obs not in tagCount:
                tagCount[obs] = 1

            # Form observation probability matrix
            obsLoc = list(flat_obs_set).index(obs[0])
            tagLoc = self.tags.index(obs[1])
            if obs[1] in tagTotal:
                obsProb[tagLoc][obsLoc] =  tagCount[obs]/tagTotal[obs[1]]
            else:
                obsProb[tagLoc][obsLoc] = 0

        self.observationProb = obsProb

def viterbi():
    '''Use Viterbi algorithm to determine the most likely sequence of POS tags'''
    pass

def wordNotinTraining():
    '''If word not in training data, use Laplace smoothing to calculate observation probability'''
    pass

def trackSequence():
    '''With Viterbi algorithm complete, track most likely sequence and print results to output file'''
    pass

def output_file(filename, soln):
    # Create output file
    sys.stdout = open(filename, 'w')

    # Write matrix to output file
    for row in soln:
        for col in row:
            sys.stdout.write(str(col) + " ")
        sys.stdout.write("\n")

    # TODO: Write results to output file

    # Close file
    sys.stdout.close()
    sys.stdout = sys.__stdout__

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
    hmm.transitionProbCounting()
    hmm.observationProbCounting()
    # output_file(args.outputfile, hmm.observationProb)
    print(np.sum(hmm.observationProb, axis=1))