import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

# Fungsi untuk membandingkan saham
def compare_stocks(target_stock, financial_table, consider_subsector=True):
    if target_stock not in financial_table['Kode'].values:
        st.error(f"Error: Saham {target_stock} tidak ditemukan dalam dataset.")
        return None, None

    stock_frequencies = {}
    comparison_results = {}
    
    if consider_subsector:
        target_subsektor = financial_table.loc[financial_table['Kode'] == target_stock, 'Sub_Sektor'].values[0]
        filtered_table = financial_table[(financial_table['Sub_Sektor'] == target_subsektor) & (financial_table['Kode'] != target_stock)]
    else:
        filtered_table = financial_table[financial_table['Kode'] != target_stock]
    
    if filtered_table.empty:
        st.warning("Tidak ada saham lain untuk dibandingkan.")
        return None, None

    for metric in financial_table.columns:
        if metric not in ['Kode', 'Sub_Sektor']:
            target_value = financial_table.loc[financial_table['Kode'] == target_stock, metric].values[0]
            differences = abs(filtered_table[metric] - target_value)
            sorted_differences = differences.sort_values().head(5)
            comparison_results[metric] = filtered_table.loc[sorted_differences.index, 'Kode'].tolist()
            
            for stock in filtered_table.loc[sorted_differences.index, 'Kode']:
                stock_frequencies[stock] = stock_frequencies.get(stock, 0) + 1
    
    sorted_frequencies = dict(sorted(stock_frequencies.items(), key=lambda item: item[1], reverse=True))
    return comparison_results, sorted_frequencies

# Fungsi untuk mengambil daily return
def get_daily_returns(stock_list, start_date="2023-12-01", end_date="2024-12-31"):
    data = yf.download(stock_list, start=start_date, end=end_date)['Close']
    return data.pct_change().dropna()

# Fungsi untuk menghitung VaR
def calculate_var(returns, confidence_level=0.95):
    return np.percentile(returns, 100 * (1 - confidence_level))

# Load dataset financial_table.csv
financial_table = pd.read_csv("financial_table.csv")

# Streamlit UI
st.title("Analisis Saham & Value at Risk (VaR)")
target_stock = st.text_input("Masukkan Kode Saham Target", "ANJT.JK")

if st.button("Analisis"):
    (results_with_subsektor, freq_with_subsektor) = compare_stocks(target_stock, financial_table, consider_subsector=True)
    (results_without_subsektor, freq_without_subsektor) = compare_stocks(target_stock, financial_table, consider_subsector=False)
    
    if results_with_subsektor and results_without_subsektor:
        first_subsektor_stock = list(freq_with_subsektor.keys())[0]
        first_not_subsektor_stock = list(freq_without_subsektor.keys())[0]

        # Ambil daily returns
        stock_list = [target_stock, first_subsektor_stock, first_not_subsektor_stock]
        daily_returns = get_daily_returns(stock_list)

        # Hitung VaR
        VaR_Subsektor = calculate_var(daily_returns[first_subsektor_stock])
        VaR_Not_Subsektor = calculate_var(daily_returns[first_not_subsektor_stock])

        # Buat DataFrame untuk Violation Ratio
        result_df = pd.DataFrame({
            f'Return {target_stock}': daily_returns[target_stock],
            f'VaR {first_subsektor_stock}': VaR_Subsektor,
            f'VaR {first_not_subsektor_stock}': VaR_Not_Subsektor
        })
        result_df['VR With Subsektor'] = (result_df.iloc[:, 0] < result_df.iloc[:, 1]).astype(int)
        result_df['VR Without Subsektor'] = (result_df.iloc[:, 0] < result_df.iloc[:, 2]).astype(int)

        # Hitung Violation Ratio
        VR_Subsektor = result_df.iloc[:, 3].sum() / result_df.iloc[:, 3].count()
        VR_Not_Subsektor = result_df.iloc[:, 4].sum() / result_df.iloc[:, 4].count()

        # Tampilkan hasil
        st.subheader("Hasil Analisis")
        st.write(f"**Saham paling mirip dalam subsektor:** {first_subsektor_stock}")
        st.write(f"**Saham paling mirip di luar subsektor:** {first_not_subsektor_stock}")
        st.write(f"**VaR untuk {first_subsektor_stock} (dalam subsektor):** {VaR_Subsektor:.5f}")
        st.write(f"**VaR untuk {first_not_subsektor_stock} (di luar subsektor):** {VaR_Not_Subsektor:.5f}")
        st.write(f"**Violation Ratio dalam subsektor:** {VR_Subsektor:.5f}")
        st.write(f"**Violation Ratio di luar subsektor:** {VR_Not_Subsektor:.5f}")
        st.dataframe(result_df)
