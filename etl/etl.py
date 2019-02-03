###############################################################################
#
# Import libraries
#
###############################################################################

from bs4 import BeautifulSoup
import datetime
import json
import imp
import pandas as pd
import smtplib
import sys
import time
import urllib2





###############################################################################
#
# Load env file
#
###############################################################################

env = imp.load_source('env', '../_env/env.py')





###############################################################################
#
# Define functions
#
###############################################################################

#####
#
# Email an alert if any errors present during the data load
#
# emailSettings {dict} - email credentials
# subject {string} - email subject
# message {string} - email body
# exitProcess {boolean} - exit or continue the process
#
#####
def email(emailSettings, subject, message, exitProcess = True):
    headers = (
        'From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n' % (
            emailSettings['fromAddress'], 
            emailSettings['toAddress'], 
            subject
        )
    )
    headers = headers + message
    
    server = smtplib.SMTP(host = emailSettings['host'], port = emailSettings['port'])
    server.starttls()
    server.login(emailSettings['user'], emailSettings['password'])
    server.sendmail(emailSettings['fromAddress'], emailSettings['toAddress'], headers)
    server.quit()
    
    if exitProcess:
        sys.exit()    

#####
#
# Call an API endpoint
#
# site {string} - the web address for the API call
#
# return - the API response in JSON format
#
#####
def returnApiJson(site):
    response = urllib2.urlopen(site)
    
    return json.load(response)

#####
#
# Get all tradeable BTC markets on the Bittrex exchange
#
# renameMap {dict} - rename certain markets to match the nomenclature on the
#    site we pull the repo information from
#
# return - an object with data on Bittrex markets
#
#####
def getBittrexBtcMarkets(renameMap):
    site = 'https://bittrex.com/api/v1.1/public/getmarkets'
    allBittrexBtcMarkets = returnApiJson(site)
    allBittrexBtcMarkets = filter(lambda x : x['BaseCurrency'] == 'BTC', allBittrexBtcMarkets['result'])
    
    site = 'https://bittrex.com/api/v1.1/public/getcurrencies'
    allBittrexMarketsTxCost = returnApiJson(site)['result']
    
    dataset = []
    
    for market in allBittrexBtcMarkets:
        txData = filter(lambda x : x['Currency'] == market['MarketCurrency'], allBittrexMarketsTxCost)

        market.update({
            'CoinType': txData[0]['CoinType'],
            'TxFee': txData[0]['TxFee']
        })
    
        if market['MarketCurrency'] in renameMap:
             market.update({
                'MarketCurrencyLong': renameMap[market['MarketCurrency']]
            })           
        
        dataset.append(market)
    
    return dataset    
 
#####
#
# Find Github repo information for a market
#
# longName {string} - the crypto market long name
# shortName {string} - the crypto market short name
#
# return - an object with all repos for a crypto asset
#
#####   
def getGitRepos(longName, shortName):
    data = []
    site = 'https://www.coingecko.com/en/coins/' + longName + '/developer#panel'
    header = {
       'User-Agent': 'Mozilla/5.0'
    }
    
    request = urllib2.Request(site, headers = header)
    page = urllib2.urlopen(request)
    soup = BeautifulSoup(page, 'html.parser')

    for node in soup.find_all('a', href=True, text=True):
        if 'github' in node['href']:
            data.append({
                'longName': longName,
                'shortName': shortName,
                'repoName': node.text,
                'repoLocation': node['href']
            })

    return data

