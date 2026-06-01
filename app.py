import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Supply Chain Analytics", page_icon="🚚", layout="wide")

# ==========================================
# FUNGSI MEMUAT DATA
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('Supply_chain_dataset.csv')
        # Mengambil 5 baris pertama sebagai daftar pemasok aktif
        alt_df = df.head(5).copy()
        alt_df['Supplier'] = ['PT. Logistik Alpha', 'PT. Bina Sentosa', 'CV. Makmur Jaya', 'PT. Trans Nusa', 'CV. Karya Logistik']
        alt_df.set_index('Supplier', inplace=True)
        return df, alt_df
    except FileNotFoundError:
        st.error("Sistem tidak dapat menemukan database 'Supply_chain_dataset.csv'.")
        return pd.DataFrame(), pd.DataFrame()

df, alt_df = load_data()

if df.empty:
    st.stop()

# ==========================================
# SIDEBAR NAVIGASI PROFESIONAL
# ==========================================
st.sidebar.title("🚚 Supply Chain Analytics")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Pilih Modul Analisis:",
    [
        "📊 Ringkasan Kinerja Pemasok",
        "💰 Evaluasi Biaya & Kualitas",
        "☔ Analisis Risiko Operasional",
        "📉 Proyeksi Skenario Pasar",
        "⏱️ Pemodelan SLA Pengiriman",
        "🛡️ Profil Risiko Finansial",
        "🎲 Simulasi Ketahanan (Monte Carlo)",
        "🏆 Rekomendasi Eksekutif (DSS)"
    ]
)
st.sidebar.markdown("---")
st.sidebar.caption("Dashboard v1.0 | Divisi Procurement")

# ==========================================================
# 0. RINGKASAN DATA
# ==========================================================
if menu == "📊 Ringkasan Kinerja Pemasok":
    st.title("📊 Ringkasan Kinerja Pemasok (Aktif)")
    st.write("Database historis kinerja pemasok utama bulan ini. Data ini menjadi landasan untuk seluruh modul evaluasi sistem.")
    st.dataframe(alt_df[['price_per_unit', 'quality_score', 'delivery_time_days', 'on_time_delivery_rate', 'defect_rate']], use_container_width=True)

# ==========================================================
# 1. CERTAINTY -> EVALUASI BIAYA & KUALITAS
# ==========================================================
elif menu == "💰 Evaluasi Biaya & Kualitas":
    st.title("💰 Evaluasi Biaya & Kualitas Barang")
    
    with st.expander("📚 Landasan Teori: Decision Under Certainty"):
        st.write("""
        **Pengambilan Keputusan dalam Kondisi Pasti (Certainty)**
        Pada kondisi ini, pengambil keputusan mengetahui dengan pasti nilai hasil (payoff) dari setiap alternatif yang ada. Tidak ada probabilitas atau ketidakpastian. 
        Dalam modul ini, kita mengasumsikan harga kontrak (`price_per_unit`) dan kualitas barang (`quality_score`) adalah nilai tetap yang tidak akan berubah. Evaluasi dilakukan murni menggunakan perbandingan rasio tertimbang antara Biaya (Cost) dan Kualitas (Benefit).
        """)
        
    col1, col2 = st.columns(2)
    with col1:
        w_price = st.slider("Fokus Efisiensi Biaya (Cost)", 0.1, 1.0, 0.6)
    with col2:
        w_quality = st.slider("Fokus Kualitas Barang (Quality)", 0.1, 1.0, 0.4)
        
    norm_price = alt_df['price_per_unit'].min() / alt_df['price_per_unit']
    norm_qual = alt_df['quality_score'] / alt_df['quality_score'].max()    
    
    alt_df['Skor Efisiensi (0-1)'] = (norm_price * w_price) + (norm_qual * w_quality)
    best_supplier = alt_df['Skor Efisiensi (0-1)'].idxmax()
    
    st.dataframe(alt_df[['price_per_unit', 'quality_score', 'Skor Efisiensi (0-1)']].sort_values(by='Skor Efisiensi (0-1)', ascending=False))
    st.success(f"**Pemasok Paling Efisien:** {best_supplier}")

