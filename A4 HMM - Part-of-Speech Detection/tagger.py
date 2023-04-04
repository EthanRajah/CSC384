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
    def __init__(self, training_list, test_file, output):
        self.trainingList = training_list
        self.testFile = test_file
        self.outputFile = output
        self.observations = []
        self.hiddenStates = []
        self.testSentences = []
        self.initialProb = np.array([])
        self.transitionProb = np.array([])
        self.observationProb = np.array([])
        self.observationSet = []
        self.tags = ["AJ0", "AJC", "AJS", "AT0", "AV0", "AVP", "AVQ", "CJC", "CJS", "CJT", "CRD",
        "DPS", "DT0", "DTQ", "EX0", "ITJ", "NN0", "NN1", "NN2", "NP0", "ORD", "PNI",
        "PNP", "PNQ", "PNX", "POS", "PRF", "PRP", "PUL", "PUN", "PUQ", "PUR", "TO0",
        "UNC", 'VBB', 'VBD', 'VBG', 'VBI', 'VBN', 'VBZ', 'VDB', 'VDD', 'VDG', 'VDI',
        'VDN', 'VDZ', 'VHB', 'VHD', 'VHG', 'VHI', 'VHN', 'VHZ', 'VM0', 'VVB', 'VVD',
        'VVG', 'VVI', 'VVN', 'VVZ', 'XX0', 'ZZ0', 'AJ0-AV0', 'AJ0-VVN', 'AJ0-VVD',
        'AJ0-NN1', 'AJ0-VVG', 'AVP-PRP', 'AVQ-CJS', 'CJS-PRP', 'CJT-DT0', 'CRD-PNI', 'NN1-NP0', 'NN1-VVB',
        'NN1-VVG', 'NN2-VVZ', 'VVD-VVN', 'AV0-AJ0', 'VVN-AJ0', 'VVD-AJ0', 'NN1-AJ0', 'VVG-AJ0', 'PRP-AVP',
        'CJS-AVQ', 'PRP-CJS', 'DT0-CJT', 'PNI-CRD', 'NP0-NN1', 'VVB-NN1', 'VVG-NN1', 'VVZ-NN2', 'VVN-VVD']

    def parseTraining(self):
        '''Parse training data and create two lists, one for the words (observations) and one for the POS tags (hidden states)'''

        words = []
        posTags = []

        for training_file in self.trainingList:
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

        # Split test data into sentences
        self.sentenceSeperationTest(symbol)

    def sentenceSeperationTest(self, symbol):
        '''Split test data into sentences using symbol of choice (i.e. periods, colons etc)'''

        words = []
        with open(self.testFile, 'r') as f:
            for line in f:
                words.append(line.strip())

        sentences = []
        sentence = []
        for word in words:
            if word == symbol:
                sentences.append(sentence)
                sentence = []
            else:
                sentence.append(word)

        self.testSentences = sentences

    def initialProbCounting(self):
        '''Create matrix for the initial probabilities for each POS tag - P(S0)'''
        
        numSentences = len(self.hiddenStates)
        initProb = np.zeros((1, len(self.tags)))
        initStates = []

        # Get first column of hiddenStates matrix
        for sentence in self.hiddenStates:
            initStates.append(sentence[0])

        initCount = Counter(initStates)

        # Using initCount, create initProb array of initial probabilities for each POS tag
        for tag in initCount:
            i1 = self.tags.index(tag)
            initProb[0][i1] = initCount[tag]/numSentences

        # Set class variables for future use
        self.initialProb = initProb[0]

    def transitionProbCounting(self):
        '''Create matrix for transition probabilities between POS tags - P(Sk+1|Sk).
        Each starting POS tag has a probability distribution over the next POS tag.'''
        
        tagCount = dict()
        tranProb = np.zeros((len(self.tags), len(self.tags)))

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
                i1 = self.tags.index(tag1)
                i2 = self.tags.index(tag2)
                tranProb[i1][i2] = (count+1)/(tagCount[tag1]+len(self.tags))

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

            # Form observation probability matrix - (N x M)
            obsLoc = list(flat_obs_set).index(obs[0])
            tagLoc = self.tags.index(obs[1])
            if obs[1] in tagTotal:
                obsProb[tagLoc][obsLoc] =  tagCount[obs]/tagTotal[obs[1]]
            else:
                obsProb[tagLoc][obsLoc] = 0

        self.observationProb = obsProb
        self.observationSet = list(flat_obs_set)

