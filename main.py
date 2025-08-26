import csv

import random
import datetime
import pandas as pd

import requests
from bs4 import BeautifulSoup

stocks_bought = []
current_stocks = []
stock = []


def get_random_stock_data():
    num_of_lines = 0
    # checking line length of file
    with open('stocks.csv', encoding="utf8") as f:
        num_of_lines = len(f.readlines())

    random_number = random.randint(2, num_of_lines)
    lines = []
    # getting the data at the specified line from the stocks.csv file
    with open('stocks.csv', encoding="utf8") as f:
        for i, line in enumerate(f):
            if i == random_number - 1:
                lines.append(line.split(','))
    stock_ticker = ""
    stock_name = ""

    # some stocks in the file that i had got had ticker symbol first, some had the name first
    if len(lines[0][0].split()) > 1:
        stock_ticker = lines[0][1]
        stock_name = lines[0][0]
    else:
        stock_ticker = lines[0][0]
        stock_name = lines[0][1]

    get_yahoo_data(stock_ticker, stock_ticker)


def read_csv_file(csv_file):
    with open(csv_file, 'r') as file:
        csv_file_reader = csv.reader(file, delimiter=',')
        # checking if the share already has been bought and updating total shares bought etc
        for row in csv_file_reader:
            return row


# this finds the live stock data from yahoo finance
def get_yahoo_data(symbol, name="", limit=False, stop=False):
    from time import sleep
    from timeit import default_timer as timer

    import time
    start = timer()

    name = name.strip("")

    total_bought = 1

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
    yahoo_finance_url = f'https://finance.yahoo.com/quote/{symbol}'
    r = requests.get(yahoo_finance_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    previous_share_value = 0
    try:
        import yfinance as yf

        yfinance_ticker = yf.Ticker(symbol)
        if yfinance_ticker.info['longName'] != 'longName':
            name = yfinance_ticker.info['longName']
            share_value = soup.find('div', {'class': 'container svelte-mgkamr'}).find_all('fin-streamer')[0].text
            percentage_change = soup.find('div', {'class': 'container svelte-mgkamr'}).find_all('fin-streamer')[
                2].text
            change = soup.find('div', {'class': 'container svelte-mgkamr'}).find_all('fin-streamer')[1].text
            closing_time = soup.find('div', {'class': 'container svelte-mgkamr'}).find_all('fin-streamer')[0].text
            # gets rid of commas as with commas, errors are shown since it can not be converted to float
            share_value = share_value.replace(",", "")
            total_share_average = float(share_value)

            if limit:
                print("Current price of stock is: " + share_value)

                max_asked_price = float(input("Set the maximum price you are willing to pay per share"))
                if isfloat(max_asked_price):
                    sleep(5)
                    share_value = soup.find('div', {'class': 'container svelte-mgkamr'}).find_all('fin-streamer')[
                        0].text
                    total_bought = float(share_value)

                    if total_bought > max_asked_price:
                        print("The asking stock price has not been reached and so cannot be bought")
                        exit()

            elif stop:
                print("Current price of stock is: " + share_value)
                stop_asked_price = float(
                    input("Set a price above the current price that converts your order to a market order"))
                if isfloat(stop_asked_price):
                    sleep(5)
                    share_value = soup.find('div', {'class': 'container svelte-mgkamr'}).find_all('fin-streamer')[
                        0].text
                    total_bought = float(share_value)
                if total_bought < float(stop_asked_price):
                    print("The current stock price did not meet your requirment")
                    exit()

            # sometimes the price is not available and will give '-' as a share value so checking to see if the string could be a float
            if not isfloat(share_value):
                get_random_stock_data()

            row = read_csv_file('stockData.csv')
            # getting and storing data
            if row[0] == symbol:
                total_bought = float(row[5]) + 1
                previous_share_value = float(row[2])
                total_share_average = (previous_share_value + float(share_value)) / total_bought

            date_time = datetime.datetime.now()
            time = date_time.time().strftime('%H:%M:%S')
            return_on_investment = 0

            # if the stock has already been bought by the user before
            if total_bought > 1:
                return_on_investment = float(share_value) - float(previous_share_value)

                df = pd.read_csv('currentStocks.csv')
                df.loc[df["Ticker"] == symbol, "Return"] = return_on_investment
                df.loc[df["Ticker"] == symbol, "Share Value"] = total_bought
                df.loc[df["Ticker"] == symbol, "Shares"] = share_value
                df.to_csv("currentStocks.csv", index=False)

            stock_less_detail = {
                'Ticker': symbol,
                'Stock Name': name,
                'Share Value': share_value,
                'Shares': str(total_bought),
                'Share Average': str(total_share_average),
                'Return': return_on_investment

            }
            stock_to_find = {
                'Ticker': symbol,
                'Stock Name': name,
                'Share Value': share_value,
                'Change': change,
                'Percentage Change': percentage_change
            }
            stock_greater_detail = {
                'Ticker': symbol,
                'Stock Name': name,
                'Share Value': share_value,
                'Change': change,
                'Percentage Change': percentage_change,
                'Shares': str(total_bought),
                'Share Average': str(total_share_average),
                'Date Bought': date_time.strftime('%d/%m/%y'),
                'Time Bought': time
            }

            # only appends if the stock does not already exist or the share value is not found
            if share_value != '':
                stocks_bought.append(stock_greater_detail)
                print(stock_to_find)
                # only add unique stocks
                if total_bought == 1:
                    current_stocks.append(stock_less_detail)
            stock.append(stock_to_find)
            print("My program took", timer() - start, "to run")

            return stock_greater_detail

        return None







    # some stocks cannot be found on yahoo finance so they get deleted from the csv file
    except AttributeError:
        update_stocks_csv(symbol, name, remove=True)
    except Exception as e:
        print(e)


def update_stocks_csv(symbol, name, remove=False):
    import os
    temp_file = 'stocks_temp.csv'
    with open('stocks.csv', 'r', encoding="utf8") as inp, open(temp_file, 'w', encoding="utf8", newline='') as out:
        writer = csv.writer(out)
        for row in csv.reader(inp):
            if remove and row[0] != symbol and row[1] != name:
                writer.writerow(row)
            elif not remove:
                writer.writerow(row)

    os.replace(temp_file, 'stocks.csv')


# find info on a stock
def findStock():
    ticker_symbol = input("Enter in the Ticker Symbol of the stock: ")
    get_yahoo_data(ticker_symbol, "")
    if len(ticker_symbol) == 0:
        print("No ticker symbol was entered")
    elif len(stock) == 0:
        print("'" + ticker_symbol + "'" + " Could not be found")


# produces a report from currentStocks.csv
def produces_a_report():
    import datetime
    stocks_list = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}

    ticker_name = ""
    csv_filename = ""
    with open("currentStocks.csv", 'r') as file:
        csv_file_reader = csv.reader(file, delimiter=',')
        # checking if the share already has been bought and updating total shares bought etc
        for row in csv_file_reader:
            if row[0] != "Ticker":
                ticker_name = row[0]
                stock_name = row[1]

                fetched_return_on_investment = row[5]
                fetched_share_average = float(row[4])
                share_details = (get_yahoo_data(ticker_name))

                print(ticker_name)
                if share_details is not None:

                    share_value = share_details['Share Value']

                    difference_in_stock_price = (fetched_share_average - float(share_value))
                    growth = difference_in_stock_price / float(share_value)

                    return_on_investment = float(share_value) - float(fetched_share_average)

                    date_time = datetime.datetime.now()

                    stock = {
                        'Ticker': ticker_name,
                        'Stock Name': stock_name,
                        'Share Average': fetched_share_average,
                        'Current Price': share_value,
                        'Return': return_on_investment,
                        'Date': date_time.strftime('%d/%m/%y'),
                        'Time': date_time.time().strftime('%H:%M:%S')
                    }
                    stocks_list.append(stock)
                    date_time = datetime.datetime.now()
                    date_time_as_a_string = date_time.strftime('%d-%m-%y')
                    csv_filename = "StockDataOf-" + date_time_as_a_string + ".csv"
                with open(("CurrentStockHistory/" + csv_filename), 'w', newline='') as f:

                    fieldnames = ['Ticker', 'Stock Name', 'Share Average', 'Current Price', 'Return', 'Date', 'Time']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for stock in stocks_list:
                        writer.writerow({fieldnames[0]: stock[fieldnames[0]], fieldnames[1]: stock[fieldnames[1]],
                                         fieldnames[2]: stock[fieldnames[2]], fieldnames[3]: stock[fieldnames[3]],
                                         fieldnames[4]: stock[fieldnames[4]], fieldnames[5]: stock[fieldnames[5]],
                                         fieldnames[6]: stock[fieldnames[6]]})


