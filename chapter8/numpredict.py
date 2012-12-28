import random
import math

def winePrice(rating, age):
    """Articifical wine price model.

    Keyword arguments:
        rating -- float, a wine's rating
        age    -- int, the current age of a wine

    """
    # peak age is older for "good" wine and almost immediate for "bad" wine
    peak_age = rating - 50
  
    # Calculate price based on rating
    price = rating / 2.0

    if age > peak_age:
        # Past its peak, goes bad in 10 years
        price = price * (5 - 0.5 * (age - peak_age))
    else:
        # Increases to 5x original value as it approaches its peak
        price = price * ( 5 * (age / peak_age))

    if price < 0:
        # Can't have negative prices!
        price = 0

    return price


def wineSet1(seed):
    """Artificial wine price data set.

    Keyword args:
        seed -- int, seed for random number generator

    """
    random.seed(seed)
    rows = []
    
    for i in range(200):
        # Create a random age and rating
        rating = random.random() * 50 + 50 # rating is U ~ [50, 100] 
        age    = random.random() * 50 # rating is U ~ [0, 50]

        # Get fundamental value
        price  = winePrice(rating,age)
    
        # Add some noise 
        price  *= (random.random() * 0.4 + 0.8) # U ~ [0.8, 1.2]

        # Add to the dataset
        rows.append({'input':(rating ,age), 'result':price})

    return rows

def euclidean(v1, v2):
    """Euclidean distance between two vectors.

    Keyword arguments:
        v1 -- vector of floats
        v2 -- vector of floats

    """
    d = 0.0
    for i in range(len(v1)):
        d += (v1[i] - v2[i])**2

    return math.sqrt(d)


def getDistances(data, vec1):
    """Computes the similarity between vec1 and every other vector in data.
    Currently, similarity is measured by the Euclidean distance between vectors
    of item attributes.
    
    Keyword arguments:
        data -- data set containing items and their attributes
        vec1 -- vector of attributes for item of interest

    """
    distancelist = []
  
    # Loop over every item in the dataset
    for i in range(len(data)):
        vec2 = data[i]['input']
    
        # Add the distance and the index
        distancelist.append((euclidean(vec1,vec2),i))
  
    # Sort (in-place!) by distance
    distancelist.sort()

    return distancelist

def knnEstimate(data, vec1, k=5):
    """Computes the k-NN for a item from data with a vector vec1 of attributes.

    Keyword arguments:
        data -- data set containing items and their attributes
        vec1 -- vector of attributes for item of interest
        k    -- number of nearest neighbors to average over

    """
    # Get sorted distances
    dlist = getDistances(data, vec1)
    avg   = 0.0
  
    # Take the average of the top k results
    for i in range(k):
        idx = dlist[i][1]
        avg += data[idx]['result']
    avg = avg / float(k)

    return avg

def inverseWeight(dist, num=1.0, const=0.1):
    """ Weighting function for neighbors.

    A neighbor is weighted inversely proportional to its distance from the item
    of interest.

    Keyword arguments:
        dist  -- float, distance between an item and the item of interest
        num   -- float, parameter to tweak
        const -- float, need to add a small amount to each distance to prevent
                 some items receiveing extremely large weights.

    """
    return num / (dist + const)

def subtractWeight(dist, const=1.0):
    """ Weighting function for neighbors.

    The distance between a neighbor and the item of interest is subtracted
    from a constant.

    Keyword arguments:
        dist  -- float, distance between an item and the item of interest
        const -- float, constant from which the distances between items
                 are subtracted.

    """
    if dist > const: 
        return 0
    else: 
        return const - dist

def gaussianWeight(dist, sigma=1.0):
    """ Weighting function for neighbors.

    A neighbor is weighted using a Gaussian function.

    Keyword arguments:
        dist  -- float, distance between an item and the item of interest
        sigma -- float, controls how fast the weights decline with distance.
                 Neighbor weights will decline more quickly for low values
                 of sigma.

    """
    return math.e**(-dist**2 / (2.0 * sigma**2))

def knnWeightedEstimate(data, vec1, k=5, weightf=gaussianWeight):
    """Computes the weighted k-NN for a item from data with a vector vec1 of
    attributes.

    Keyword arguments:
        data    -- data set containing items and their attributes
        vec1    -- vector of attributes for item of interest
        k       -- number of nearest neighbors to average over
        weightf -- weighting function
        
    """
    # Get distances
    dlist=getDistances(data, vec1)
    avg=0.0
    totalweight=0.0
  
    # Get weighted average
    for i in range(k):
        dist        = dlist[i][0]
        idx         = dlist[i][1]
        weight      = weightf(dist)
        avg         += weight * data[idx]['result']
        totalweight += weight
        
    # catch degenerate case!
    if totalweight==0:
        return 0
    
    # compute the weighted average
    avg = avg / totalweight

    return avg

def divideData(data, test=0.05):
    """ Divides data into training and testing sets.

    Keyword arguments:
        data -- data set containing items and their attributes
        test -- fraction of data to be included in the test set

    """
    trainset = []
    testset  = []

    # divide data randomly
    for row in data:
        if random.random() < test:
            testset.append(row)
        else:
            trainset.append(row)

    return trainset, testset

