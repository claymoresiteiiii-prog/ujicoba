import pandas as pd
import random

data = []
# Tren harga dasar (base price) di tingkat peternak (estimasi tren historis)
prices = {
    2020: 6500, 2021: 6700, 2022: 6900,
    2023: 7200, 2024: 7400, 2025: 7500, 2026: 7700
}

for year in range(2020, 2027):
    volume_akumulasi_2_minggu = 0
    
    for week in range(1, 53):
        # Rata-rata volume harian untuk minggu tersebut (40-70 liter)
        vol_harian = round(random.uniform(40, 70), 2)
        
        # Susu yang dihasilkan dalam seminggu (harian x 7)
        vol_mingguan = vol_harian * 7
        
        # Kumpulkan terus volume susu selama berjalan
        volume_akumulasi_2_minggu += vol_mingguan
        
        # Simulasi harga fluktuatif mingguan
        price = prices[year] + random.randint(-200, 200)
        price = round(price / 50) * 50
        
        # Hitung laba JIKA minggu ini adalah kelipatan 2 (minggu ke-2, ke-4, ke-6, dst)
        if week % 2 == 0:
            # Mengalikan total volume 2 minggu dengan harga dasar susu tahun tersebut
            laba_2_mingguan = round(volume_akumulasi_2_minggu * prices[year])
            # Reset penampung volume kembali menjadi 0 untuk perhitungan 2 minggu berikutnya
            volume_akumulasi_2_minggu = 0 
        else:
            # Karena belum cukup 2 minggu, tidak ada laba yang dicairkan/dihitung
            laba_2_mingguan = 0 
            
        data.append([year, week, vol_harian, vol_mingguan, price, laba_2_mingguan])

# Membuat DataFrame 
df = pd.DataFrame(data, columns=[
    'Tahun', 'Minggu Ke', 'Volume Harian (Liter)', 
    'Volume Mingguan (Liter)', 'Harga per Liter (Rp)', 
    'Laba Pendapatan 2 Mingguan (Rp)'
])

# Simpan ke CSV
df.to_csv('data_susu_sapi_dengan_laba.csv', index=False)
