import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Amang Farm", layout="wide")

st.title("🐄 Dashboard Analisis Peternakan Sapi Perah")
st.markdown("Sistem otomatis untuk pembersihan, visualisasi, dan prediksi tren penjualan susu Amang Farm.")

# ==========================================
# FUNGSI PIPELINE PEMBERSIHAN DATA
# ==========================================
def auto_cleaning_pipeline(raw_df):
    """
    Fungsi pipeline untuk membersihkan data secara otomatis:
    1. Menghapus baris kosong.
    2. Konversi tipe data string ke numerik.
    3. Imputasi nilai hilang (NaN) dengan Median.
    4. Koreksi nilai negatif menjadi absolut.
    """
def auto_cleaning_pipeline(raw_df):
    """
    Fungsi pipeline untuk membersihkan data secara otomatis:
    1. Menghapus baris kosong.
    2. Konversi tipe data string ke numerik.
    3. Imputasi nilai hilang (NaN) dengan Median.
    4. Koreksi nilai negatif menjadi absolut.
    """
    df_clean = raw_df.copy()
    
    # 1. Menghapus baris yang seluruh isinya kosong
    df_clean.dropna(how='all', inplace=True)
    
    # 2. Standarisasi Tipe Data Numerik
    # Pastikan nama variabel di bawah ini (kolom_harus_numerik) konsisten
    kolom_harus_numerik = ['Volume Mingguan (Liter)', 'Volume Harian (Liter)', 'Harga per Liter (Rp)', 'Minggu Ke', 'Tahun', 'Bulan']
    
    for col in kolom_harus_numerik: 
        if col in df_clean.columns:
            # Jika kolom terbaca sebagai teks (object), bersihkan koma ribuan
            if df_clean[col].dtype == object:
                df_clean[col] = df_clean[col].astype(str).str.replace(',', '', regex=True)
            # Paksa menjadi angka, jika gagal akan menjadi NaN
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            
    # 3. Menangani Missing Values (Imputasi Median untuk angka, 'Tidak Diketahui' untuk teks)
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df_clean[col].isnull().any():
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())
            
    object_cols = df_clean.select_dtypes(include=['object']).columns
    for col in object_cols:
        if df_clean[col].isnull().any():
            df_clean[col] = df_clean[col].fillna("Tidak Diketahui")
            
    # 4. Koreksi Anomali Nilai Negatif (Mengubah angka minus menjadi plus)
    for col in numeric_cols:
        df_clean[col] = df_clean[col].abs()
        
    return df_clean

# 1. Fitur Upload Dataset
uploaded_file = st.file_uploader("📂 Unggah file CSV Amang Farm:", type=["csv"])

