import pandas as pd
import yfinance as yf
import os


def get_stock_data(tickers, start_date, end_date):
    data = {}
    for ticker in tickers:
        data[ticker] = yf.download(ticker, start=start_date, end=end_date)
    return data


def load_fear_and_greed_data(file_path):
    return pd.read_csv(file_path, parse_dates=["Date"], index_col="Date")


def calculate_transaction_fees(price, shares, action):
    fee = price * shares * 0.001425  
    tax = price * shares * 0.003 if action == "Sell" else 0  # only selling need tax!!!
    return round(fee, 2), round(tax, 2)


def execute_trading_strategy(stock_data, fgi_data, tickers, initial_cash=2000000, output_file="history.csv"):
    cash = initial_cash
    holdings = {ticker: 0 for ticker in tickers}  # 
    margin_debt = 0  # 保證金借款 in Chinese

    # add headers if file not exist
    if not os.path.exists(output_file):
        with open(output_file, "w") as f:
            f.write("台股代碼(名稱),交易類別,成交價(元),張數,手續費(張),證交稅(元),借券費(元),融資金額,收付金額,時間,市場情緒\n")
    for date in fgi_data.index:
        if date not in stock_data[tickers[0]].index:
            continue
        fgi = fgi_data.loc[date, 'Fear_and_Greed_Index']

        for ticker in tickers:
            close_price = stock_data[ticker].loc[date, ('Close',ticker)]
            transaction_log = []

            # stategic logic
            if fgi <= 25:  # Extreme Fear -> buy 4 
                shares = 4 
                cost = close_price * shares * 1000
                fee, tax = calculate_transaction_fees(close_price * 1000, shares, "Buy")
                if cash < cost + fee: # not enough money
                    continue
                else:
                    cash -= cost + fee
                holdings[ticker] += shares
                transaction_log.append({
                    "台股代碼(名稱)": ticker,
                    "交易類別": "現股買進",
                    "成交價(元)": close_price,
                    "張數": shares,
                    "手續費(張)": fee,
                    "證交稅(元)": tax,
                    "借券費(元)": 0,
                    "融資金額": 0,
                    "收付金額": -(cost + fee),
                    "時間": date.date(),
                    "市場情緒": "極度恐慌"
                })

            elif 26 <= fgi <= 44:  # Fear -> buy 2
                shares = 2
                cost = close_price * shares * 1000
                fee, tax = calculate_transaction_fees(close_price * 1000, shares, "Buy")
                if cash < cost + fee: # not enough money
                    continue
                else:
                    cash -= cost + fee
                holdings[ticker] += shares
                transaction_log.append({
                    "台股代碼(名稱)": ticker,
                    "交易類別": "現股買進",
                    "成交價(元)": close_price,
                    "張數": shares,
                    "手續費(張)": fee,
                    "證交稅(元)": tax,
                    "借券費(元)": 0,
                    "融資金額": 0,
                    "收付金額": -(cost + fee),
                    "時間": date.date(),
                    "市場情緒": "恐慌"
                })
            elif 45 <= fgi <= 55:  # Neutral -> hold
                 continue
            elif 56 <= fgi <= 74:  # Greed -> sell 2
                shares = min(2, holdings[ticker])  
                if shares > 0: # enough share
                    cost = close_price * shares * 1000
                    fee, tax = calculate_transaction_fees(close_price * 1000, shares, "Sell")
                    cash += cost - fee - tax
                    holdings[ticker] -= shares
                    transaction_log.append({
                        "台股代碼(名稱)": ticker,
                        "交易類別": "現股賣出",
                        "成交價(元)": close_price,
                        "張數": shares,
                        "手續費(張)": fee,
                        "證交稅(元)": tax,
                        "借券費(元)": 0,
                        "融資金額": 0,
                        "收付金額": cost - fee - tax,
                        "時間": date.date(),
                        "市場情緒": "貪婪"
                    })
            elif 75 <= fgi:  # Extreme Greed -> sell 4 
                shares = min(4, holdings[ticker])  
                if shares > 0: # enough share
                    cost = close_price * shares * 1000
                    fee, tax = calculate_transaction_fees(close_price * 1000, shares, "Sell")
                    cash += cost - fee - tax
                    holdings[ticker] -= shares
                    transaction_log.append({
                        "台股代碼(名稱)": ticker,
                        "交易類別": "現股賣出",
                        "成交價(元)": close_price,
                        "張數": shares,
                        "手續費(張)": fee,
                        "證交稅(元)": tax,
                        "借券費(元)": 0,
                        "融資金額": 0,
                        "收付金額": cost - fee - tax,
                        "時間": date.date(),
                        "市場情緒": "極度貪婪"
                    })
     
            if transaction_log:
                with open(output_file, "a") as f:
                    for log in transaction_log:
                        f.write(",".join(map(str, log.values())) + "\n")


    print(f"交易歷程已追加至 {output_file}")
    export_asset_summary(cash, holdings, margin_debt, stock_data, tickers)


def export_asset_summary(cash, holdings, margin_debt, stock_data, tickers, initial_cash=2000000, output_file="asset_summary.csv"):
    

    securities_value = sum(holdings[ticker] * stock_data[ticker].loc["2024-12-31", ('Close',ticker)] * 1000 for ticker in tickers)
    net_assets = cash + securities_value - margin_debt
    profit = net_assets - initial_cash
    total_return_rate = (profit / initial_cash) * 100
    maintenance_ratio = net_assets / margin_debt if margin_debt > 0 else "N/A"
    # add headers if file not exist
    if not os.path.exists(output_file):
        with open(output_file, "w") as f:
            f.write("現金資產,證券資產,信用借款,淨資產,獲利,總報酬率(%),整戶維持率(%)\n")

    
    with open(output_file, "a") as f:
        f.write(
            f"{cash},{securities_value},{margin_debt},{net_assets},{profit},{total_return_rate},{maintenance_ratio}\n"
        )

    print(f"資產總計表已輸出至 {output_file}")

    # main
if __name__ == "__main__":
    # params
    tickers = ["00646.TW", "00662.TW", "00757.TW"]  
    start_date = "2024-09-03"  
    end_date = "2025-01-01" # need 1/1 to cover 12/31
    fgi_file_path = "./fear_and_greed_index.csv" 
    # fetch date
    stock_data = get_stock_data(tickers, start_date, end_date)
    fgi_data = load_fear_and_greed_data(fgi_file_path)
   
    execute_trading_strategy(stock_data, fgi_data, tickers)

