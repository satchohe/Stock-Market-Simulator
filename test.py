import requests
from bs4 import BeautifulSoup
import json
from main import get_yahoo_data


class Test:
    def __init__(self):
        a = ""

        st = get_yahoo_data()
        st.get_yahoo_data(self, "aapl")
