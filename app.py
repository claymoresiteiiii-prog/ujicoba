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
uploaded_file = st.file_uploader("📂 Unggah file CSV Anda (Format: Tahun, Bulan, Minggu Ke, Hari/Tanggal, Volume, Harga):", type=["csv"])

if uploaded_file is not None:
    # Membaca file
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
            if df[col].isnull().any():
                df[col] = df[col].fillna("Tidak Diketahui")
        st.success(f"✅ Data dibersihkan untuk menjaga integritas analisis.")
    else:
        st.success("✅ Data siap diolah.")

    # ==========================================
    # 2. PRE-PROCESSING & FILTERING
    # ==========================================
    if 'Volume Mingguan (Liter)' not in df.columns and 'Volume Harian (Liter)' in df.columns:
        df['Volume Mingguan (Liter)'] = df['Volume Harian (Liter)'] * 7

    # Kalkulasi Profit (Volume * Harga)
    if 'Harga per Liter (Rp)' in df.columns and 'Volume Mingguan (Liter)' in df.columns:
        df['Estimasi Profit (Rp)'] = df['Volume Mingguan (Liter)'] * df['Harga per Liter (Rp)']

    st.sidebar.header("⚙️ Pengaturan Filter")
    df_final = df.copy()

    # A. Filter Tahun
    if 'Tahun' in df_final.columns:
        list_tahun = sorted(df_final['Tahun'].unique().tolist())
        opsi_tahun = ["Semua Tahun"] + list_tahun
        tahun_terpilih = st.sidebar.selectbox("Pilih Tahun Analisis:", opsi_tahun)
        if tahun_terpilih != "Semua Tahun":
            df_final = df_final[df_final['Tahun'] == tahun_terpilih]
    else:
        tahun_terpilih = "Semua Tahun"

    # Pembuatan Kolom Bulan otomatis (Jika belum ada)
    if 'Minggu Ke' in df.columns and 'Bulan' not in df.columns:
        df['Bulan'] = np.ceil(df['Minggu Ke'] / 4.33).astype(int).apply(lambda x: 12 if x > 12 else x)
        df_final['Bulan'] = np.ceil(df_final['Minggu Ke'] / 4.33).astype(int).apply(lambda x: 12 if x > 12 else x)

    # B. Filter Bulan
    if 'Bulan' in df_final.columns:
        list_bulan = sorted(df_final['Bulan'].unique().tolist())
        opsi_bulan = ["Semua Bulan"] + list_bulan
        bulan_terpilih = st.sidebar.selectbox("Pilih Bulan:", opsi_bulan)
        if bulan_terpilih != "Semua Bulan":
            df_final = df_final[df_final['Bulan'] == bulan_terpilih]

    # C. Filter Mingguan
    if 'Minggu Ke' in df_final.columns:
        list_minggu = sorted(df_final['Minggu Ke'].unique().tolist())
        opsi_minggu = ["Semua Minggu"] + list_minggu
        minggu_terpilih = st.sidebar.selectbox("Pilih Minggu Ke:", opsi_minggu)
        if minggu_terpilih != "Semua Minggu":
            df_final = df_final[df_final['Minggu Ke'] == minggu_terpilih]

    # D. Filter Harian
    col_harian = 'Hari' if 'Hari' in df_final.columns else 'Tanggal' if 'Tanggal' in df_final.columns else None
    if col_harian:
        list_hari = df_final[col_harian].unique().tolist()
        try: list_hari = sorted(list_hari)
        except: pass
        
        opsi_hari = [f"Semua {col_harian}"] + list_hari
        hari_terpilih = st.sidebar.selectbox(f"Pilih {col_harian}:", opsi_hari)
        if hari_terpilih != f"Semua {col_harian}":
            df_final = df_final[df_final[col_harian] == hari_terpilih]

    # E. Filter Profit Tertinggi / Terendah
    if 'Estimasi Profit (Rp)' in df_final.columns:
        opsi_profit = ["Semua Data", "Top 10 Profit Tertinggi", "Top 10 Profit Terendah"]
        profit_terpilih = st.sidebar.selectbox("Filter Profit / Penjualan:", opsi_profit)
        
        if profit_terpilih == "Top 10 Profit Tertinggi":
            df_final = df_final.nlargest(10, 'Estimasi Profit (Rp)')
            st.sidebar.success("✅ Menampilkan 10 data penjualan dengan profit tertinggi.")
        elif profit_terpilih == "Top 10 Profit Terendah":
            df_final = df_final.nsmallest(10, 'Estimasi Profit (Rp)')
            st.sidebar.warning("⚠️ Menampilkan 10 data penjualan dengan profit terendah.")

    st.divider()

    # ==========================================
    # 3. ANALISIS UNIVARIAT & BIVARIAT
    # ==========================================
    required_cols = ['Harga per Liter (Rp)', 'Volume Mingguan (Liter)']
    if all(col in df_final.columns for col in required_cols):
        
        if df_final.empty:
            st.warning("⚠️ Tidak ada data untuk kombinasi filter yang dipilih.")
        else:
            st.header(f"📊 2. Analisis Deskriptif & Hubungan ({tahun_terpilih})")
            col1, col2 = st.columns(2)
            
            with col1:
                fig_vol = px.histogram(df_final, x="Volume Mingguan (Liter)", nbins=20,
                                     title="Distribusi Volume Produksi", color_discrete_sequence=['#54A24B'])
                st.plotly_chart(fig_vol, use_container_width=True)
                
                vol_mean = df_final['Volume Mingguan (Liter)'].mean()
                vol_std = df_final['Volume Mingguan (Liter)'].std() if len(df_final) > 1 else 0
                st.write(f"**Analisis Volume:** Rata-rata produksi adalah **{vol_mean:.2f} Liter**. Variabilitas data (Std Dev) sebesar **{vol_std:.2f}**.")
            
            with col2:
                if 'Bulan' in df_final.columns:
                    vol_bulan = df_final.groupby('Bulan')['Volume Mingguan (Liter)'].mean().reset_index()
                    fig_bulan = px.bar(vol_bulan, x='Bulan', y='Volume Mingguan (Liter)', 
                                       title="Rata-rata Penjualan per Bulan", color_continuous_scale='Blues')
                    st.plotly_chart(fig_bulan, use_container_width=True)
                    
                    if not vol_bulan.empty:
                        max_month = vol_bulan.loc[vol_bulan['Volume Mingguan (Liter)'].idxmax(), 'Bulan']
                        st.write(f"**Analisis Musiman:** Puncak rata-rata tertinggi ada pada **Bulan {int(max_month)}**.")

            st.divider()

            # ==========================================
            # 4. ANALISIS MULTIVARIAT & KORELASI
            # ==========================================
            st.header("🌐 3. Analisis Multivariat & Korelasi")
            col3, col4 = st.columns(2)

            with col3:
                if len(df_final) > 1:
                    fig_korelasi = px.scatter(df_final, x="Harga per Liter (Rp)", y="Volume Mingguan (Liter)", 
                                             trendline="ols", title="Korelasi: Harga vs Volume",
                                             color_discrete_sequence=['#E45756'])
                    st.plotly_chart(fig_korelasi, use_container_width=True)
                    
                    corr_val = df_final['Harga per Liter (Rp)'].corr(df_final['Volume Mingguan (Liter)'])
                    st.write(f"**Analisis Korelasi:** Nilai korelasi antar variabel adalah **{corr_val:.2f}**.")
                else:
                    st.info("ℹ️ Data tidak cukup untuk membuat plot korelasi (minimal 2 baris data dibutuhkan).")

            with col4:
                # Menggunakan warna berdasarkan Estimasi Profit agar perbedaan penjualan terlihat jelas
                if 'Minggu Ke' in df_final.columns and 'Estimasi Profit (Rp)' in df_final.columns:
                    fig_multi = px.scatter(df_final, x="Minggu Ke", y="Volume Mingguan (Liter)", 
                                           size="Estimasi Profit (Rp)", color="Harga per Liter (Rp)",
                                           title="Bubble Chart: Profit, Volume & Harga")
                    st.plotly_chart(fig_multi, use_container_width=True)

            st.divider()

            # ==========================================
            # 5. CHART TREND & PREDIKSI (Berdasarkan Dataset Utuh)
            # ==========================================
            st.header("📈 4. Prediksi Tren Penjualan Masa Depan")
            
            # Prediksi tetap menggunakan df asli
            df_pred = df.sort_values(by=['Tahun', 'Minggu Ke'] if 'Tahun' in df.columns else ['Minggu Ke']).reset_index()
            df_pred['Urutan_Waktu'] = df_pred.index + 1
            X = df_pred[['Urutan_Waktu']].values
            y = df_pred['Volume Mingguan (Liter)'].values

            if len(df_pred) > 1:
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

                slope = model.coef_[0]
                st.info(f"""
                **💡 Hasil Analisis Prediksi Tren Global (Semua Waktu):**
                1. **Arah Tren:** Penjualan diprediksi akan **{'Meningkat' if slope > 0 else 'Menurun'}**.
                2. **Kecepatan Perubahan:** Rata-rata perubahan volume adalah **{abs(slope):.2f} Liter** per minggu.
                """)
            else:
                st.warning("Data historis tidak cukup untuk membuat model prediksi tren.")

    else:
        st.error(f"❌ Kolom data tidak lengkap. Pastikan CSV memiliki kolom: {required_cols}")
else:
    st.info("👈 Silakan unggah file CSV Amang Farm di menu samping.")
