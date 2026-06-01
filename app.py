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
# INJEKSI CSS: TEMA HITAM PUTIH & TRANSISI
# ==========================================
st.markdown("""
<style>
    /* 1. Efek Transisi Animasi Masuk (Fade In & Slide Up) */
    @keyframes smoothTransition {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0px); }
    }
    div.block-container {
        animation: smoothTransition 0.6s ease-out;
    }
    
    /* 2. Tema Hitam Putih (Dark Monochrome) */
    [data-testid="stAppViewContainer"] {
        background-color: #000000; /* Latar Belakang Hitam Pekat */
        color: #FFFFFF; /* Teks Putih */
    }
    [data-testid="stSidebar"] {
        background-color: #111111; /* Sidebar Abu-abu sangat gelap */
    }
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0); /* Header Transparan */
    }
    
    /* Modifikasi kotak metrik & expander agar kontras hitam putih */
    div[data-testid="stMetricValue"] {
        color: #FFFFFF;
    }
    div[data-testid="stExpander"] {
        background-color: #1A1A1A;
        border: 1px solid #333333;
    }
</style>
""", unsafe_allow_html=True)

# Set gaya grafik Matplotlib agar cocok dengan tema gelap
plt.style.use('dark_background')

# ==========================================
# FUNGSI MEMUAT DATA
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('Supply_chain_dataset.csv')
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
st.sidebar.title("🚚 Supply Chain DSS")
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
st.sidebar.caption("Dashboard v2.0 | Dark Edition")

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
    st.title("💰 Evaluasi Biaya & Kualitas")
    
    with st.expander("📚 Landasan Teori: Decision Under Certainty"):
        st.write("""
        **Pengambilan Keputusan dalam Kondisi Pasti (Certainty)**
        Pada kondisi ini, kita mengetahui dengan pasti nilai hasil (payoff) dari setiap alternatif. Evaluasi ini dilakukan murni menggunakan data kontrak statis (Harga per Unit dan Skor Kualitas) tanpa memasukkan elemen probabilitas gangguan di masa depan.
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
        Berbeda dengan *Certainty*, kondisi ini melibatkan peluang yang diketahui dari data historis. Kita menghitung **Expected Value (Nilai Harapan)** dengan mengalikan probabilitas pengiriman sukses dengan harga normal, ditambah probabilitas gagal dikalikan dengan beban denda keterlambatan.
        """)
        
    penalty_rate = st.number_input("Estimasi Faktor Denda Keterlambatan (Misal: 1.5x dari harga barang)", value=1.5, step=0.1)
    
    p_sukses = alt_df['on_time_delivery_rate']
    p_gagal = 1 - alt_df['on_time_delivery_rate']
    alt_df['Expected Cost (Proyeksi Biaya)'] = (p_sukses * alt_df['price_per_unit']) + (p_gagal * (alt_df['price_per_unit'] * penalty_rate))
    
    st.bar_chart(alt_df['Expected Cost (Proyeksi Biaya)'])
    st.success(f"**Pemasok dengan Risiko Biaya Terendah:** {alt_df['Expected Cost (Proyeksi Biaya)'].idxmin()}")

# ==========================================================
# 3. UNCERTAINTY -> PROYEKSI SKENARIO PASAR
# ==========================================================
elif menu == "📉 Proyeksi Skenario Pasar":
    st.title("📉 Proyeksi Skenario Pasar")
    
    with st.expander("📚 Landasan Teori: Decision Under Uncertainty"):
        st.write("""
        **Pengambilan Keputusan dalam Kondisi Ketidakpastian (Uncertainty)**
        Kondisi ini terjadi ketika probabilitas kejadian di masa depan tidak diketahui. Oleh karena itu, digunakan pendekatan preferensi psikologis:
        * **Maximax:** Strategi Sangat Optimis (memilih nilai terbaik dari kemungkinan terbaik).
        * **Maximin:** Strategi Defensif/Pesimis (memilih nilai terbaik dari kemungkinan terburuk).
        * **Laplace:** Strategi Berimbang (mengasumsikan semua skenario memiliki peluang yang sama).
        """)
        
    alt_df['Estimasi Profit (Normal)'] = alt_df['price_per_unit'] * 0.30
    alt_df['Estimasi Profit (Volatil)'] = alt_df['Estimasi Profit (Normal)'] * (1 - alt_df['demand_volatility_index'])
    
    payoff_matrix = alt_df[['Estimasi Profit (Normal)', 'Estimasi Profit (Volatil)']]
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
    st.title("⏱️ Pemodelan Waktu Pengiriman")
    
    with st.expander("📚 Landasan Teori: Probabilistic Modeling"):
        st.write("""
        **Pemodelan Probabilistik**
        Data mentah waktu pengiriman diekstrak untuk menemukan parameternya (Mean dan Standar Deviasi), kemudian dicocokkan ke fungsi Distribusi Normal. Dari model distribusi matematika ini, kita dapat mengestimasi probabilitas terjadinya keterlambatan secara presisi.
        """)
        
    fig, ax = plt.subplots(figsize=(10, 4))
    data = df['delivery_time_days'].dropna()
    # Menggunakan warna abu-abu/putih agar serasi dengan tema gelap
    ax.hist(data, bins=20, density=True, alpha=0.6, color='#FFFFFF', label='Data Riil')
    
    mu, std = stats.norm.fit(data)
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = stats.norm.pdf(x, mu, std)
    ax.plot(x, p, color='#00FFCC', linewidth=2, label=f'Distribusi Normal\n($\\mu$={mu:.2f}, $\\sigma$={std:.2f})')
    ax.legend()
    st.pyplot(fig)
    
    batas_hari = st.slider("Target Batas Waktu Pengiriman (Hari):", 1, 30, 10)
    prob_telat = 1 - stats.norm.cdf(batas_hari, mu, std)
    st.warning(f"Probabilitas pengiriman melewati batas {batas_hari} hari adalah sebesar **{prob_telat:.2%}**.")

