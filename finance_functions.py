import yfinance as yf # type: ignore
import pandas as pd
import requests
from langchain_core.tools import tool

@tool
def get_stock_prices(tickers: str, period: str="1000d", interval: str="1d") -> pd.DataFrame:
    """
    Function to get historical price given the period and the interval
    :Parameters:
    period : str
        Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    interval : str
        Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        Intraday data cannot extend last 60 days
    """
    data = yf.download(list(tickers), group_by='column', period=period, interval=interval)
    return data[['Close', 'Volume']]

@tool
def get_financials(ticker: str) -> str:
    """
    Function to get the financial of a company
    :Parameters:
    ticker: str
        Valid inputs: TSLA, AAPL, ..., you can get them from get_tickers
    """
    tck = yf.Ticker(ticker)
    df = tck.get_financials()
    df.to_csv(f"../data/{ticker.lower()}_financials.csv")
    return f"Saved the information in ../data/{ticker.lower()}_financials.csv, this is a preview \n" + df.head().to_markdown() 


@tool
def get_multiple_financials(tickers: str) -> str:
    """
    Function to get the financials for multiple tickers
    Args:
        tickers (str): valid inputs are TSLA, AAPL, ..., you can get them from get_tickers

    Returns:
        str: Preview of the final dataframe with all the financials
    """
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
    df.to_csv(f"../data/{tickers.join("_").lower()}_financials.csv")
    return f"Saved the information in ../data/{tickers.join("_").lower()}_financials.csv, this is a preview \n" + df.head().to_markdown() 

@tool
def get_institutional_holders(ticker: str) -> str:
    """
    Function to get all the institutional holders of the ticker stock
    Args:
        ticker (str): valid inputs are TSLA, AAPL, ..., you can get them from get_tickers

    Returns:
        str: header of the saved file with the requested information
    """
    tck = yf.Ticker(ticker)
    df = tck.institutional_holders
    df.to_csv(f"../data/{ticker.lower()}_institutional_information.csv")
    return f"Saved the information in ../data/{ticker.lower()}_institutional_information.csv, this is a preview \n" + df.head().to_markdown() 

@tool
def get_ticker(company_name: str) -> str:
    """
    Get the ticker based on the company name
    Parameters:
    company_name: str
        Free text
    """
    yfinance_url = "https://query2.finance.yahoo.com/v1/finance/search"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    params = {"q": company_name, "quotes_count": 1, "country": "United States"}

    res = requests.get(url=yfinance_url, params=params, headers={'User-Agent': user_agent})
    data = res.json()

    return data['quotes'][0]['symbol'] if data and data["quotes"] else None