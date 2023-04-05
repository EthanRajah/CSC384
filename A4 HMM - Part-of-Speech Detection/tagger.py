import os
import sys
import argparse
from collections import Counter
from collections import defaultdict
from itertools import chain
import numpy as np
import time

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
        self.obsPos = []
        self.tagTotal = dict()
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
        obsPos = []

        for training_file in self.trainingList:
            # Open training file, for each line split on colon, appending first element to words list and second element to posTags list
            with open(training_file, 'r') as f:
                for line in f:
                    line = line.split(':')
                    word = line[0].strip()
                    pos = line[1].strip()
                    
                    if word != '' and pos != '':
                        obsPos.append((word, pos))
                        words.append(word)
                        posTags.append(pos)

                    if word not in self.observationSet and word != '':
                        self.observationSet.append(word)

                    if pos not in self.tagTotal and pos != '':
                        self.tagTotal[pos] = 1
                    elif pos != '':
                        self.tagTotal[pos] += 1

        self.observations = words
        self.hiddenStates = posTags
        self.obsPos = obsPos

        # Create dictionary of words and their index in observationSet
        self.observationDict = dict()
        for i in range(len(self.observationSet)):
            self.observationDict[self.observationSet[i]] = i
        
        # Create dictionary of POS tags and their index in tags
        self.tagDict = dict()
        for i in range(len(self.tags)):
            self.tagDict[self.tags[i]] = i

    def sentenceSeperation(self, symbols):
        '''Create matrices of words and POS tags using symbol of choice (i.e. periods, colons etc) to split sentences'''
        
        sentences = []
        sentence = []
        posTagSentence = []
        posTagSentences = []
        # Split observations and hiddenStates into sentences by symbols specified, putting symbols in their own sentence
        for i in range(len(self.observations)):
            if self.observations[i] in symbols:
                sentence.append(self.observations[i])
                sentences.append(sentence)
                sentence = []
                posTagSentence.append(self.hiddenStates[i])
                posTagSentences.append(posTagSentence)
                posTagSentence = []
            else:
                sentence.append(self.observations[i])
                posTagSentence.append(self.hiddenStates[i])
        
        # Overwrite observations array with sentences array and hiddenStates array with posTagSentences array
        self.observations = sentences
        self.hiddenStates = posTagSentences

        # Split test data into sentences
        self.sentenceSeperationTest(symbols)

    def sentenceSeperationTest(self, symbols):
        '''Split test data into sentences using symbol of choice (i.e. periods, colons etc)'''

        words = []
        with open(self.testFile, 'r') as f:
            for line in f:
                if line.strip() != '':
                    words.append(line.strip())

        sentences = []
        sentence = []
        # Split test words into sentences by symbols specified, putting symbols in their own sentence
        for word in words:
            if word in symbols:
                sentence.append(word)
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
            i1 = self.tagDict[tag]
            initProb[0][i1] = initCount[tag]/numSentences

        # Set class variables for future use
        self.initialProb = initProb[0]

    def transitionProbCounting(self):
        '''Create matrix for transition probabilities between POS tags - P(Sk+1|Sk).
        Each starting POS tag has a probability distribution over the next POS tag.'''
        
        tagCount = dict()
        tranProb = np.ones((len(self.tags), len(self.tags)))

        for sentence in self.hiddenStates:
            for i in range(1,len(sentence)):
                if sentence[i-1] not in tagCount:
                    tagCount[sentence[i-1]] = 1
                else:
                    tagCount[sentence[i-1]] += 1
                
                i1 = self.tagDict[sentence[i-1]]
                i2 = self.tagDict[sentence[i]]
                tranProb[i1][i2] += 1
        
        for tag in self.tags:
            ind1 = self.tagDict[tag]
            if tag in tagCount:
                tranProb[ind1] = tranProb[ind1] / (tagCount[tag] + len(self.tags))
            else:
                tranProb[ind1] = tranProb[ind1] / (len(self.tags))

        self.transitionProb = tranProb

    def observationProbCounting(self):
        '''Create matrix for observation probabilities of word observation, given POS tag - P(ek|Sk).
        Each POS tag has a probability distribution over observed words.'''
        
        tagCount = dict()
        obsProb = np.zeros((len(self.tags), (len(self.observationSet))))

        # Get count of word given POS tag using obs_pos list and tagCount dictionary
        for obs in self.obsPos:
            if obs in tagCount:
                tagCount[obs] += 1
            elif obs not in tagCount:
                tagCount[obs] = 1

            # Form observation probability matrix - (N x M)
            obsLoc = self.observationDict[obs[0]]
            tagLoc = self.tagDict[obs[1]]
            if obs[1] in self.tagTotal:
                obsProb[tagLoc][obsLoc] =  tagCount[obs]/self.tagTotal[obs[1]]
            else:
                obsProb[tagLoc][obsLoc] = 0

        self.observationProb = obsProb

def viterbi(hmm, E):
    '''Use Viterbi algorithm to determine the most likely sequence of POS tags for one sentence'''

    # Initialize matrices for Viterbi algorithm
    prob = np.zeros((len(E), len(hmm.tags)))
    prev = np.zeros((len(E), len(hmm.tags)))

    # Initialize first column of prob matrix and prev matrix with initial probabilities
    for i in range(len(hmm.tags)):
        # Check if word is in training data
        if E[0] in hmm.observationSet:
            e0 = hmm.observationDict[E[0]]
            prob[0][i] = hmm.initialProb[i]*hmm.observationProb[i][e0]
            prev[0][i] = None
        else:
            prob[0][i] = hmm.initialProb[i]
            prev[0][i] = None
    # For time steps 1 to length(E)-1, find each current state's most likely prior state, x
    for t in range(1, len(E)):
        for i in range(len(hmm.tags)):
            # Check if word is in training data
            if E[t] in hmm.observationSet:
                e = hmm.observationDict[E[t]]
                # Find most likely prior state, x
                x = np.argmax(prob[t-1,:]*hmm.transitionProb[:,i]*hmm.observationProb[i][e])
                prob[t][i] = prob[t-1][x]*hmm.transitionProb[x][i]*hmm.observationProb[i][e]
                prev[t][i] = x
            else:
                x = np.argmax(prob[t-1,:]*hmm.transitionProb[:,i])
                prob[t][i] = prob[t-1][x]*hmm.transitionProb[x][i]
                prev[t][i] = x

    return prob, prev

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

def measureAccuracy(hmm, trueLabels, symbols):
    '''Measure accuracy of predicted POS tags against true labels'''
    
    words = []
    posTags = []
    predictions = []

    with open(trueLabels, 'r') as f:
        for line in f:
            line = line.split(':')
            if line[0].strip() != '' and line[1].strip() != '':
                words.append(line[0].strip())
                posTags.append(line[1].strip())
    
    # Read predicted POS tags from output file
    with open(hmm.outputFile, 'r') as f:
        for line in f:
            line = line.split(':')
            if line[0].strip() != '' and line[1].strip() != '':
                predictions.append(line[1].strip())
    
    # Calculate accuracy
    correct = 0
    for i in range(len(predictions)):
        if predictions[i] == posTags[i]:
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
    # t0 = time.time()
    hmm = HMM(training_list, test_file, output)
    hmm.parseTraining()
    hmm.sentenceSeperation(['.', '?', '!'])
    hmm.initialProbCounting()
    hmm.transitionProbCounting()
    hmm.observationProbCounting()
    trackSequence(hmm)
    # measureAccuracy(hmm, 'true_labels.txt', ['.' , '?', '!'])
    # t1 = time.time()
    # print('Time: ' + str(t1-t0))
    
    