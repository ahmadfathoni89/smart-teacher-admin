import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- CONFIG FIX KUNCI AQ ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = None

if API_KEY:
    # transport="rest" wajib untuk kunci format AQ
    genai.configure(api_key=API_KEY, transport="rest")
    model = genai.GenerativeModel('models/gemini-1.5-flash')
else:
    st.error("⚠️ API Key belum dimasukkan di Secrets!")

# --- LOGIKA JP PERMENDIKDASMEN 13/2025 ---
def get_jp_logic(mapel):
    special = ["PABP", "PJOK", "Bahasa Inggris", "Bahasa Jawa"]
    if mapel in special:
        return "Disusun untuk 1 kali pertemuan tuntas (Blok JP)."
    return "Materi dibagi rapi per 2 JP per pertemuan (Deep Learning)."

# --- UI APLIKASI ---
st.set_page_config(page_title="Gen-Guru AI 2025", layout="wide")
st.title("📝 Generator Administrasi Guru TA 2025/2026")
st.info("Sesuai Permendikdasmen No. 13 Tahun 2025")

with st.sidebar:
    st.header("📋 Identitas")
    sekolah = st.text_input("Nama Sekolah", "SD Negeri ...")
    guru = st.text_input("Nama Guru", "Nama Guru, S.Pd.")
    nip = st.text_input("NIP", "19xxxx")
    kepsek = st.text_input("Kepala Sekolah", "Nama Kepsek, M.Pd.")
    st.divider()
    mapel = st.selectbox("Mata Pelajaran", ["Bahasa Indonesia", "Matematika", "IPAS", "PABP", "PJOK", "Bahasa Inggris", "Bahasa Jawa"])
    kelas = st.text_input("Kelas", "4")
    fase = st.text_input("Fase", "B")

if 'data' not in st.session_state:
    st.session_state.data = {}

def ai_gen(prompt):
    try:
        res = model.generate_content(prompt)
        return res.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- TAB PROSES BERURUTAN ---
t1, t2, t3, t4 = st.tabs(["1. PROTA", "2. PROMES", "3. CP/TP/ATP", "4. MODUL AJAR"])

with t1:
    if st.button("Generate PROTA"):
        with st.spinner("AI sedang menyusun Prota..."):
            p = f"Buatlah Tabel Program Tahunan (PROTA) {mapel} Kelas {kelas} sesuai Permendikdasmen 13/2025. Referensi buku Kemendikdasmen."
            st.session_state.data['prota'] = ai_gen(p)
    if 'prota' in st.session_state.data:
        st.markdown(st.session_state.data['prota'])

with t2:
    if 'prota' not in st.session_state.data:
        st.warning("Generate Prota dulu!")
    else:
        if st.button("Generate PROMES"):
            with st.spinner("Menyusun Promes..."):
                p = f"Berdasarkan Prota ini: {st.session_state.data['prota']}, buatkan Tabel PROMES ganjil & genap."
                st.session_state.data['promes'] = ai_gen(p)
        if 'promes' in st.session_state.data:
            st.markdown(st.session_state.data['promes'])

with t3:
    if 'promes' not in st.session_state.data:
        st.warning("Generate Promes dulu!")
    else:
        if st.button("Generate CP, TP & ATP"):
            with st.spinner("Menganalisis Kompetensi..."):
                p = f"Breakdown CP, TP, dan ATP untuk {mapel} Kelas {kelas} sesuai Permendikdasmen 13/2025."
                st.session_state.data['atp'] = ai_gen(p)
        if 'atp' in st.session_state.data:
            st.markdown(st.session_state.data['atp'])

with t4:
    if 'atp' not in st.session_state.data:
        st.warning("Generate ATP dulu!")
    else:
        logic = get_jp_logic(mapel)
        st.info(f"Aturan Pembagian JP: {logic}")
        if st.button("Generate MODUL AJAR LENGKAP"):
            with st.spinner("Menyusun Modul Ajar Detail..."):
                p = f"""Buatkan Modul Ajar (MA) lengkap {mapel} Kelas {kelas}. 
                Aturan JP: {logic}. Harus mencakup: 
                1. Langkah Pembelajaran (Pendahuluan, Inti, Penutup). 
                2. Bahan Ajar Materi. 
                3. Asesmen Formatif & Sumatif. 
                Referensi: Buku Kemendikdasmen terbaru. Format rapi."""
                st.session_state.data['ma'] = ai_gen(p)
        if 'ma' in st.session_state.data:
            st.markdown(st.session_state.data['ma'])
            
            # FITUR CETAK PDF
            if st.button("📥 Download PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=10)
                isi = f"ADMINISTRASI GURU\nSekolah: {sekolah}\nGuru: {guru}\n\n{st.session_state.data['ma']}"
                pdf.multi_cell(0, 5, isi.encode('latin-1', 'replace').decode('latin-1'))
                pdf.output("Modul_Ajar.pdf")
                with open("Modul_Ajar.pdf", "rb") as f:
                    st.download_button("Simpan PDF", f, "Modul_Ajar.pdf")
