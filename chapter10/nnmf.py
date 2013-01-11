""" The Non-negative matrix factorization algorithm tries to reconstruct 
the articles matrix as closely as possible by calculating the best 
features and weight matrices. 

The features matrix: features matrix has a row for each feature and a 
column for each word. Thus each feature is effectivly a list of word
weights. The ij-entry in the features matrix indicates how important 
that word is for a given feature. Each feature should represent a 
theme tha emerged from a set of articles. Since each feature is a 
combination of different words, it should be clear that reconstructing
the articles matrix is a matter of combining rows from the features 
matrix in different amounts (i.e., weights).

The weights matrix: the weights matrix maps the features matrix to the
articles matrix. Each row is an article, and each column is a feature.
The ij-entry indicates how strongly a given feature is present in each
article.

While in principle, the NNMF algorithm can reconstruct the articles 
matrix exactly, in practice this is rarely possible. The idea is to 
try and reproduce/reconstruct the articles matrix from the features 
matrix as closely as possible by choosing appropriate weights for the 
features.

"""

import numpy as np

def costFunction(A, B):
    """Need a way to measure just how close the result is. This function 
    computes the sum of squared differences between two matrices, A and 
    B, which is used as the measure of cost.

    """
    return np.sum((A - B)**2)

def factorize(v, pc=10, iter=50, seed=42):
    """The update rules generates four new update matrices.  In these 
    descriptions, the original articles matrix is referred to as the 
    data matrix:
    
    - hn: The transposed weight matrix multiplied by the data matrix.
    - hd: The transposed weight matrix multiplied by itself, multiplied
          by the features matrix.
    - wn: The data matrix multiplied by the transposed features matrix.
    - wd: The weights matrix multiplied by the features matrix 
          multiplied by the transposed features matrix.

    For detailed derivation of the multiplicative update rules see:

        http://hebb.mit.edu/people/seung/papers/nmfconverge.pdf
    
    Function requires user to specify, pc, the number of features you 
    want to find.  In some cases, you'll know how many features you 
    expect to find in the data, but in other cases, you'll have no 
    idea how many to specify. Generally no way to automatically 
    determine the correct number of components, but experimentation 
    can help find the appropriate range.
    
    """
    ic = np.shape(v)[0]
    fc = np.shape(v)[1]

    # Initialize the weight and feature matrices with random values
    np.random.seed(seed)
    w = np.random.random((ic, pc))
    h = np.random.random((pc, fc))

    # Perform operation a maximum of iter times
    for i in range(iter):
        wh = w.dot(h)
    
        # Calculate the current difference
        cost = costFunction(v, wh)

        # keep trak of progess
        if i%10 == 0: 
            print cost
    
        # Terminate if the matrix has been fully factorized
        if cost == 0: 
            break
    
        # Update features matrix
        hn = (w.T).dot(v)
        hd = ((w.T).dot(w)).dot(h) + 0.000000001 
  
        h  = (h * hn) / hd

        # Update weights matrix
        wn = v.dot(h.T)
        wd = w.dot(h.dot(h.T)) + 0.000000001

        w  = (w * wn) / wd   
    
    return w, h
