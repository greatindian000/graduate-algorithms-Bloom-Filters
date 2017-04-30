########################################################################
# File name: BloomDriver.py
# Author: Steven Calhoun
# Class: CS 6505
# Date: 3/15/2016
# Description: Driver for the project
########################################################################

################################################################################
# Python libraries
################################################################################
# Used for printing how long each step takes
import time

# Used for random word generation and random hashing
import random

# Conatinas list of ascii lower/upper letters and digits, helps with random word generation
import string

# Various math functions like ceiling or constants like e
import math

# System and os commands
import sys
import os

# Helps saving results of simulation to json
import json

################################################################################
# Constants
################################################################################
HASH_RANDOM_SIZE = 1000000000
UNIVERSE_STRING_CHAR_COUNT = 3
UNIVERSE_SIZE = (len(string.ascii_uppercase) + len(string.ascii_lowercase) + len(string.digits))**UNIVERSE_STRING_CHAR_COUNT
SIMULATION_QUERY_COUNT = 200000
C_VALUES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 50]
N_VALUES = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

################################################################################
# main function
################################################################################
def main():
  tests = createTests(C_VALUES, N_VALUES)
  testResults = {}
  for cVal in C_VALUES:
    testResults[cVal] = {}
  totalStart = time.time()

  largestSubsetSize = 0
  for i, test in enumerate(tests):
    m = test["n"]/test["c"]
    if m > largestSubsetSize:
      largestSubsetSize = m

  largestSubset = Subset(largestSubsetSize)

  for i, test in enumerate(tests):
    startTime = time.time()
    print
    print "************************************************************"
    print "Running test: " + str(i+1) + " of " + str(len(tests))

    # Create the bloom filter then run on universe and subset
    bloom = BloomFilter(test["n"], test['c'])
    bloom.insertSubset(largestSubset.subset[:bloom.m])
    results = bloom.simulate(SIMULATION_QUERY_COUNT, largestSubset.subset[:bloom.m])

    testResults[test["c"]][test["n"]] = {
      "n": test["n"],
      "c": test["c"],
      "m": bloom.m,
      "k": bloom.k,
      "universeSize": UNIVERSE_SIZE,
      "expectedFPRate": results["expectedFPRate"],
      "negativeCount": results["negativeCount"],
      "positiveCount": results["positiveCount"],
      "falseNegatives": results["falseNegatives"],
      "falsePositives": results["falsePositives"],
      "actualFPRate": results["actualFPRate"]
    }

    print
    print "Elapsed time: " + str(time.time() - startTime)
    print

  # Write to file
  if not os.path.exists("results"):
    os.makedirs("results")

  fileName = time.strftime("%Y_%m_%d-%H_%M_%S") + ".json"
  saveToJson(testResults, "results/" + fileName)

  print "Total elapsed time: " + str(time.time() - totalStart)

################################################################################
# Hash Function class
################################################################################
class HashFunction():
  # Create function from size and seed
  def __init__(self, size):
    self.size = size
    self.seed = random.randint(0, HASH_RANDOM_SIZE)
    self.start = random.randint(0, HASH_RANDOM_SIZE)

  # Compute using the function
  def compute(self, string):
    # Recreation of an fnv hashing function
    result = self.start
    for i, char in enumerate(string):
      result = (result * self.seed) ^ ord(char)

    return int(result%self.size)

################################################################################
# Subset class
################################################################################
class Subset():
  def __init__(self, size):
    self.size = size
    self.generate()

  def generate(self):
    self.subset = []

    newString = ''
    for i in range(0, self.size):
      printOver("Generating Subset: " + str(int(float(i)/float(self.size)*100)) + "%")

      word = generateWord()
      while word in self.subset:
        word = generateWord()

      self.subset.append(word)
    printOver(" "*24)

################################################################################
# Bloom Filter class
################################################################################
class BloomFilter:
  # Initializer
  def __init__(self, n, c):
    # Size of universe and subset
    self.n = n
    self.c = c
    self.m = self.n/self.c

    # Hash array
    self.H = [0] * self.n

    # Calculation of k (number of hash functions)
    self.k = int(math.ceil(self.c*math.log(2)))

    self.expectedFPRate = (1-math.e**((-self.k)/self.c))**self.k

    # Create all the hashing functions
    self.hashingFunctions = []
    for i in range(0, self.k):
      self.hashingFunctions.append(HashFunction(self.n))

  # Insert a new value
  def insert(self, x):
    # Run each hash function
    for i in range(0, self.k):
      self.H[self.hashingFunctions[i].compute(x)] = 1

  # Query for a value
  def query(self, y):
    # Query with each hashing function, only true if all are 1
    for i in range(0, self.k):
      if self.H[self.hashingFunctions[i].compute(y)] == 0:
        return False
    return True

  def insertSubset(self, subset):
    for i, value in enumerate(subset):
      printOver("Inserting Values: " + str(int(float(i)/float(len(subset))*100)) + "%")

      self.insert(value)
    printOver(" "*24)

  def simulate(self, queryCount, subset):
    negativeCount = 0
    positiveCount = 0
    falsePositives = 0
    falseNegatives = 0

    # Query each value and keep up with the results
    for i in range(queryCount):
      printOver("Querying Values: " + str(int(float(i)/float(queryCount)*100)) + "%")
      word = generateWord()

      result = self.query(word)
      if result == False:
        negativeCount += 1
        if word in subset:
          falseNegatives += 1
      elif result == True:
        positiveCount += 1
        if word not in subset:
          falsePositives += 1

    printOver(" "*24)

    actualFPRate = float(falsePositives)/float(queryCount)

    # Print the results
    print
    print "Bloom info"
    print self

    print
    print "Query Info"
    print "Universe size: " + str(UNIVERSE_SIZE)
    print "Negative count: " + str(negativeCount)
    print "Positive count: " + str(positiveCount)
    print "Correct positives: " + str(positiveCount-falsePositives)
    print "False negatives: " + str(falseNegatives)
    print "False positives: " + str(falsePositives)
    print "Actual FP Rate: " + str(actualFPRate)

    # Return results
    results = {
      "negativeCount": negativeCount,
      "positiveCount": positiveCount,
      "falseNegatives": falseNegatives,
      "falsePositives": falsePositives,
      "actualFPRate": actualFPRate,
      "expectedFPRate": self.expectedFPRate
    }

    return results

  # Print the bloom filter
  def __str__(self):
    returnStr = ""
    returnStr += "n: " + str(self.n) + "\n"
    returnStr += "m: " + str(self.m) + "\n"
    returnStr += "c: " + str(self.c) + "\n"
    returnStr += "k: " + str(self.k) + "\n"
    returnStr += "Expected FP Rate: " + str(self.expectedFPRate)

    return returnStr

################################################################################
# Bloom Filter class
################################################################################
# Print over a terminal line
def printOver(line):
  sys.stdout.write("\r%s" % line)
  sys.stdout.flush()

# Save to json file
def saveToJson(data, filename):
  with open(filename, 'w+') as jsonFile:
    json.dump(data, jsonFile, sort_keys=True, indent=2)

# Generate random word
def generateWord():
  newString = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(UNIVERSE_STRING_CHAR_COUNT))
  return newString

def createTests(cValues, nValues):
  tests = []
  for cVal in cValues:
    for nVal in nValues:
      test = {}
      test['c'] = cVal
      test['n'] = nVal
      tests.append(test)
  return tests

if __name__ == "__main__":
  main()
