import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="DSS Supply Chain", layout="wide")

# ==========================================
# FUNGSI MEMUAT DATA
# ==========================================
@st.cache_data
def load_data():
    try:
        # Membaca file dataset
        df = pd.read_csv('Supply_chain_dataset.csv')
        
        # Mengambil 5 baris pertama sebagai dummy supplier alternatif untuk dianalisis
        alt_df = df.head(5).copy()
        alt_df['Supplier'] = ['Supplier A', 'Supplier B', 'Supplier C', 'Supplier D', 'Supplier E']
        alt_df.set_index('Supplier', inplace=True)
        return df, alt_df
    except FileNotFoundError:
        st.error("File 'Supply_chain_dataset.csv' tidak ditemukan. Pastikan file berada di folder yang sama dengan file Python ini.")
        return pd.DataFrame(), pd.DataFrame()

df, alt_df = load_data()

# Menghentikan eksekusi jika data tidak ada
if df.empty:
    st.stop()

# ==========================================
# SIDEBAR NAVIGASI
# ==========================================
st.sidebar.title("Navigasi Materi")
st.sidebar.markdown("Mata Kuliah: **Pengantar Teori Pengambilan Keputusan**")
materi = st.sidebar.radio(
    "Pilih Modul Pembelajaran:",
    [
        "1. Decision Under Certainty",
        "2. Decision Under Risk",
        "3. Decision Under Uncertainty",
        "4. Probabilistic Modeling",
        "5. Utility & Risk Preference",
        "6. Simulation & Sensitivity",
        "7. Decision Support System (DSS)"
    ]
)

# ==========================================================
# MATERI 1: DECISION UNDER CERTAINTY
# ==========================================================
if materi == "1. Decision Under Certainty":
    st.title("Materi 1: Decision Under Certainty")
    
    st.info("""
    **Penjelasan Materi:**
    Kondisi *Certainty* (Kepastian) terjadi ketika pengambil keputusan mengetahui dengan pasti hasil (payoff) dari setiap alternatif. 
    Kita mengevaluasi data faktual yang ada (misalnya harga kontrak yang sudah tetap) tanpa probabilitas acak.
    """)
    
    st.write("### Data Alternatif Supplier (Atribut Pasti)")
    st.dataframe(alt_df[['price_per_unit', 'quality_score', 'delivery_time_days']])
    
    st.write("### Simulasi Keputusan")
    st.write("Tentukan preferensi bobot kriteria yang paling penting bagi perusahaan saat ini:")
    
    col1, col2 = st.columns(2)
    with col1:
        w_price = st.slider("Bobot Harga (Semakin besar = cari termurah)", 0.1, 1.0, 0.6)
    with col2:
        w_quality = st.slider("Bobot Kualitas (Semakin besar = cari kualitas terbaik)", 0.1, 1.0, 0.4)
        
    # Normalisasi Data
    norm_price = alt_df['price_per_unit'].min() / alt_df['price_per_unit'] # Cost (Makin kecil makin baik)
    norm_qual = alt_df['quality_score'] / alt_df['quality_score'].max()    # Benefit (Makin besar makin baik)
    
    # Perhitungan Skor
    alt_df['Skor Kepastian'] = (norm_price * w_price) + (norm_qual * w_quality)
    best_supplier = alt_df['Skor Kepastian'].idxmax()
    
    st.write("**Hasil Evaluasi Deterministik:**")
    st.dataframe(alt_df[['Skor Kepastian']].sort_values(by='Skor Kepastian', ascending=False))
    st.success(f"**Keputusan Terbaik:** {best_supplier}")

# ==========================================================
# MATERI 2: DECISION UNDER RISK (EV)
# ==========================================================
elif materi == "2. Decision Under Risk":
    st.title("Materi 2: Decision Under Risk (Expected Value)")
    
    st.info("""
    **Penjelasan Materi:**
    Kondisi *Risk* terjadi ketika hasil keputusan dipengaruhi oleh probabilitas kejadian (dari data historis). 
    Kita menggunakan *Expected Value* (Nilai Harapan) dengan memperhitungkan peluang sukses dan gagal.
    """)
    
    st.write("### Data Probabilitas Ketepatan Waktu")
    st.dataframe(alt_df[['price_per_unit', 'on_time_delivery_rate']])
    
    penalty_rate = st.number_input("Tentukan Faktor Penalti jika terjadi keterlambatan (Misal: 1.5 = denda 50%)", value=1.5, step=0.1)
    
    # Menghitung EV Biaya
    p_sukses = alt_df['on_time_delivery_rate']
    p_gagal = 1 - alt_df['on_time_delivery_rate']
    
    alt_df['Expected Cost (EV)'] = (p_sukses * alt_df['price_per_unit']) + (p_gagal * (alt_df['price_per_unit'] * penalty_rate))
    
    st.write("**Hasil Perhitungan Expected Value (Biaya Harapan):**")
    st.bar_chart(alt_df['Expected Cost (EV)'])
    st.success(f"**Rekomendasi (EV Biaya Terendah):** {alt_df['Expected Cost (EV)'].idxmin()}")

