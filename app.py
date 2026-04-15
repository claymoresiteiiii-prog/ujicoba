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

    st.sidebar.header("⚙️ Pengaturan Filter Data")
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

    # ==========================================
    # FITUR BARU: FILTER TAMPILAN GRAFIK
    # ==========================================
    st.sidebar.markdown("---")
    st.sidebar.header("👁️ Tampilan Visualisasi")
    
    opsi_grafik = [
        "1. Analisis Deskriptif & Musiman",
        "2. Analisis Profit & Pendapatan",
        "3. Korelasi & Persentase Profit",
        "4. Prediksi Tren Penjualan"
    ]
    
    grafik_ditampilkan = st.sidebar.multiselect(
        "Pilih grafik yang ingin ditampilkan:",
        options=opsi_grafik,
        default=opsi_grafik # Secara otomatis mencentang semua pilihan di awal
    )

    st.divider()

    # ==========================================
    # 3. ANALISIS UNIVARIAT & BIVARIAT
    # ==========================================
    required_cols = ['Harga per Liter (Rp)', 'Volume Mingguan (Liter)']
    if all(col in df_final.columns for col in required_cols):
        
        if df_final.empty:
            st.warning("⚠️ Tidak ada data untuk kombinasi filter yang dipilih.")
        else:
            
            if "1. Analisis Deskriptif & Musiman" in grafik_ditampilkan:
                st.header(f"📊 Analisis Deskriptif & Hubungan ({tahun_terpilih})")
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_vol = px.histogram(df_final, x="Volume Mingguan (Liter)", nbins=20,
                                         title="Distribusi Volume Produksi", color_discrete_sequence=['#54A24B'])
                    st.plotly_chart(fig_vol, use_container_width=True)
                    
                    vol_mean = df_final['Volume Mingguan (Liter)'].mean()
                    vol_std = df_final['Volume Mingguan (Liter)'].std() if len(df_final) > 1 else 0
                    st.write(f"**Analisis Volume:** Rata-rata produksi adalah **{vol_mean:.2f} Liter**. Variabilitas data (Std Dev) sebesar **{vol_std:.2f}**.")
                    st.info(f"💡 **Kesimpulan:** Sebagian besar produksi berpusat di sekitar nilai rata-rata {vol_mean:.0f} liter. Nilai variabilitas {vol_std:.0f} menunjukkan rentang fluktuasi produksi antar periode. Semakin kecil angkanya, semakin stabil produksi susu Anda.")
                
                with col2:
                    if 'Bulan' in df_final.columns:
                        vol_bulan = df_final.groupby('Bulan')['Volume Mingguan (Liter)'].mean().reset_index()
                        fig_bulan = px.bar(vol_bulan, x='Bulan', y='Volume Mingguan (Liter)', 
                                           title="Rata-rata Penjualan per Bulan", color_continuous_scale='Blues')
                        st.plotly_chart(fig_bulan, use_container_width=True)
                        
                        if not vol_bulan.empty:
                            max_month = vol_bulan.loc[vol_bulan['Volume Mingguan (Liter)'].idxmax(), 'Bulan']
                            min_month = vol_bulan.loc[vol_bulan['Volume Mingguan (Liter)'].idxmin(), 'Bulan']
                            st.write(f"**Analisis Musiman:** Puncak rata-rata tertinggi ada pada **Bulan {int(max_month)}**.")
                            st.info(f"💡 **Kesimpulan:** Periode paling produktif terjadi pada **Bulan {int(max_month)}**, sedangkan titik terendah ada pada **Bulan {int(min_month)}**. Disarankan untuk memaksimalkan persiapan stok pakan atau nutrisi ekstra menjelang bulan puncak produktivitas.")

                st.divider()

            # ==========================================
            # 4. ANALISIS PROFIT & PENDAPATAN
            # ==========================================
            if "2. Analisis Profit & Pendapatan" in grafik_ditampilkan:
                st.header("💰 Analisis Profit & Pendapatan")
                if 'Estimasi Profit (Rp)' in df_final.columns:
                    if 'Tahun' in df_final.columns and 'Minggu Ke' in df_final.columns:
                        df_final['Label Waktu'] = "Thn " + df_final['Tahun'].astype(str) + " - Mg " + df_final['Minggu Ke'].astype(str)
                    elif col_harian:
                        df_final['Label Waktu'] = df_final[col_harian].astype(str)
                    else:
                        df_final['Label Waktu'] = "Baris Data ke-" + df_final.index.astype(str)
                    
                    df_plot_profit = df_final.sort_values('Estimasi Profit (Rp)', ascending=False)

                    fig_profit = px.bar(df_plot_profit, x='Label Waktu', y='Estimasi Profit (Rp)',
                                        title=f"Grafik Profit/Penjualan ({profit_terpilih})",
                                        text_auto='.2s', 
                                        color='Estimasi Profit (Rp)', color_continuous_scale='Greens')
                    
                    fig_profit.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                    st.plotly_chart(fig_profit, use_container_width=True)
                    
                    if not df_plot_profit.empty:
                        total_profit_view = df_plot_profit['Estimasi Profit (Rp)'].sum()
                        top_label = df_plot_profit.iloc[0]['Label Waktu']
                        top_profit = df_plot_profit.iloc[0]['Estimasi Profit (Rp)']
                        st.info(f"💡 **Kesimpulan:** Total pendapatan dari data yang ditampilkan adalah **Rp {total_profit_view:,.0f}**. Titik pendapatan tertinggi tercatat pada **{top_label}** sebesar **Rp {top_profit:,.0f}**. Fluktuasi pada grafik ini membantu Anda melihat pola mingguan/bulanan mana yang memberi keuntungan finansial terbanyak.")

                st.divider()

            # ==========================================
            # 5. ANALISIS MULTIVARIAT & PERSENTASE
            # ==========================================
            if "3. Korelasi & Persentase Profit" in grafik_ditampilkan:
                st.header("🌐 Analisis Multivariat & Persentase Profit")
                col3, col4 = st.columns(2)

                with col3:
                    if len(df_final) > 1:
                        fig_korelasi = px.scatter(df_final, x="Harga per Liter (Rp)", y="Volume Mingguan (Liter)", 
                                                 trendline="ols", title="Korelasi: Harga vs Volume",
                                                 color_discrete_sequence=['#E45756'])
                        st.plotly_chart(fig_korelasi, use_container_width=True)
                        
                        corr_val = df_final['Harga per Liter (Rp)'].corr(df_final['Volume Mingguan (Liter)'])
                        st.write(f"**Analisis Korelasi:** Nilai korelasi antar variabel adalah **{corr_val:.2f}**.")
                        
                        if corr_val > 0.5: sifat_korelasi = "Positif Kuat (Seiring kenaikan harga, volume produksi juga naik)."
                        elif corr_val > 0: sifat_korelasi = "Positif Lemah."
                        elif corr_val < -0.5: sifat_korelasi = "Negatif Kuat (Seiring kenaikan harga, volume justru turun, atau sebaliknya)."
                        elif corr_val < 0: sifat_korelasi = "Negatif Lemah."
                        else: sifat_korelasi = "Sangat Lemah / Tidak ada hubungan yang jelas."
                        
                        st.info(f"💡 **Kesimpulan:** Hubungan antara Harga dan Volume adalah **{sifat_korelasi}** Analisis ini dapat menjadi acuan untuk menentukan strategi penetapan harga tanpa mengorbankan angka volume penjualan.")
                    else:
                        st.info("ℹ️ Data tidak cukup untuk membuat plot korelasi (minimal 2 baris data dibutuhkan).")

                with col4:
                    if 'Bulan' in df_final.columns and 'Estimasi Profit (Rp)' in df_final.columns:
                        profit_per_bulan = df_final.groupby('Bulan')['Estimasi Profit (Rp)'].sum().reset_index()
                        profit_per_bulan['Label Bulan'] = "Bulan " + profit_per_bulan['Bulan'].astype(str)
                        
                        fig_pie = px.pie(profit_per_bulan, values='Estimasi Profit (Rp)', names='Label Bulan',
                                         title="Distribusi Persentase Profit per Bulan",
                                         hole=0.4, 
                                         color_discrete_sequence=px.colors.sequential.Teal)
                        
                        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig_pie, use_container_width=True)
                        
                        if not profit_per_bulan.empty:
                            best_month_row = profit_per_bulan.loc[profit_per_bulan['Estimasi Profit (Rp)'].idxmax()]
                            st.info(f"💡 **Kesimpulan:** Kontribusi profit paling besar disumbangkan oleh **{best_month_row['Label Bulan']}** dengan total persentase tertinggi. Menjaga retensi performa pada bulan-bulan ini sangat krusial untuk kestabilan pendapatan tahunan Amang Farm.")
                    else:
                        st.info("ℹ️ Data 'Bulan' atau 'Estimasi Profit (Rp)' tidak ditemukan untuk membuat grafik persentase.")

                st.divider()

            # ==========================================
            # 6. CHART TREND & PREDIKSI
            # ==========================================
            if "4. Prediksi Tren Penjualan" in grafik_ditampilkan:
                st.header("📈 Prediksi Tren Penjualan Masa Depan")
                
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
                    kondisi = 'Meningkat' if slope > 0 else 'Menurun'
                    st.info(f"""
                    **💡 Hasil Analisis Prediksi Tren Global (Semua Waktu):**
                    1. **Arah Tren:** Penjualan diprediksi akan **{kondisi}**.
                    2. **Kecepatan Perubahan:** Rata-rata perubahan volume adalah **{abs(slope):.2f} Liter** per minggu.
                    
                    **Kesimpulan:** Secara proyeksi linear, bisnis peternakan Anda sedang dalam tren **{kondisi}**. {"Gunakan momentum ini untuk mempertimbangkan ekspansi kandang atau penambahan sapi." if slope > 0 else "Diperlukan evaluasi segera terhadap faktor penyebab penurunan seperti nutrisi pakan, cuaca, atau kesehatan ternak agar tren segera berbalik positif."}
                    """)
                else:
                    st.warning("Data historis tidak cukup untuk membuat model prediksi tren.")

    else:
        st.error(f"❌ Kolom data tidak lengkap. Pastikan CSV memiliki kolom: {required_cols}")
else:
    st.info("👈 Silakan unggah file CSV Amang Farm di menu samping.")