# ==========================================================
# 2. RISK -> ANALISIS RISIKO OPERASIONAL
# ==========================================================
elif menu == "☔ Analisis Risiko Operasional":
    st.title("☔ Analisis Risiko Operasional")
    
    with st.expander("📚 Landasan Teori: Decision Under Risk (Expected Value)"):
        st.write("""
        **Pengambilan Keputusan dalam Kondisi Berisiko (Risk)**
        Berbeda dengan *Certainty*, kondisi ini melibatkan probabilitas (peluang) yang sudah diketahui dari data historis. 
        Modul ini menggunakan metrik historis `on_time_delivery_rate` sebagai probabilitas sukses. Kita menghitung **Expected Value (Nilai Harapan)** dengan mengalikan probabilitas kejadian dengan dampak finansialnya (harga barang vs denda keterlambatan).
        """)
        
    penalty_rate = st.number_input("Estimasi Faktor Kerugian per Keterlambatan (Misal: 1.5x dari harga barang)", value=1.5, step=0.1)
    
    p_sukses = alt_df['on_time_delivery_rate']
    p_gagal = 1 - alt_df['on_time_delivery_rate']
    alt_df['Proyeksi Biaya Riil (Expected Cost)'] = (p_sukses * alt_df['price_per_unit']) + (p_gagal * (alt_df['price_per_unit'] * penalty_rate))
    
    st.bar_chart(alt_df['Proyeksi Biaya Riil (Expected Cost)'])
    st.success(f"**Pemasok dengan Risiko Biaya Terendah:** {alt_df['Proyeksi Biaya Riil (Expected Cost)'].idxmin()}")

# ==========================================================
# 3. UNCERTAINTY -> PROYEKSI SKENARIO PASAR
# ==========================================================
elif menu == "📉 Proyeksi Skenario Pasar":
    st.title("📉 Proyeksi Skenario Pasar")
    
    with st.expander("📚 Landasan Teori: Decision Under Uncertainty"):
        st.write("""
        **Pengambilan Keputusan dalam Kondisi Ketidakpastian (Uncertainty)**
        Kondisi ini terjadi ketika kita tahu apa saja skenario yang mungkin terjadi di masa depan, tetapi kita **tidak tahu nilai probabilitasnya**. 
        Oleh karena itu, digunakan pendekatan preferensi psikologis:
        * **Maximax (Strategi Agresif):** Memilih nilai keuntungan terbesar dari semua hasil maksimum (Sangat Optimis).
        * **Maximin (Strategi Defensif):** Memilih nilai terbaik dari semua kemungkinan terburuk (Sangat Pesimis / Main Aman).
        * **Laplace (Berimbang):** Mengasumsikan probabilitas semua skenario adalah sama besar (Rata-rata).
        """)
        
    alt_df['Estimasi Profit (Normal)'] = alt_df['price_per_unit'] * 0.30
    alt_df['Estimasi Profit (Krisis)'] = alt_df['Estimasi Profit (Normal)'] * (1 - alt_df['demand_volatility_index'])
    
    payoff_matrix = alt_df[['Estimasi Profit (Normal)', 'Estimasi Profit (Krisis)']]
    st.write("#### Matriks Skenario Profitabilitas")
    st.dataframe(payoff_matrix)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Strategi Agresif (Maximax)", payoff_matrix.max(axis=1).idxmax())
    col2.metric("Strategi Defensif (Maximin)", payoff_matrix.min(axis=1).idxmax())
    col3.metric("Strategi Berimbang (Laplace)", payoff_matrix.mean(axis=1).idxmax())

