import sqlalchemy as sa

alphaVantageApiKey = ''
emailCredentials = {
    'fromAddress': '',
    'toAddress': '',
    'host': '',
    'port': '',
    'user': '',
    'password': ''
}
dbCredentials = {
    'user': '',
    'password': '',
    'server': '',
    'database': ''
}
dbConnStr = 'mssql+pyodbc://' \
    + dbCredentials['user'] + ':' \
    + dbCredentials['password'] + '@' \
    + dbCredentials['server'] + '/' \
    + dbCredentials['database'] \
    + '?driver=sqlserver'
dbEngine = sa.create_engine(dbConnStr)
githubCredentials = {
    'clientId': '',
    'clientSecret': ''
}