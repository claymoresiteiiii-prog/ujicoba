import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Amang Farm", layout="wide")

st.title("🐄 Dashboard Analisis Cerdas Peternakan Sapi Perah")
st.markdown("Unggah file CSV Anda, dan sistem akan otomatis membuatkan grafik interaktif beserta penjelasan yang mudah dipahami.")

# 1. Fitur Upload Dataset
uploaded_file = st.file_uploader("📂 Masukkan file CSV Anda di sini:", type=["csv"])

if uploaded_file is not None:
    # Membaca data
    df = pd.read_csv(uploaded_file)
    
    # ==========================================
    # PRE-PROCESSING (Penyesuaian Otomatis Kedua File)
    # ==========================================
    # 1. Membuat kolom "Bulan" dari "Minggu Ke" (Asumsi 1 bulan = 4.33 minggu)
    if 'Minggu Ke' in df.columns and 'Bulan' not in df.columns:
        df['Bulan'] = np.ceil(df['Minggu Ke'] / 4.33).astype(int)
        df['Bulan'] = df['Bulan'].apply(lambda x: 12 if x > 12 else x)

    # 2. Jika file tidak punya 'Volume Mingguan' tapi punya 'Volume Harian', kita buatkan otomatis
    if 'Volume Mingguan (Liter)' not in df.columns and 'Volume Harian (Liter)' in df.columns:
        df['Volume Mingguan (Liter)'] = df['Volume Harian (Liter)'] * 7

    st.success("✅ Data berhasil dimuat dan disesuaikan!")
    with st.expander("👀 Lihat Contoh Data yang Diproses (Klik untuk membuka)"):
        st.dataframe(df.head())

    st.divider()

    # Pastikan data esensial ada sebelum menggambar grafik
    if 'Harga per Liter (Rp)' in df.columns and 'Volume Mingguan (Liter)' in df.columns:

        # ==========================================
        # 1. ANALISIS UNIVARIAT
        # ==========================================
        st.header("📊 1. Analisis Univariat (Fokus Satu Hal)")
        st.markdown("Mari kita lihat satu per satu kondisi dari variabel peternakan Anda.")
        
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
            **💡 Kesimpulan Analisis Harga:**
            * Rata-rata harga susu secara keseluruhan adalah **Rp {harga_rata:,.0f}** per liter.
            * Harga pasar yang paling sering Anda dapatkan (paling dominan) adalah **Rp {harga_tersering:,.0f}** per liter.
            """)

        with col2:
            # Grafik Distribusi Volume Mingguan
            fig_vol = px.histogram(df, x="Volume Mingguan (Liter)", nbins=20,
                             title="Distribusi Jumlah Produksi Susu Mingguan",
                             color_discrete_sequence=['#54A24B'])
            fig_vol.update_layout(yaxis_title="Jumlah Minggu (Frekuensi)")
            st.plotly_chart(fig_vol, use_container_width=True)
            
            # Teks Analisis Otomatis
            vol_rata = df['Volume Mingguan (Liter)'].mean()
            vol_max = df['Volume Mingguan (Liter)'].max()
            st.info(f"""
            **💡 Kesimpulan Analisis Produksi:**
            * Rata-rata peternakan menyetorkan **{vol_rata:,.0f} liter** susu setiap minggunya.
            * Pencapaian rekor panen tertinggi yang pernah dicatat adalah **{vol_max:,.0f} liter** dalam seminggu.
            """)

        st.divider()

        # ==========================================
        # 2. ANALISIS BIVARIAT
        # ==========================================
        st.header("📈 2. Analisis Bivariat (Hubungan Dua Variabel)")
        st.markdown("Apakah waktu (bulan) memengaruhi jumlah susu? Atau apakah harga dipengaruhi oleh volume?")

        col3, col4 = st.columns(2)

        with col3:
            # Grafik Musiman
            vol_bulan = df.groupby('Bulan')['Volume Mingguan (Liter)'].mean().reset_index()
            fig_bulan = px.bar(vol_bulan, x='Bulan', y='Volume Mingguan (Liter)', 
                               title="Rata-rata Penjualan Susu Berdasarkan Bulan (Pola Musim)",
                               text_auto='.0f', color='Volume Mingguan (Liter)', 
                               color_continuous_scale='Blues')
            st.plotly_chart(fig_bulan, use_container_width=True)
            
            # Teks Analisis Otomatis
            bulan_max = vol_bulan.loc[vol_bulan['Volume Mingguan (Liter)'].idxmax()]['Bulan']
            bulan_min = vol_bulan.loc[vol_bulan['Volume Mingguan (Liter)'].idxmin()]['Bulan']
            st.info(f"""
            **💡 Kesimpulan Tren Musiman:**
            * **Bulan Terbaik:** Lonjakan penjualan rata-rata tertinggi terjadi pada bulan ke-**{int(bulan_max)}**.
            * **Bulan Terlemah:** Penjualan rata-rata paling anjlok terjadi di bulan ke-**{int(bulan_min)}**. (Saran: Periksa kembali kualitas pakan sapi pada periode ini).
            """)

        with col4:
            # Hubungan Harga dan Volume
            fig_korelasi = px.scatter(df, x="Harga per Liter (Rp)", y="Volume Mingguan (Liter)", 
                                      trendline="ols", title="Korelasi: Harga Pasar vs Volume Produksi",
                                      opacity=0.6, color_discrete_sequence=['#E45756'])
            st.plotly_chart(fig_korelasi, use_container_width=True)
            
            st.info("""
            **💡 Kesimpulan Korelasi:**
            * Garis lurus pada grafik menunjukkan *tren*. Jika garisnya mendatar, artinya perubahan harga di pasaran tidak memiliki hubungan langsung dengan kemampuan biologi sapi dalam memproduksi susu pada minggu tersebut.
            """)

        st.divider()

        # ==========================================
        # 3. ANALISIS MULTIVARIAT
        # ==========================================
        st.header("🌐 3. Analisis Multivariat (Melihat Gambaran Besar)")
        st.markdown("Mari gabungkan 3 hingga 4 variabel (Waktu, Produksi, Harga, dan Laba) ke dalam satu peta visualisasi.")

        # Skenario 1: Jika dataset memiliki Laba Pendapatan (File Kedua)
        if 'Laba Pendapatan 2 Mingguan (Rp)' in df.columns:
            df_laba = df[df['Laba Pendapatan 2 Mingguan (Rp)'] > 0]
            
            fig_multi = px.scatter(df_laba, x="Minggu Ke", y="Volume Mingguan (Liter)", 
                                   size="Laba Pendapatan 2 Mingguan (Rp)", color="Tahun",
                                   hover_name="Bulan", size_max=45,
                                   title="Peta Bisnis: Minggu vs Volume vs Laba vs Tahun")
            st.plotly_chart(fig_multi, use_container_width=True)
            
            total_laba = df_laba['Laba Pendapatan 2 Mingguan (Rp)'].sum()
            st.success(f"""
            **💡 Penjelasan Grafik Multivariat (File Lengkap):**
            Grafik *Bubble Chart* ini menganalisis 4 variabel sekaligus:
            1. Sumbu X = Perjalanan waktu (Minggu).
            2. Sumbu Y = Liter susu yang diproduksi.
            3. Warna = Perbandingan antar Tahun.
            4. **Besar Bulatan = Jumlah Laba.** Semakin besar bulatan, semakin tinggi cuan/pembayaran yang diterima minggu tersebut.
            
            *Total perputaran uang (laba kotor) yang tercatat dalam sistem Anda adalah **Rp {total_laba:,.0f}**.*
            """)

        # Skenario 2: Jika dataset hanya memiliki Harga dan Volume (File Pertama)
        else:
            fig_multi = px.scatter(df, x="Minggu Ke", y="Volume Mingguan (Liter)", 
                                   size="Harga per Liter (Rp)", color="Tahun",
                                   hover_name="Bulan", size_max=20,
                                   title="Tren Produksi Sepanjang Tahun (Ukuran Titik = Harga Susu)")
            st.plotly_chart(fig_multi, use_container_width=True)
            
            st.success("""
            **💡 Penjelasan Grafik Multivariat (File Tanpa Laba):**
            Grafik ini menganalisis 4 variabel sekaligus:
            1. Sumbu X = Perjalanan waktu dari minggu ke minggu.
            2. Sumbu Y = Total liter susu mingguan.
            3. Warna = Membedakan produksi antar tahun.
            4. **Besar Bulatan = Harga per Liter.** Semakin besar bulatan, artinya pada minggu tersebut harga susu sedang sangat bagus/mahal.
            """)

    else:
        st.error("❌ File CSV tidak memiliki kolom dasar (Harga per Liter / Volume Harian) yang dibutuhkan.")
else:
    st.info("👈 Silakan unggah file CSV di bagian atas. Anda bisa menggunakan file pertama maupun file kedua Anda!")