def isInt(num):
    try:
        int(num)
        return True
    except ValueError:
        print("int Error")
        return False


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        print("Float Error")
        return False


def user_managed_stock_buy():
    while True:
        stock_ticker = input(print("Enter in the stock ticker you wish to buy"))
        stock_amount = int(input(print("Enter in the number of the stock you wish to buy")))
        if isInt(stock_amount):
            buy_type = int(input("Choose from:\nMarket Price[1]\nLimit Order[2]\nStop Order[3]\nStop Limit[4]"))

            if isInt(stock_amount) and (isInt(stock_amount) > 0 or isInt(buy_type) < 5):
                int_buy_type = int(buy_type)
                match int_buy_type:
                    case 1:
                        for i in range(0, stock_amount):
                            get_yahoo_data(stock_ticker, "")
                    case 2:
                        get_yahoo_data(stock_ticker, "", True)



# produces a report every month
date_time = datetime.datetime.now()
day_of_the_week = date_time.isoweekday()
if day_of_the_week < 6:
    oldest_date = ""

    with open('lastRan.csv', 'r') as file:
        csv_file_reader = csv.reader(file, delimiter=',')
        for row in csv_file_reader:
            if row[0] != 'Date':
                oldest_date = row[0]
                break


    current_date = date_time.strftime('%d')
    if current_date == oldest_date.split("-")[0]:

        produces_a_report()
        print("Report produced")

    else:

        get_random_stock_data()

        with open('stockData.csv', 'a', newline='') as f:
            fieldnames = ['Ticker', 'Stock Name', 'Share Value', 'Change', 'Percentage Change', 'Shares', 'Share Average',
                          'Date Bought', 'Time Bought']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            for stock in stocks_bought:
                writer.writerow({fieldnames[0]: stock[fieldnames[0]], fieldnames[1]: stock[fieldnames[1]],
                                 fieldnames[2]: stock[fieldnames[2]], fieldnames[3]: stock[fieldnames[3]],
                                 fieldnames[4]: stock[fieldnames[4]], fieldnames[5]: stock[fieldnames[5]],
                                 fieldnames[6]: stock[fieldnames[6]], fieldnames[7]: stock[fieldnames[7]],
                                 fieldnames[8]: stock[fieldnames[8]]})

        with open('currentStocks.csv', 'a', newline='') as f:

            fieldnames = ['Ticker', 'Stock Name', 'Share Value',
                          'Shares', 'Share Average', 'Return']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            for stock in current_stocks:
                writer.writerow({fieldnames[0]: stock[fieldnames[0]], fieldnames[1]: stock[fieldnames[1]],
                                 fieldnames[2]: stock[fieldnames[2]], fieldnames[3]: stock[fieldnames[3]],
                                 fieldnames[4]: stock[fieldnames[4]], fieldnames[5]: stock[fieldnames[5]]})

else:
    if day_of_the_week == 6:
        print("The Stock Market is closed on Saturdays")
    else:
        print("The Stock Market is closed on Sundays")
