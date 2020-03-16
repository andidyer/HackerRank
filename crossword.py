import math
import os
import random
import re
import sys
import time

"""A program to solve a crossword puzzle on a grid.
    See problem:
    https://www.hackerrank.com/challenges/crossword-puzzle/problem.

    This program uses recursion and backtracing to find the solution.

    TODO:
    1. Customise input to accept txt files with customisable puzzles.
    2. Add verbose
    """

#Auxiliary functions here
def getSlots(crossword):
    """Function to get all slots, vertical and horizontal.
        TODO:
        1. Find a more efficient way of doing this, without repeating myself."""
    #Horizontal first
    span = []
    for i,row in enumerate(crossword):
        for j,col in enumerate(row):
            cell = crossword[i][j]
            if cell == '-':
                span += [(i,j)]
            else:
                if len(span)>1:
                    yield span
                span = []
        if len(span)>1:
            yield span
        span = []

    #Same again vertically
    for i,col in enumerate(crossword[0]):
        for j,row in enumerate(crossword):
            cell = crossword[j][i]
            if cell == '-':
                span += [(j,i)]
            else:
                if len(span)>1:
                    yield span
                span = []
        if len(span)>1:
            yield span
        span = []

class Utils:
    @staticmethod
    def intersect(l0,l1):
        """Quick set intersection on two lists"""
        A = set(l0)
        B = set(l1)
        I = set.intersection(A,B)
        return list(I)
    
    @staticmethod
    def findConnection(Slot_a, Slot_b, modify=True):
        """Find connections between two Slot objects.
            Input:
            Slot_A, SlotB:  Two Slot objects
            Output:
            I:  Intersecting cell
            Modify:
            if modify==True, update the connections attributes of the Slot objects
            TODO:
            1. Should this be an instance method of the Slot object?"""
        A,O = set(Slot_a.locs),set(Slot_b.locs)
        I = list(set.intersection(A,O))
        if I == []:
            return
        else:
            I = I[0]
        if modify:
            Slot_a.connections.append((Slot_b, I))
            Slot_b.connections.append((Slot_a, I))
        return I

class Slot:
    def __init__(self, locs):
        """Slot object.
        Input:
        locs: the list of cells that the slot covers"""
        self.length = len(locs)
        self.locs = locs
        self.connections = []
        self.c2i = {loc:i for (i,loc) in enumerate(locs)}
        self.form = '-' * self.length
        self.possible_words = []

    def checkWordLength(self, word, modify=True):
        """Checks if a word is compatible (correct length)"""
        possible = len(word) == self.length
        if not possible:
            return False
        if modify:
            self.possible_words.append(word)
        return True

    def slotMatch(self, neighbour, loc, word):
        """Checks if a slot and a candidate word are compatible.
            Meant for a neighbouring slot"""
        selfInd = self.c2i[loc]
        nbrInd = neighbour.c2i[loc]
        
        A = word[selfInd]
        B = neighbour.form[nbrInd]
        
        if A == B:
            return True
        elif B == '-':
            return True
        else:
            return False

    def tryWord(self, word):
        """See if a word fits in this slot."""
        for cxn, loc in self.connections:
            if self.slotMatch(cxn,loc,word) == False:
                return False
        return True
        
    def fill(self, word):
        """fill word hypothesis"""
        self.form = word

    def revert(self):
        """revert word hypothesis"""
        self.form = '-' * self.length

    def fillCrossword(self, grid):
        """Takes mutable copy of crossword and fills
            with what information the slot object contains"""
        for (row,col), i in self.c2i.items():
            grid[row][col] = self.form[i]
        

def solve(Slot_Q, Word_Q, root=True):
    """Recursive backtracing function for solving the slots
        Input:
        slots: a list of Slot objects
        words: a list of words

        Output:
        None if failed; else the completed slots

        TODO:
        1. Try to obviate one of the success case return statements
        """
    if len(Slot_Q) == 0:
        #print('Solution found')
        return True

    current = Slot_Q[0]

    candidates = Utils.intersect(current.possible_words, Word_Q)
    result = False
    while candidates != []:
        cand = candidates.pop(0)
        if current.tryWord(cand) == True:
            current.fill(cand)

            #New queues to pass to next recursion level
            Slot_Q_prime = Slot_Q[:]
            Word_Q_prime = Word_Q[:]
            Slot_Q_prime.remove(current)
            Word_Q_prime.remove(cand)

            #Recursion
            result = solve(Slot_Q_prime, Word_Q_prime, root=False)
            if result == True:
                #print('solution found')
                return True
            
    #Has reached a dead end
    #Backtrace
    if result == False:
        #print('dead end')
        current.revert()


# Complete the crosswordPuzzle function below.
def crosswordPuzzle(crossword, words):
    """Outer function for solving the crossword.
        Input:
        crossword:  crossword, in the form of a list of strings in the correct format
        words:      correct words
        Output:
        completed crossword (not the same object ss the original crossword)"""

    #Split into 2D list of strings for convenience
    crossword = list(list(row) for row in crossword)

    #Get slots
    slots = []
    for s in getSlots(crossword):
        slots += [Slot(s)]

    #Find connections between slots
    for i,s0 in enumerate(slots):
        for j,s1 in enumerate(slots[i+1:]):
            Utils.findConnection(s0,s1)

    #Find possible words per slot
    for w in words:
        for s in slots:
            s.checkWordLength(w)

    #Sort slots by number of possible words
    #Intuitively, it should require less backtracing to handle the singletons (or fewtons) first
    slots.sort(key = lambda x: len(x.possible_words))

    #Make shallow copies that can be modified and passed through the recursive functino
    SQ = slots[:]
    WQ = words[:]

    #solve function to start here
    solve(SQ,WQ)

    #Solve the crossword one slot at a time
    for s in slots:
        s.fillCrossword(crossword)

    #Rejoin into original list of strings format
    crossword = [''.join(row) for row in crossword]
    return crossword
    

if __name__ == '__main__':
    crossword = []

    grid = ['+-++++++++',
            '+-++++++++',
            '+-------++',
            '+-++++++++',
            '+-++++++++',
            '+------+++',
            '+-+++-++++',
            '+++++-++++',
            '+++++-++++',
            '++++++++++']
    words = 'AGRA;NORWAY;ENGLAND;GWALIOR'

    words = words.split(';')

    for line in grid:
        crossword.append(line)

    #Get the completed grid
    result = crosswordPuzzle(crossword, words)

    #Print it
    print('\n'.join(result))
    print('\n')
