import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Amang Farm", layout="wide")

st.title("🐄 Dashboard Analisis Cerdas Peternakan Sapi Perah")
st.markdown("Unggah file CSV Anda (misal: `data_susu_sapi_dengan_laba.csv`), dan sistem akan otomatis membuatkan grafik beserta penjelasan yang mudah dipahami.")

# 1. Fitur Upload Dataset
uploaded_file = st.file_uploader("📂 Masukkan file CSV Anda di sini:", type=["csv"])

if uploaded_file is not None:
    # Membaca data
    df = pd.read_csv(uploaded_file)
    
    # Menambahkan kolom "Bulan" dari "Minggu Ke" (Asumsi 1 bulan = 4.33 minggu)
    if 'Minggu Ke' in df.columns and 'Bulan' not in df.columns:
        df['Bulan'] = np.ceil(df['Minggu Ke'] / 4.33).astype(int)
        df['Bulan'] = df['Bulan'].apply(lambda x: 12 if x > 12 else x)

    st.success("✅ Data berhasil dimuat!")
    with st.expander("👀 Lihat Contoh Data (Klik untuk membuka)"):
        st.dataframe(df.head())

    st.divider()

    # ==========================================
    # 1. ANALISIS UNIVARIAT
    # ==========================================
    st.header("📊 1. Analisis Univariat (Fokus Satu Hal)")
    st.markdown("Mari kita lihat satu per satu kondisi dari variabel peternakan Anda, tanpa mencampurnya dengan yang lain.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Grafik Distribusi Harga
        fig_harga = px.histogram(df, x="Harga per Liter (Rp)", nbins=20, 
                                 title="Berapa harga yang paling sering berlaku?",
                                 color_discrete_sequence=['#4C78A8'])
        fig_harga.update_layout(yaxis_title="Jumlah Minggu (Frekuensi)")
        st.plotly_chart(fig_harga, use_container_width=True)
        
        # Teks Analisis Otomatis
        harga_rata = df['Harga per Liter (Rp)'].mean()
        harga_tersering = df['Harga per Liter (Rp)'].mode()[0]
        st.info(f"""
        **💡 Cara Membaca:**
        Batang yang paling tinggi menunjukkan harga yang paling sering didapatkan oleh peternakan.
        * **Harga Rata-rata:** Rp {harga_rata:,.0f} per liter.
        * **Harga Paling Sering Muncul:** Rp {harga_tersering:,.0f} per liter.
        """)

    with col2:
        # Pengecekan: Apakah kolom Volume Mingguan ada?
        if "Volume Mingguan (Liter)" in df.columns:
            # Grafik Distribusi Volume Mingguan
            fig_vol = px.box(df, y="Volume Mingguan (Liter)", 
                             title="Apakah produksi susu stabil atau sering naik-turun?",
                             color_discrete_sequence=['#54A24B'])
            st.plotly_chart(fig_vol, use_container_width=True)
            
            # Teks Analisis Otomatis
            vol_rata = df['Volume Mingguan (Liter)'].mean()
            st.info(f"""
            **💡 Cara Membaca:**
            Grafik kotak (boxplot) ini melihat kestabilan produksi. Titik di luar kotak adalah anomali.
            * Rata-rata peternakan menghasilkan **{vol_rata:,.0f} liter** susu per minggunya.
            """)
            
        # Jika tidak ada, cek apakah ada Volume Harian (sebagai cadangan)
        elif "Volume Harian (Liter)" in df.columns:
            fig_vol = px.box(df, y="Volume Harian (Liter)", 
                             title="Distribusi Volume Harian (Liter)",
                             color_discrete_sequence=['#54A24B'])
            st.plotly_chart(fig_vol, use_container_width=True)
            st.warning("⚠️ Menampilkan grafik berdasarkan 'Volume Harian' karena kolom 'Volume Mingguan' tidak ditemukan pada file ini.")
        
        else:
            st.error("❌ Kolom data Volume Susu tidak ditemukan di file CSV Anda.")
        **💡 Cara Membaca:**
        Grafik kotak (boxplot) ini melihat kestabilan produksi. Titik di luar kotak adalah anomali (produksi sangat sedikit atau sangat banyak).
        * Rata-rata peternakan menghasilkan **{vol_rata:,.0f} liter** susu per minggunya.
        """)

    st.divider()

    # ==========================================
    # 2. ANALISIS BIVARIAT
    # ==========================================
    st.header("📈 2. Analisis Bivariat (Mencari Hubungan Dua Hal)")
    st.markdown("Di sini kita melihat apakah satu hal memengaruhi hal lainnya. Misalnya, apakah waktu (bulan) memengaruhi jumlah susu?")

    col3, col4 = st.columns(2)

    with col3:
        # Grafik Musiman
        vol_bulan = df.groupby('Bulan')['Volume Mingguan (Liter)'].mean().reset_index()
        fig_bulan = px.bar(vol_bulan, x='Bulan', y='Volume Mingguan (Liter)', 
                           title="Rata-rata Produksi Susu Berdasarkan Bulan",
                           text_auto='.0f', color='Volume Mingguan (Liter)', 
                           color_continuous_scale='Blues')
        st.plotly_chart(fig_bulan, use_container_width=True)
        
        # Teks Analisis Otomatis
        bulan_max = vol_bulan.loc[vol_bulan['Volume Mingguan (Liter)'].idxmax()]['Bulan']
        bulan_min = vol_bulan.loc[vol_bulan['Volume Mingguan (Liter)'].idxmin()]['Bulan']
        st.info(f"""
        **💡 Kesimpulan Hubungan Bulan & Produksi:**
        Ternyata, bulan sangat berpengaruh pada hasil perah. 
        * **Bulan Terbaik:** Bulan ke-{int(bulan_max)} memiliki produksi rata-rata tertinggi.
        * **Bulan Terlemah:** Bulan ke-{int(bulan_min)} adalah saat produksi sedang paling turun. Ini bisa jadi bahan evaluasi kualitas pakan di bulan tersebut.
        """)

    with col4:
        # Hubungan Harga dan Volume
        fig_korelasi = px.scatter(df, x="Harga per Liter (Rp)", y="Volume Mingguan (Liter)", 
                                  trendline="ols", title="Apakah Harga Tinggi Membuat Produksi Naik?",
                                  opacity=0.6, color_discrete_sequence=['#E45756'])
        st.plotly_chart(fig_korelasi, use_container_width=True)
        
        st.info("""
        **💡 Kesimpulan Korelasi:**
        Perhatikan garis merah di atas grafik. 
        * Jika garis merah **naik ke kanan**, berarti saat harga mahal, sapi menghasilkan lebih banyak susu. 
        * Jika garisnya **mendatar**, berarti naik-turunnya harga pasar tidak ada hubungannya dengan seberapa banyak susu yang keluar dari sapi.
        """)

    st.divider()

    # ==========================================
    # 3. ANALISIS MULTIVARIAT
    # ==========================================
    st.header("🌐 3. Analisis Multivariat (Melihat Gambaran Besar)")
    st.markdown("Mari gabungkan semuanya! Kita akan melihat pola **Waktu (Tahun & Minggu)**, **Volume Susu**, dan besaran **Laba Pendapatan** dalam satu pandangan.")

    if 'Laba Pendapatan 2 Mingguan (Rp)' in df.columns:
        # Filter Laba > 0 agar grafik fokus pada minggu gajian/pencairan uang
        df_laba = df[df['Laba Pendapatan 2 Mingguan (Rp)'] > 0]
        
        # Bubble Chart yang sangat representatif
        fig_multi = px.scatter(df_laba, 
                               x="Minggu Ke", 
                               y="Volume Mingguan (Liter)", 
                               size="Laba Pendapatan 2 Mingguan (Rp)", 
                               color="Tahun",
                               hover_name="Bulan",
                               size_max=40,
                               title="Peta Bisnis: Pergerakan Volume & Laba Sepanjang Tahun")
        st.plotly_chart(fig_multi, use_container_width=True)
        
        # Teks Analisis Otomatis
        total_laba = df_laba['Laba Pendapatan 2 Mingguan (Rp)'].sum()
        st.success(f"""
        **💡 Cara Membaca Grafik Multivariat di Atas:**
        Grafik ini (Bubble Chart) sangat canggih karena menceritakan 4 hal sekaligus:
        1. **Kiri ke Kanan (Sumbu X):** Menunjukkan perjalanan waktu dari minggu ke-1 hingga minggu ke-52.
        2. **Atas ke Bawah (Sumbu Y):** Menunjukkan tinggi rendahnya jumlah susu yang disetor.
        3. **Warna Titik:** Menunjukkan perbedaan Tahun (lihat legenda warna di sebelah kanan).
        4. **Besar Bulatan (Bubble):** Semakin besar bulatannya, semakin besar UANG/LABA yang cair pada minggu tersebut.

        *(Total seluruh perputaran uang/laba yang tercatat dalam data Anda adalah sebesar **Rp {total_laba:,.0f}**).*
        """)
    else:
        st.warning("Data Anda tidak memiliki kolom 'Laba Pendapatan 2 Mingguan (Rp)' untuk analisis ini.")

else:
    st.info("👈 Silakan unggah (upload) file dataset CSV di atas untuk memulai analisis otomatis.")
