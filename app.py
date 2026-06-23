import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- CONFIG KUNCI AQ ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = None

if API_KEY:
    # transport="rest" wajib untuk kunci format AQ agar tidak Error 401
    genai.configure(api_key=API_KEY, transport="rest")
    # Gunakan 'models/gemini-1.5-flash' (lengkap dengan awalan models/) agar tidak Error 404
    model = genai.GenerativeModel('models/gemini-1.5-flash')
else:
    st.error("⚠️ API Key belum diisi di Secrets!")

# --- LOGIKA JP (PERMEN 13/2025) ---
def get_jp_logic(mapel):
    special = ["PABP", "PJOK", "Bahasa Inggris", "Bahasa Jawa"]
    if mapel in special:
        return "1 kali pertemuan tuntas (Sesuai Permen No. 13 Tahun 2025)"
    return "Dibagi rata per 2 Jam Pelajaran (JP) per pertemuan (Deep Learning)"

# --- UI STREAMLIT ---
st.set_page_config(page_title="Gen-Guru AI 2025", layout="wide")
st.title("🚀 Generator Administrasi Guru 2025")
st.subheader("Sesuai Permendikdasmen No. 13 Tahun 2025")

with st.sidebar:
    st.header("📋 Data Identitas")
    sekolah = st.text_input("Nama Sekolah", "SD Negeri ...")
    guru = st.text_input("Nama Guru", "Nama Anda, S.Pd.")
    nip = st.text_input("NIP", "19xxxx")
    kepsek = st.text_input("Kepala Sekolah", "Nama Kepsek, M.Pd.")
    st.divider()
    mapel = st.selectbox("Mata Pelajaran", ["Bahasa Indonesia", "Matematika", "IPAS", "PABP", "PJOK", "Bahasa Inggris", "Bahasa Jawa"])
    kelas = st.text_input("Kelas", "4")
    fase = st.text_input("Fase", "B")

if 'admin_data' not in st.session_state:
    st.session_state.admin_data = {}

def panggil_ai(prompt):
    try:
        # Tambahan safety settings agar output tidak terpotong
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Waduh, Error: {str(e)}"

# --- ALUR GENERATE ---
t1, t2, t3, t4 = st.tabs(["1. PROTA", "2. PROMES", "3. CP/ATP", "4. MODUL AJAR"])

with t1:
    if st.button("Buat PROTA"):
        with st.spinner("AI sedang menyusun Prota..."):
            p = f"Buatlah Tabel Program Tahunan (PROTA) {mapel} Kelas {kelas} sesuai Permendikdasmen 13/2025. Referensi buku: https://buku.kemendikdasmen.go.id/katalog."
            st.session_state.admin_data['prota'] = panggil_ai(p)
    if 'prota' in st.session_state.admin_data:
        st.markdown(st.session_state.admin_data['prota'])

with t2:
    if 'prota' in st.session_state.admin_data:
        if st.button("Buat PROMES"):
            with st.spinner("Menyusun Promes..."):
                p = f"Berdasarkan Prota ini: {st.session_state.admin_data['prota']}, buatkan Tabel PROMES ganjil & genap."
                st.session_state.admin_data['promes'] = panggil_ai(p)
        if 'promes' in st.session_state.admin_data:
            st.markdown(st.session_data.admin_data['promes'])
    else: st.info("Selesaikan Prota dulu.")

with t4:
    if 'prota' in st.session_state.admin_data:
        jp = get_jp_logic(mapel)
        st.info(f"Aturan JP: {jp}")
        if st.button("Buat MODUL AJAR LENGKAP"):
            with st.spinner("AI sedang menyusun Modul Ajar + Bahan Ajar + Asesmen..."):
                p = f"""Buatkan Modul Ajar {mapel} Kelas {kelas} Fase {fase}. 
                Pembagian JP: {jp}. 
                Lengkapi dengan: Bahan Ajar, Asesmen Formatif (Rubrik), dan Sumatif (Soal & Kunci). 
                Acuan: Permendikdasmen 13/2025 dan buku dari https://buku.kemendikdasmen.go.id/katalog. 
                Format rapi, spasi rata, siap cetak."""
                st.session_state.admin_data['ma'] = panggil_ai(p)
        if 'ma' in st.session_state.admin_data:
            st.markdown(st.session_state.admin_data['ma'])
            
            # FITUR CETAK
            if st.button("📥 Download PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=10)
                txt = f"ADMINISTRASI GURU 2025\nSekolah: {sekolah}\nGuru: {guru}\n\n{st.session_state.admin_data['ma']}"
                pdf.multi_cell(0, 5, txt.encode('latin-1', 'replace').decode('latin-1'))
                pdf.output("Modul_Ajar.pdf")
                with open("Modul_Ajar.pdf", "rb") as f:
                    st.download_button("Klik untuk Simpan", f, "Modul_Ajar.pdf")
