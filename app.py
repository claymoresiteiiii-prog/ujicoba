import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Dashboard Analisis Amang Farm", layout="wide")

st.title("🐄 Dashboard Analisis Data Peternakan Sapi Perah")
st.markdown("""
Aplikasi ini melakukan analisis data secara Univariat, Bivariat, dan Multivariat 
dari dataset operasional peternakan susu sapi.
""")

# 1. Upload Dataset
uploaded_file = st.file_uploader("Unggah file CSV Anda (misal: data_susu_sapi_dengan_laba.csv)", type=["csv"])

if uploaded_file is not None:
    # Membaca data
    df = pd.read_csv(uploaded_file)
    
    # Feature Engineering Sederhana: Membuat kolom Bulan dari Minggu Ke-
    if 'Minggu Ke' in df.columns and 'Bulan' not in df.columns:
        df['Bulan'] = np.ceil(df['Minggu Ke'] / 4.33).astype(int)
        # Membatasi maksimal bulan 12
        df['Bulan'] = df['Bulan'].apply(lambda x: 12 if x > 12 else x)

    st.subheader("Preview Data")
    st.dataframe(df.head())

    st.divider()

    # ==========================================
    # 2. ANALISIS UNIVARIAT
    # ==========================================
    st.header("📊 1. Analisis Univariat")
    st.markdown("Melihat distribusi masing-masing variabel secara mandiri.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribusi Harga Susu (Rp/Liter)")
        if 'Harga per Liter (Rp)' in df.columns:
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.histplot(df['Harga per Liter (Rp)'], kde=True, color='skyblue', ax=ax)
            ax.set_title('Rentang Harga yang Paling Sering Terjadi')
            ax.set_xlabel('Harga per Liter (Rp)')
            st.pyplot(fig)
            
    with col2:
        st.subheader("Distribusi Volume Mingguan")
        if 'Volume Mingguan (Liter)' in df.columns:
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.boxplot(y=df['Volume Mingguan (Liter)'], color='lightgreen', ax=ax)
            ax.set_title('Sebaran dan Outlier Volume Susu Mingguan')
            st.pyplot(fig)

    st.divider()

    # ==========================================
    # 3. ANALISIS BIVARIAT
    # ==========================================
    st.header("📈 2. Analisis Bivariat")
    st.markdown("Menganalisis hubungan antar dua variabel.")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Pola Musiman: Bulan vs Volume Susu")
        if 'Bulan' in df.columns and 'Volume Mingguan (Liter)' in df.columns:
            # Mengelompokkan rata-rata volume per bulan
            monthly_vol = df.groupby('Bulan')['Volume Mingguan (Liter)'].mean().reset_index()
            fig = px.bar(monthly_vol, x='Bulan', y='Volume Mingguan (Liter)', 
                         title='Rata-rata Penjualan/Produksi Susu per Bulan',
                         labels={'Bulan': 'Bulan ke-', 'Volume Mingguan (Liter)': 'Rata-rata Volume (L)'},
                         color='Volume Mingguan (Liter)', color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("Korelasi Harga vs Volume")
        if 'Harga per Liter (Rp)' in df.columns and 'Volume Mingguan (Liter)' in df.columns:
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.scatterplot(data=df, x='Harga per Liter (Rp)', y='Volume Mingguan (Liter)', alpha=0.6, ax=ax)
            sns.regplot(data=df, x='Harga per Liter (Rp)', y='Volume Mingguan (Liter)', scatter=False, color='red', ax=ax)
            ax.set_title('Apakah Harga Mempengaruhi Volume Produksi?')
            st.pyplot(fig)

    st.divider()

    # ==========================================
    # 4. ANALISIS MULTIVARIAT
    # ==========================================
    st.header("🌐 3. Analisis Multivariat")
    st.markdown("Menganalisis interaksi tiga variabel atau lebih secara bersamaan (Waktu, Volume, Harga, dan Laba).")

    if all(col in df.columns for col in ['Tahun', 'Minggu Ke', 'Volume Mingguan (Liter)', 'Harga per Liter (Rp)']):
        st.subheader("Tren Penjualan (Volume, Harga, dan Tahun)")
        
        # Line chart dinamis menggunakan Plotly
        fig = px.line(df, x='Minggu Ke', y='Volume Mingguan (Liter)', color='Tahun',
                      hover_data=['Harga per Liter (Rp)'],
                      title="Perbandingan Tren Volume Produksi Susu Sepanjang Tahun",
                      markers=True)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Peta Hubungan Laba, Volume, dan Harga")
        # Scatter plot 3 dimensi atau Bubble Chart
        # X: Harga, Y: Volume, Size: Laba, Color: Tahun
        if 'Laba Pendapatan 2 Mingguan (Rp)' in df.columns:
            # Filter laba > 0 agar visualisasi lebih bersih (karena laba dihitung per 2 minggu)
            df_laba = df[df['Laba Pendapatan 2 Mingguan (Rp)'] > 0]
            
            fig2 = px.scatter(df_laba, x="Harga per Liter (Rp)", y="Volume Mingguan (Liter)", 
                              size="Laba Pendapatan 2 Mingguan (Rp)", color="Tahun",
                              hover_name="Minggu Ke", size_max=40,
                              title="Analisis Kinerja: Harga vs Volume vs Laba Berdasarkan Tahun")
            st.plotly_chart(fig2, use_container_width=True)
            
else:
    st.info("Silakan unggah file CSV di bagian atas untuk melihat hasil analisis.")