# ==========================================================
# 4. PROBABILISTIC -> PEMODELAN SLA PENGIRIMAN
# ==========================================================
elif menu == "⏱️ Pemodelan SLA Pengiriman":
    st.title("⏱️ Pemodelan Waktu Pengiriman (SLA)")
    
    with st.expander("📚 Landasan Teori: Probabilistic Modeling"):
        st.write("""
        **Pemodelan Probabilistik**
        Data historis logistik yang mentah (seperti waktu tempuh pengiriman) diekstrak untuk menemukan parameter populasinya (Mean/Rata-rata dan Standar Deviasi). 
        Parameter ini kemudian dicocokkan (fitting) ke dalam bentuk fungsi Distribusi Normal (Kurva Lonceng). Dengan memiliki model matematika distribusi ini, kita bisa menghitung peluang (probabilitas) kejadian spesifik, misalnya: "Berapa persen peluang pengiriman memakan waktu lebih dari 10 hari?"
        """)
        
    fig, ax = plt.subplots(figsize=(10, 4))
    data = df['delivery_time_days'].dropna()
    ax.hist(data, bins=20, density=True, alpha=0.5, color='#2E86C1', label='Data Riil')
    
    mu, std = stats.norm.fit(data)
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = stats.norm.pdf(x, mu, std)
    ax.plot(x, p, 'k', linewidth=2, label=f'Distribusi Kurva Normal\n($\\mu$={mu:.2f}, $\\sigma$={std:.2f})')
    ax.legend()
    st.pyplot(fig)
    
    st.write("#### Evaluasi Batas Toleransi SLA")
    batas_hari = st.slider("Target Maksimal Waktu Pengiriman (Hari):", 1, 30, 10)
    prob_telat = 1 - stats.norm.cdf(batas_hari, mu, std)
    st.warning(f"Berdasarkan model logistik, terdapat probabilitas sebesar **{prob_telat:.2%}** bahwa pengiriman akan meleset dari target {batas_hari} hari.")

# ==========================================================
# 5. UTILITY -> PROFIL RISIKO FINANSIAL
# ==========================================================
elif menu == "🛡️ Profil Risiko Finansial":
    st.title("🛡️ Profil Risiko Finansial")
    
    with st.expander("📚 Landasan Teori: Utility & Risk Preference"):
        st.write("""
        **Teori Utilitas dan Preferensi Risiko**
        Nilai nominal uang (misalnya profit Rp 100 Juta) tidak selalu dirasakan sama nilai gunanya (*utility*) oleh perusahaan yang berbeda. 
        Teori ini membedakan pengambil keputusan menjadi 3 tipe:
        1. **Risk Averse (Menghindari Risiko):** Direpresentasikan dengan fungsi Logaritmik. Mereka lebih memilih untung pasti yang kecil daripada bertaruh untuk untung besar.
        2. **Risk Neutral (Netral):** Direpresentasikan dengan fungsi Linier. Utilitas sama persis dengan nominal Expected Value.
        3. **Risk Seeker (Menyukai Risiko):** Direpresentasikan dengan fungsi Kuadratik/Eksponensial. Rela mengambil risiko tinggi demi keuntungan maksimal.
        """)
        
    preference = st.selectbox("Pilih Profil Manajemen Risiko:", 
                              ["Konservatif (Menghindari Risiko / Risk Averse)", 
                               "Moderat (Netral / Risk Neutral)", 
                               "Agresif (Berani Ambil Risiko / Risk Seeker)"])
    
    alt_df['Base Profit'] = alt_df['price_per_unit'] * 0.25
    
    if "Konservatif" in preference:
        alt_df['Skor Utilitas Finansial'] = np.log(alt_df['Base Profit'])
    elif "Agresif" in preference:
        alt_df['Skor Utilitas Finansial'] = alt_df['Base Profit']**2
    else:
        alt_df['Skor Utilitas Finansial'] = alt_df['Base Profit']
        
    st.dataframe(alt_df[['Base Profit', 'Skor Utilitas Finansial']].sort_values(by='Skor Utilitas Finansial', ascending=False))

