import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression

# Konfigurasi Halaman (Lebar Penuh)
st.set_page_config(page_title="Dashboard Amang Farm - Skripsi", layout="wide", page_icon="🐄")

st.title("🐄 Dashboard Analisis Penjualan Susu Amang Farm")
st.markdown("Sistem ini disesuaikan dengan metodologi skripsi: *Analisis dan Visualisasi Data Penjualan Susu Pada Hewan Ternak*.")

# ==========================================
# 1. FUNGSI PIPELINE PEMBERSIHAN DATA (Sesuai Bab 4.1.2)
# ==========================================
@st.cache_data 
def auto_cleaning_pipeline(raw_df):
    """
    Pembersihan data sesuai prosedur skripsi: penanganan missing values (median),
    koreksi anomali (Winsorizing/Moving Average), dan standarisasi.
    """
    df_clean = raw_df.copy()
    
    # Menghapus baris kosong mayoritas [cite: 568]
    df_clean.dropna(how='all', inplace=True)
    
    # Standarisasi kolom utama sesuai skripsi [cite: 535]
    kolom_skripsi = [
        'Tahun', 'Minggu Ke', 'Volume Harian (Liter)', 
        'Volume Mingguan (Liter)', 'Harga per Liter (Rp)', 
        'Laba Pendapatan 2 Mingguan (Rp)'
    ]
    
    for col in kolom_skripsi:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Penanganan Missing Values dengan Median [cite: 563, 716]
    for col in df_clean.select_dtypes(include=[np.number]).columns:
        if df_clean[col].isnull().any():
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())
            
    # Mitigasi Outlier: Volume wajar 40-70 liter [cite: 583]
    if 'Volume Harian (Liter)' in df_clean.columns:
        # Winsorizing: Memangkas nilai > 100 ke batas rasional (misal 75) [cite: 585]
        df_clean.loc[df_clean['Volume Harian (Liter)'] > 100, 'Volume Harian (Liter)'] = 75
        
    # Mitigasi Outlier: Harga wajar Rp6.500-Rp7.700 [cite: 587]
    if 'Harga per Liter (Rp)' in df_clean.columns:
        df_clean.loc[df_clean['Harga per Liter (Rp)'] < 2000, 'Harga per Liter (Rp)'] = df_clean['Harga per Liter (Rp)'].median()
        
    return df_clean

# ==========================================
# SIDEBAR & UPLOAD FILE
# ==========================================
st.sidebar.header("📂 Menu Unggah Data")
uploaded_file = st.sidebar.file_uploader("Unggah file CSV (data_susu_sapi_dengan_laba.csv):", type=["csv"])

