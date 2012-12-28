import httplib
from xml.dom.minidom import parse, parseString, Node

# import developer keys
from developerkeys import *

devKey    = productionDevKey
appKey    = productionAppKey
certKey   = productionCertKey
serverUrl = productionServerUrl
userToken = productionUserToken

def get_FindingHeaders(apicall, globalId="EBAY-US", serviceVersion = "1.12.0"):
    """Generates a dictionary of headers to pass to httplib for use in  calling
    the eBay Finding API.

    Keyword arguments:
        apicall        -- A valid eBay Finding API call. See the online
                          reference for details:

                          http://developer.ebay.com/DevZone/finding/CallRef/index.html

        globalID       -- Each eBay site maps to a unique eBay global ID. You must
                          specify a global ID in the X-EBAY-SOA-GLOBAL-ID HTTP
                          header for each API call. (default: 'EBAY-US' or '0'
                          for eBay US)

        serviceVersion -- The API level to which the application conforms.

    """
    headers = {"X-EBAY-SOA-SERVICE-NAME": "FindingService",
               "X-EBAY-SOA-OPERATION-NAME": apicall,	
               "X-EBAY-SOA-SERVICE-VERSION": serviceVersion,
               "X-EBAY-SOA-GLOBAL-ID": globalId,
               "X-EBAY-SOA-SECURITY-APPNAME": appKey,
               "X-EBAY-SOA-REQUEST-DATA-FORMAT": "XML"}
    return headers

def get_TradingHeaders(apicall, siteId=0, version = 803):
    """Generates a dictionary of headers to pass to httplib for use in  calling
    the eBay Trading API.

    Keyword arguments:
        apicall -- A valid eBay Trading API call. See the online reference for
                   details:

                      http://developer.ebay.com/DevZone/XML/docs/Reference/eBay/
                              
        siteID  -- The eBay site you specify in your requests affects the
                   business logic and validation rules that are applied to
                   the request. For example, the eBay US site (0) and eBay
                   Germany (77) site follow different rules due to differences
                   between US and EU law, buyer behavior, and other factors.
                   (default: 0 for eBay US)

        version -- The API level to which the application conforms. As of
                   February 2013 the lowest schema version supported by eBay is
                   707 (default: 803).

    """
    headers = {"X-EBAY-API-COMPATIBILITY-LEVEL": str(version),	
               "X-EBAY-API-DEV-NAME": devKey,
               "X-EBAY-API-APP-NAME": appKey,
               "X-EBAY-API-CERT-NAME": certKey,
               "X-EBAY-API-CALL-NAME": apicall,
               "X-EBAY-API-SITEID": str(siteId),
               "Content-Type": "text/xml"}
    return headers

def send_FindingRequest(apicall, globalId, xmlparameters):
    """Opens a connection with the eBay server, posts the XML for the Finding
    API call, extracts the data, and parses the result.

    Keyword arguments:
        apicall       -- A valid call to the eBay Finding API. For details see:

                         http://developer.ebay.com/DevZone/finding/Concepts/FindingAPIGuide.html
        
        globalId      -- Each eBay site maps to a unique eBay global ID. You
                         must specify a global ID in the X-EBAY-SOA-GLOBAL-ID
                         HTTP header for each API call. (default: 'EBAY-US'
                         for eBay US)
                         
        xmlparameters -- XML parameters of for the request

    """
    connection = httplib.HTTPConnection("svcs.ebay.com")
    connection.request("POST", '/services/search/FindingService/v1?', \
                       xmlparameters, get_FindingHeaders(apicall, globalId))
    response = connection.getresponse()

    # Check to see if successful connection achieved
    if response.status != 200:
        print "Error sending request:" + response.reason
    else: 
        data = response.read()
        connection.close()

    return data

def send_TradingRequest(apicall, siteID, xmlparameters):
    """Opens a connection with the eBay server, posts the XML for the Trading
    API call, extracts the data, and parses the result.

    Keyword arguments:
        apicall       -- A valid call to the eBay Trading API.
        
        siteID        -- The eBay site you specify in your requests affects the
                         business logic and validation rules that are applied to
                         the request. For example, the eBay US site (0) and
                         eBay Germany (77) site follow different rules due to
                         differences between US and EU law, buyer behavior, and
                         other factors. (default: '0' for eBay US)
                         
        xmlparameters -- XML parameters of for the request

    """
    connection = httplib.HTTPSConnection(serverUrl)
    connection.request("POST", '/ws/api.dll', xmlparameters, \
                       get_TradingHeaders(apicall, siteID))
    response = connection.getresponse()

    # Check to see if successful connection achieved
    if response.status != 200:
        print "Error sending request:" + response.reason
    else: 
        data = response.read()
        connection.close()

    return data
  