# ==========================================================
# MATERI 3: DECISION UNDER UNCERTAINTY
# ==========================================================
elif materi == "3. Decision Under Uncertainty":
    st.title("Materi 3: Decision Under Uncertainty")
    
    st.info("""
    **Penjelasan Materi:**
    Kondisi *Uncertainty* terjadi saat kita tahu apa saja kemungkinan keadaan (States of Nature), tetapi kita **TIDAK TAHU probabilitasnya**. 
    Metode:
    * **Maximax:** Sangat optimis (memilih nilai maksimum dari hasil maksimum).
    * **Maximin:** Sangat pesimis (memilih nilai maksimum dari hasil minimum).
    * **Laplace:** Menganggap semua skenario punya probabilitas yang sama (Rata-rata).
    """)
    
    st.write("### Matriks Keuntungan (Payoff Matrix) Proyeksi Margin")
    
    # Simulasi Payoff Matrix
    alt_df['Profit_Normal'] = alt_df['price_per_unit'] * 0.30
    alt_df['Profit_Krisis'] = alt_df['Profit_Normal'] * (1 - alt_df['demand_volatility_index'])
    
    payoff_matrix = alt_df[['Profit_Normal', 'Profit_Krisis']]
    st.dataframe(payoff_matrix)
    
    # Perhitungan
    max_payoff = payoff_matrix.max(axis=1) # Nilai maksimum tiap baris
    min_payoff = payoff_matrix.min(axis=1) # Nilai minimum tiap baris
    laplace_payoff = payoff_matrix.mean(axis=1) # Rata-rata
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Maximax (Optimis)", max_payoff.idxmax())
    col2.metric("Maximin (Pesimis)", min_payoff.idxmax())
    col3.metric("Laplace (Rata-rata)", laplace_payoff.idxmax())

# ==========================================================
# MATERI 4: PROBABILISTIC MODELING
# ==========================================================
elif materi == "4. Probabilistic Modeling":
    st.title("Materi 4: Probabilistic Modeling")
    
    st.info("""
    **Penjelasan Materi:**
    Mengubah *raw data* menjadi fungsi distribusi (misalnya Distribusi Normal). Dengan memahami bentuk distribusinya, kita bisa mengestimasi probabilitas risiko spesifik.
    """)
    
    st.write("### Distribusi Waktu Pengiriman (Delivery Time Days)")
    
    fig, ax = plt.subplots(figsize=(8, 4))
    data = df['delivery_time_days'].dropna()
    
    # Plot histogram
    ax.hist(data, bins=20, density=True, alpha=0.6, color='b', label='Data Historis')
    
    # Plot Normal Curve
    mu, std = stats.norm.fit(data)
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = stats.norm.pdf(x, mu, std)
    
    # PERBAIKAN: Menggunakan \\mu dan \\sigma agar tidak muncul warning
    ax.plot(x, p, 'k', linewidth=2, label=f'Distribusi Normal\n($\\mu$={mu:.2f}, $\\sigma$={std:.2f})')
    ax.legend()
    st.pyplot(fig)
    
    st.write("### Hitung Risiko Keterlambatan")
    batas_hari = st.slider("Tentukan batas toleransi waktu (hari):", 1, 30, 10)
    prob_telat = 1 - stats.norm.cdf(batas_hari, mu, std)
    
    st.warning(f"Peluang pengiriman memakan waktu lebih dari {batas_hari} hari adalah **{prob_telat:.2%}**")