if uploaded_file is not None:
    df_mentah = pd.read_csv(uploaded_file)
    df_bersih = auto_cleaning_pipeline(df_mentah)
    
    # Pre-processing tambahan (Feature Engineering) [cite: 574, 592]
    df = df_bersih.copy()
    if 'Bulan' not in df.columns and 'Minggu Ke' in df.columns:
        df['Bulan'] = np.ceil(df['Minggu Ke'] / 4.33).astype(int).clip(1, 12)
    
    # Tampilan Pembersihan Data [cite: 712]
    st.header("🧹 1. Hasil Pembersihan Data (Bab 4.1.2)")
    tab_raw, tab_clean = st.tabs(["📄 Data Mentah", "✨ Data Terverifikasi (Auto-Cleaning)"])
    with tab_raw:
        st.dataframe(df_mentah.head(10), use_container_width=True)
    with tab_clean:
        st.dataframe(df.head(10), use_container_width=True)
    st.success("Logika Skripsi Diterapkan: Missing values diisi median, outlier volume (>100L) dikoreksi.")

    # ==========================================
    # SIDEBAR FILTER
    # ==========================================
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Filter & Tampilan")
    
    list_tahun = sorted(df['Tahun'].unique().tolist())
    tahun_terpilih = st.sidebar.selectbox("Pilih Tahun Analisis:", ["Semua Tahun"] + list_tahun)
    
    df_final = df.copy()
    if tahun_terpilih != "Semua Tahun":
        df_final = df_final[df_final['Tahun'] == tahun_terpilih]

    tampil_univariat = st.sidebar.checkbox("Analisis Univariat", value=True)
    tampil_bivariat = st.sidebar.checkbox("Analisis Bivariat", value=True)
    tampil_multivariat = st.sidebar.checkbox("Analisis Multivariat", value=True)
    tampil_prediksi = st.sidebar.checkbox("Prediksi Tren (12 Minggu)", value=True)

    # ==========================================
    # 2. ANALISIS UNIVARIAT (Bab 4.1.3 pt 1) [cite: 644]
    # ==========================================
    if tampil_univariat:
        st.header(f"📊 Analisis Univariat ({tahun_terpilih})")
        c1, c2 = st.columns(2)
        with c1:
            fig_hist_vol = px.histogram(df_final, x="Volume Mingguan (Liter)", 
                                        title="Distribusi Volume Produksi (Histogram)", 
                                        color_discrete_sequence=['#54A24B'])
            st.plotly_chart(fig_hist_vol, use_container_width=True)
            st.info("Fungsi: Memetakan kestabilan kapasitas produksi peternakan. [cite: 650]")
        with c2:
            fig_hist_harga = px.histogram(df_final, x="Harga per Liter (Rp)", 
                                          title="Distribusi Harga Jual (Histogram)", 
                                          color_discrete_sequence=['#1F77B4'])
            st.plotly_chart(fig_hist_harga, use_container_width=True)
            st.info("Fungsi: Melihat sebaran harga pasar yang berlaku selama periode operasional. [cite: 647]")

    # ==========================================
    # 3. ANALISIS BIVARIAT (Bab 4.1.3 pt 2) [cite: 653]
    # ==========================================
    if tampil_bivariat:
        st.header(f"📈 Analisis Bivariat ({tahun_terpilih})")
        c3, c4 = st.columns(2)
        with c3:
            # Tren Produksi Bulanan
            vol_bulan = df_final.groupby('Bulan')['Volume Mingguan (Liter)'].mean().reset_index()
            fig_bar_bulan = px.bar(vol_bulan, x='Bulan', y='Volume Mingguan (Liter)', 
                                   title="Rata-rata Produksi Bulanan (Seasonality)", 
                                   color='Volume Mingguan (Liter)', color_continuous_scale='Blues')
            st.plotly_chart(fig_bar_bulan, use_container_width=True)
            st.info("Fungsi: Mendeteksi pola musiman (seasonality) produksi. [cite: 656]")
        with c4:
            # Korelasi Harga vs Volume
            fig_scatter = px.scatter(df_final, x="Harga per Liter (Rp)", y="Volume Mingguan (Liter)", 
                                     trendline="ols", title="Korelasi: Harga vs Volume")
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.info("Fungsi: Menguji hubungan supply & demand (elastisitas harga). [cite: 660, 732]")

    # ==========================================
    # 4. ANALISIS MULTIVARIAT (Bab 4.1.3 pt 3) [cite: 663]
    # ==========================================
    if tampil_multivariat:
        st.header(f"🌐 Analisis Multivariat: Peta Bisnis Amang Farm")
        # Bubble Chart sesuai Bab 4.1.4: Minggu (X), Volume (Y), Tahun (Color), Laba (Size) [cite: 665]
        fig_bubble = px.scatter(df_final, x="Minggu Ke", y="Volume Mingguan (Liter)", 
                                size="Laba Pendapatan 2 Mingguan (Rp)", color="Tahun",
                                hover_name="Tahun", size_max=40,
                                title="Bubble Chart: Minggu vs Volume vs Laba vs Tahun")
        st.plotly_chart(fig_bubble, use_container_width=True)
        st.info("Fungsi: Memantau kesehatan finansial dan operasional secara serentak (4 dimensi). [cite: 666]")

    # ==========================================
    # 5. PREDIKSI TREN (Bab 4.2.2 & 5.1) [cite: 737]
    # ==========================================
    if tampil_prediksi:
        st.header("📈 Prediksi Tren Penjualan 12 Minggu Ke Depan")
        
        df_pred = df_final.sort_values(by=['Tahun', 'Minggu Ke']).reset_index(drop=True)
        df_pred['Urutan_Waktu'] = df_pred.index + 1
        
        X = df_pred[['Urutan_Waktu']].values
        y = df_pred['Volume Mingguan (Liter)'].values
        
        if len(df_pred) > 5:
            model = LinearRegression().fit(X, y)
            # Proyeksi 12 Minggu 
            future_X = np.array(range(len(df_pred) + 1, len(df_pred) + 13)).reshape(-1, 1)
            future_y = model.predict(future_X)
            
            df_trend = pd.concat([
                pd.DataFrame({'Waktu': df_pred['Urutan_Waktu'], 'Volume': y, 'Keterangan': 'Historis'}),
                pd.DataFrame({'Waktu': future_X.flatten(), 'Volume': future_y, 'Keterangan': 'Prediksi (12 Mg)'})
            ])
            
            fig_line_pred = px.line(df_trend, x='Waktu', y='Volume', color='Keterangan', 
                                    title="Proyeksi Volume Produksi (Linear Regression)",
                                    color_discrete_map={"Historis": "blue", "Prediksi (12 Mg)": "red"})
            st.plotly_chart(fig_line_pred, use_container_width=True)
            
            kondisi = "NAIK 📈" if model.coef_[0] > 0 else "TURUN 📉"
            st.warning(f"**Kesimpulan Early Warning System:** Tren produksi diproyeksikan **{kondisi}**. [cite: 742]")
        else:
            st.error("Data tidak cukup untuk melakukan prediksi (Minimal 6 baris data).")

else:
    st.info("👈 Silakan unggah file CSV skripsi Anda (data_susu_sapi_dengan_laba.csv) untuk memulai analisis.")
