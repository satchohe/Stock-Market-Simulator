Stock Portfolio Simulator
=========================

This project is a command-line application written in Python that simulates a simple stock portfolio management system. It fetches live stock data, allows the user to buy and sell stocks, and generates performance reports.

### Technologies Used

The application is built using a combination of Python's standard libraries and several external modules to handle financial data and file operations.

*   **Python**: The core programming language.
    
*   **yfinance**: A powerful and reliable library for fetching real-time and historical stock data from Yahoo Finance. This is the primary method for retrieving financial information.
    
*   **pandas**: A data analysis and manipulation library used for efficient handling of structured data, particularly for reading and writing CSV files.
    
*   **requests and BeautifulSoup**: These libraries are used for web scraping, providing a way to retrieve and parse HTML content from websites. While the code relies more heavily on yfinance, these libraries demonstrate the use of web scraping techniques.
    
*   **csv**: A built-in Python module for working with comma-separated value files.
    
*   **datetime**: A built-in Python module for handling dates and times, used for timestamping data.
    
*   **os**: A built-in Python module for interacting with the operating system, used to manage files.
    

### Key Features

*   **Live Stock Data**: Fetches real-time stock prices and information from Yahoo Finance.
    
*   **Order Types**: Supports different types of stock purchase orders, including:
    
    *   **Market Order**: Buys a stock immediately at the current market price.
        
    *   **Limit Order**: Buys a stock only if its price is at or below a specified maximum price.
        
    *   **Stop Order**: Converts to a market order to buy a stock once its price reaches a specified stop price.
        
*   **Portfolio Management**: Tracks shares bought, calculates the average share price, and determines the return on investment.
    
*   **File Storage**: Persists portfolio data by saving it to CSV files.
    
*   **Automated Reporting**: Automatically generates a daily report of the portfolio's performance.
