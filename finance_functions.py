import yfinance as yf # type: ignore
import pandas as pd
import requests

def STOCK(ticker, period="max"):
    """
    Function to get open, high, low, ... data of a stock in a tabular format
    :Parameters:
    period : str
        Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    interval : str
        Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        Intraday data cannot extend last 60 days
    """
    return yf.Ticker(ticker).history(period=period).reset_index(drop=False)

def get_stock_prices(tickers, period="1000d", interval="1d"):
    """
    :Parameters:
    period : str
        Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    interval : str
        Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        Intraday data cannot extend last 60 days
    """
    data = yf.download(list(tickers), group_by='column', period=period, interval=interval)
    return data[['Close', 'Volume']]

def get_financials(ticker):
    tck = yf.Ticker(ticker)
    return tck.get_financials()

def get_multiple_financials(tickers):
    tickers = [yf.Ticker(ticker) for ticker in tickers]
    dfs = [] # list for each ticker's dataframe
    for ticker in tickers:
        # get each financial statement
        pnl = ticker.financials
        bs = ticker.balancesheet
        cf = ticker.cashflow

        # concatenate into one dataframe
        fs = pd.concat([pnl, bs, cf])

        # make dataframe format nicer
        # Swap dates and columns
        data = fs.T
        # reset index (date) into a column
        data = data.reset_index()
        # Rename old index from '' to Date
        data.columns = ['Date', *data.columns[1:]]
        # Add ticker to dataframe
        data['Ticker'] = ticker.ticker
        dfs.append(data)
    df = pd.concat(dfs, ignore_index=True)
    df = df.T.drop_duplicates().T
    df = df.set_index(['Ticker','Date'])
    return df

def get_institutional_holders(ticker):
    tck = yf.Ticker(ticker)
    return tck.institutional_holders

def get_ticker(company_name):
    """
    Get the ticker based on the company name
    Parameters:
    company_name: str
        Free text
    """
    yfinance_url = "https://query2.finance.yahoo.com/v1/finance/search"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    params = {"q": company_name, "quotes_count": 1, "country": "United States"}

    res = requests.get(url=yfinance_url, params=params, headers={'User-Agent': user_agent})
    data = res.json()

    company_code = data['quotes'][0]['symbol']
    return company_code