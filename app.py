import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import os

# --- KONFIGURASI AMAN ---
# Mengambil API Key dari Secrets
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = None

if API_KEY:
    # Perbaikan khusus untuk kunci AQ: 
    # Menggunakan konfigurasi dasar tanpa tambahan parameter transport jika tidak perlu
    genai.configure(api_key=API_KEY)
    
    # Kita gunakan gemini-1.5-flash karena lebih ringan dan seringkali lebih lancar 
    # untuk autentikasi kunci baru, tapi jika ingin Pro bisa diganti 'gemini-1.5-pro'
    model = genai.GenerativeModel('gemini-1.5-flash') 
else:
    st.error("⚠️ API Key belum dimasukkan di Secrets Streamlit!")

# --- LOGIKA JP ---
def get_subject_logic(mapel):
    special = ["PABP", "PJOK", "Bahasa Inggris", "Bahasa Jawa"]
    if mapel in special:
        return "Disusun untuk 1 kali pertemuan tuntas (Blok JP)."
    return "Materi dibagi rapi per 2 JP per pertemuan (Deep Learning)."

# --- UI APLIKASI ---
st.set_page_config(page_title="Gen-Guru AI 2025", layout="wide")
st.title("🚀 Auto-Admin Guru 2025")
st.caption("Khusus Permendikdasmen No. 13 Tahun 2025 | Kompatibel Kunci AQ")

with st.sidebar:
    st.header("📋 Identitas")
    sekolah = st.text_input("Nama Sekolah", "SD Negeri ...")
    guru = st.text_input("Nama Guru", "Nama Anda, S.Pd.")
    nip = st.text_input("NIP", "19xxxx")
    kepsek = st.text_input("Kepala Sekolah", "Nama Kepsek, M.Pd.")
    st.divider()
    mapel = st.selectbox("Mata Pelajaran", ["Bahasa Indonesia", "Matematika", "IPAS", "PABP", "PJOK", "Bahasa Inggris", "Bahasa Jawa"])
    kelas = st.text_input("Kelas", "4")
    fase = st.text_input("Fase", "B")

if 'data' not in st.session_state:
    st.session_state.data = {}

def generate_konten(prompt):
    try:
        # Menambahkan parameter tambahan agar lebih stabil
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error saat Generate: {str(e)}"

# --- TAB PROSES ---
t1, t2, t3, t4 = st.tabs(["PROTA", "PROMES", "ATP", "MODUL AJAR"])

with t1:
    if st.button("Generate PROTA"):
        with st.spinner("Sedang memproses..."):
            p = f"Buatlah Tabel Program Tahunan (PROTA) {mapel} Kelas {kelas} sesuai Permendikdasmen 13/2025. Referensi: https://buku.kemendikdasmen.go.id/katalog."
            st.session_state.data['prota'] = generate_konten(p)
    if 'prota' in st.session_state.data:
        st.markdown(st.session_state.data['prota'])

with t2:
    if 'prota' in st.session_state.data:
        if st.button("Generate PROMES"):
            with st.spinner("Membuat jadwal semester..."):
                p = f"Berdasarkan data Prota ini: {st.session_state.data['prota']}, buatkan Tabel PROMES ganjil dan genap."
                st.session_state.data['promes'] = generate_konten(p)
        if 'promes' in st.session_state.data:
            st.markdown(st.session_state.data['promes'])
    else: st.warning("Buat PROTA dulu.")

with t3:
    if 'promes' in st.session_state.data:
        if st.button("Generate ATP"):
            with st.spinner("Menyusun ATP..."):
                p = f"Buatlah Alur Tujuan Pembelajaran (ATP) untuk {mapel} Kelas {kelas} dengan CP terbaru."
                st.session_state.data['atp'] = generate_konten(p)
        if 'atp' in st.session_state.data:
            st.markdown(st.session_state.data['atp'])
    else: st.warning("Buat PROMES dulu.")

with t4:
    if 'atp' in st.session_state.data:
        st.info(f"Aturan JP: {get_subject_logic(mapel)}")
        if st.button("Generate MODUL AJAR"):
            with st.spinner("Menyusun Modul Ajar Detail..."):
                logic = get_subject_logic(mapel)
                p = f"Buat Modul Ajar {mapel} Kelas {kelas}. Aturan JP: {logic}. Lengkapi dengan Bahan Ajar, Asesmen Formatif & Sumatif sesuai Permendikdasmen 13/2025."
                st.session_state.data['ma'] = generate_konten(p)
        if 'ma' in st.session_state.data:
            st.markdown(st.session_state.data['ma'])
            
            # FITUR PDF
            if st.button("📥 Download PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=10)
                isi = f"ADMINISTRASI GURU\nSekolah: {sekolah}\nGuru: {guru}\n\n{st.session_state.data['ma']}"
                pdf.multi_cell(0, 5, isi.encode('latin-1', 'replace').decode('latin-1'))
                pdf.output("Modul_Ajar.pdf")
                with open("Modul_Ajar.pdf", "rb") as f:
                    st.download_button("Klik untuk Simpan", f, "Modul_Ajar.pdf")
    else: st.warning("Buat ATP dulu.")