def viterbi(hmm, E):
    '''Use Viterbi algorithm to determine the most likely sequence of POS tags for one sentence'''

    # Initialize matrices for Viterbi algorithm
    prob = np.zeros((len(E), len(hmm.tags)))
    prev = np.zeros((len(E), len(hmm.tags)))

    # Initialize first column of prob matrix and prev matrix with initial probabilities
    for i in range(len(hmm.tags)):
        # Check if word is in training data
        if E[0] in hmm.observationSet:
            e0 = hmm.observationSet.index(E[0])
            prob[0][i] = hmm.initialProb[i]*hmm.observationProb[i][e0]
            prev[0][i] = None
        else:
            prob[0][i], prev[0][i] = wordNotinTraining(hmm, prob, prev, E[0], i, 0)
    # For time steps 1 to length(E)-1, find each current state's most likely prior state, x
    for t in range(1, len(E)):
        for i in range(len(hmm.tags)):
            # Check if word is in training data
            if E[t] in hmm.observationSet:
                e = hmm.observationSet.index(E[t])
                # Find most likely prior state, x
                x = np.argmax(prob[t-1,:]*hmm.transitionProb[:,i]*hmm.observationProb[i][e])
                prob[t][i] = prob[t-1][x]*hmm.transitionProb[x][i]*hmm.observationProb[i][e]
                prev[t][i] = x
            else:
                prob[t][i], prev[t][i] = wordNotinTraining(hmm, prob, prev, E[t], i, t)

    return prob, prev

def wordNotinTraining(hmm, prob, prev, word, i, t):
    '''If word not in training data, calculate most likely POS tag for current word'''
    
    # Use overall POS distribution for tag index i to calculate most likely POS tag for current word
    e = np.argmax(hmm.observationProb[i, :])

    if t == 0:
        # Base case - first word in sentence
        prob[t][i] = hmm.initialProb[i]*hmm.observationProb[i][e]
        prev[t][i] = None
    
    else:
        # Recursive case
        x = np.argmax(prob[t-1,:]*hmm.transitionProb[:,i]*hmm.observationProb[i][e])
        prob[t][i] = prob[t-1][x]*hmm.transitionProb[x][i]*hmm.observationProb[i][e]
        prev[t][i] = x

    return prob[t][i], prev[t][i]

def trackSequence(hmm):
    '''Use Viterbi to track most likely sequence of POS tags for each sentence and print results to output file'''
    
    fullSequenceInds = []
    
    # Perform Viterbi algorithm on each sentence in test data
    for sentence in hmm.testSentences:
        prob, prev = viterbi(hmm, sentence)
        # Find index of most likely final POS state
        finalState = np.argmax(prob[-1,:])
        # Track indices of most likely sequence of POS states
        sequence = [finalState]
        for i in range(len(sentence)-1, 0, -1):
            # Get index of most likely prior POS for final POS and work backwards
            if prev[i][sequence[-1]] != None:
                sequence.append(int(prev[i][sequence[-1]]))
            else:
                break
        sequence.reverse()
        fullSequenceInds.append(sequence)
    # Print results to output file
    output_file(hmm, fullSequenceInds)

def measureAccuracy(hmm, trueLabels, symbol):
    '''Measure accuracy of predicted POS tags against true labels'''
    
    words = []
    posTags = []
    predictions = []

    with open(trueLabels, 'r') as f:
        for line in f:
            line = line.split(':')
            words.append(line[0].strip())
            posTags.append(line[1].strip())
    
    sentences = []
    sentence = []
    posTagSentence = []
    posTagSentences = []
    for i, word in enumerate(words):
        if word == symbol:
            sentences.append(sentence)
            sentence = []
            posTagSentences.append(posTagSentence)
            posTagSentence = []
        else:
            sentence.append(word)
            posTagSentence.append(posTags[i])
    
    # Flatten list of lists of POS tags
    posTagSentences = list(chain.from_iterable(posTagSentences))

    # Read predicted POS tags from output file
    with open(hmm.outputFile, 'r') as f:
        for line in f:
            line = line.split(':')
            predictions.append(line[1].strip())
    
    # Calculate accuracy
    correct = 0
    for i in range(len(predictions)):
        if predictions[i] == posTagSentences[i]:
            correct += 1
    accuracy = correct/len(predictions)
    print('Accuracy: ' + str(accuracy))
    
def output_file(hmm, sequence):
    '''Create output file with predicted POS tags for each word in test data'''
    
    # Create output file
    filename = hmm.outputFile
    sys.stdout = open(filename, 'w')

    # Output words and corresponding POS tags, seperated by colon using stdout
    for i in range(len(hmm.testSentences)):
        for j in range(len(hmm.testSentences[i])):
            sys.stdout.write(hmm.testSentences[i][j] + ' : ' + hmm.tags[sequence[i][j]])
            sys.stdout.write('\n')

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
    test_file = args.testfile
    output = args.outputfile

    # Initialize HMM class and parse training data
    hmm = HMM(training_list, test_file, output)
    hmm.parseTraining()
    hmm.sentenceSeperation('.')
    hmm.initialProbCounting()
    hmm.transitionProbCounting()
    hmm.observationProbCounting()
    trackSequence(hmm)
    measureAccuracy(hmm, 'training1.txt', '.')

    # Print transition probabilities to an output file
    # sys.stdout = open('transition_probabilities.txt', 'w')
    # for i in range(len(hmm.tags)):
    #     for j in range(len(hmm.tags)):
    #         sys.stdout.write(str(hmm.transitionProb[i][j]) + ' ')
    #     sys.stdout.write('\n')
    # sys.stdout.close()
    # sys.stdout = sys.__stdout__

    