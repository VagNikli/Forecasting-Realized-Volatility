# Realized Volatility Calculation for ASML and BMW Stocks

This project computes the daily realized volatility for two stocks, **ASML** and **BMW**, using minute-by-minute price data for 10 days. The methodology leverages Monte Carlo simulations and statistical techniques to calculate realized volatility based on randomly selected intraday price points.

---

## Project Objective

The goal is to calculate the daily realized volatility of two stocks by following these steps:
1. Select intraday price points randomly for each day.
2. Compute log returns from the selected price points.
3. Calculate realized volatility using the root mean squared formula.
4. Repeat the process 100 times for each day to obtain the final realized volatility.

---

## Methodology

The realized volatility is computed as follows:

1. **Extract Start of Day (SOD) and End of Day (EOD) Prices**:
   - SOD is the price at 9:00 AM.
   - EOD is the price at 5:29 PM.

2. **Randomly Select 5 Intraday Prices**:
   - Five random price points are chosen in chronological order between SOD and EOD.

3. **Calculate Log Returns**:
- Compute six log returns:
  - \( r_1 = \log(p_1 / \text{SOD}) \)
  - \( r_2 = \log(p_2 / p_1) \)
  - \( r_3 = \log(p_3 / p_2) \)
  - \( r_4 = \log(p_4 / p_3) \)
  - \( r_5 = \log(p_5 / p_4) \)
  - \( r_6 = \log(\text{EOD} / p_5) \)

4. **Calculate Realized Volatility**:
   - Compute the root mean squared of the log returns:
     \[
     \text{Realized Volatility} = \sqrt{\frac{r_1^2 + r_2^2 + r_3^2 + r_4^2 + r_5^2 + r_6^2}{6}} \times 16
     \]

5. **Monte Carlo Simulations**:
   - Perform 100 simulations per day with different random selections of intraday prices.
   - Compute the final realized volatility as the root mean squared of all simulated volatilities.

---

## Project Structure

- **`ASML NA EQUITY.csv`**: Contains minute-by-minute price data for ASML stock.
- **`BMW GY EQUITY.csv`**: Contains minute-by-minute price data for BMW stock.
- **`Realized_Vol_Python.py`**: Python script implementing the realized volatility calculation.
- **`asml_realized_volatility.csv`**: Output file containing realized volatility for ASML.
- **`bmw_realized_volatility.csv`**: Output file containing realized volatility for BMW.

---

## How to Run the Code

### Prerequisites

1. Install Python (version 3.6 or higher).
2. Install required libraries:
   ```bash
   pip install pandas numpy
## Steps to Execute

1. **Prepare the Dataset**:
   - Ensure the `ASML NA EQUITY.csv` and `BMW GY EQUITY.csv` files are in the same directory as the script.

2. **Run the Script**:
   - Execute the Python script:
     ```bash
     python Realized_Vol_Python.py
     ```

3. **Output**:
   - The script generates two CSV files:
     - `asml_realized_volatility.csv`
     - `bmw_realized_volatility.csv`


## Results

Each output CSV file contains the following columns:

- **Date**: The date for which the realized volatility is calculated.
- **Realized Volatility**: The calculated daily realized volatility based on 100 simulations.

---

## Additional Information

This project demonstrates the application of:

- **Monte Carlo Simulations**: To account for randomness in intraday price selection.
- **Statistical Analysis**: Using log returns and root mean squared techniques to measure volatility.

