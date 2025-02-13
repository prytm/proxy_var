import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Load data
final_df = pd.read_csv('final_df.csv', delimiter=',')

# Judul Aplikasi
st.title('Perbandingan Saham')

# Input pengguna untuk target
st.header("Masukkan Data Saham Target")

# Menggunakan st.columns untuk mengatur layout
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    target_stock = st.text_input("Kode Saham Target (contoh: CBDK.JK):", value="CBDK.JK")
with col2:
    target_roa = st.number_input("Return on Assets (RoA) Target (%):", value=14.69)
with col3:
    target_mc = st.number_input("Market Cap Target (dalam Rupiah):", value=624462420000)
with col4:
    target_roe = st.number_input("Return on Equity (RoE) Target (%):", value=35.61)

# Daftar subsektor
subsektor_options = final_df['Sub Sektor'].unique().tolist()
target_subsektor = st.selectbox("Sub Sektor Target:", options=subsektor_options)

# Filter data sesuai subsektor
def filter_data():
    return final_df[(final_df['Sub Sektor'] == target_subsektor) & (final_df['Kode'] != target_stock)]

def plot_with_bollinger(stock_code):
    try:
        stock_data = yf.download(stock_code, period="1y")
        stock_data['SMA'] = stock_data['Close'].rolling(window=20).mean()
        stock_data['Upper'] = stock_data['SMA'] + (2 * stock_data['Close'].rolling(window=20).std())
        stock_data['Lower'] = stock_data['SMA'] - (2 * stock_data['Close'].rolling(window=20).std())

        plt.figure(figsize=(10, 5))
        plt.plot(stock_data['Close'], label=stock_code, color='blue')
        plt.plot(stock_data['SMA'], label='SMA 20', color='orange')
        plt.fill_between(stock_data.index, stock_data['Lower'], stock_data['Upper'], color='gray', alpha=0.2)
        plt.title(f'Bollinger Bands untuk {stock_code}')
        plt.xlabel('Tanggal')
        plt.ylabel('Harga Penutupan')
        plt.legend()
        st.pyplot(plt)
    except Exception as e:
        st.error(f"Error fetching data for {stock_code}: {e}")

# Menampilkan hasil saham yang dibandingkan
filtered_df = filter_data()
if not filtered_df.empty:
    st.write("Hasil Saham yang Dibandingkan dalam Sub Sektor:")
    st.dataframe(filtered_df[['Kode', 'RoA', 'Market Cap', 'RoE']])
    for stock in filtered_df['Kode'].head(3):
        plot_with_bollinger(stock)
else:
    st.warning("Tidak ada saham lain dalam subsektor yang dipilih.")
