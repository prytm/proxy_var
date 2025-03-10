import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy.spatial.distance import mahalanobis

# Load data
final_df = pd.read_csv('final_df (5).csv', delimiter=',')

st.set_page_config(
    page_title="Risk Projection",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded")

# Custom CSS to inject into Streamlit
st.markdown("""
<style>
/* Adjust the size and alignment of the CALL and PUT value containers */
.metric-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 8px; /* Adjust the padding to control height */
    width: auto; /* Auto width for responsiveness, or set a fixed width if necessary */
    margin: 0 auto; /* Center the container */
}

/* Custom classes for CALL and PUT values */
.metric-call {
    background-color: #90ee90; /* Light green background */
    color: black; /* Black font color */
    margin-right: 10px; /* Spacing between CALL and PUT */
    border-radius: 10px; /* Rounded corners */
}

.metric-put {
    background-color: #ffcccb; /* Light red background */
    color: black; /* Black font color */
    border-radius: 10px; /* Rounded corners */
}

/* Style for the value text */
.metric-value {
    font-size: 1.5rem; /* Adjust font size */
    font-weight: bold;
    margin: 0; /* Remove default margins */
}

/* Style for the label text */
.metric-label {
    font-size: 1rem; /* Adjust font size */
    margin-bottom: 4px; /* Spacing between label and value */
}

</style>
""", unsafe_allow_html=True)

# Navbar di sebelah kiri
with st.sidebar:
    st.title("📊 Risk-Projection Model")
    st.write("`Created by:`")
    linkedin_url = "https://www.linkedin.com/in/prytm/"
    st.markdown(f'<a href="{linkedin_url}" target="_blank" style="text-decoration: none; color: inherit;"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="25" height="25" style="vertical-align: middle; margin-right: 10px;">`Priya Tammam`</a>', unsafe_allow_html=True)

    target_stock = st.text_input("Stock Target Code (ex: CBDK.JK):", value = "CBDK.JK")
    target_aset = st.number_input("Total Aset Target (in IDR):", value=18156999226)
    target_eku = st.number_input("Total Ekuitas Target (in IDR):", value=8142575417)
    target_mc = st.number_input("Market Cap Target (in IDR):", value=2301591670000)
    target_laba = st.number_input("Laba Bersih Periode Tahun Berjalan (in IDR):", value=479102365)
    
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
    
def calculate_mahalanobis_distance(filtered_table, target_aset, target_mc, target_eku, target_laba):
    """
    Menghitung Mahalanobis Distance antara saham target dan saham lainnya.
    """
    features = ['Total Aset', 'Market Cap', 'Total Ekuitas', 'Laba Bersih']
    data = filtered_table[features]
    
    # Hitung matriks kovarians dan inversinya (gunakan pseudo-inverse)
    cov_matrix = np.cov(data.T)
    inv_cov_matrix = np.linalg.inv(cov_matrix)  # Gunakan pseudo-inverse agar tetap bisa dihitung
    
    # Buat vektor saham target
    target_vector = np.array([target_aset, target_mc, target_eku, target_laba])
    
    # Dictionary untuk menyimpan jarak Mahalanobis
    distance_details = {}
    
    # Hitung Mahalanobis Distance untuk setiap saham
    for index, row in filtered_table.iterrows():
        stock_vector = np.array(row[features])
        distance = mahalanobis(stock_vector, target_vector, inv_cov_matrix)
        distance_details[row['Kode']] = distance
    
    # Urutkan berdasarkan jarak terkecil
    sorted_distances = sorted(distance_details.items(), key=lambda x: x[1])[:3]
    
    return sorted_distances, distance_details
    
def compare_with_subsektor():
    """
    Membandingkan dengan saham dalam subsektor yang sama.
    """
    filtered_table = comparison_table[(comparison_table['Sub Sektor'] == target_subsektor) & 
                                      (comparison_table['Kode'] != target_stock)]
    if filtered_table.empty:
        print(f"Warning: Tidak ada saham lain dalam subsektor {target_subsektor} untuk dibandingkan.\n")
        return [], {}
    
    return calculate_mahalanobis_distance(filtered_table, target_aset, target_mc, target_eku, target_laba)
    
def compare_without_subsektor():
    """
    Membandingkan dengan semua saham tanpa mempertimbangkan subsektor.
    """
    filtered_table = comparison_table[comparison_table['Kode'] != target_stock]
    if filtered_table.empty:
        print("Warning: Tidak ada saham lain untuk dibandingkan.\n")
        return [], {}
    
    return calculate_mahalanobis_distance(filtered_table, target_aset, target_mc, target_aset, target_laba)

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
            'Distance': details[stock],
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
st.title("Mahalanobis Risk-Projection Model")

# Tabel Input
input_data = {
    "Stock" : [target_stock],
    "Total Assets" : [target_aset],
    "Market Cap" : [market_cap],
    "Total Equities" : [target_eku],
    "Net Income" : [target_laba]
}
input_df = pd.DataFrame(input_data)
st.table(input_df)

st.write("Results considering Sub-Sector")
if min_stocks_with_subsektor:
    df_with_subsektor = create_result_df(min_stocks_with_subsektor, details_with_subsektor)
    col_df, col_plot = st.columns(2)

    with col_df:
        st.write('Closest Stock Considering Sub-Sector')
        st.dataframe(df_with_subsektor, use_container_width=True)  # Perbaikan di sini

    with col_plot:
        subsektor_stock = min_stocks_with_subsektor[0][0]
        target_date_subsektor = final_df[final_df['Kode'] == subsektor_stock]['Date'].iloc[0]

        try:
            st.write(f"Daily Returns Graph; {subsektor_stock}")
            data = yf.download(subsektor_stock, start=target_date_subsektor, end=pd.to_datetime(target_date_subsektor) + pd.DateOffset(years=1), interval = '1wk')['Close']
            daily_returns_1 = data.pct_change().dropna()

            # Hitung Bollinger Bands
            sma, upper_band, lower_band = calculate_bollinger_bands(daily_returns_1)

            data = data.squeeze()
            sma = sma.squeeze()
            upper_band = upper_band.squeeze()
            lower_band = lower_band.squeeze()

            plt.figure(figsize=(12, 5)) # Ukuran plot disesuaikan
            plt.plot(daily_returns_1.index, daily_returns_1.values, label='Daily Return')
            plt.plot(sma, label='SMA (10)')
            plt.plot(upper_band, label='Upper Band', linestyle='dashed', linewidth=1.1)
            plt.plot(lower_band, label='Lower Band', linestyle='dashed', linewidth=1.1)
            plt.fill_between(daily_returns_1.index, lower_band, upper_band, color='gray', alpha=0.2)
            plt.title(f"{subsektor_stock} Daily Returns")
            plt.xlabel("Date")
            plt.ylabel("Daily Returns")
            plt.legend()
            plt.grid(True)
            st.pyplot(plt)
        except Exception as e:
            st.error(f"Error fetching data for {subsektor_stock}: {e}")
else:
    st.write("Tidak ada hasil dalam subsektor yang sama.\n")

# Bagian tanpa subsektor
st.write("Results without considering Sub-Sector")
if min_stocks_without_subsektor:
    df_without_subsektor = create_result_df(min_stocks_without_subsektor, details_without_subsektor)

    # Bagi layout menjadi dua kolom: DataFrame dan Plot
    col_df, col_plot = st.columns(2)

    with col_df:
        st.write('Closest Stock without Considering Sub-Sector')
        st.dataframe(df_without_subsektor, use_container_width=True)  # Perbaikan di sini

    with col_plot:
        not_subsektor_stock = min_stocks_without_subsektor[0][0]
        target_date_not_subsektor = final_df[final_df['Kode'] == not_subsektor_stock]['Date'].iloc[0]

        try:
            st.write(f"Daily Returns Graph; {not_subsektor_stock}")
            data = yf.download(not_subsektor_stock, start=target_date_not_subsektor, end=pd.to_datetime(target_date_not_subsektor) + pd.DateOffset(years=1),interval = '1wk')['Close']
            daily_returns_2 = data.pct_change().dropna()

            # Hitung Bollinger Bands
            sma, upper_band, lower_band = calculate_bollinger_bands(daily_returns_2)
            # Ubah menjadi 1D array
            data = data.squeeze()
            sma = sma.squeeze()
            upper_band = upper_band.squeeze()
            lower_band = lower_band.squeeze()

            plt.figure(figsize=(12, 5)) # Ukuran plot disesuaikan
            plt.plot(daily_returns_2.index, daily_returns_2.values, label='Daily Return')
            plt.plot(sma, label='SMA (10)')
            plt.plot(upper_band, label='Upper Band', linestyle='dashed', linewidth=1.1)
            plt.plot(lower_band, label='Lower Band', linestyle='dashed', linewidth=1.1)
            plt.fill_between(daily_returns_2.index, lower_band, upper_band, color='gray', alpha=0.2)
            plt.title(f"{not_subsektor_stock} Daily Returns")
            plt.xlabel("Date")
            plt.ylabel("Daily Returns")
            plt.legend()
            plt.grid(True)
            st.pyplot(plt)
        except Exception as e:
            st.error(f"Error fetching data for {not_subsektor_stock}: {e}")
else:
    st.write("Tidak ada hasil yang ditemukan.\n")