def get_SingleValue(node, tag):
    """ DOM parsing is tedious! This function is a simple convenience method
    which finds a specified node and returns its contents.

    Keyword arguments:
        node -- The Node object represents a single node in the document tree.
        tag  -- The bit of information that you wish to extract from the node.

    """
    nl = node.getElementsByTagName(tag)

    # check that node is non-empty
    if len(nl) > 0:
        tagNode = nl[0]
        # check for child nodes
        if tagNode.hasChildNodes():
            return tagNode.firstChild.nodeValue
    # if empty, return NaN
    else:
        return 'NaN'

def findItemsAdvanced(keywords, categoryId=None, globalId='EBAY-US', maxPage=1):
    """Performing a search is just a matter of creating the XML parameters for
    the Finding API call and passing them to the send_Request function.

    Keyword arguments:
        keywords   -- Specify one or more words to use in a search query for
                      finding items on eBay. By default, queries search item
                      titles only. When running queries, it is best to include
                      complete keywords values--eBay checks words in context
                      with each other. If you are using a URL request and your
                      keyword query consists of multiple words, use "%20" to
                      separate the words. For example, use "Harry%20Potter" to
                      search for items containing those words in any order.
                      Queries aren't case-sensitive, so it doesn't matter
                      whether you use uppercase or lowercase letters. 

                      You can incorporate wildcards in a multi-word search. For
                      example, "ap*%20ip*" returns results for "apple ipod"
                      among other matches. The words "and" and "or" are treated
                      like any other word (and not their logical connotation).
                      Only use "and", "or", or "the" if you are searching for
                      listings containing those specific words.

                      Max length: 350. The maximum length for a single word is
                      98. Min length: 2.
                    
        categoryId -- Specifies the category from which you want to retrieve
                      item listings. This field can be repeated to include
                      multiple categories. Up to three (3) categories can be
                      specified. 

                      If a specified category ID doesn't match an existing
                      category for the site, eBay returns an invalid-category
                      error message. To determine valid categories, use the
                      Trading API GetCategories call. 

                      findItemsAdvanced requires that you specify keywords
                      and/or a categoryId in the request. The exception to this
                      rule is when the Seller item filter is used. The Seller
                      item filter can be used without specifying either keywords
                      or categoryId to retrieve all active items for the
                      specified seller. 

                      Category searches are not supported on the eBay Italy site
                      (global ID EBAY-IT) at this time. Max length: 10.

        globalId   -- Each eBay site maps to a unique eBay global ID. You
                      must specify a global ID in the X-EBAY-SOA-GLOBAL-ID
                      HTTP header for each API call. (default: 'EBAY-US'
                      for eBay US)

        maxPage    -- Maximum number of pages of results to return (default: 1).
                      Note that eBay enforces a maximum page number of 100 which
                      limits search results to 10,000 (max of 100 entries per
                      page and max of 100 pages returned).
                    
    The findItemsAdvanced function returns a list of the item IDs, along with
    their description, current price, and auction details.
    
    """
    results   = []

    for i in range(1, maxPage + 1):
        # XML Request
        xml = "<?xml version='1.0' encoding='utf-8'?>" +\
              "<findItemsAdvancedRequest " +\
              "xmlns='http://www.ebay.com/marketplace/search/v1/services'>" +\
              "<keywords>" + keywords + "</keywords>" +\
              "<paginationInput>" +\
              "<pageNumber>" + str(i) + "</pageNumber>" +\
              "<entriesPerPage> 100 </entriesPerPage>" +\
              "</paginationInput>"
        # if a categoryId is specified, then include this in XML request
        if categoryId != None:
            xml += "<categoryId>" + str(categoryId) + "</categoryId>"
        # don't forget to end XML request!
        xml += "</findItemsAdvancedRequest>"

        # NowmMake the Finding API call to extract the data
        data      = send_FindingRequest('findItemsAdvanced', globalId, xml)
        response  = parseString(data)
        itemNodes = response.getElementsByTagName('item')
    
        for item in itemNodes:
            itemId         = get_SingleValue(item, 'itemId')
            itemTitle      = get_SingleValue(item, 'title')
            itemSubtitle   = get_SingleValue(item, 'subtitle')
            itemCategoryId = get_SingleValue(item, 'categoryId')
            itemPrice      = get_SingleValue(item, 'currentPrice')
            isBestOffer    = get_SingleValue(item, 'bestOfferEnabled')
            isBuyItNow     = get_SingleValue(item, 'buyItNowAvailable')
            listingStarts  = get_SingleValue(item, 'startTime')
            listingEnds    = get_SingleValue(item, 'endTime')
            listingType    = get_SingleValue(item, 'listingType')
            results.append((itemId, itemTitle, itemSubtitle, itemCategoryId, \
                            itemPrice, isBestOffer, isBuyItNow, listingStarts, \
                            listingEnds, listingType))

    return results

