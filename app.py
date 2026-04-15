import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression

# Konfigurasi Halaman agar responsif dan tidak menabrak
st.set_page_config(page_title="Dashboard Amang Farm", layout="wide")

st.title("🐄 Dashboard Analisis Cerdas Peternakan Sapi Perah")
st.markdown("Sistem otomatis untuk pembersihan, visualisasi, dan prediksi tren penjualan susu Amang Farm.")

# 1. Fitur Upload Dataset
uploaded_file = st.file_uploader("📂 Unggah file CSV Anda (Format: Tahun, Minggu Ke, Volume, Harga):", type=["csv"])

if uploaded_file is not None:
    # Membaca data
    df = pd.read_csv(uploaded_file)
    
    # ==========================================
    # 1. DATA CLEANING (Pembersihan Data)
    # ==========================================
    st.header("🧹 1. Pembersihan Data Otomatis")
    # Langkah awal kritis untuk memastikan kualitas dan integritas data[cite: 120, 121].
    
    jml_missing = df.isnull().sum().sum()
    if jml_missing > 0:
        df.dropna(how='all', inplace=True)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                # Mengisi nilai kosong dengan Median untuk menjaga akurasi[cite: 121].
                df[col] = df[col].fillna(df[col].median())
        
        object_cols = df.select_dtypes(include=['object']).columns
        for col in object_cols:
            df[col] = df[col].fillna("Tidak Diketahui")
        st.success(f"✅ Berhasil membersihkan {jml_missing} nilai kosong.")
    else:
        st.success("✅ Data Bersih: Tidak ditemukan nilai kosong[cite: 122].")

    # ==========================================
    # 2. PRE-PROCESSING & FILTERING
    # ==========================================
    # Penyiapan kolom esensial[cite: 124].
    if 'Volume Mingguan (Liter)' not in df.columns and 'Volume Harian (Liter)' in df.columns:
        df['Volume Mingguan (Liter)'] = df['Volume Harian (Liter)'] * 7

    # Filter Tahun di Sidebar agar area utama tetap rapi
    st.sidebar.header("⚙️ Pengaturan Filter")
    if 'Tahun' in df.columns:
        list_tahun = sorted(df['Tahun'].unique().tolist())
        opsi_tahun = ["Semua Tahun"] + list_tahun
        tahun_terpilih = st.sidebar.selectbox("Pilih Tahun Analisis:", opsi_tahun)
        df_final = df[df['Tahun'] == tahun_terpilih].copy() if tahun_terpilih != "Semua Tahun" else df.copy()
    else:
        df_final = df.copy()
        tahun_terpilih = "Semua Tahun"

    # Penyesuaian Kolom Bulan
    if 'Minggu Ke' in df_final.columns and 'Bulan' not in df_final.columns:
        df_final['Bulan'] = np.ceil(df_final['Minggu Ke'] / 4.33).astype(int).apply(lambda x: 12 if x > 12 else x)

    with st.expander("👀 Lihat Sampel Data Terproses"):
        st.dataframe(df_final.head())

    st.divider()

    # Pastikan kolom esensial ada sebelum visualisasi
    if 'Harga per Liter (Rp)' in df_final.columns and 'Volume Mingguan (Liter)' in df_final.columns:

        # ==========================================
        # 3. ANALISIS UNIVARIAT & BIVARIAT (Baris 1)
        # ==========================================
        st.header(f"📊 2. Analisis Deskriptif & Hubungan ({tahun_terpilih})")
        col1, col2 = st.columns(2)
        
        with col1:
            # Univariat: Distribusi Volume [cite: 260]
            fig_vol = px.histogram(df_final, x="Volume Mingguan (Liter)", nbins=20,
                                 title="Distribusi Volume Produksi", color_discrete_sequence=['#54A24B'])
            st.plotly_chart(fig_vol, use_container_width=True)
        
        with col2:
            # Bivariat: Pola Musiman per Bulan [cite: 263]
            vol_bulan = df_final.groupby('Bulan')['Volume Mingguan (Liter)'].mean().reset_index()
            fig_bulan = px.bar(vol_bulan, x='Bulan', y='Volume Mingguan (Liter)', 
                               title="Rata-rata Penjualan per Bulan (Pola Musiman)", color_continuous_scale='Blues')
            st.plotly_chart(fig_bulan, use_container_width=True)

        st.divider()

        # ==========================================
        # 4. ANALISIS MULTIVARIAT & KORELASI (Baris 2)
        # ==========================================
        st.header("🌐 3. Analisis Multivariat & Korelasi")
        col3, col4 = st.columns(2)

        with col3:
            # Korelasi Harga vs Volume [cite: 263]
            fig_korelasi = px.scatter(df_final, x="Harga per Liter (Rp)", y="Volume Mingguan (Liter)", 
                                      trendline="ols", title="Korelasi: Harga vs Volume Produksi",
                                      color_discrete_sequence=['#E45756'])
            st.plotly_chart(fig_korelasi, use_container_width=True)

        with col4:
            # Multivariat: Hubungan Kompleks [cite: 267]
            fig_multi = px.scatter(df_final, x="Minggu Ke", y="Volume Mingguan (Liter)", 
                                   size="Harga per Liter (Rp)", color="Bulan",
                                   title="Bubble Chart: Waktu vs Volume vs Harga")
            st.plotly_chart(fig_multi, use_container_width=True)

        st.divider()

        # ==========================================
        # 5. CHART TREND & PREDIKSI (BARIS 3 - FULL WIDTH)
        # ==========================================
        st.header("📈 4. Prediksi Tren Penjualan Masa Depan")
        st.markdown("Menggunakan model Regresi Linear untuk memprediksi volume penjualan pada tahun berikutnya.")

        # Persiapan Data Prediksi (Seluruh Data Historis)
        df_pred = df.sort_values(by=['Tahun', 'Minggu Ke']).reset_index()
        df_pred['Urutan_Waktu'] = df_pred.index + 1
        
        X = df_pred[['Urutan_Waktu']].values
        y = df_pred['Volume Mingguan (Liter)'].values

        model = LinearRegression()
        model.fit(X, y)

        # Prediksi 52 Minggu ke Depan (1 Tahun Berikutnya)
        minggu_ke_depan = 52
        last_index = df_pred['Urutan_Waktu'].max()
        future_X = np.array(range(last_index + 1, last_index + minggu_ke_depan + 1)).reshape(-1, 1)
        future_y = model.predict(future_X)

        # Dataframe untuk Plotting
        df_historis = pd.DataFrame({'Waktu': df_pred['Urutan_Waktu'], 'Volume': y, 'Status': 'Historis'})
        df_masa_depan = pd.DataFrame({'Waktu': future_X.flatten(), 'Volume': future_y, 'Status': 'Prediksi Masa Depan'})
        df_total_trend = pd.concat([df_historis, df_masa_depan])

        fig_trend = px.line(df_total_trend, x='Waktu', y='Volume', color='Status',
                            title="Proyeksi Penjualan Susu Amang Farm (Historis vs Prediksi)",
                            color_discrete_map={'Historis': '#4C78A8', 'Prediksi Masa Depan': '#E45756'})
        
        # Menambahkan garis tren linear (OLS)
        fig_trend.add_traces(px.scatter(df_total_trend, x='Waktu', y='Volume', trendline="ols").data[1])
        
        st.plotly_chart(fig_trend, use_container_width=True)

        # Interpretasi hasil untuk manajemen Amang Farm
        slope = model.coef_[0]
        arah = "naik" if slope > 0 else "turun"
        st.info(f"""
        **💡 Interpretasi Prediksi:**
        * Berdasarkan data historis, tren penjualan susu Amang Farm diprediksi akan terus **{arah}**.
        * Rata-rata perubahan volume produksi per minggu adalah **{abs(slope):.2f} Liter**.
        * **Rekomendasi:** Gunakan data ini untuk mengatur stok pakan dan kapasitas penyimpanan susu pada tahun mendatang[cite: 100].
        """)

    else:
        st.error("❌ File tidak memiliki kolom 'Harga per Liter (Rp)' atau 'Volume Mingguan (Liter)'.")
else:
    st.info("👈 Silakan unggah file CSV data penjualan Amang Farm untuk memulai.")
    
