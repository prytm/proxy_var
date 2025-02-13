import streamlit as st
import pandas as pd

final_df = pd.read_csv('final_df.csv', delimiter = ',')

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

# Konversi ke DataFrame (pastikan final_df sudah didefinisikan)
comparison_table = pd.DataFrame(final_df)  # Ganti dengan data Anda

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
            'Persentase RoA': details[stock]['RoA'],
            'Persentase MC': details[stock]['Market Cap'],
            'Persentase RoE': details[stock]['RoE']
        }
        data.append(row)
    return pd.DataFrame(data)

# Tampilkan hasil dengan subsektor jika ada
st.header("Hasil dengan Mempertimbangkan Sub Sektor")
if min_stocks_with_subsektor:
    df_with_subsektor = create_result_df(min_stocks_with_subsektor, details_with_subsektor)
    st.write(df_with_subsektor)
else:
    st.write("Tidak ada hasil dalam subsektor yang sama.\n")

# Tampilkan hasil tanpa subsektor
st.header("Hasil tanpa Mempertimbangkan Sub Sektor")
if min_stocks_without_subsektor:
    df_without_subsektor = create_result_df(min_stocks_without_subsektor, details_without_subsektor)
    st.write(df_without_subsektor)
else:
    st.write("Tidak ada hasil yang ditemukan.\n")
