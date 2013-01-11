import numpy as np
import feedparser
import re

feedlist=['http://feeds.reuters.com/reuters/businessNews',
          'http://feeds.reuters.com/reuters/companyNews',
          'http://feeds.reuters.com/news/wealth',
          'http://feeds.reuters.com/reuters/bankruptcyNews',
          'http://feeds.reuters.com/reuters/bondsNews',
          'http://feeds.reuters.com/news/deals',
          'http://feeds.reuters.com/news/economy',
          'http://feeds.reuters.com/reuters/financialServicesrealEstateNews',
          'http://feeds.reuters.com/reuters/hotStocksNews',
          'http://feeds.reuters.com/reuters/newIssuesNews',
          'http://feeds.reuters.com/reuters/mergersNews',
          'http://feeds.reuters.com/reuters/privateequityNews',
          'http://feeds.reuters.com/reuters/governmentfilingsNews',
          'http://feeds.reuters.com/reuters/smallBusinessNews',
          'http://feeds.reuters.com/reuters/summitNews',
          'http://feeds.reuters.com/reuters/USdollarreportNews',
          'http://feeds.reuters.com/news/usmarkets',
          'http://feeds.reuters.com/reuters/basicmaterialsNews',
          'http://feeds.reuters.com/reuters/cyclicalconsumergoodsNews',
          'http://feeds.reuters.com/reuters/USenergyNews',
          'http://feeds.reuters.com/reuters/environment',
          'http://feeds.reuters.com/reuters/financialsNews',
          'http://feeds.reuters.com/reuters/UShealthcareNews',
          'http://feeds.reuters.com/reuters/industrialsNews',
          'http://feeds.reuters.com/reuters/USmediaDiversifiedNews',
          'http://feeds.reuters.com/reuters/noncyclicalconsumergoodsNews',
          'http://feeds.reuters.com/reuters/technologysectorNews',
          'http://feeds.reuters.com/reuters/UStechnologyTelcomNews',
          'http://feeds.reuters.com/reuters/telecomsectorNews',
          'http://feeds.reuters.com/reuters/utilitiesNews']

def stripHTML(article):
    """Strips HTML and/or Markup tags from a given article. Function 
    returns a string containing only the text elements of the original
    article.

    """
    # initialize an empty string which will be filled with text
    raw_text = ''
    # initialize a marker
    s = 0

    for char in article:
        # mark start of HTML tag
        if char == '<': 
            s = 1
        # mark end of HTML tag and add white space to raw_text
        elif char == '>':
            s = 0
            raw_text += ' '
        elif s == 0: 
            raw_text += char
    return raw_text


def separateWords(text, min_length=3):
    """Extracts separate words from s string of text. Function returns 
    a list of individual words greater than some minimum word length.

    """
    # split the text into separate words 
    split_text = re.compile('\\W*')
    
    return [s.lower() for s in split_text.split(text) if len(s) > min_length]

def get_articleWords(min_length=3):
    """Function loops over all the news feeds, parses them with 
    feedparser, strips out the HTML, and extracts the individual words
    using the functions defined above. 

    It keeps tracks of how many times each word is used overall, as 
    well as how many times it is used in each individual article.

    The function defines three variables:
        - allwords: keeps a count of word usage across all the 
                    different articles.
        - articlewords: the counts of the words in each article. 
        - articletitles: is a list of the titles of the articles.
        
    """
    # define important variables
    allWords      = {}
    articleWords  = []
    articleTitles = []

    # define a counter
    ec = 0

    # Loop over every feed
    for feed in feedlist:
        tmp_feed = feedparser.parse(feed)
    
        # Loop over every article
        for article in tmp_feed.entries:
            # Ignore identical articles
            if article.title in articleTitles: 
                continue
      
            # Extract the words
            tmp_txt = article.title.encode('utf8') + \
                      stripHTML(article.description.encode('utf8'))
                  
            words = separateWords(tmp_txt, min_length)
            articleWords.append({})
            articleTitles.append(article.title)
      
            # Increase the counts for this word in allWords and articleWords
            for word in words:
                allWords.setdefault(word, 0)
                allWords[word] += 1
                articleWords[ec].setdefault(word, 0)
                articleWords[ec][word] += 1
            ec += 1
    return allWords, articleWords, articleTitles

