import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Amang Farm", layout="wide")

st.title("🐄 Dashboard Analisis Cerdas Peternakan Sapi Perah")
st.markdown("Sistem otomatis untuk pembersihan, visualisasi, dan prediksi tren penjualan susu Amang Farm.")

# 1. Fitur Upload Dataset
uploaded_file = st.file_uploader("📂 Unggah file CSV Anda (Format: Tahun, Minggu Ke, Volume, Harga):", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # ==========================================
    # 1. DATA CLEANING
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
        st.success(f"✅ Data dibersihkan untuk menjaga integritas analisis[cite: 120, 121].")
    else:
        st.success("✅ Data siap diolah[cite: 122].")

    # ==========================================
    # 2. PRE-PROCESSING
    # ==========================================
    if 'Volume Mingguan (Liter)' not in df.columns and 'Volume Harian (Liter)' in df.columns:
        df['Volume Mingguan (Liter)'] = df['Volume Harian (Liter)'] * 7

    st.sidebar.header("⚙️ Pengaturan Filter")
    if 'Tahun' in df.columns:
        list_tahun = sorted(df['Tahun'].unique().tolist())
        opsi_tahun = ["Semua Tahun"] + list_tahun
        tahun_terpilih = st.sidebar.selectbox("Pilih Tahun Analisis:", opsi_tahun)
        df_final = df[df['Tahun'] == tahun_terpilih].copy() if tahun_terpilih != "Semua Tahun" else df.copy()
    else:
        df_final = df.copy()
        tahun_terpilih = "Semua Tahun"

    if 'Minggu Ke' in df_final.columns and 'Bulan' not in df_final.columns:
        df_final['Bulan'] = np.ceil(df_final['Minggu Ke'] / 4.33).astype(int).apply(lambda x: 12 if x > 12 else x)

    st.divider()

    # ==========================================
    # 3. ANALISIS UNIVARIAT & BIVARIAT
    # ==========================================
    if 'Harga per Liter (Rp)' in df_final.columns and 'Volume Mingguan (Liter)' in df_final.columns:
        st.header(f"📊 2. Analisis Deskriptif & Hubungan ({tahun_terpilih})")
        col1, col2 = st.columns(2)
        
        with col1:
            # Grafik Univariat [cite: 260]
            fig_vol = px.histogram(df_final, x="Volume Mingguan (Liter)", nbins=20,
                                 title="Distribusi Volume Produksi", color_discrete_sequence=['#54A24B'])
            st.plotly_chart(fig_vol, use_container_width=True)
            
            # --- SYNTAX ANALISIS UNIVARIAT ---
            vol_mean = df_final['Volume Mingguan (Liter)'].mean()
            vol_std = df_final['Volume Mingguan (Liter)'].std()
            st.write(f"**Analisis Volume:** Rata-rata produksi mingguan adalah **{vol_mean:.2f} Liter**. Variabilitas data (Std Dev) sebesar **{vol_std:.2f}**, menunjukkan tingkat stabilitas produksi pada periode ini.")
        
        with col2:
            # Grafik Bivariat [cite: 263]
            vol_bulan = df_final.groupby('Bulan')['Volume Mingguan (Liter)'].mean().reset_index()
            fig_bulan = px.bar(vol_bulan, x='Bulan', y='Volume Mingguan (Liter)', 
                               title="Rata-rata Penjualan per Bulan", color_continuous_scale='Blues')
            st.plotly_chart(fig_bulan, use_container_width=True)
            
            # --- SYNTAX ANALISIS MUSIMAN ---
            max_month = vol_bulan.loc[vol_bulan['Volume Mingguan (Liter)'].idxmax(), 'Bulan']
            st.write(f"**Analisis Musiman:** Puncak produksi tertinggi terjadi pada **Bulan {int(max_month)}**. Informasi ini krusial untuk menentukan strategi pengelolaan stok pakan[cite: 100, 104].")

        st.divider()

        # ==========================================
        # 4. ANALISIS MULTIVARIAT & KORELASI
        # ==========================================
        st.header("🌐 3. Analisis Multivariat & Korelasi")
        col3, col4 = st.columns(2)

        with col3:
            fig_korelasi = px.scatter(df_final, x="Harga per Liter (Rp)", y="Volume Mingguan (Liter)", 
                                      trendline="ols", title="Korelasi: Harga vs Volume",
                                      color_discrete_sequence=['#E45756'])
            st.plotly_chart(fig_korelasi, use_container_width=True)
            
            # --- SYNTAX ANALISIS KORELASI ---
            corr_val = df_final['Harga per Liter (Rp)'].corr(df_final['Volume Mingguan (Liter)'])
            st.write(f"**Analisis Korelasi:** Nilai korelasi antar variabel adalah **{corr_val:.2f}**. Hal ini menunjukkan kekuatan hubungan antara harga pasar dan volume produksi susu[cite: 264, 266].")

        with col4:
            fig_multi = px.scatter(df_final, x="Minggu Ke", y="Volume Mingguan (Liter)", 
                                   size="Harga per Liter (Rp)", color="Bulan",
                                   title="Bubble Chart: Waktu, Volume & Harga")
            st.plotly_chart(fig_multi, use_container_width=True)
            st.write("**Analisis Multivariat:** Grafik ini memadukan waktu, volume, dan harga sekaligus untuk mengidentifikasi pola tersembunyi yang tidak terlihat pada analisis satu dimensi[cite: 267, 268].")

        st.divider()

        # ==========================================
        # 5. CHART TREND & PREDIKSI
        # ==========================================
        st.header("📈 4. Prediksi Tren Penjualan Masa Depan")
        
        df_pred = df.sort_values(by=['Tahun', 'Minggu Ke']).reset_index()
        df_pred['Urutan_Waktu'] = df_pred.index + 1
        X = df_pred[['Urutan_Waktu']].values
        y = df_pred['Volume Mingguan (Liter)'].values

        model = LinearRegression()
        model.fit(X, y)

        future_X = np.array(range(len(df_pred) + 1, len(df_pred) + 53)).reshape(-1, 1)
        future_y = model.predict(future_X)

        df_total_trend = pd.concat([
            pd.DataFrame({'Waktu': df_pred['Urutan_Waktu'], 'Volume': y, 'Status': 'Historis'}),
            pd.DataFrame({'Waktu': future_X.flatten(), 'Volume': future_y, 'Status': 'Prediksi'})
        ])

        fig_trend = px.line(df_total_trend, x='Waktu', y='Volume', color='Status',
                            title="Proyeksi Penjualan Susu (Historis vs Prediksi)")
        st.plotly_chart(fig_trend, use_container_width=True)

        # --- SYNTAX ANALISIS PREDIKSI ---
        slope = model.coef_[0]
        st.info(f"""
        **💡 Hasil Analisis Prediksi Tren:**
        1. **Arah Tren:** Penjualan diprediksi akan **{'Meningkat' if slope > 0 else 'Menurun'}**.
        2. **Kecepatan Perubahan:** Rata-rata perubahan volume adalah **{abs(slope):.2f} Liter** per minggu.
        3. **Rekomendasi Strategis:** Berdasarkan analisis prediktif ini, Amang Farm dapat melakukan pengambilan keputusan berbasis bukti untuk perencanaan stok dan target penjualan tahun depan[cite: 130, 140, 142].
        """)

    else:
        st.error("❌ Kolom data tidak lengkap.")
else:
    st.info("👈 Silakan unggah file CSV Amang Farm.")
