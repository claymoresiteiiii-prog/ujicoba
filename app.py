import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Analisis Peternakan", layout="wide")
st.title("🐄 Dashboard Analisis Data Penjualan Sapi & Susu")
st.write("Unggah data Excel Anda untuk memulai analisis Univariat, Bivariat, dan Multivariat.")

# 1. Fitur Upload File Excel
uploaded_file = st.file_uploader("Upload file Excel (.xlsx atau .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Membaca data Excel
    df = pd.read_excel(uploaded_file)
    
    st.success("Data berhasil diunggah!")
    st.write("**Pratinjau Data:**")
    st.dataframe(df.head())
    
    # Memisahkan kolom numerik dan kategorikal untuk pilihan dropdown
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    all_columns = df.columns.tolist()

    st.markdown("---")
    
    # Membuat Tab untuk masing-masing analisis
    tab1, tab2, tab3 = st.tabs(["📊 Analisis Univariat", "📈 Analisis Bivariat", "🌌 Analisis Multivariat"])

    # ==========================================
    # TAB 1: ANALISIS UNIVARIAT
    # ==========================================
    with tab1:
        st.header("Analisis Univariat")
        st.write("Melihat distribusi satu variabel secara mandiri (Misal: Distribusi Harga Sapi atau Liter Susu).")
        
        uni_col = st.selectbox("Pilih Variabel (Numerik):", numeric_columns, key="uni")
        
        if uni_col:
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.histplot(df[uni_col], kde=True, color="skyblue", ax=ax)
            ax.set_title(f"Distribusi {uni_col}")
            ax.set_xlabel(uni_col)
            ax.set_ylabel("Frekuensi")
            st.pyplot(fig)
            
            st.write("**Statistik Deskriptif:**")
            st.write(df[uni_col].describe())

    # ==========================================
    # TAB 2: ANALISIS BIVARIAT
    # ==========================================
    with tab2:
        st.header("Analisis Bivariat")
        st.write("Menganalisis hubungan antara dua variabel (Misal: Hubungan Waktu/Bulan dengan Penjualan Susu).")
        
        col1, col2 = st.columns(2)
        with col1:
            x_biv = st.selectbox("Pilih Variabel X (Sumbu Horizontal):", all_columns, key="biv_x")
        with col2:
            y_biv = st.selectbox("Pilih Variabel Y (Sumbu Vertikal - Numerik):", numeric_columns, key="biv_y")
            
        if x_biv and y_biv:
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Jika X adalah kategorikal/waktu dan Y numerik, gunakan Barplot atau Boxplot
            if df[x_biv].dtype == 'object' or len(df[x_biv].unique()) < 20:
                sns.boxplot(x=df[x_biv], y=df[y_biv], palette="Set2", ax=ax)
                plt.xticks(rotation=45)
            # Jika X dan Y numerik, gunakan Scatterplot
            else:
                sns.scatterplot(x=df[x_biv], y=df[y_biv], color="coral", ax=ax)
                
            ax.set_title(f"Hubungan antara {x_biv} dan {y_biv}")
            st.pyplot(fig)

    # ==========================================
    # TAB 3: ANALISIS MULTIVARIAT
    # ==========================================
    with tab3:
        st.header("Analisis Multivariat")
        st.write("Menganalisis interaksi tiga variabel atau lebih (Misal: Tren penjualan berdasarkan liter susu, harga, dan jenis sapi/musim).")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            x_multi = st.selectbox("Pilih Variabel X:", numeric_columns, key="multi_x")
        with col2:
            y_multi = st.selectbox("Pilih Variabel Y:", numeric_columns, key="multi_y")
        with col3:
            hue_multi = st.selectbox("Pilih Variabel Pengelompokan (Warna):", all_columns, key="multi_hue")
            
        if x_multi and y_multi and hue_multi:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Scatterplot dengan Hue (warna) sebagai dimensi ketiga
            sns.scatterplot(data=df, x=x_multi, y=y_multi, hue=hue_multi, palette="viridis", size=hue_multi, sizes=(50, 200), ax=ax)
            
            ax.set_title(f"Interaksi {x_multi} dan {y_multi} dikelompokkan berdasarkan {hue_multi}")
            # Pindahkan legenda ke luar grafik agar tidak menutupi data
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            st.pyplot(fig)
            
        st.markdown("---")
        st.write("**Korelasi Antar Semua Variabel Numerik (Heatmap):**")
        # Hanya menghitung korelasi untuk kolom numerik
        corr = df[numeric_columns].corr()
        fig_corr, ax_corr = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax_corr)
        st.pyplot(fig_corr)

else:
    st.info("Silakan unggah file Excel di sebelah kiri/atas untuk melihat analisis.")