#####
#
# Parse commit information in Github for a repo
#
# repoName {string} - the name of the repo on Github
# marketName {string} - the name of the crypto market
# githubCredentials {dict} - the key and id used to call data from the github API
#
# return - an object with dates and authors for all repo commits
#
#####
def getRepoUpdateDates(repoName, marketName, githubCredentials):
    meta = []
    iterate = True
    index = 1

    while iterate:
        repoApi = 'https://api.github.com/repos/' \
            + repoName \
            + '/commits?page=' + str(index) + '&per_page=100' \
            + '&client_id=' + githubCredentials['clientId'] \
            + '&client_secret=' + githubCredentials['clientSecret']
        
        data = returnApiJson(repoApi)
        
        if data:
            for commit in data:
                date = commit['commit']['author']['date'].replace('T', '').replace('Z', '')
                date = datetime.datetime.strptime(date, '%Y-%m-%d%H:%M:%S')
                
                meta.append({
                    'author': commit['commit']['author']['email'],
                    'market': marketName,
                    'repoName': repoName,
                    'updated': date
                })
            
            index += 1
        else:
            iterate = False
    
    return meta

#####
#
# Get pricing time series
#
# shortName {string} - the market ticker
# apiKey {string} - the api key for the pricing API
#
# return - the pricing time series as a JSON object
#
#####
def getPricing(shortName, apiKey):
    site = 'https://www.alphavantage.co/query?' \
        + 'function=DIGITAL_CURRENCY_DAILY&' \
        + 'symbol=' + shortName + '&' \
        + 'market=USD&' \
        + 'apikey=' + apiKey
    
    return returnApiJson(site)

#####
#
# Map pricing results from the pricing API
#
# pricing {dict} - pricing data returned from API that requires mapping
#
# return - an object with ohlc data
#
#####
def mapPricingResults(pricing):
    return {
        'date': pricing[0],
        'openPrice': pricing[1]['1a. open (USD)'],
        'highPrice': pricing[1]['2a. high (USD)'],
        'lowPrice': pricing[1]['3a. low (USD)'],
        'closePrice': pricing[1]['4a. close (USD)'],
        'volume': pricing[1]['5. volume']
    }

#####
#
# Read text file to string
#
# fileName {string} - the file to read to string
#
# return - string text from file
#
#####
def readFile(fileName):
    contents = open(fileName, 'r')
    return contents.read()

#####
#
# Execute SQL with no output
#
# sql {string} - the sql query to execute
# engine - the sql alchemy engine
#
#####
def runSql(sql, engine):
    conn = engine.raw_connection()
    conn.execute(sql)
    conn.close()





###############################################################################
#
# Define variables
#
###############################################################################

errors = []
repos = []
updateDates = []
totalPricing = pd.DataFrame(columns = [
    'closePrice', 
    'date', 
    'highPrice', 
    'lowPrice', 
    'openPrice', 
    'volume', 
    'ticker'
])
# Bittrex naming doesn't match coingecko (where we pull the Github information 
# from), so we'll need to use the following naming in the getBittrexBtcMarkets() 
# function for the following coins
renameMap = {
    'THC': 'hempcoin-thc',
    'KORE': 'korecoin',
    'VIA': 'viacoin',
    'IOC': 'iocoin',
    'BURST': 'burst',
    'XRP': 'ripple',
    'AMP': 'hyperspace-synereo',
    'XLM': 'stellar',
    'SBD': 'steem-dollars',
    'VRM': 'veriumreserve',
    'GBG': 'golos-gold',
    'SWT': 'swarm-city',
    'GBYTE': 'obyte',
    'MORE': 'more-one',
    'WINGS': 'wings',
    'RLC': 'iexec-rlc',
    'SNT': 'status',
    'MCO': 'crypto-com',
    'PAY': 'tenx',
    'BCH': 'bitcoin-cash',
    'SRN': 'sirin-labs-token',
    'WAX': 'wax',
    'ZRX': '0x',
    'TUSD': 'true-usd',
    'POLY': 'polymath-network',
    'CBC': 'cashbet-coin',
    'ENJ': 'enjin-coin',
    'IHT': 'iht-real-estate-protocol',
    'XHV': 'haven',
    'SOLVE': 'solve-care',
    'USDS': 'stronghold-usd',
    'LBA': 'libra-credit'
}
try:
    allBittrexBtcMarkets = getBittrexBtcMarkets(renameMap)
