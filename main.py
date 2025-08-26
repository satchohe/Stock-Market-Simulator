import csv
import random
import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import os
import time

# Global lists
stocks_bought = []
current_stocks = []
stock_details = []


def get_random_stock_data():
    #Fetches a random stock ticker from stocks.csv and processes it.
    num_of_lines = 0
    try:
        with open('stocks.csv', encoding="utf8") as f:
            num_of_lines = len(f.readlines())
    except FileNotFoundError:
        print("stocks.csv not found.")
        return

    if num_of_lines <= 1:
        print("stocks.csv is empty or has no data.")
        return

    random_number = random.randint(2, num_of_lines)
    lines = []
    with open('stocks.csv', encoding="utf8") as f:
        for i, line in enumerate(f):
            if i == random_number - 1:
                lines.append(line.split(','))
                break

    if not lines:
        print("Could not retrieve a random line from stocks.csv.")
        return

    line_data = lines[0]
    stock_ticker = line_data[0].strip()
    stock_name = line_data[1].strip()

    get_yahoo_data(stock_ticker, stock_name)


def get_existing_stock_data(symbol):
    #Reads stock data for a given symbol from currentStocks.csv.
    try:
        df = pd.read_csv('currentStocks.csv')
        existing_stock = df[df["Ticker"] == symbol]
        if not existing_stock.empty:
            return existing_stock.iloc[0]
        return None
    except FileNotFoundError:
        return None