def makeMatrix(allw, articlew, min_num=3, max_percent=0.60):
    """Now we have dictionaries of counts for the words in all articles,
    as well as counts for each article, all of which has to converted 
    into matrix that can be used in later analysis.  

    First step is to create a list of words to be used as the columns 
    of the matrix. To reduce the size of the overall matrix I will 
    eliminate words that appear in only a couple of articles and also 
    those that appear in too many articles.

    To start, try only including words that appear in more than 
    min_num of articles, but fewer than some max_percent of the total
    number of articles.
    
    """
    wordVec = []
  
    # Only take words that are common but not too common
    for word, count in allw.items():
        if count > min_num and count < len(articlew) * max_percent: 
            wordVec.append(word) 
  
    # Create the word matrix
    l1 = [[(word in f and f[word] or 0) for word in wordVec] for f in articlew]
    return l1, wordVec



def showFeatures(w, h, titles, wordvec, out='features.txt'):
    """Exactly how you view results of NNMF is a bit complicated. Every
    feature in the features matrix has a weighting that indicates how
    strongly each word applies to that feature, so you might try 
    displaying the top five or ten words in each feature to see what 
    the most important words are in each feature.

    The equivalent column in the weights matrix tells you how much 
    this particular feature applies to each of the articles, so it is 
    often interesting to show the top few articles and see how strongly
    a particular feature applies to them.

    This function loops over each word of the features and creates a 
    list of all the word weights and words from the word vector.  It 
    sorts the list so that the most heavily weighted words for that 
    feature appear at the start of the list, and then prints the first
    10 of these words. Hopefully this gives some idea of the theme 
    represented by a particular feature.

    After displaying each feature, the function loops over the article
    titles and sorts them according to their value in the weights 
    matrix for that article and feature. It then prints the titles of 
    3 articles most strongly associated with that feature, along with 
    the value from the weights matrix. Sometimes a feature will be 
    important for several related articles, and that sometimes a 
    feature will only show up prominately in a single article.
    
    """
    outfile = file(out,'w')  
    pc, wc = np.shape(h)

    # create storage containers for sorted features
    toppatterns=[[] for i in range(len(titles))]
    patternnames=[]
  
    # Loop over all the features
    for i in range(pc):
        slist=[]
        # Create a list of words and their weights
        for j in range(wc):
            slist.append((h[i,j], wordvec[j]))
        # Reverse sort the word list
        slist.sort()
        slist.reverse()
    
        # Print the first ten elements
        n = [s[1] for s in slist[0:10]]
        outfile.write(str(n) + '\n')
        patternnames.append(n)
    
        # Create a list of articles for this feature
        flist = []
        for j in range(len(titles)):
            # Add the article with its weight
            flist.append((w[j, i], titles[j]))
            toppatterns[j].append((w[j, i], i, titles[j]))
    
        # Reverse sort the list
        flist.sort()
        flist.reverse()
    
        # Show the top 3 articles
        for f in flist[0:3]:
            outfile.write(str(f)+'\n')
        outfile.write('\n')

    outfile.close()

    # Return the pattern names for later use
    return toppatterns, patternnames

def showArticles(titles, toppatterns ,patternnames, out='articles.txt'):
    """Alternative way to display the data is to show each article and 
    the top 3 features that apply to it.  This allows you to see if an 
    article consists of equal amounts of several themes of a single 
    strong theme.

    """
    outfile = file(out,'w')  
  
    # Loop over all the articles
    for j in range(len(titles)):
        outfile.write(titles[j].encode('utf8') + '\n')
    
        # Get the top features for this article and reverse sort them
        toppatterns[j].sort()
        toppatterns[j].reverse()
    
        # Print the top three patterns
        for i in range(3):
            outfile.write(str(toppatterns[j][i][0]) + ' ' + \
                          str(patternnames[toppatterns[j][i][1]])+'\n')
        outfile.write('\n')
    
    outfile.close()
