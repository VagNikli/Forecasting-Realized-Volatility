import pandas as pd
import numpy as np

# Load the CSV files
asml_path = r"C:\Users\vagel\Desktop\Python Challenge\ASML NA EQUITY.csv"
bmw_path = r"C:\Users\vagel\Desktop\Python Challenge\BMW GY EQUITY.csv"

asml_data = pd.read_csv(asml_path)
bmw_data = pd.read_csv(bmw_path)

# Convert timestamp column to datetime
asml_data['timestamp'] = pd.to_datetime(asml_data['timestamp'])
bmw_data['timestamp'] = pd.to_datetime(bmw_data['timestamp'])

# Sort the data by timestamp
asml_data = asml_data.sort_values(by='timestamp')
bmw_data = bmw_data.sort_values(by='timestamp')

# Filter data to contain only 9:00 AM to 5:29 PM
def filter_data_by_time(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])  # Ensure timestamp is datetime
    df_filtered = df[(df['timestamp'].dt.hour >= 9) & (df['timestamp'].dt.hour <= 17)]
    df_filtered = df_filtered[(df_filtered['timestamp'].dt.minute >= 0) & (df_filtered['timestamp'].dt.minute <= 29)]
    return df_filtered

# Calculate log returns
def calculate_log_returns(prices):
    log_returns = []
    for i in range(1, len(prices)):
        log_returns.append(np.log(prices[i] / prices[i - 1]))
    return log_returns

def calculate_realized_volatility(prices, sod, eod):
    # Convert prices to a NumPy array for correct indexing
    prices = np.array(prices)
    
    # Randomly select 5 points in chronological order
    random_indices = np.random.choice(len(prices), size=5, replace=False)
    selected_prices = np.sort(prices[random_indices])
    
    # Define the selected daily prices
    p1, p2, p3, p4, p5 = selected_prices
    
    # Calculate the log returns
    r1 = np.log(p1 / sod)
    r2 = np.log(p2 / p1)
    r3 = np.log(p3 / p2)
    r4 = np.log(p4 / p3)
    r5 = np.log(p5 / p4)
    r6 = np.log(eod / p5)
    
    # Calculate the realized volatility
    realized_volatility = np.sqrt((r1**2 + r2**2 + r3**2 + r4**2 + r5**2 + r6**2) / 6) * 16
    return realized_volatility

# Utilize Monte Carlo Simulation for each day
def monte_carlo_simulation(df, num_simulations=100):
    # Store the results of the volatility for each day
    results = []
    
    # Group data by date
    df['date'] = df['timestamp'].dt.date
    grouped_data = df.groupby('date')
    
    for date, data in grouped_data:
        # Extract SOD and EOD prices
        sod = data[data['timestamp'].dt.hour == 9].iloc[0]['price'] if not data[data['timestamp'].dt.hour == 9].empty else None
        eod = data[data['timestamp'].dt.hour == 17].iloc[-1]['price'] if not data[data['timestamp'].dt.hour == 17].empty else None
        
        # Check for missing SOD or EOD prices
        if sod is None or eod is None:
            print(f"Warning: Missing SOD or EOD price for {date}. Skipping this day.")
            continue
        
        # Get the prices for the day
        prices = data['price'].tolist()
        
        # Run the 100 Monte Carlo Simulation 
        volatilities = []
        for i in range(num_simulations):
            volatility = calculate_realized_volatility(prices, sod, eod)
            volatilities.append(volatility)
        
        # Compute the root mean squared of the volatilities
        rms_volatility = np.sqrt(np.mean(np.square(volatilities)))
        
        # Store the result
        results.append({'date': date, 'realized_volatility': rms_volatility})
    
    # Convert results to DataFrame and return
    return pd.DataFrame(results)

# Apply the filtering function to both datasets
asml_data_filtered = filter_data_by_time(asml_data)
bmw_data_filtered = filter_data_by_time(bmw_data)

# Run Monte Carlo Simulation for each stock
asml_results = monte_carlo_simulation(asml_data_filtered)
bmw_results = monte_carlo_simulation(bmw_data_filtered)

# Save the results to CSV
asml_results.to_csv('asml_realized_volatility.csv', index=False)
bmw_results.to_csv('bmw_realized_volatility.csv', index=False)

print(asml_results.head())
print(bmw_results.head())