def GetCategories(query='', CategoryParent=None, siteID=0):
    """Function takes a string and a parent ID and returns all the categories
    containing that string within that top-level category. If the parent ID is
    missing, the function dislays a list of all the top-level categories.

    Keyword arguments:
        query          -- A string containing the search query
        
        CategoryParent -- Specifies the ID of the highest-level category to
                          return, along with its subcategories. If no parent
                          category is specified, all categories are returned
                          for the specified site. (Please do not pass a value
                          of 0; zero (0) is an invalid value for
                          CategoryParent.) To determine available category IDs,
                          call GetCategories with no filters and use a
                          DetailLevel value of ReturnAll. If you specify
                          multiple parent categories, the hierarchy for each one
                          is returned.
                          
        siteID         -- The eBay site you specify in your requests affects the
                          business logic and validation rules that are applied
                          to the request. For example, the eBay US site (0)
                          and eBay Germany (77) site follow different rules
                          due to differences between US and EU law, buyer
                          behavior, and other factors. (default: 0 for eBay US)

    """
    lquery = query.lower()
    xml    = "<?xml version='1.0' encoding='utf-8'?>"+\
             "<GetCategoriesRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">"+\
             "<RequesterCredentials>" +\
             "<eBayAuthToken>" + userToken + "</eBayAuthToken>" +\
             "</RequesterCredentials>" +\
             "<DetailLevel>ReturnAll</DetailLevel>"+\
             "<ViewAllNodes>true</ViewAllNodes>"+\
             "<CategorySiteID>" + str(siteID) + "</CategorySiteID>"
    # if CategoryParent is specified, then include this in the XML request 
    if CategoryParent == None:
        xml += "<LevelLimit>1</LevelLimit>"
    else:
        xml += "<CategoryParent>" + str(CategoryParent) + "</CategoryParent>"
    # Don't forget to end the XML request!
    xml          += "</GetCategoriesRequest>"

    # Make the Trading API call and extract the data
    data         = send_TradingRequest('GetCategories', siteID, xml)
    categoryList = parseString(data)
    catNodes     = categoryList.getElementsByTagName('Category')

    for node in catNodes:
        catid = get_SingleValue(node, 'CategoryID')
        name  = get_SingleValue(node, 'CategoryName')
        if name.lower().find(lquery) != -1:
            print catid, name

