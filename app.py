import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Amang Farm", layout="wide")

st.title("🐄 Dashboard Analisis Cerdas Peternakan Sapi Perah")
st.markdown("Unggah file CSV Anda untuk melakukan pembersihan data, visualisasi, dan prediksi tren masa depan.")

# 1. Fitur Upload Dataset
uploaded_file = st.file_uploader("📂 Masukkan file CSV Anda di sini:", type=["csv"])

if uploaded_file is not None:
    # Membaca data
    df = pd.read_csv(uploaded_file)
    
    # ==========================================
    # DATA CLEANING (Penanganan Missing Values)
    # ==========================================
    st.header("🧹 1. Pembersihan Data Otomatis")
    
    jml_missing = df.isnull().sum().sum()
    
    if jml_missing > 0:
        df.dropna(how='all', inplace=True)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                df[col] = df[col].fillna(df[col].median())
        
        object_cols = df.select_dtypes(include=['object']).columns
        for col in object_cols:
            df[col] = df[col].fillna("Tidak Diketahui")
            
        st.success("✅ Pembersihan selesai: Data siap untuk pemodelan prediktif[cite: 121, 123].")
    else:
        st.success("✅ Data Bersih: Integritas data terjamin untuk analisis[cite: 122].")

    # ==========================================
    # PRE-PROCESSING & FILTERING
    # ==========================================
    # Standarisasi kolom esensial
    if 'Volume Mingguan (Liter)' not in df.columns and 'Volume Harian (Liter)' in df.columns:
        df['Volume Mingguan (Liter)'] = df['Volume Harian (Liter)'] * 7

    # Filter Tahun di Sidebar
    if 'Tahun' in df.columns:
        list_tahun = sorted(df['Tahun'].unique().tolist())
        opsi_tahun = ["Semua Tahun"] + list_tahun
        st.sidebar.header("⚙️ Pengaturan Filter")
        tahun_terpilih = st.sidebar.selectbox("Pilih Tahun Analisis:", opsi_tahun)
        
        df_final = df[df['Tahun'] == tahun_terpilih].copy() if tahun_terpilih != "Semua Tahun" else df.copy()
    else:
        df_final = df.copy()
        tahun_terpilih = "Semua Tahun"

    # Penyesuaian kolom waktu
    if 'Minggu Ke' in df_final.columns and 'Bulan' not in df_final.columns:
        df_final['Bulan'] = np.ceil(df_final['Minggu Ke'] / 4.33).astype(int).apply(lambda x: 12 if x > 12 else x)

    st.divider()

    # ==========================================
    # VISUALISASI DASAR (UNIVARIAT & BIVARIAT)
    # ==========================================
    if 'Harga per Liter (Rp)' in df_final.columns and 'Volume Mingguan (Liter)' in df_final.columns:
        
        # ... (Bagian Univariat & Bivariat tetap seperti kode Anda sebelumnya)
        st.header(f"📊 2. Analisis Deskriptif - Tahun {tahun_terpilih}")
        st.markdown("Menggambarkan data historis untuk memahami apa yang telah terjadi[cite: 133, 134].")
        # [Visualisasi Univariat & Bivariat Anda di sini]
        
        st.divider()

        # ==========================================
        # 📈 5. ANALISIS TREN & PREDIKSI (NEW)
        # ==========================================
        st.header("📈 5. Analisis Tren & Prediksi Penjualan")
        st.markdown("""
        Bagian ini menggunakan **Analisis Prediktif** untuk menjawab pertanyaan: *'Apa yang kemungkinan akan terjadi di masa depan?'*.
        """)

        # Menyiapkan data untuk regresi (X = Waktu/Minggu, Y = Volume)
        # Kita gunakan 'Minggu Ke' sebagai urutan waktu linear
        df_pred = df.sort_values(by=['Tahun', 'Minggu Ke'])
        
        # Membuat urutan waktu continuous (misal: Minggu 1 s/d 200)
        df_pred['Timeline'] = range(1, len(df_pred) + 1)
        
        X = df_pred[['Timeline']].values
        y = df_pred['Volume Mingguan (Liter)'].values

        # Membuat model Regresi Linear
        model = LinearRegression()
        model.fit(X, y)
        
        # Prediksi untuk 12 minggu ke depan (3 bulan)
        future_weeks = 12
        last_week = df_pred['Timeline'].max()
        X_future = np.array(range(last_week + 1, last_week + future_weeks + 1)).reshape(-1, 1)
        y_future = model.predict(X_future)

        # Gabungkan data historis dan prediksi untuk visualisasi
        hist_trace = pd.DataFrame({'Waktu': df_pred['Timeline'], 'Volume': y, 'Status': 'Historis'})
        future_trace = pd.DataFrame({'Waktu': X_future.flatten(), 'Volume': y_future, 'Status': 'Prediksi'})
        df_trend = pd.concat([hist_trace, future_trace])

        # Plotting Chart Trend
        fig_trend = px.line(df_trend, x='Waktu', y='Volume', color='Status',
                            title="Proyeksi Tren Penjualan Susu (Historis vs Masa Depan)",
                            labels={'Waktu': 'Urutan Minggu (Total)', 'Volume': 'Volume (Liter)'},
                            color_discrete_map={'Historis': '#4C78A8', 'Prediksi': '#E45756'})
        
        # Tambahkan garis tren (trendline) linear
        fig_trend.add_traces(px.scatter(df_trend, x='Waktu', y='Volume', trendline="ols").data[1])
        
        st.plotly_chart(fig_trend, use_container_width=True)

        # Interpretasi Prediksi
        slope = model.coef_[0]
        kondisi_tren = "MENINGKAT" if slope > 0 else "MENURUN"
        
        st.info(f"""
        **💡 Kesimpulan Prediksi Tren:**
        * Berdasarkan data historis, tren penjualan susu Amang Farm secara umum cenderung **{kondisi_tren}**.
        * Rata-rata perubahan volume setiap minggunya adalah sebesar **{abs(slope):.2f} Liter**.
        * **Rekomendasi:** Jika tren {kondisi_tren.lower()}, Amang Farm harus menyesuaikan {'stok pakan dan kapasitas kandang' if slope > 0 else 'strategi pemasaran dan evaluasi kesehatan ternak'}[cite: 103, 104].
        """)

    else:
        st.error("❌ Kolom esensial tidak ditemukan untuk melakukan analisis tren.")
else:
    st.info("👈 Silakan unggah file CSV Amang Farm untuk memulai analisis.")