def get_yahoo_data(symbol, name="", shares_to_buy=1, order_type="market", max_price=None, stop_price=None):
    """
    Finds and processes live stock data from Yahoo Finance.
    Returns a dictionary of stock details or None if unsuccessful.
    """
    print(f"Fetching data for {symbol}...")
    start_time = time.time()

    try:
        yfinance_ticker = yf.Ticker(symbol)
        info = yfinance_ticker.info

        if not info or 'longName' not in info:
            print(f"Could not find valid data for {symbol}. Deleting from list.")
            update_stocks_csv(symbol, name, remove=True)
            return None

        name = info.get('longName', name)
        share_value = info.get('currentPrice')
        change = info.get('regularMarketChange')
        percentage_change = info.get('regularMarketChangePercent')

        if not isinstance(share_value, (float, int)):
            print(f"No current price available for {symbol}. Skipping.")
            return None

        # Handle different order types
        if order_type == "limit":
            if share_value > max_price:
                print(f"Current price of {share_value} is above your limit price of {max_price}. Order not executed.")
                return None

        if order_type == "stop":
            if share_value < stop_price:
                print(f"Current price of {share_value} is below your stop price of {stop_price}. Order not triggered.")
                return None
            print(f"Stop price of {stop_price} reached. Executing as a market order.")

        # If order is executed, proceed with purchase
        existing_stock = get_existing_stock_data(symbol)
        total_shares = shares_to_buy
        share_average = share_value
        return_on_investment = 0

        if existing_stock is not None:
            total_shares = existing_stock['Shares'] + shares_to_buy
            previous_total_value = existing_stock['Shares'] * existing_stock['Share Average']
            new_total_value = previous_total_value + (share_value * shares_to_buy)
            share_average = new_total_value / total_shares
            return_on_investment = (share_value - existing_stock['Share Average']) * existing_stock['Shares']

        date_time = datetime.datetime.now()

        stock_data = {
            'Ticker': symbol,
            'Stock Name': name,
            'Share Value': share_value,
            'Change': change,
            'Percentage Change': percentage_change,
            'Shares': total_shares,
            'Share Average': share_average,
            'Return': return_on_investment,
            'Date Bought': date_time.strftime('%d/%m/%y'),
            'Time Bought': date_time.time().strftime('%H:%M:%S')
        }

        print(stock_data)

        # Append to global lists
        stocks_bought.append(stock_data)
        stock_details.append(stock_data)

        if existing_stock is None:
            current_stocks.append({
                'Ticker': symbol,
                'Stock Name': name,
                'Share Value': share_value,
                'Shares': total_shares,
                'Share Average': share_average,
                'Return': return_on_investment
            })

        print(f"Program took {time.time() - start_time:.2f} seconds to run.")
        return stock_data

    except requests.exceptions.RequestException as e:
        print(f"Network error fetching data for {symbol}: {e}")
    except yf.exceptions.YFDownloadException as e:
        print(f"Yfinance download error for {symbol}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        update_stocks_csv(symbol, name, remove=True)

    return None


def update_stocks_csv(symbol, name, remove=False):
    #Removes a stock from the stocks.csv file if it's invalid.
    temp_file = 'stocks_temp.csv'
    try:
        with open('stocks.csv', 'r', encoding="utf8") as inp, open(temp_file, 'w', encoding="utf8", newline='') as out:
            writer = csv.writer(out)
            for row in csv.reader(inp):
                if remove and (row[0].strip() == symbol or row[1].strip() == name):
                    continue
                writer.writerow(row)
        os.replace(temp_file, 'stocks.csv')
    except FileNotFoundError:
        print("stocks.csv not found.")
    except Exception as e:
        print(f"Error updating stocks.csv: {e}")


def find_stock():
#Allows the user to search for and view details of a specific stock.
    ticker_symbol = input("Enter in the Ticker Symbol of the stock: ").strip().upper()
    if not ticker_symbol:
        print("No ticker symbol was entered.")
        return

    data = get_yahoo_data(ticker_symbol, "")
    if not data:
        print(f"'{ticker_symbol}' could not be found.")


def produce_a_report():
    #Produces a report from currentStocks.csv.
    try:
        df = pd.read_csv("currentStocks.csv")
        if df.empty:
            print("No stocks to report on.")
            return

        report_stocks = []
        for index, row in df.iterrows():
            ticker_name = row['Ticker']
            stock_name = row['Stock Name']
            fetched_share_average = row['Share Average']

            # Fetch the latest data for the report
            share_details = get_yahoo_data(ticker_name, stock_name, shares_to_buy=0)

            if share_details is not None:
                current_price = share_details['Share Value']
                return_on_investment = (current_price - fetched_share_average) * row['Shares']
                date_time = datetime.datetime.now()

                report_stock = {
                    'Ticker': ticker_name,
                    'Stock Name': stock_name,
                    'Share Average': fetched_share_average,
                    'Current Price': current_price,
                    'Return': return_on_investment,
                    'Date': date_time.strftime('%d/%m/%y'),
                    'Time': date_time.time().strftime('%H:%M:%S')
                }
                report_stocks.append(report_stock)

        if report_stocks:
            date_time_as_a_string = datetime.datetime.now().strftime('%d-%m-%y')
            csv_filename = f"CurrentStockHistory/StockDataOf-{date_time_as_a_string}.csv"

            with open(csv_filename, 'w', newline='') as f:
                fieldnames = ['Ticker', 'Stock Name', 'Share Average', 'Current Price', 'Return', 'Date', 'Time']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(report_stocks)
            print("Report produced successfully.")
        else:
            print("Could not produce a report. No valid stock data found.")

    except FileNotFoundError:
        print("currentStocks.csv not found.")


def user_managed_stock_buy():
    #Manages the user's stock purchase process with different order types.
    while True:
        stock_ticker = input("Enter the stock ticker you wish to buy: ").strip().upper()
        if not stock_ticker:
            print("No ticker entered. Please try again.")
            continue

        try:
            stock_amount = int(input("Enter the number of shares you wish to buy: "))
            if stock_amount <= 0:
                print("Amount must be greater than zero.")
                continue
        except ValueError:
            print("Invalid input. Please enter a number for the amount of shares.")
            continue

        print("Choose from:")
        print("1. Market Order")
        print("2. Limit Order")
        print("3. Stop Order")
        print("4. Stop Limit Order")

        try:
            buy_type = int(input("Enter your choice (1-4): "))
        except ValueError:
            print("Invalid input. Please enter a number for the order type.")
            continue

        max_price = None
        stop_price = None

        if buy_type == 2:
            try:
                max_price = float(input("Set the maximum price you are willing to pay per share: "))
                get_yahoo_data(stock_ticker, "", shares_to_buy=stock_amount, order_type="limit", max_price=max_price)
            except ValueError:
                print("Invalid price. Please enter a number.")
        elif buy_type == 3:
            try:
                stop_price = float(input("Set the stop price (above current price) to trigger the buy: "))
                get_yahoo_data(stock_ticker, "", shares_to_buy=stock_amount, order_type="stop", stop_price=stop_price)
            except ValueError:
                print("Invalid price. Please enter a number.")
        elif buy_type == 4:
            print("Stop-limit order logic is not implemented in this version.")
        else:
            # Market order
            get_yahoo_data(stock_ticker, "", shares_to_buy=stock_amount, order_type="market")

        break


# Main execution logic
date_time = datetime.datetime.now()
day_of_the_week = date_time.isoweekday()

if day_of_the_week < 6:
    oldest_date = ""
    last_ran_file_exists = False
    try:
        with open('lastRan.csv', 'r') as file:
            csv_file_reader = csv.reader(file, delimiter=',')
            for row in csv_file_reader:
                if row[0] != 'Date':
                    oldest_date = row[0]
                    last_ran_file_exists = True
                    break
    except FileNotFoundError:
        print("lastRan.csv not found. Assuming first run.")

    current_date = date_time.strftime('%d')
    if last_ran_file_exists and current_date == oldest_date.split("-")[0]:
        produce_a_report()
    else:
        get_random_stock_data()

        # Writing to CSV files
        try:
            with open('stockData.csv', 'a', newline='') as f:
                fieldnames = ['Ticker', 'Stock Name', 'Share Value', 'Change', 'Percentage Change', 'Shares',
                              'Share Average',
                              'Date Bought', 'Time Bought']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if f.tell() == 0:
                    writer.writeheader()
                writer.writerows(stocks_bought)

            with open('currentStocks.csv', 'w', newline='') as f:  # Use 'w' to overwrite and update
                fieldnames = ['Ticker', 'Stock Name', 'Share Value', 'Shares', 'Share Average', 'Return']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(current_stocks)

            with open('lastRan.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Date'])
                writer.writerow([date_time.strftime('%d-%m-%y')])
        except Exception as e:
            print(f"Error writing to CSV files: {e}")

else:
    if day_of_the_week == 6:
        print("The Stock Market is closed on Saturdays.")
    else:
        print("The Stock Market is closed on Sundays.")