def GetItem(itemID, siteID=0):
    """Function executes a GetItem call to the eBay Trading API. eBay provides
    attributes specific to different item types.  It is also possible to get
    details such as the seller's rating, number of bids, the starting price,
    etc.

    To get the details of an item you need to make an eBay API call to GetItem,
    passing the item's ID as return by the search function.

    Keyword arguments:
        itemID -- Specifies the ItemID that uniquely identifies the item
                  listing for which to retrieve the data. 

                  ItemID is a required input in most cases. SKU can be
                  used instead in certain cases (see the description of SKU).
                  If both ItemID and SKU are specified for items where the
                  inventory tracking method is ItemID, ItemID takes precedence.

                  Max length: 19 (Note: The eBay database specifies 38. ItemIDs
                  are usually 9 to 12 digits).

       siteID  -- The eBay site you specify in your requests affects the
                  business logic and validation rules that are applied to the
                  request. For example, the eBay US site (0) and eBay
                  Germany (77) site follow different rules due to
                  differences between US and EU law, buyer behavior, and
                  other factors. (default: 0 for eBay US)

    """
    # XML parameters for API call 
    xml = "<?xml version='1.0' encoding='utf-8'?>"+\
          "<GetItemRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">"+\
          "<RequesterCredentials><eBayAuthToken>" + userToken + "</eBayAuthToken>" +\
          "</RequesterCredentials>" + \
          "<ItemID>" + str(itemID) + "</ItemID>"+\
          "<IncludeItemSpecifics>true</IncludeItemSpecifics>" +\
          "<DetailLevel>ItemReturnAttributes</DetailLevel>"+\
          "</GetItemRequest>"

    # make the call to the Trading API and extract the data
    data      = send_TradingRequest('GetItem', siteID, xml)

    # create an empty dictionary to store the results
    result    = {}

    # parse the data
    response  = parseString(data)
    
    # extract item specific data
    itemNodes = response.getElementsByTagName('Item')
    for item in itemNodes:
        # Generic product information
        result['itemId']   = get_SingleValue(item, 'ItemID')
        result['title']    = get_SingleValue(item, 'Title')
        result['subTitle'] = get_SingleValue(item, 'SubTitle')

        # Specific product information
        NameValueList = response.getElementsByTagName('NameValueList')
        ItemSpecifics = {}
        
        for NameValuePair in NameValueList:
            Name                = get_SingleValue(NameValuePair, 'Name')
            ItemSpecifics[Name] = get_SingleValue(NameValuePair, 'Value')
        result['itemSpecifics'] = ItemSpecifics

        # Price information
        result['startPrice']    = get_SingleValue(item, 'StartPrice')
        result['reservePrice']  = get_SingleValue(item, 'ReservePrice')
        result['currentPrice']  = get_SingleValue(item, 'CurrentPrice')
        result['buyItNowPrice'] = get_SingleValue(item, 'BuyItNowPrice')
        result['floorPrice']    = get_SingleValue(item, 'FloorPrice')
        result['ceilingPrice']  = get_SingleValue(item, 'CeilingPrice')

        # Bidding information 
        result['bidCount']     = get_SingleValue(item, 'BidCount')
        result['bidIncrement'] = get_SingleValue(item, 'BidIncrement')

        # Auction information
        result['listingType']     = get_SingleValue(item, 'ListingType')
        result['listingDuration'] = get_SingleValue(item, 'ListingDuration')
        result['startTime']       = get_SingleValue(item, 'StartTime')
        result['endTime']         = get_SingleValue(item, 'EndTime')
        result['timeLeft']        = get_SingleValue(item, 'TimeLeft')

        # Seller information
        result['feedbackScore']      = get_SingleValue(item,'FeedbackScore')
        result['feedbackRatingStar'] = get_SingleValue(item,'FeedbackRatingStar')

    return result

