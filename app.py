import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression

# Konfigurasi Halaman (Lebar Penuh)
st.set_page_config(page_title="Dashboard Amang Farm", layout="wide", page_icon="🐄")

st.title("🐄 Dashboard Analisis Peternakan Sapi Perah")
st.markdown("Sistem otomatis untuk pembersihan, visualisasi, dan prediksi tren penjualan susu Amang Farm.")

# ==========================================
# FUNGSI PIPELINE PEMBERSIHAN DATA
# ==========================================
@st.cache_data 
def auto_cleaning_pipeline(raw_df):
    """
    Fungsi pipeline untuk membersihkan data secara otomatis.
    """
    df_clean = raw_df.copy()
    
    # 1. Menghapus baris yang seluruh isinya kosong
    df_clean.dropna(how='all', inplace=True)
    
    # 2. Standarisasi Tipe Data Numerik
    kolom_harus_numerik = ['Volume Mingguan (Liter)', 'Volume Harian (Liter)', 'Harga per Liter (Rp)', 'Minggu Ke', 'Tahun', 'Bulan']
    
    for col in kolom_harus_numerik: 
        if col in df_clean.columns:
            if df_clean[col].dtype == object:
                df_clean[col] = df_clean[col].astype(str).str.replace(',', '', regex=True)
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            
    # 3. Menangani Missing Values
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df_clean[col].isnull().any():
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())
            
    object_cols = df_clean.select_dtypes(include=['object']).columns
    for col in object_cols:
        if df_clean[col].isnull().any():
            df_clean[col] = df_clean[col].fillna("Tidak Diketahui")
            
    # 4. Koreksi Anomali Nilai Negatif
    for col in numeric_cols:
        df_clean[col] = df_clean[col].abs()
        
    return df_clean

# ==========================================
# SIDEBAR & UPLOAD FILE
# ==========================================
st.sidebar.header("📂 Menu Unggah Data")
uploaded_file = st.sidebar.file_uploader("Unggah file CSV Amang Farm:", type=["csv"])

