import pandas as pd
import numpy as np
import logging
import os
from concurrent.futures import ProcessPoolExecutor


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Configuration Variables
data_path = ""  # Adjust if needed
simulations = 100  # Number of Monte Carlo runs per day
output_path = ""  # Ensure write permissions

def load_and_preprocess_data(file_path):
    """
    Loads and preprocesses stock data:
    - Converts timestamps
    - Sorts chronologically
    - Filters trading hours 09:00-17:29
    """
    try:
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(by='timestamp')

        # Filter market hours (09:00 to 17:29)
        df_filtered = df[(df['timestamp'].dt.strftime('%H:%M') >= '09:00') & 
                         (df['timestamp'].dt.strftime('%H:%M') <= '17:29')]

        return df_filtered

    except Exception as e:
        logging.error(f"Error loading file {file_path}: {e}")
        return None

def extract_sod_eod(df):
    """
    Extracts Start-of-Day (SOD) and End-of-Day (EOD) prices for each trading day.
    Handles missing timestamps by interpolating from nearby values.
    """
    sod_eod = {}
    df['date'] = df['timestamp'].dt.date
    grouped_data = df.groupby('date')

    for date, data in grouped_data:
        sod_row = data[data['timestamp'].dt.strftime('%H:%M') == '09:00']
        eod_row = data[data['timestamp'].dt.strftime('%H:%M') == '17:29']

        if sod_row.empty:
            sod = data.iloc[0]['price']  # Use first available price
        else:
            sod = sod_row.iloc[0]['price']

        if eod_row.empty:
            eod = data.iloc[-1]['price']  # Use last available price
        else:
            eod = eod_row.iloc[0]['price']

        sod_eod[date] = (sod, eod)

    return sod_eod

def calculate_realized_volatility(prices, sod, eod):
    """
    Computes the realized volatility using:
    - Random selection of 5 intraday prices (chronologically sorted).
    - Calculation of log returns.
    - RMS of log returns to compute realized volatility.
    """
    prices = np.array(prices)

    if len(prices) < 6:  # Need at least 6 points (SOD + 5 intraday + EOD)
        return None

    # Select 5 **unique** random indices within valid intraday range
    random_indices = np.sort(np.random.choice(len(prices) - 2, size=5, replace=False) + 1)
    selected_prices = prices[random_indices]

    p1, p2, p3, p4, p5 = selected_prices

    # Compute log returns
    log_returns = np.log([p1 / sod, p2 / p1, p3 / p2, p4 / p3, p5 / p4, eod / p5])

    # Compute realized volatility (annualized)
    return np.sqrt(np.mean(log_returns ** 2)) * 16

def monte_carlo_day(date, prices, sod, eod, num_simulations):
    """
    Runs Monte Carlo simulations for a single day.
    Returns a tuple (date, realized_volatility).
    """
    volatilities = [
        calculate_realized_volatility(prices, sod, eod)
        for _ in range(num_simulations)
    ]

    volatilities = [v for v in volatilities if v is not None]

    if volatilities:
        rms_volatility = np.sqrt(np.mean(np.square(volatilities)))
        return date, rms_volatility
    return date, None

def monte_carlo_simulation(df, sod_eod, num_simulations=simulations):
    """
    Runs Monte Carlo simulations in parallel for all available trading days.
    Uses multiprocessing to speed up calculations.
    """
    results = []
    df['date'] = df['timestamp'].dt.date
    grouped_data = df.groupby('date')

    with ProcessPoolExecutor() as executor:
        futures = []
        for date, data in grouped_data:
            if date not in sod_eod:
                continue

            sod, eod = sod_eod[date]
            prices = data['price'].values

            futures.append(executor.submit(monte_carlo_day, date, prices, sod, eod, num_simulations))

        # Collect results
        for future in futures:
            date, volatility = future.result()
            if volatility is not None:
                results.append({'Date': date, 'realized_volatility': volatility})
                print(f"Date: {date}, Realized Volatility: {volatility:.6f}")

    return pd.DataFrame(results)

def save_results(results, filename):
    """
    Saves the final results as a CSV file with error handling.
    """
    try:
        file_path = os.path.join(output_path, filename) if output_path else filename

        # Ensure file is not open in another program
        if os.path.exists(file_path):
            os.remove(file_path)  # Remove before writing to prevent conflicts

        results.to_csv(file_path, index=False)
        logging.info(f"Results saved to {file_path}")

    except Exception as e:
        logging.error(f"Error saving file {filename}: {e}")

def main():
    """
    Main function to execute the entire pipeline.
    """
    # File paths
    asml_file = os.path.join(data_path, 'ASML NA EQUITY.csv')
    bmw_file = os.path.join(data_path, 'BMW GY EQUITY.csv')

    # Load and preprocess data
    asml_data = load_and_preprocess_data(asml_file)
    bmw_data = load_and_preprocess_data(bmw_file)

    if asml_data is None or bmw_data is None:
        logging.error("Error loading data. Exiting.")
        return

    # Extract SOD and EOD prices
    asml_sod_eod = extract_sod_eod(asml_data)
    bmw_sod_eod = extract_sod_eod(bmw_data)

    # Run Monte Carlo simulations (Parallelized)
    print("\nCalculating realized volatility for ASML...\n")
    asml_results = monte_carlo_simulation(asml_data, asml_sod_eod)

    print("\nCalculating realized volatility for BMW...\n")
    bmw_results = monte_carlo_simulation(bmw_data, bmw_sod_eod)

    # Save results
    save_results(asml_results, 'asml_realized_volatility.csv')
    save_results(bmw_results, 'bmw_realized_volatility.csv')

if __name__ == "__main__":
    main()