def GetAllBidders(itemID, siteID=0):
    """Function executes a GetAllBidders call to the eBay Trading API. Use this
    call to retrieve a list of the eBay users that bid on a specified listing,
    regardless of whether the listing has ended.

    Keyword arguments:
        itemID -- Specifies the ItemID that uniquely identifies the item
                  listing for which to retrieve the data. 

                  ItemID is a required input in most cases. SKU can be
                  used instead in certain cases (see the description of SKU).
                  If both ItemID and SKU are specified for items where the
                  inventory tracking method is ItemID, ItemID takes precedence.

                  Max length: 19 (Note: The eBay database specifies 38. ItemIDs
                  are usually 9 to 12 digits).

       siteID  -- The eBay site you specify in your requests affects the
                  business logic and validation rules that are applied to the
                  request. For example, the eBay US site (0) and eBay
                  Germany (77) site follow different rules due to
                  differences between US and EU law, buyer behavior, and
                  other factors. (default: 0 for eBay US)

    """
    # XML parameters for API call 
    xml = "<?xml version='1.0' encoding='utf-8'?>"+\
          "<GetAllBiddersRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">"+\
          "<RequesterCredentials><eBayAuthToken>" + userToken + "</eBayAuthToken>" +\
          "</RequesterCredentials>" + \
          "<ItemID>" + str(itemID) + "</ItemID>"+\
          "<CallMode>ViewAll</CallMode>" +\
          "<IncludeBiddingSummary>true</IncludeBiddingSummary>" +\
          "</GetAllBiddersRequest>"

    # make the call to the Trading API and extract the data
    data      = send_TradingRequest('GetAllBidders', siteID, xml)

    # function returns a list of dictionaries (one for each offer)
    result    = []

    # parse the data
    response  = parseString(data)
    
    # extract offer specific data
    offerNodes = response.getElementsByTagName('Offer')
    for offer in offerNodes:
        # create an empty dictionary
        tmp_result = {}
        
        # Generic offer information
        tmp_result['action']              = get_SingleValue(offer, 'Action')
        tmp_result['convertedPrice']      = get_SingleValue(offer, 'ConvertedPrice')
        tmp_result['currency']            = get_SingleValue(offer, 'Currency')
        tmp_result['highestBid']          = get_SingleValue(offer, 'HighestBid')
        tmp_result['maxBid']              = get_SingleValue(offer, 'MaxBid')
        tmp_result['myMaxBid']            = get_SingleValue(offer, 'MyMaxBid')
        tmp_result['quantity']            = get_SingleValue(offer, 'Quantity')
        tmp_result['secondChanceEnabled'] = get_SingleValue(offer, 'SecondChanceEnabled')
        tmp_result['siteCurrency']        = get_SingleValue(offer, 'SiteCurrency')
        tmp_result['timeBid']             = get_SingleValue(offer, 'TimeBid')
        tmp_result['highBidder']          = get_SingleValue(offer, 'HighBidder')
        tmp_result['highestBid']          = get_SingleValue(offer, 'HighestBid')
        
        # Bidder specific information
        tmp_user = {}

        tmp_user['aboutMePage']             = get_SingleValue(offer, 'AboutMePage')
        tmp_user['feedbackRatingStar']      = get_SingleValue(offer, 'FeedbackRatingStar')
        tmp_user['feedbackScore']           = get_SingleValue(offer, 'FeedbackScore')
        tmp_user['positiveFeedbackPercent'] = get_SingleValue(offer, 'PositiveFeedbackPercent')
        tmp_user['userId']                  = get_SingleValue(offer, 'UserID')
        
        # User bidding summary information
        tmp_bid_summary = {}

        tmp_bid_summary['bidActivityWithSeller']  = get_SingleValue(offer, 'BidActivityWithSeller')
        tmp_bid_summary['bidRetractions']         = get_SingleValue(offer, 'BidRetractions')
        tmp_bid_summary['bidsToUniqueCategories'] = get_SingleValue(offer, 'BidsToUniqueCategories')
        tmp_bid_summary['bidsToUniqueSellers']    = get_SingleValue(offer, 'BidsToUniqueSellers')
        tmp_bid_summary['summaryDays']            = get_SingleValue(offer, 'SummaryDays')
        tmp_bid_summary['totalBids']              = get_SingleValue(offer, 'TotalBids')

        # Item specific bid details
        tmp_item_bid_details = {}

        tmp_item_bid_details['bidCount']    = get_SingleValue(offer, 'BidCount')
        tmp_item_bid_details['categoryId']  = get_SingleValue(offer, 'CategoryID')
        tmp_item_bid_details['itemId']      = get_SingleValue(offer, 'ItemID')
        tmp_item_bid_details['lastBidTime'] = get_SingleValue(offer, 'LastBidTime')
        tmp_item_bid_details['sellerId']    = get_SingleValue(offer, 'SellerID')

        # Adde the nested dictionaries
        tmp_bid_summary['itemBidDetails'] = tmp_item_bid_details
        tmp_user['biddingSummary']        = tmp_bid_summary 
        tmp_result['user']                = tmp_user

        # Add the dictionaries to the offer list
        result.append(tmp_result)
        
    return result

def generateLaptopDataset():
    searchResults = findItemsAdvanced('laptop', categoryId=175672)
    result        = []
    for result in searchResults:
        item   = GetItem(result[0])
        specs  = item['itemSpecifics']
        try:
            data=(float(att['12']),float(att['26444']),
                  float(att['26446']),float(att['25710']),
                  float(item['feedback']))
            entry={'input':data,'result':float(item['price'])}
            result.append(entry)
        except:
            print item['title'] + ' failed'
    return result


