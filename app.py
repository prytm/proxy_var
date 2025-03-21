import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy.spatial.distance import mahalanobis

# Load data
final_df = pd.read_csv('final_df.csv', delimiter=',')
df_var = pd.read_csv('df_var.csv', delimiter = ',')

st.set_page_config(
    page_title="Risk Projection",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Custom CSS to inject into Streamlit
st.markdown("""
<style>

/* Adjust the size and alignment of the CALL and PUT value containers */
.metric-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 8px;
    width: auto;
    margin: 0 auto;
}

/* Custom classes for CALL and PUT values */
.metric-99 {
    background-color: #90ee90; /* Light green background */
    color: black; /* Black font color */
    margin-right: 10px; /* Spacing between CALL and PUT */
    border-radius: 10px; /* Rounded corners */
}

.metric-1 {
    background-color: #ffcccb; /* Light red background */
    color: black; /* Black font color */
    border-radius: 10px; /* Rounded corners */
}

/* Style for the value text */
.metric-value {
    font-size: 1.5rem; /* Adjust font size */
    font-weight: bold;
    text-align: center;
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

    target_stock = st.text_input("Stock Target Code (ex: KAQI.JK):", value = "KAQI.JK")
    target_aset = st.number_input("Total Assets Target (in IDR):", value=74129409370)
    target_eku = st.number_input("Total Equities Target (in IDR):", value=59158929209)
    target_mc = st.number_input("Market Cap Target (in IDR):", value=531000000)
    target_laba = st.number_input("net Profit Current Year Period (in IDR):", value=73414622023)

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

    # Informasi tempat mendapatkan data
    st.markdown("---")
    st.markdown("Get the financial report IPO data from<br>**[e-IPO Indonesia](https://e-ipo.co.id/)**", unsafe_allow_html=True)
    
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
        filtered_table = comparison_table[ (comparison_table['Kode'] != target_stock)]
    
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

subsektor_stock = min_stocks_with_subsektor[0][0]
subsektor_data = df_var[df_var['Kode'] == subsektor_stock]
var = subsektor_data['VaR'].values[0]

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
def calculate_bollinger_bands(data, window=10):
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
    "Market Cap" : [target_mc],
    "Total Equities" : [target_eku],
    "Net Income" : [target_laba]
}
input_df = pd.DataFrame(input_data)
st.table(input_df)

# VaR Value

st.markdown(f"""
    <div class = "metric-container metric-1">
        <div>
            <div class = "metric-label">📉 Value at Risk</div>
            <div class = "metric-value">{var:.2f}</div>
        </div>
    </div>
""", unsafe_allow_html = True)

st.markdown("")
st.markdown("")

st.header("Weekly Returns Plot Projection")
st.info("Explore how the daily returns projection with 95% confidence interval Moving Average fluctuate 3 months after IPO")

subsektor_stock = min_stocks_with_subsektor[0][0]
target_date_subsektor = final_df[final_df['Kode'] == subsektor_stock]['Date'].iloc[0]

try:
    data = yf.download(subsektor_stock, start=target_date_subsektor, end=pd.to_datetime(target_date_subsektor) + pd.DateOffset(months = 3), interval = '1d')['Close']
    daily_returns_1 = data.pct_change().dropna()

    sma, upper_band, lower_band = calculate_bollinger_bands(daily_returns_1)

    data = data.squeeze()
    sma = sma.squeeze()
    upper_band = upper_band.squeeze()
    lower_band = lower_band.squeeze()

    plt.style.use('dark_background')  # Gunakan style dark
    
    plt.figure(figsize=(12, 5))
    plt.plot(daily_returns_1.index, daily_returns_1.values, label='Daily Return', color='cyan')
    plt.plot(sma, label='SMA (10)', color='orange')
    plt.plot(upper_band, label='Upper Band', linestyle='dashed', linewidth=1.1, color='green', alpha = 0.5)
    plt.plot(lower_band, label='Lower Band', linestyle='dashed', linewidth=1.1, color='red', alpha = 0.5)
    plt.fill_between(daily_returns_1.index, lower_band, upper_band, color='gray', alpha=0.2)
    
    plt.title(f"{subsektor_stock} Weekly Returns", color='white')
    plt.xlabel("Date", color='white')
    plt.ylabel("Weekly Returns", color='white')
    plt.tick_params(colors='white')  # Warna sumbu x & y
    plt.legend()
    plt.grid(True, color='gray', alpha = 0.5)
    st.pyplot(plt)
except Exception as e:
    st.error(f"Error fetching data for {subsektor_stock}: {e}")
    st.write("Tidak ada hasil")

st.header("Closest Stocks")

st.write("Closest stocks considering Sub-Sector")
if min_stocks_with_subsektor:
    df_with_subsektor = create_result_df(min_stocks_with_subsektor, details_with_subsektor)
    st.dataframe(df_with_subsektor, use_container_width=True)  # Perbaikan di sini

# Bagian tanpa subsektor
st.write("Closest stocks without considering Sub-Sector")
if min_stocks_without_subsektor:
    df_without_subsektor = create_result_df(min_stocks_without_subsektor, details_without_subsektor)
    st.dataframe(df_without_subsektor, use_container_width=True)  # Perbaikan di sini