# ==========================================================
# 5. UTILITY -> PROFIL RISIKO FINANSIAL
# ==========================================================
elif menu == "🛡️ Profil Risiko Finansial":
    st.title("🛡️ Profil Risiko Finansial")
    
    with st.expander("📚 Landasan Teori: Utility & Risk Preference"):
        st.write("""
        **Teori Utilitas dan Preferensi Risiko**
        Nominal uang memiliki nilai guna (*utility*) yang berbeda tergantung pada profil perusahaan.
        Fungsi logaritmik digunakan untuk manajemen Konservatif (Risk Averse), fungsi linier untuk Netral, dan fungsi kuadratik untuk manajemen Agresif (Risk Seeker).
        """)
        
    preference = st.selectbox("Pilih Profil Manajemen Risiko:", 
                              ["Konservatif (Risk Averse / Logaritmik)", 
                               "Netral (Risk Neutral / Linier)", 
                               "Agresif (Risk Seeker / Kuadratik)"])
    
    alt_df['Base Profit'] = alt_df['price_per_unit'] * 0.25
    
    if "Konservatif" in preference:
        alt_df['Skor Utilitas'] = np.log(alt_df['Base Profit'])
    elif "Agresif" in preference:
        alt_df['Skor Utilitas'] = alt_df['Base Profit']**2
    else:
        alt_df['Skor Utilitas'] = alt_df['Base Profit']
        
    st.dataframe(alt_df[['Base Profit', 'Skor Utilitas']].sort_values(by='Skor Utilitas', ascending=False))

# ==========================================================
# 6. SIMULATION -> SIMULASI KETAHANAN
# ==========================================================
elif menu == "🎲 Simulasi Ketahanan (Monte Carlo)":
    st.title("🎲 Simulasi Ketahanan (Monte Carlo)")
    
    with st.expander("📚 Landasan Teori: Simulation & Sensitivity"):
        st.write("""
        **Simulasi Monte Carlo & Analisis Sensitivitas**
        Kondisi lapangan diuji dengan menghasilkan ribuan skenario data acak untuk melihat dampaknya pada hasil akhir. Analisis ini menguji seberapa kebal (*robust*) sistem jika variabel tingkat kecacatan (*defect rate*) mengalami gejolak tak terduga.
        """)
        
    iterations = st.slider("Jumlah Iterasi Skenario Acak", 500, 5000, 1000)
    
    if st.button("Jalankan Uji Stres"):
        with st.spinner("Komputasi iterasi berjalan..."):
            mc_results = []
            np.random.seed(42)
            for supplier in alt_df.index:
                base_defect = alt_df.loc[supplier, 'defect_rate']
                sim_data = np.random.normal(loc=base_defect, scale=0.03, size=iterations)
                sim_data = np.clip(sim_data, 0, None) 
                prob_high = np.sum(sim_data > 0.08) / iterations
                mc_results.append(prob_high)
                
            alt_df['Probabilitas Defect >8%'] = mc_results
            st.bar_chart(alt_df['Probabilitas Defect >8%'])
            st.success(f"**Pemasok Paling Stabil:** {alt_df['Probabilitas Defect >8%'].idxmin()}")

# ==========================================================
# 7. DSS -> REKOMENDASI EKSEKUTIF
# ==========================================================
elif menu == "🏆 Rekomendasi Eksekutif (DSS)":
    st.title("🏆 Rekomendasi Eksekutif (DSS)")
    
    with st.expander("📚 Landasan Teori: Decision Support System"):
        st.write("""
        **Sistem Pendukung Keputusan (MCDM)**
        Sistem mengintegrasikan matriks keputusan multi-kriteria (Biaya, Kualitas, Kecepatan) yang telah dinormalisasi. Berdasarkan bobot interaktif, sistem akan mengevaluasi kinerja dan menghasilkan pemeringkatan (ranking) alternatif terbaik tanpa peramalan waktu masa depan.
        """)
        
    st.write("#### Preferensi Operasional Hari Ini")
    col1, col2, col3 = st.columns(3)
    w_cost = col1.number_input("Prioritas Efisiensi Biaya", 0.0, 1.0, 0.4)
    w_qual = col2.number_input("Prioritas Kualitas Barang", 0.0, 1.0, 0.3)
    w_time = col3.number_input("Prioritas Kecepatan Waktu", 0.0, 1.0, 0.3)
    
    matriks = alt_df[['price_per_unit', 'quality_score', 'delivery_time_days']].copy()
    matriks['Norm_Cost'] = matriks['price_per_unit'].min() / matriks['price_per_unit']
    matriks['Norm_Qual'] = matriks['quality_score'] / matriks['quality_score'].max()
    matriks['Norm_Time'] = matriks['delivery_time_days'].min() / matriks['delivery_time_days']
    
    matriks['Skor DSS'] = (matriks['Norm_Cost'] * w_cost) + (matriks['Norm_Qual'] * w_qual) + (matriks['Norm_Time'] * w_time)
    hasil_akhir = matriks[['Skor DSS']].sort_values(by='Skor DSS', ascending=False)
    
    st.write("#### Peringkat Pemasok (Ranking)")
    st.dataframe(hasil_akhir)
    st.success(f"**Kesimpulan:** Sistem DSS menetapkan **{hasil_akhir.index[0]}** sebagai pemasok paling strategis.")
    st.balloons()