if uploaded_file is not None:
    df_mentah = pd.read_csv(uploaded_file)
    
    # ==========================================
    # 1. PROSES & TAMPILAN DATA CLEANING
    # ==========================================
    st.header("🧹 1. Pipeline Pembersihan Data Otomatis")
    
    # Menjalankan Pipeline
    df_bersih = auto_cleaning_pipeline(df_mentah)
    
    # Tab untuk perbandingan data
    tab_raw, tab_clean, tab_info = st.tabs(["📄 Data Sebelum Cleaning", "✨ Data Sesudah Cleaning", "ℹ️ Penjelasan Proses"])
    
    with tab_raw:
        st.subheader("Data Mentah (Original)")
        st.dataframe(df_mentah.head(10), use_container_width=True)
        st.write(f"Sjumlah baris awal: `{len(df_mentah)}` | Total nilai kosong: `{df_mentah.isnull().sum().sum()}`")

    with tab_clean:
        st.subheader("Data Hasil Pipeline")
        st.dataframe(df_bersih.head(10), use_container_width=True)
        st.write(f"Jumlah baris akhir: `{len(df_bersih)}` | Total nilai kosong: `{df_bersih.isnull().sum().sum()}`")

    with tab_info:
        st.subheader("Proses yang Dilakukan:")
        st.markdown("""
        1.  **Drop Empty Rows**: Menghapus baris yang tidak memiliki data sama sekali.
        2.  **Type Casting**: Memaksa kolom Volume dan Harga menjadi angka (meskipun ada kesalahan input teks).
        3.  **Missing Value Imputation**: Mengisi data kosong dengan **Median** (nilai tengah) untuk menjaga distribusi data.
        4.  **Anomali Handling**: Mengubah nilai negatif (salah input) menjadi nilai positif absolut.
        5.  **String Normalization**: Mengisi kolom teks yang kosong dengan label 'Tidak Diketahui'.
        """)

    # --- KESIMPULAN OTOMATIS PIPELINE ---
    st.info(f"""
    💡 **Kesimpulan Pembersihan:** Sistem mendeteksi `{df_mentah.isnull().sum().sum()}` data kosong dan telah memperbaikinya secara otomatis. 
    Data kini memiliki integritas **100% siap olah** tanpa adanya nilai anomali atau tipe data yang tidak sinkron.
    """)

    # Gunakan df_bersih untuk analisis selanjutnya
    df = df_bersih.copy()

    # ==========================================
    # 2. PRE-PROCESSING & FILTERING
    # ==========================================
    if 'Volume Mingguan (Liter)' not in df.columns and 'Volume Harian (Liter)' in df.columns:
        df['Volume Mingguan (Liter)'] = df['Volume Harian (Liter)'] * 7

    if 'Harga per Liter (Rp)' in df.columns and 'Volume Mingguan (Liter)' in df.columns:
        df['Estimasi Profit (Rp)'] = df['Volume Mingguan (Liter)'] * df['Harga per Liter (Rp)']

    st.sidebar.header("⚙️ Pengaturan Filter Data")
    df_final = df.copy()

    # --- FILTER TAHUN ---
    if 'Tahun' in df_final.columns:
        list_tahun = sorted(df_final['Tahun'].unique().tolist())
        opsi_tahun = ["Semua Tahun"] + list_tahun
        tahun_terpilih = st.sidebar.selectbox("Pilih Tahun Analisis:", opsi_tahun)
        if tahun_terpilih != "Semua Tahun":
            df_final = df_final[df_final['Tahun'] == tahun_terpilih]
    else:
        tahun_terpilih = "Semua Tahun"

    # --- FILTER PROFIT TOP 10 ---
    if 'Estimasi Profit (Rp)' in df_final.columns:
        opsi_profit = ["Semua Data", "Top 10 Profit Tertinggi", "Top 10 Profit Terendah"]
        profit_terpilih = st.sidebar.selectbox("Filter Profit / Penjualan:", opsi_profit)
        if profit_terpilih == "Top 10 Profit Tertinggi":
            df_final = df_final.nlargest(10, 'Estimasi Profit (Rp)')
        elif profit_terpilih == "Top 10 Profit Terendah":
            df_final = df_final.nsmallest(10, 'Estimasi Profit (Rp)')

    # --- FILTER TAMPILAN GRAFIK ---
    st.sidebar.markdown("---")
    st.sidebar.header("👁️ Tampilan Visualisasi")
    tampil_deskriptif = st.sidebar.checkbox("1. Analisis Deskriptif", value=True)
    tampil_profit = st.sidebar.checkbox("2. Analisis Profit (Juta Rp)", value=True)
    tampil_korelasi = st.sidebar.checkbox("3. Korelasi & Persentase", value=True)
    tampil_prediksi = st.sidebar.checkbox("4. Prediksi Tren", value=True)

    st.divider()

    # ==========================================
    # 3. VISUALISASI DATA
    # ==========================================
    if df_final.empty:
        st.warning("⚠️ Tidak ada data untuk filter tersebut.")
    else:
        # --- 1. ANALISIS DESKRIPTIF ---
        if tampil_deskriptif:
            st.header(f"📊 Analisis Deskriptif ({tahun_terpilih})")
            c1, c2 = st.columns(2)
            with c1:
                fig_vol = px.histogram(df_final, x="Volume Mingguan (Liter)", title="Distribusi Volume Produksi", color_discrete_sequence=['#54A24B'])
                st.plotly_chart(fig_vol, use_container_width=True)
                vol_mean = df_final['Volume Mingguan (Liter)'].mean()
                st.info(f"💡 **Kesimpulan:** Rata-rata produksi mingguan Anda berada di angka **{vol_mean:.2f} Liter**.")
            with c2:
                if 'Bulan' in df_final.columns:
                    vol_bulan = df_final.groupby('Bulan')['Volume Mingguan (Liter)'].mean().reset_index()
                    fig_bulan = px.bar(vol_bulan, x='Bulan', y='Volume Mingguan (Liter)', title="Trend Produksi Bulanan", color_continuous_scale='Blues')
                    st.plotly_chart(fig_bulan, use_container_width=True)
                    max_month = vol_bulan.loc[vol_bulan['Volume Mingguan (Liter)'].idxmax(), 'Bulan']
                    st.info(f"💡 **Kesimpulan:** Produksi tertinggi secara historis tercapai pada **Bulan {int(max_month)}**.")

        # --- 2. ANALISIS PROFIT (FORMAT JUTA RP) ---
        if tampil_profit:
            st.header("💰 Analisis Profit & Pendapatan")
            if 'Estimasi Profit (Rp)' in df_final.columns:
                df_final['Profit (Juta Rp)'] = df_final['Estimasi Profit (Rp)'] / 1_000_000
                df_final['Label Waktu'] = "Mg " + df_final['Minggu Ke'].astype(int).astype(str) if 'Minggu Ke' in df_final.columns else df_final.index.astype(str)
                
                fig_profit = px.bar(df_final.sort_values('Profit (Juta Rp)', ascending=False), 
                                    x='Label Waktu', y='Profit (Juta Rp)',
                                    color='Profit (Juta Rp)', color_continuous_scale='Greens',
                                    title="Profit per Periode (Satuan: Juta Rupiah)")
                fig_profit.update_traces(texttemplate='Rp %{y:.2f} Jt', textposition="outside")
                st.plotly_chart(fig_profit, use_container_width=True)
                
                top_p = df_final['Estimasi Profit (Rp)'].max()
                st.info(f"💡 **Kesimpulan:** Keuntungan tertinggi dalam satu periode mencapai **Rp {top_p:,.0f}**. Gunakan data ini untuk menetapkan target minimum profit.")

        # --- 3. KORELASI & PERSENTASE ---
        if tampil_korelasi:
            st.header("🌐 Analisis Korelasi & Distribusi")
            c3, c4 = st.columns(2)
            with c3:
                fig_corr = px.scatter(df_final, x="Harga per Liter (Rp)", y="Volume Mingguan (Liter)", trendline="ols", title="Korelasi Harga vs Volume")
                st.plotly_chart(fig_corr, use_container_width=True)
                st.info("💡 **Kesimpulan:** Garis tren menunjukkan bagaimana perubahan harga mempengaruhi volume produksi Anda.")
            with c4:
                if 'Bulan' in df_final.columns:
                    profit_pie = df_final.groupby('Bulan')['Estimasi Profit (Rp)'].sum().reset_index()
                    fig_pie = px.pie(profit_pie, values='Estimasi Profit (Rp)', names='Bulan', title="Kontribusi Profit per Bulan", hole=0.4)
                    fig_pie.update_traces(textinfo='percent+label')
                    st.plotly_chart(fig_pie, use_container_width=True)
                    best_m = profit_pie.loc[profit_pie['Estimasi Profit (Rp)'].idxmax(), 'Bulan']
                    st.info(f"💡 **Kesimpulan:** Bulan **{int(best_m)}** memberikan kontribusi keuntungan terbesar bagi peternakan.")

        # --- 4. PREDIKSI TREN ---
        if tampil_prediksi:
            st.header("📈 Prediksi Tren Penjualan")
            df_pred = df.sort_values(by=['Tahun', 'Minggu Ke']).reset_index()
            df_pred['Urutan_Waktu'] = df_pred.index + 1
            X = df_pred[['Urutan_Waktu']].values
            y = df_pred['Volume Mingguan (Liter)'].values
            if len(df_pred) > 1:
                model = LinearRegression().fit(X, y)
                future_X = np.array(range(len(df_pred) + 1, len(df_pred) + 12)).reshape(-1, 1)
                future_y = model.predict(future_X)
                
                df_trend = pd.concat([
                    pd.DataFrame({'Waktu': df_pred['Urutan_Waktu'], 'Volume': y, 'Status': 'Historis'}),
                    pd.DataFrame({'Waktu': future_X.flatten(), 'Volume': future_y, 'Status': 'Prediksi'})
                ])
                fig_trend = px.line(df_trend, x='Waktu', y='Volume', color='Status', title="Proyeksi Volume Produksi Kedepan")
                st.plotly_chart(fig_trend, use_container_width=True)
                
                kondisi = "Naik 📈" if model.coef_[0] > 0 else "Turun 📉"
                st.info(f"💡 **Kesimpulan:** Tren produksi kedepan diprediksi akan **{kondisi}** dengan rata-rata perubahan {abs(model.coef_[0]):.2f} liter per minggu.")

else:
    st.info("👈 Silakan unggah file CSV Amang Farm di sidebar.")
print(f"Jumlah baris awal: {len(raw_df)}")
print(f"Jumlah baris setelah dibersihkan: {len(df_clean)}")