# ==========================================================
# MATERI 5: UTILITY & RISK PREFERENCE
# ==========================================================
elif materi == "5. Utility & Risk Preference":
    st.title("Materi 5: Utility & Risk Preference")
    
    st.info("""
    **Penjelasan Materi:**
    Teori utilitas memodelkan preferensi subjektif. Pengambil keputusan diklasifikasikan menjadi *Risk-Averse* (menghindari risiko), *Risk-Neutral*, dan *Risk-Seeker* (menyukai risiko).
    """)
    
    preference = st.selectbox("Pilih Profil Risiko Perusahaan:", 
                              ["Risk Averse (Menghindari Risiko - Logaritmik)", 
                               "Risk Neutral (Netral - Linier)", 
                               "Risk Seeker (Menyukai Risiko - Kuadratik)"])
    
    # Mengambil base profit
    alt_df['Base Profit'] = alt_df['price_per_unit'] * 0.25
    
    if "Averse" in preference:
        alt_df['Utility Score'] = np.log(alt_df['Base Profit'])
    elif "Seeker" in preference:
        alt_df['Utility Score'] = alt_df['Base Profit']**2
    else:
        alt_df['Utility Score'] = alt_df['Base Profit']
        
    st.write(f"**Skor Utilitas berdasarkan profil {preference}:**")
    st.dataframe(alt_df[['Base Profit', 'Utility Score']].sort_values(by='Utility Score', ascending=False))

# ==========================================================
# MATERI 6: SIMULATION & SENSITIVITY
# ==========================================================
elif materi == "6. Simulation & Sensitivity":
    st.title("Materi 6: Simulation & Sensitivity")
    
    st.info("""
    **Penjelasan Materi:**
    *Monte Carlo Simulation* menggunakan angka acak berulang-ulang (ribuan kali) untuk melihat dampak fluktuasi pada hasil akhir dan menguji seberapa kuat (robust) sebuah keputusan.
    """)
    
    st.write("### Monte Carlo Simulation (Fluktuasi Defect Rate)")
    iterations = st.slider("Jumlah Iterasi Simulasi", 100, 5000, 1000)
    
    if st.button("Jalankan Simulasi"):
        mc_results = []
        np.random.seed(42)
        for supplier in alt_df.index:
            base_defect = alt_df.loc[supplier, 'defect_rate']
            # Simulasi normal
            sim_data = np.random.normal(loc=base_defect, scale=0.03, size=iterations)
            sim_data = np.clip(sim_data, 0, None) # Mencegah nilai negatif
            # Hitung peluang jika defect rate melebihi 8%
            prob_high = np.sum(sim_data > 0.08) / iterations
            mc_results.append(prob_high)
            
        alt_df['Prob_Defect_Tinggi (>8%)'] = mc_results
        st.write("**Hasil Simulasi:** Peluang cacat barang melampaui batas kritis (8%)")
        st.bar_chart(alt_df['Prob_Defect_Tinggi (>8%)'])
        st.success(f"**Supplier Paling Tahan Banting (Robust):** {alt_df['Prob_Defect_Tinggi (>8%)'].idxmin()}")

# ==========================================================
# MATERI 7: DECISION SUPPORT SYSTEM (DSS)
# ==========================================================
elif materi == "7. Decision Support System (DSS)":
    st.title("Materi 7: Decision Support System (DSS)")
    
    st.info("""
    **Penjelasan Materi:**
    DSS menggabungkan semua kriteria keputusan (MCDM) untuk merangking alternatif terbaik berdasarkan preferensi tanpa harus melakukan peramalan/prediksi ke masa depan.
    """)
    
    st.write("### Dasbor Pengambil Keputusan (Integrasi Kriteria)")
    col1, col2, col3 = st.columns(3)
    w_cost = col1.number_input("Bobot Biaya (Target: Minimum)", 0.0, 1.0, 0.4)
    w_qual = col2.number_input("Bobot Kualitas (Target: Maksimum)", 0.0, 1.0, 0.3)
    w_time = col3.number_input("Bobot Waktu (Target: Minimum)", 0.0, 1.0, 0.3)
    
    # Evaluasi Multi-Kriteria
    matriks = alt_df[['price_per_unit', 'quality_score', 'delivery_time_days']].copy()
    
    # Normalisasi Data (Cost & Benefit)
    matriks['Norm_Cost'] = matriks['price_per_unit'].min() / matriks['price_per_unit']
    matriks['Norm_Qual'] = matriks['quality_score'] / matriks['quality_score'].max()
    matriks['Norm_Time'] = matriks['delivery_time_days'].min() / matriks['delivery_time_days']
    
    matriks['Skor DSS Akhir'] = (matriks['Norm_Cost'] * w_cost) + (matriks['Norm_Qual'] * w_qual) + (matriks['Norm_Time'] * w_time)
    hasil_akhir = matriks[['Skor DSS Akhir']].sort_values(by='Skor DSS Akhir', ascending=False)
    
    st.write("### Rekomendasi Peringkat Akhir Sistem")
    st.dataframe(hasil_akhir.style.highlight_max(axis=0, color='lightgreen'))
    st.balloons()
    st.success(f"Sistem merekomendasikan **{hasil_akhir.index[0]}** sebagai pemasok terbaik hari ini.")