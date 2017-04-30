########################################################################
# File name: plotData.py
# Author: Steven Calhoun
# Class: CS 6505
# Date: 3/31/2016
# Description: Plot data of simulation
########################################################################

# import plotly
import plotly.graph_objs as go
import plotly

import sys
import os
import time
import json
import random

def main():
  # Read data
  jsonData = loadData(sys.argv[1])

  # Create visualization
  visualizeData(jsonData)

def visualizeData(data):
  # Creat output directory
  if not os.path.exists("graphs"):
    os.makedirs("graphs")

  # Create random colors
  colors = createColors(len(data))

  # Create traces
  traces = createTraces(data, colors)

  # Plot
  plotTraces(traces)

def createTraces(data, colors):
  traces = []
  cValues = []
  for i, cVal in enumerate(data):
    cValues.append(int(cVal))

  cValues.sort()

  for i, cVal in enumerate(cValues):
    actualFPRates = []
    expectedFPRates = []
    nValues = []

    for nVal in data[str(cVal)]:
      # Keep up with all nvalues
      nValues.append(int(nVal))

      # Get expected and actual fp rates
      runResult = data[str(cVal)][nVal]
      actualFPRates.append(runResult["actualFPRate"])
      expectedFPRates.append(runResult["expectedFPRate"])

    # Sort nvalues
    nValues.sort()

    # Add traces
    traces.append(createExpectedTrace(cVal, nValues, expectedFPRates, colors[i]))
    traces.append(createActualTrace(cVal, nValues, actualFPRates, colors[i]))

  return traces

# Plot data
def plotTraces(data):
  layout = dict(title = 'Bloom Filter Simulation', xaxis = dict(title = 'n'), yaxis = dict(title = 'False Positive Rate'), )
  config = dict(data=data, layout=layout)

  fileName = time.strftime("%Y_%m_%d-%H_%M_%S")
  plotly.offline.plot(config, filename='graphs/' + fileName + '_plot.html')

# Create an actual trace (solid line)
def createActualTrace(cValue, nValues, actualFPRates, color):
  actualFpRateLine = go.Scatter(
      x = nValues,
      y = actualFPRates,
      mode = 'lines',
      name = 'c = ' + str(cValue) + ' - Actual',
      line = dict(color=color)
  )

  return actualFpRateLine

# Create an actual trace (dashed line)
def createExpectedTrace(cValue, nValues, expectedFPRates, color):
  expectedFpRateLine = go.Scatter(
      x = nValues,
      y = expectedFPRates,
      mode = 'lines',
      name = 'c = ' + str(cValue) + ' - Expected',
      line = dict(dash='dash', color=color)
  )

  return expectedFpRateLine

# Create random colors
def createColors(numberOfColors):
  colors = []

  for i in range(numberOfColors):
    r = lambda: random.randint(0,255)
    color = 'rgb(' + str(r()) + ',' + str(r()) + ',' + str(r()) +')'
    colors.append(color)

  return colors

# Load in json data
def loadData(fileName):
  with open(fileName, 'r') as fp:
    jsonData = json.load(fp)

  return jsonData

if __name__ == "__main__":
  main()