except Exception as inst:
        errors.append({
            'longName': None,
            'shortName': None,
            'error': 'BTC Markets Load Error',
            'output': (str(type(inst)) + str(inst.args)).replace("'", '')
        })

        email(
            env.emailCredentials, 
            'Data Warehouse Process Error',
            'The crypto data load had an error that resulted in the process halting ' \
            + 'when calling Bittrex markets in getBittrexBtcMarkets and ' \
            + 'getBittrexMarketsTxCost. See the errorsExtCrypto in the data warehouse'
        )

# Github has an API call limit of 5000 per hour. This will be used to track 
# how much time has elapsed if we hit the limit so that we can sleep the process
# until we can pull data again
analysisStartTime = time.time()
# The running call limit. If we hit 5000, we will add another 5000 for the next
# call limit.
githubLimit = 5000





###############################################################################
#
# Run logic
#
###############################################################################

for market in allBittrexBtcMarkets:
    # Used to measure time elapsed to ensure we stay below the pricing API
    # call limit.
    iterationStartTime = time.time()
    
    longName = market['MarketCurrencyLong'].lower().replace(' ', '-')
    shortName = market['MarketCurrency']
    symbol = market['MarketName']

    try:
        marketRepos = getGitRepos(longName, shortName)        
    except Exception as inst:
        errors.append({
            'longName': longName,
            'shortName': shortName,
            'error': 'Could not pull git repos from coingecko.com',
            'output': (str(type(inst)) + str(inst.args)).replace("'", '')
        })
    
    try:
        for repo in marketRepos:
            repos.append(repo)
            
            dates = getRepoUpdateDates(repo['repoName'], shortName, env.githubCredentials)
            
            for date in dates:
                updateDates.append(date)
    except Exception as inst:
        errors.append({
            'repo': longName,
            'shortName': shortName,
            'error': 'Could not pull ' + repo['repoName'] + ' from github',
            'output': (str(type(inst)) + str(inst.args)).replace("'", '')
        })

    try:
        data = getPricing(shortName, env.alphaVantageApiKey)
        data = map(mapPricingResults, data['Time Series (Digital Currency Daily)'].iteritems())
        data = pd.DataFrame(data)
        data['ticker'] = shortName
        totalPricing = totalPricing.append(data)
    except Exception as inst:
        errors.append({
            'longName': longName,
            'shortName': shortName,
            'error': 'Could not get pricing',
            'output': (str(type(inst)) + str(inst.args)).replace("'", '')
        })
    # There is an API call limit on pricing, so we need to wait if the process took
    # less than 20 seconds for one iteration
    sleepTime = 20 - (time.time() - iterationStartTime)
                      
    if sleepTime > 0:
        time.sleep(sleepTime)
 
    # There is an API call limit on the github API, so we need to wait if the 
    # process took less than 1 hour for 5000 calls
    if len(updateDates) > githubLimit * 100:
        sleepTime = 3600 - int((time.time() - analysisStartTime))
        
        if sleepTime > 0:
            time.sleep(3600 - int((time.time() - analysisStartTime)))
            githubLimit += 5000
            analysisStartTime = time.time()

# Generate the database schema for the data inserts        
createSchemaSql = readFile('../schema/schema.sql')
runSql(createSchemaSql)

# Load data to SQL database
totalPricing.to_sql('cryptoTotalPricingExt', env.dbEngine, if_exists = 'append', index = False)
pd.DataFrame(updateDates).to_sql('cryptoRepoUpdateDatesExt', env.dbEngine, if_exists = 'append', index = False)
pd.DataFrame(repos).to_sql('cryptoReposExt', env.dbEngine, if_exists = 'append', index = False)
pd.DataFrame(errors).to_sql('cryptoErrorsExt', env.dbEngine, if_exists = 'append', index = False)
pd.DataFrame(allBittrexBtcMarkets).to_sql('cryptoAllBittrexMarketsExt', env.dbEngine, if_exists = 'append', index = False)