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
col1, col2 = st.columns(2)  # Baris pertama: 2 kolom
col3, col4 = st.columns(2)  # Baris kedua: 2 kolom

# Input di baris pertama
with col1:
    target_stock = st.text_input("Kode Saham Target (contoh: CBDK.JK):", value="CBDK.JK")
with col2:
    target_roa = st.number_input("Return on Assets (RoA) Target (%):", value=14.69)

# Input di baris kedua
with col3:
    target_mc = st.number_input("Market Cap Target (dalam Rupiah):", value=624462420000)
with col4:
    target_roe = st.number_input("Return on Equity (RoE) Target (%):", value=35.61)

# Daftar pilihan subsektor
subsektor_options = [
    'Oil, Gas, & Coal', 'Basic Materials', 'Banks',
    'Healthcare Equipment & Providers', 'Software & IT Service',
    'Logistics & Deliveries', 'Food & Beverage', 'Industrial Goods',
    'Consumer Services', 'Telecommunication', 'Industrial Services',
    'Retailing', 'Automobiles & Components', 'Alternative Energy',
    'Media & Entertainment', 'Properties & Real Estate',
    'Heavy Constructions & Civil', 'Nondurable Household Products ',
    'Leisure Goods', 'Household Goods', 'Utilities',
    'Food & Staples Retailing ', 'Technology Hardware',
    'Financing Service', 'Property & Real Estate',
    'Phramaceuticals & Healthcare', 'Utilites',
    'Multi Sector Holdings', 'Nondurable Household Products',
    'Apparel & Luxury Goods'
]

# Dropdown untuk memilih subsektor
target_subsektor = st.selectbox("Sub Sektor Target:", options=subsektor_options, index=subsektor_options.index('Property & Real Estate'))

# Konversi ke DataFrame
comparison_table = pd.DataFrame(final_df)

def calculate_percentage(filtered_table):
    """
    Menghitung persentase perbedaan dengan saham target.
    """
    total_percentage = {}
    percentage_details = {}

    for metric, target_value in zip(['RoA', 'Market Cap', 'RoE'], [target_roa, target_mc, target_roe]):
        differences = abs(filtered_table[metric] - target_value)
        percentage = (differences / abs(target_value)) * 100  # Gunakan abs untuk menghindari pembagian negatif
        filtered_table[f'{metric}_Percentage'] = percentage

        for stock, percent in zip(filtered_table['Kode'], percentage):
            if stock not in total_percentage:
                total_percentage[stock] = 0
                percentage_details[stock] = {}
            total_percentage[stock] += percent
            percentage_details[stock][metric] = percent

    # Urutkan berdasarkan total persentase terkecil (mendekati 0)
    sorted_total = sorted(total_percentage.items(), key=lambda x: abs(x[1]))[:3]

    return sorted_total, percentage_details

def compare_with_subsektor():
    """
    Membandingkan dengan saham dalam subsektor yang sama.
    """
    filtered_table = comparison_table[(comparison_table['Sub Sektor'] == target_subsektor) &
                                      (comparison_table['Kode'] != target_stock)]
    if filtered_table.empty:
        st.warning(f"Warning: Tidak ada saham lain dalam subsektor {target_subsektor} untuk dibandingkan.\n")
        return [], {}

    return calculate_percentage(filtered_table)

def compare_without_subsektor():
    """
    Membandingkan dengan semua saham tanpa mempertimbangkan subsektor.
    """
    filtered_table = comparison_table[comparison_table['Kode'] != target_stock]
    return calculate_percentage(filtered_table)

# Jalankan perbandingan
min_stocks_with_subsektor, details_with_subsektor = compare_with_subsektor()
min_stocks_without_subsektor, details_without_subsektor = compare_without_subsektor()

# Fungsi untuk membuat DataFrame dari hasil perbandingan
def create_result_df(sorted_stocks, details):
    """
    Membuat DataFrame dari hasil perbandingan.
    """
    data = []
    for stock, _ in sorted_stocks:
        row = {
            'Kode': stock,
            'RoA': f"{details[stock]['RoA']:.2f}%",
            'Market Cap': f"{details[stock]['Market Cap']:.2f}%",
            'RoE': f"{details[stock]['RoE']:.2f}%"
        }
        data.append(row)
    return pd.DataFrame(data)

# Fungsi untuk menghitung Bollinger Bands
def calculate_bollinger_bands(data, window=15):
    """
    Menghitung Bollinger Bands.
    """
    sma = data.rolling(window=window).mean()
    std = data.rolling(window=window).std()
    upper_band = sma + (2 * std)
    lower_band = sma - (2 * std)
    return sma, upper_band, lower_band

# Tampilkan hasil dengan subsektor jika ada
st.write("Hasil dengan Mempertimbangkan Sub Sektor")
if min_stocks_with_subsektor:
    df_with_subsektor = create_result_df(min_stocks_with_subsektor, details_with_subsektor)
    
    # Bagi layout menjadi dua kolom: DataFrame dan Plot
    col_df, col_plot = st.columns([1, 2])  # Tabel lebih kecil, grafik lebih besar
    
    with col_df:
        st.dataframe(df_with_subsektor)  # Gunakan dataframe interaktif
    
    with col_plot:
        subsektor_stock = min_stocks_with_subsektor[0][0]
        if not final_df[final_df['Kode'] == subsektor_stock].empty:
            target_date_subsektor = final_df[final_df['Kode'] == subsektor_stock]['Date'].iloc[0]
            try:
                st.write(f"Grafik Perubahan Harga Saham {subsektor_stock}")
                
                # Ambil data dari Yahoo Finance
                data = yf.download(subsektor_stock, start=target_date_subsektor, 
                                   end=pd.to_datetime(target_date_subsektor) + pd.DateOffset(years=1))['Close']
                daily_returns_1 = data.pct_change().dropna()
                
                # Hitung Bollinger Bands
                sma, upper_band, lower_band = calculate_bollinger_bands(daily_returns_1)

                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(daily_returns_1.index, daily_returns_1.values, label='Daily Return')
                ax.plot(sma, label='SMA (10)')
                ax.plot(upper_band, label='Upper Band', linestyle='dashed', linewidth=1.1)
                ax.plot(lower_band, label='Lower Band', linestyle='dashed', linewidth=1.1)
                ax.fill_between(daily_returns_1.index, lower_band, upper_band, color='gray', alpha=0.2)
                ax.set_title(f"Perubahan Harga Saham {subsektor_stock} dengan Bollinger Bands")
                ax.set_xlabel("Tanggal")
                ax.set_ylabel("Daily Returns")
                ax.legend()
                ax.grid(True)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error fetching data for {subsektor_stock}: {e}")
        else:
            st.warning(f"Data untuk {subsektor_stock} tidak ditemukan.")
else:
    st.write("Tidak ada hasil dalam subsektor yang sama.\n")