# ==========================================================
# 6. SIMULATION -> SIMULASI KETAHANAN
# ==========================================================
elif menu == "🎲 Simulasi Ketahanan (Monte Carlo)":
    st.title("🎲 Simulasi Ketahanan Pemasok (Monte Carlo)")
    
    with st.expander("📚 Landasan Teori: Simulation & Sensitivity"):
        st.write("""
        **Simulasi dan Analisis Sensitivitas**
        Kondisi lapangan yang sangat dinamis tidak bisa dievaluasi hanya dengan satu titik data. 
        **Simulasi Monte Carlo** menggunakan algoritma untuk menghasilkan ribuan skenario data acak berdasarkan parameter yang ada (misal: defect rate). Analisis ini menguji seberapa *robust* (tahan banting) operasional pemasok jika terjadi goncangan/variasi data ekstrem yang tidak terduga.
        """)
        
    iterations = st.slider("Jumlah Iterasi Simulasi Skenario", 500, 5000, 1000)
    
    if st.button("Jalankan Uji Stres (Stress Test)"):
        with st.spinner("Menjalankan komputasi simulasi..."):
            mc_results = []
            np.random.seed(42)
            for supplier in alt_df.index:
                base_defect = alt_df.loc[supplier, 'defect_rate']
                sim_data = np.random.normal(loc=base_defect, scale=0.03, size=iterations)
                sim_data = np.clip(sim_data, 0, None) 
                prob_high = np.sum(sim_data > 0.08) / iterations
                mc_results.append(prob_high)
                
            alt_df['Risiko Defect Kritis (>8%)'] = mc_results
            st.bar_chart(alt_df['Risiko Defect Kritis (>8%)'])
            st.success(f"**Pemasok Paling Stabil (Robust):** {alt_df['Risiko Defect Kritis (>8%)'].idxmin()}")

# ==========================================================
# 7. DSS -> REKOMENDASI EKSEKUTIF
# ==========================================================
elif menu == "🏆 Rekomendasi Eksekutif (DSS)":
    st.title("🏆 Dasbor Rekomendasi Eksekutif (DSS)")
    
    with st.expander("📚 Landasan Teori: Decision Support System (DSS)"):
        st.write("""
        **Sistem Pendukung Keputusan (DSS)**
        Tahap puncak di mana seluruh perhitungan dari modul sebelumnya diintegrasikan. 
        Sistem ini mengimplementasikan metode **MCDM (Multi-Criteria Decision Making)**. Algoritma menyelaraskan berbagai variabel yang satuannya berbeda (seperti Biaya dalam bentuk Rupiah, Waktu dalam bentuk Hari, dan Kualitas dalam bentuk Skor) dengan cara menormalisasi nilainya, mengalikannya dengan bobot preferensi pengguna, dan memberikan satu peringkat rekomendasi akhir secara otomatis.
        """)
        
    st.write("#### Atur Parameter Prioritas Operasional")
    col1, col2, col3 = st.columns(3)
    w_cost = col1.number_input("Prioritas Efisiensi Biaya", 0.0, 1.0, 0.4)
    w_qual = col2.number_input("Prioritas Kualitas Barang", 0.0, 1.0, 0.3)
    w_time = col3.number_input("Prioritas Kecepatan Pengiriman", 0.0, 1.0, 0.3)
    
    matriks = alt_df[['price_per_unit', 'quality_score', 'delivery_time_days']].copy()
    matriks['Norm_Cost'] = matriks['price_per_unit'].min() / matriks['price_per_unit']
    matriks['Norm_Qual'] = matriks['quality_score'] / matriks['quality_score'].max()
    matriks['Norm_Time'] = matriks['delivery_time_days'].min() / matriks['delivery_time_days']
    
    matriks['Skor Evaluasi Akhir'] = (matriks['Norm_Cost'] * w_cost) + (matriks['Norm_Qual'] * w_qual) + (matriks['Norm_Time'] * w_time)
    hasil_akhir = matriks[['Skor Evaluasi Akhir']].sort_values(by='Skor Evaluasi Akhir', ascending=False)
    
    st.write("#### Peringkat Pemasok (Supplier Ranking)")
    st.dataframe(hasil_akhir.style.highlight_max(axis=0, color='#17A589'))
    
    st.success(f"**Kesimpulan Sistem:** Berdasarkan algoritma pembobotan saat ini, **{hasil_akhir.index[0]}** adalah pilihan pemasok paling strategis.")
    st.balloons()