def testAlgorithm(algf, trainset, testset):
    """ Tests a given algorithm by predicting a values in testset by applying
    the algf to the data in trainset.  Function returns the mean-square error
    (MSE) of algf.

    Keyword arguments:
        algf     -- algorithm/function to be evaluated
        trainset -- training data
        testset  -- testing data

    """
    error = 0.0

    # loop over each row in testset  
    for row in testset:
        # predict the result using trainset
        guess = algf(trainset, row['input'])
        # compute the sum of squared errors
        error += (row['result'] - guess)**2

    # compute the MSE
    MSE = error / len(testset)

    return MSE

def crossValidate(algf, data, trials=100, test=0.05):
    """Performs cross-validation of an algorithm on a data set. Specifically,
    function returns the average MSE of an algorithm over a number of trials.

    Keyword arguments:
        algf   -- algorithm/function to be evaluated
        data   -- data set containing items and their attributes
        trials -- number of times to call testAlgorithm
        test   -- fraction of data to be included in the test set

    """
    error = 0.0
    for i in range(trials):
        trainset, testset = divideData(data, test)
        error += testAlgorithm(algf, trainset, testset)
    return error / trials

def wineSet2(seed):
    """Artificial wine price data set. Adds two variables: aisle, which has no
    impact on price, and bottlesize which does impact the price of a bottle but
    has a very different scale than rating and age variables.

    Keyword args:
        seed -- int, seed for random number generator

    """
    
    rows=[]

    # generate the various attributes that determine bottle price
    for i in range(200):
        rating     = random.random() * 50 + 50
        age        = random.random() * 50 
        aisle      = float(random.randint(1, 20))
        bottlesize = [375.0, 750.0, 1500.0][random.randint(0, 2)]
        price      = winePrice(rating, age)
        price      *= (bottlesize / 750.0)
        price      *= (random.random() * 0.2 + 0.9) # U ~ [0.9, 1.1]
        rows.append({'input':(rating, age, aisle, bottlesize), 'result':price})

    return rows

def rescale(data,scale):
    """Re-scales data attributes.

    Keywords arguments:
        data  -- data set containing items and their attributes
        scale -- vector of floats which are used to rescale variables (should
                 have same length as number of attributes).

    """
    scaleddata = []
    for row in data:
        scaled = [scale[i] * row['input'][i] for i in range(len(scale))]
        scaleddata.append({'input':scaled,'result':row['result']})
    return scaleddata

def createCostFunction(algf, data):
    """Wrapper function used to optimize crossValidate by choosing the scale.

    Keyword arguments:
        algf   -- algorithm/function to be evaluated
        data   -- data set containing items and their attributes

    """
    def costf(scale):
        """Converts crossValidate into a cost function. Want to choose values
        for scale in order to minimize average mean-square prediction error.

        Keyword arguments:
            scale -- vector of floats which are used to rescale variables (should
                     have same length as number of attributes).

        """
        sdata=rescale(data, scale)
        return crossValidate(algf,sdata,trials=10)
    
    return costf

# Domain over which to search for optimal weights (assumes that weights cannot exceed 20!)
weightdomain = [(0, 20)] * 4

def wineSet3(seed):
    """Artificial wine price data set. Reverts to wineSet1 variables, then
    captures the idea that wine is purchased by two different groups of people:
    those who purchase wine at liquor stores and those that purchase wine at
    discount stores. 

    Keyword args:
        seed -- int, seed for random number generator

    """
    rows = wineSet1(seed)

    for row in rows:
        # Wine was bought at a discount store (this variable is unobserved!)
        if random.random() < 0.5:
            row['result'] *= 0.6
    return rows

def probguess(data, vec1, low, high, k=5, weightf=gaussian):
    """Function returns a value between 0 and 1 representing the probability
    that the price of an item with attributes vec1 lies between low and high.

    Keyword arugments:
        data    -- data set containing items and their attributes
        vec1    -- vector of attributes describing the item of interest
        low     -- lower bound on the price range
        high    -- upper bound on the price range
        k       -- number of neighbors to use in the calculation
        weightf -- the weighting function to apply to the raw distance measures

    """
    dlist   = getDistances(data, vec1)
    nweight = 0.0
    tweight = 0.0

    for i in range(k):
        dist   = dlist[i][0]
        idx    = dlist[i][1]
        weight = weightf(dist)
        v      = data[idx]['result']
    
        # Is this point in the range?
        if v >= low and v <= high:
            nweight += weight

        tweight += weight

    # Catch a degenerate case (don't think this could happen with most weightf)
    if tweight == 0:
        return 0
  
  # The probability is the weights in the range divided by all the weights
  return nweight / tweight

"""
from pylab import *

def cumulativegraph(data,vec1,high,k=5,weightf=gaussian):
  t1=arange(0.0,high,0.1)
  cprob=array([probguess(data,vec1,0,v,k,weightf) for v in t1])
  plot(t1,cprob)
  show()


def probabilitygraph(data,vec1,high,k=5,weightf=gaussian,ss=5.0):
  # Make a range for the prices
  t1=arange(0.0,high,0.1)
  
  # Get the probabilities for the entire range
  probs=[probguess(data,vec1,v,v+0.1,k,weightf) for v in t1]
  
  # Smooth them by adding the gaussian of the nearby probabilites
  smoothed=[]
  for i in range(len(probs)):
    sv=0.0
    for j in range(0,len(probs)):
      dist=abs(i-j)*0.1
      weight=gaussian(dist,sigma=ss)
      sv+=weight*probs[j]
    smoothed.append(sv)
  smoothed=array(smoothed)
    
  plot(t1,smoothed)
  show()
"""
