# Financial Market Data Analyzer

A beginner-friendly market analytics dashboard built with Python, Pandas, NumPy, Matplotlib and Streamlit.

## Features
- Upload a CSV with a `Date` column and one price column per instrument
- Compare normalized price trends
- Calculate daily percentage returns
- Summarize total returns and annualized volatility
- View daily-return correlations
- Filter instruments and date range
- Preview and download selected price data

## Important data note
The included `data/sample_prices.csv` is **synthetic sample data**, generated only to demonstrate the app. It is not real market data and should not be described as live or historical exchange data.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run:
   ```bash
   streamlit run app.py
   ```
5. Open the local URL Streamlit prints in the terminal.

## CSV format
Your CSV should look like:

```csv
Date,Instrument_A,Instrument_B
2025-01-01,100,200
2025-01-02,101,198
2025-01-03,99,202
```

## Resume bullets (use only after running and understanding the app)
**Financial Market Data Analyzer | Python, Pandas, NumPy, Matplotlib, Streamlit**
- Built an interactive dashboard to compare instrument prices, daily returns, total performance and annualized volatility.
- Implemented date/instrument filtering, return-correlation analysis and CSV upload/download.
- Visualized normalized price trends and return correlations to explore market behavior.

## Interview talking points
- Why normalize prices to 100? It makes relative percentage performance comparable across instruments with different starting prices.
- Why use `pct_change()`? It computes period-over-period percentage changes.
- What does annualized volatility mean? Here it is daily-return standard deviation multiplied by √252.
- What does correlation mean? It measures linear co-movement between return series, not causation.
- What are limitations? The sample data are synthetic; results depend on data quality and selected period; this is not a trading strategy or investment recommendation.
