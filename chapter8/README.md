# Chapter 8: Building Price Models

## Contents:

1. **numpredict.py:** Script demonstrates key ideas behind several kNN algorithms using a synthetic data set of wine prices.
2. **ebaypredict.py:** Script used to extract data from the eBay API.  
3. **optimization.y:** Various optimization routines from Chapter 5 used to find optimal parameters for kNN algorithms.

## Notes:

* There are a lot of discrepancies in this chapter between the .pdf version and the print version of *Programming Collective    Intelligence*.  I did the best I could to replicate the results from the text, but was not always successful.  Toby really should be setting the seed values for the random number generator!
* I had to completely re-write **ebaypredict.py** as the eBay API had changed significantly since *Programming Collective Intelligence* was published. TODO: implement GetBidderList and GetSellerList calls to the eBay Trading API.
* Need to re-visit **optimization.py** at some point (the optimization routines are not able to replicate the results from the text). TODO: Implement genetic algorithm routine.
