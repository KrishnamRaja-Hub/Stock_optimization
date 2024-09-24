import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

# Define function to get Indian stock names from the uploaded CSV file
@st.cache_data
def get_indian_stocks():
    file_path = 'All_Indian_Stocks_listed_in_nifty500.csv'
    stocks_df = pd.read_csv(file_path)
    stocks_df['Symbol'] = stocks_df['Symbol'] + ".NS"
    indian_stocks = dict(zip(stocks_df['Symbol'], stocks_df['Company Name']))
    return indian_stocks

# Function to get stock data
@st.cache_data
def get_stock_data(tickers, start_date, end_date):
    data = {}
    for ticker in tickers:
        data[ticker] = yf.download(ticker, start=start_date, end=end_date)
    return data

# Function to fetch news articles based on stock names
@st.cache_data
def fetch_stock_news(stock_names):
    news_api_key = "3819888439ec456fa6ff0dfcfe9d6028"
    articles = []
    for stock_name in stock_names:
        # Use double quotes around the stock name for exact match and add more filters
        url = f'https://newsapi.org/v2/everything?q="{stock_name}"&apiKey={news_api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            news_data = response.json()
            for article in news_data['articles']:
                # Additional filtering to ensure the stock name is mentioned in the title or description
                if stock_name.lower() in article['title'].lower() or stock_name.lower() in article['description'].lower():
                    articles.append(article)
    return articles


def main():
    st.title('Indian Stock Portfolio Optimizer')

    # Get the list of Indian stocks
    indian_stocks = get_indian_stocks()

    # Sidebar for stock and date selection
    st.sidebar.header('Select Stocks and Time Period')

    # Step 1: Dropdown and search functionality for stock selection
    selected_stocks = st.sidebar.multiselect(
        'Select stocks for your portfolio:',
        options=list(indian_stocks.keys()),
        format_func=lambda x: indian_stocks[x],
        default=[]
    )

    # Step 2: Date input for selecting the time period
    start_date = st.sidebar.date_input(
        'Select start date:',
        pd.to_datetime('2022-01-01')
    )
    end_date = st.sidebar.date_input(
        'Select end date:',
        pd.to_datetime('2023-01-01')
    )

    # Ensure start date is before end date
    if start_date > end_date:
        st.sidebar.error('Error: End date must fall after start date.')
    else:
        # Step 3: Add the "Analyse" button to trigger the analysis
        if st.sidebar.button('Analyse'):
            if selected_stocks:
                # Fetch stock data after both stocks and time period are selected
                stock_data = get_stock_data(selected_stocks, start_date, end_date)

                # Display raw stock data
                st.subheader('Raw Stock Data')
                for ticker, data in stock_data.items():
                    st.write(f'{indian_stocks[ticker]} ({ticker}) Stock Data')
                    st.write(data)

                # Plot closing price for each stock
                st.subheader('Stock Price Visualizations')
                for ticker, data in stock_data.items():
                    fig = px.line(
                        data,
                        x=data.index,
                        y='Close',
                        title=f'{indian_stocks[ticker]} ({ticker}) Stock Price'
                    )
                    fig.update_xaxes(title_text='Date')
                    fig.update_yaxes(title_text='Closing Price (INR)')
                    st.plotly_chart(fig)

                # Additional analysis: Simple Moving Average (SMA)
                st.subheader('Simple Moving Average (SMA) Analysis')
                for ticker, data in stock_data.items():
                    sma_period = st.slider(
                        f'Select SMA period for {indian_stocks[ticker]} ({ticker}):',
                        min_value=1, max_value=100, value=20
                    )
                    data['SMA'] = data['Close'].rolling(window=sma_period).mean()

                    # Plot SMA
                    fig_sma = px.line(
                        data,
                        x=data.index,
                        y=['Close', 'SMA'],
                        title=f'{indian_stocks[ticker]} ({ticker}) Stock Price with {sma_period}-Day SMA'
                    )
                    fig_sma.update_xaxes(title_text='Date')
                    fig_sma.update_yaxes(title_text='Price (INR)')
                    st.plotly_chart(fig_sma)

                # Step 4: Fetch and display relevant news articles only for selected stocks
                st.subheader('Relevant News')
                selected_stock_names = [indian_stocks[ticker] for ticker in selected_stocks]
                news_articles = fetch_stock_news(selected_stock_names)

                if news_articles:
                    for article in news_articles:
                        st.write(f"**{article['title']}**")
                        st.write(article['description'])
                        st.write(f"[Read more]({article['url']})")
                else:
                    st.write("No relevant news articles found.")
            else:
                st.write("Please select at least one stock to analyse.")

if __name__ == "__main__":
    st.set_page_config(page_title='Indian Stock Portfolio Optimizer', page_icon=':chart_with_upwards_trend:')
    main()