if uploaded_file is not None:
    df_mentah = pd.read_csv(uploaded_file)
    
    # ==========================================
    # 1. PROSES & TAMPILAN DATA CLEANING
    # ==========================================
    st.header("🧹 1. Pipeline Pembersihan Data Otomatis")
    df_bersih = auto_cleaning_pipeline(df_mentah)
    
    tab_raw, tab_clean = st.tabs(["📄 Data Mentah (Sebelum)", "✨ Data Siap Olah (Sesudah)"])
    with tab_raw:
        st.dataframe(df_mentah.head(5), use_container_width=True)
    with tab_clean:
        st.dataframe(df_bersih.head(5), use_container_width=True)
        
    st.success("Sistem telah membersihkan data. Integritas data kini 100% siap diolah.")

    df = df_bersih.copy()

    # ==========================================
    # 2. PRE-PROCESSING & PENGUATAN TIPE DATA
    # ==========================================
    if 'Tahun' in df.columns:
        df['Tahun'] = df['Tahun'].astype(int)
    if 'Minggu Ke' in df.columns:
        df['Minggu Ke'] = df['Minggu Ke'].astype(int)

    if 'Volume Mingguan (Liter)' not in df.columns and 'Volume Harian (Liter)' in df.columns:
        df['Volume Mingguan (Liter)'] = df['Volume Harian (Liter)'] * 7

    if 'Harga per Liter (Rp)' in df.columns and 'Volume Mingguan (Liter)' in df.columns:
        if 'Estimasi Profit (Rp)' not in df.columns:
            df['Estimasi Profit (Rp)'] = df['Volume Mingguan (Liter)'] * df['Harga per Liter (Rp)']

    if 'Bulan' not in df.columns and 'Minggu Ke' in df.columns:
        df['Bulan'] = np.ceil(df['Minggu Ke'] / 4.33).astype(int)
        df['Bulan'] = df['Bulan'].apply(lambda x: 12 if x > 12 else x)

    # ==========================================
    # --- PENGATURAN FILTER DATA ---
    # ==========================================
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Pengaturan Filter Data")
    
    df_final = df.copy()

    # FILTER TAHUN
    if 'Tahun' in df_final.columns:
        list_tahun = sorted(df_final['Tahun'].unique().tolist())
        opsi_tahun = ["Semua Tahun"] + list_tahun
        tahun_terpilih = st.sidebar.selectbox("Pilih Tahun Analisis:", opsi_tahun)
        if tahun_terpilih != "Semua Tahun":
            df_final = df_final[df_final['Tahun'] == tahun_terpilih]
    else:
        tahun_terpilih = "Semua Tahun"

    # FILTER BULAN
    if 'Bulan' in df_final.columns:
        list_bulan = sorted(df_final['Bulan'].unique().tolist())
        opsi_bulan = ["Semua Bulan"] + list_bulan
        bulan_terpilih = st.sidebar.selectbox("Pilih Bulan Analisis:", opsi_bulan)
        if bulan_terpilih != "Semua Bulan":
            df_final = df_final[df_final['Bulan'] == bulan_terpilih]

    # FILTER MINGGU
    if 'Minggu Ke' in df_final.columns:
        list_minggu = sorted(df_final['Minggu Ke'].unique().tolist())
        opsi_minggu = ["Semua Minggu"] + list_minggu
        minggu_terpilih = st.sidebar.selectbox("Pilih Minggu Analisis:", opsi_minggu)
        if minggu_terpilih != "Semua Minggu":
            df_final = df_final[df_final['Minggu Ke'] == minggu_terpilih]

    # ==========================================
    # --- PENGATURAN TAMPILAN GRAFIK (CHECKBOX) ---
    # ==========================================
    st.sidebar.markdown("---")
    st.sidebar.header("👁️ Pengaturan Tampilan Visualisasi")
    
    tampil_deskriptif = st.sidebar.checkbox("1. Analisis Univariat & Deskriptif", value=True)
    tampil_profit = st.sidebar.checkbox("2. Analisis Profit & Pendapatan", value=True)
    tampil_korelasi = st.sidebar.checkbox("3. Analisis Bivariat (Korelasi & Pie)", value=True)
    tampil_multivariat = st.sidebar.checkbox("4. Analisis Multivariat (Bubble Chart)", value=True)
    tampil_prediksi = st.sidebar.checkbox("5. Prediksi Tren", value=True)

    # ==========================================
    # 3. VISUALISASI DATA
    # ==========================================
    st.markdown("---")
    
    if df_final.empty:
        st.warning("⚠️ Tidak ada data untuk filter tersebut. Silakan atur ulang filter Anda.")
    else:
        # --- A. ANALISIS UNIVARIAT & DESKRIPTIF (Hist & Bar) ---
        if tampil_deskriptif:
            st.header(f"📊 1. Analisis Univariat & Deskriptif ({tahun_terpilih})")
            
            c1, c2 = st.columns(2)
            # Grafik Univariat 1: Histogram Volume (Dari Skripsi)
            with c1:
                fig_vol = px.histogram(df_final, x="Volume Mingguan (Liter)", title="Distribusi Jumlah Produksi Susu Mingguan", color_discrete_sequence=['#54A24B'])
                st.plotly_chart(fig_vol, use_container_width=True)
                rata_vol = df_final['Volume Mingguan (Liter)'].mean()
                st.info(f"💡 **Kesimpulan (Univariat):** Mayoritas produksi terkonsentrasi dengan nilai rata-rata **{rata_vol:.2f} liter/minggu**.")
                
            # Grafik Univariat 2: Histogram Harga (BARU DITAMBAHKAN SESUAI SKRIPSI)
            with c2:
                fig_harga = px.histogram(df_final, x="Harga per Liter (Rp)", title="Berapa harga yang paling sering berlaku?", color_discrete_sequence=['#FF9900'])
                st.plotly_chart(fig_harga, use_container_width=True)
                if 'Harga per Liter (Rp)' in df_final.columns:
                    modus_harga = df_final['Harga per Liter (Rp)'].mode()[0]
                    st.info(f"💡 **Kesimpulan (Univariat):** Harga pasar yang paling sering berlaku (modus) pada periode ini adalah **Rp {modus_harga:,.0f} per liter**.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Grafik Bivariat 1: Bar Chart Musiman (Dari Skripsi)
            vol_bulan = df_final.groupby('Bulan')['Volume Mingguan (Liter)'].mean().reset_index()
            vol_bulan['Bulan_Str'] = "Bulan " + vol_bulan['Bulan'].astype(str)
            fig_bulan = px.bar(vol_bulan, x='Bulan_Str', y='Volume Mingguan (Liter)', title="Rata-rata Penjualan Susu Berdasarkan Bulan", color='Volume Mingguan (Liter)', color_continuous_scale='Blues')
            st.plotly_chart(fig_bulan, use_container_width=True)
            if not vol_bulan.empty:
                bulan_tertinggi = vol_bulan.loc[vol_bulan['Volume Mingguan (Liter)'].idxmax(), 'Bulan_Str']
                st.info(f"💡 **Kesimpulan Musiman:** Rata-rata produksi dan penjualan tertinggi secara historis dicapai pada **{bulan_tertinggi}**.")
            
            st.markdown("---")

        # --- B. ANALISIS PROFIT (Tetap Dipertahankan Sesuai Code Awal) ---
        if tampil_profit:
            st.header("💰 2. Analisis Profit & Pendapatan")
            if 'Estimasi Profit (Rp)' in df_final.columns:
                df_final['Profit (Juta Rp)'] = df_final['Estimasi Profit (Rp)'] / 1_000_000
                df_final['Label Waktu'] = "Mg " + df_final['Minggu Ke'].astype(str)

                df_profit_tampil = df_final.sort_values(by=['Tahun', 'Minggu Ke']).tail(25)
                
                fig_profit = px.bar(df_profit_tampil, 
                                    x='Label Waktu', y='Profit (Juta Rp)',
                                    color='Profit (Juta Rp)', color_continuous_scale='Greens',
                                    title="Tren Profit (Dibatasi 25 Periode Terakhir)", text_auto='.2f')
                fig_profit.update_layout(xaxis_tickangle=-45)
                fig_profit.update_traces(textposition="outside")
                st.plotly_chart(fig_profit, use_container_width=True)
                
                if not df_profit_tampil.empty:
                    max_profit = df_profit_tampil['Profit (Juta Rp)'].max()
                    mg_max = df_profit_tampil.loc[df_profit_tampil['Profit (Juta Rp)'].idxmax(), 'Label Waktu']
                    st.info(f"💡 **Kesimpulan:** Puncak keuntungan dari rentang periode yang ditampilkan terjadi pada **{mg_max}** dengan total profit sebesar **Rp {max_profit:.2f} Juta**.")
            st.markdown("---")

        # --- C. ANALISIS BIVARIAT KORELASI & PIE ---
        if tampil_korelasi:
            st.header("🌐 3. Analisis Bivariat (Korelasi & Distribusi)")
            c3, c4 = st.columns(2)
            
            # Grafik Bivariat 2: Scatter Plot (Dari Skripsi)
            with c3:
                fig_corr = px.scatter(df_final, x="Harga per Liter (Rp)", y="Volume Mingguan (Liter)", trendline="ols", title="Korelasi: Harga Pasar vs Volume Produksi")
                st.plotly_chart(fig_corr, use_container_width=True)
                st.info("💡 **Kesimpulan Bivariat:** Pola penyebaran titik memetakan seberapa elastis pengaruh perubahan harga per liter terhadap daya serap/volume produksi susu.")
                
            # Grafik Bivariat Tambahan (Tetap Dipertahankan)
            with c4:
                profit_pie = df_final.groupby('Bulan')['Estimasi Profit (Rp)'].sum().reset_index()
                profit_pie['Bulan_Str'] = "Bulan " + profit_pie['Bulan'].astype(str)
                fig_pie = px.pie(profit_pie, values='Estimasi Profit (Rp)', names='Bulan_Str', title="Persentase Kontribusi Profit per Bulan", hole=0.4)
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
                
                if not profit_pie.empty:
                    bulan_dominan = profit_pie.loc[profit_pie['Estimasi Profit (Rp)'].idxmax(), 'Bulan_Str']
                    persentase = (profit_pie['Estimasi Profit (Rp)'].max() / profit_pie['Estimasi Profit (Rp)'].sum()) * 100
                    st.info(f"💡 **Kesimpulan:** Penyumbang profit paling dominan adalah **{bulan_dominan}** dengan kontribusi sebesar **{persentase:.1f}%**.")
            st.markdown("---")

        # --- D. ANALISIS MULTIVARIAT (BARU DITAMBAHKAN SESUAI SKRIPSI 4.1.4.C.1) ---
        if tampil_multivariat:
            st.header("🧭 4. Analisis Multivariat")
            
            # Menyiapkan kolom warna agar dibaca sebagai kategori (bukan gradasi angka)
            df_final['Tahun_Kategori'] = df_final['Tahun'].astype(str)
            
            fig_bubble = px.scatter(df_final, 
                                    x="Minggu Ke", 
                                    y="Volume Mingguan (Liter)", 
                                    size="Estimasi Profit (Rp)", 
                                    color="Tahun_Kategori",
                                    hover_name="Bulan",
                                    size_max=40,
                                    title="Peta Bisnis: Minggu vs Volume vs Laba vs Tahun")
            st.plotly_chart(fig_bubble, use_container_width=True)
            
            st.info("💡 **Kesimpulan Multivariat:** Visualisasi 4 dimensi ini membantu memantau Kesehatan Finansial dan Operasional secara serentak dari tahun ke tahun. Ukuran gelembung mewakili besaran laba yang dicairkan.")
            st.markdown("---")

        # --- E. PREDIKSI TREN (MULTIVARIAT PREDIKTIF) ---
        if tampil_prediksi:
            st.header("📈 5. Prediksi Tren Penjualan Masa Depan")
            
            df_pred = df_final.sort_values(by=['Tahun', 'Minggu Ke']).reset_index(drop=True)
            df_pred['Urutan_Waktu'] = df_pred.index + 1
            
            X = df_pred[['Urutan_Waktu']].values
            y = df_pred['Volume Mingguan (Liter)'].values
            
            if len(df_pred) > 1:
                model = LinearRegression().fit(X, y)
                future_X = np.array(range(len(df_pred) + 1, len(df_pred) + 13)).reshape(-1, 1)
                future_y = model.predict(future_X)
                
                df_trend = pd.concat([
                    pd.DataFrame({'Waktu': df_pred['Urutan_Waktu'], 'Volume': y, 'Keterangan': 'Data Historis (Real)'}),
                    pd.DataFrame({'Waktu': future_X.flatten(), 'Volume': future_y, 'Keterangan': 'Garis Prediksi (Future)'})
                ])
                
                fig_trend = px.line(df_trend, x='Waktu', y='Volume', color='Keterangan', 
                                    title=f"Proyeksi Volume Produksi 12 Minggu Kedepan ({tahun_terpilih})",
                                    color_discrete_map={"Data Historis (Real)": "blue", "Garis Prediksi (Future)": "red"})
                fig_trend.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig_trend, use_container_width=True)
                
                # Kesimpulan Regresi Linear
                kondisi = "NAIK 📈" if model.coef_[0] > 0 else "TURUN 📉"
                st.info(f"💡 **Kesimpulan Prediksi Algoritma:** Berdasarkan kemiringan garis regresi pada data historis, volume produksi 12 minggu ke depan diproyeksikan akan mengalami tren **{kondisi}**.")
else:
    st.info("👈 Silakan unggah file CSV Anda pada menu di sebelah kiri layar.")
