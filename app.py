import streamlit as st
import time
import google.generativeai as genai
from datetime import datetime
from fpdf import FPDF
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. CONFIGURAÇÃO GERAL ---
st.set_page_config(
    page_title="Reclama.Ai",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CONFIGURAÇÕES TÉCNICAS ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    modelo = genai.GenerativeModel('gemini-1.5-flash')
    IA_DISPONIVEL = True
except:
    IA_DISPONIVEL = False

try:
    EMAIL_USER = st.secrets["EMAIL_USER"]
    EMAIL_PASS = st.secrets["EMAIL_PASSWORD"]
    EMAIL_DISPONIVEL = True
except:
    EMAIL_DISPONIVEL = False

# --- 3. FUNÇÕES AUXILIARES ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, 'Reclama.Ai', 0, 1, 'L')
        self.line(10, 20, 200, 20)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150)
        self.cell(0, 10, f'Gerado via Reclama.Ai', 0, 0, 'C')

def gerar_pdf_download(texto_final, nome_arquivo):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    texto_seguro = texto_final.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, texto_seguro)
    pdf_output = pdf.output(dest='S').encode('latin-1')
    b64 = base64.b64encode(pdf_output).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{nome_arquivo}.pdf" style="text-decoration:none;"><div style="background-color:#10B981; color:white; padding:15px; border-radius:8px; text-align:center; font-weight:bold; margin-top:15px; box-shadow: 0 4px 10px rgba(16,185,129,0.2);">📥 BAIXAR PDF</div></a>'

def enviar_email_ticket(nome, contato, problema):
    if not EMAIL_DISPONIVEL: return False
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER
    msg['Subject'] = f"SUPORTE: {nome}"
    msg.attach(MIMEText(f"Nome: {nome}\nContato: {contato}\n\n{problema}", 'plain'))
    try:
        server = smtplib.SMTP_SSL('smtp.hostinger.com', 465)
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except: return False

# --- 4. CSS INTELIGENTE (RESPONSIVO) ---
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap');
        
        /* GERAL */
        .stApp { background-color: #F8FAFC; font-family: 'Plus Jakarta Sans', sans-serif; }
        header, footer, #MainMenu {visibility: hidden;}
        
        /* CARD PRINCIPAL - A MÁGICA ACONTECE AQUI */
        .app-card {
            background-color: #FFFFFF;
            border-radius: 24px;
            box-shadow: 0 10px 30px -5px rgba(0,0,0,0.05);
            border: 1px solid #EEF2F6;
            margin: 0 auto; /* Centraliza */
        }

        /* CONFIGURAÇÃO PARA PC (TELA GRANDE) */
        @media (min-width: 768px) {
            .app-card {
                max-width: 800px;
                padding: 50px;
                margin-top: 40px;
            }
            div.block-container {
                padding-top: 2rem !important;
            }
        }

        /* CONFIGURAÇÃO PARA CELULAR (TELA PEQUENA) */
        @media (max-width: 767px) {
            .app-card {
                max-width: 100%;
                padding: 25px;
                margin-top: 10px;
                box-shadow: none; /* Remove sombra no mobile para ficar clean */
                border: none;
                background-color: transparent; /* Fundo transparente no mobile */
            }
            div.block-container {
                padding-top: 1rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
            /* Aumentar tamanho da fonte no celular */
            .logo-text { font-size: 28px !important; }
            .sub-text { font-size: 14px !important; }
        }

        /* HEADER */
        .logo-text { font-size: 36px; font-weight: 800; color: #0F172A; letter-spacing: -1px; text-align: center; }
        .logo-dot { color: #10B981; }
        .sub-text { text-align: center; color: #64748B; font-size: 16px; margin-bottom: 30px; }

        /* ÍCONES */
        .icon-box { display: flex; justify-content: center; margin-bottom: 15px; }
        .icon-img { width: 56px; height: 56px; }
        
        /* BOTÕES */
        div.stButton > button {
            width: 100%; height: 54px; border-radius: 12px; font-weight: 700; font-size: 16px; border: none;
        }
        button[kind="primary"] { background-color: #0F172A; color: white; } 
        button[kind="secondary"] { background-color: #FFFFFF; color: #475569; border: 1px solid #E2E8F0; }

        /* INPUTS */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; color: #0F172A;
        }
        
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# --- 5. NAVEGAÇÃO ---
if 'nav' not in st.session_state: st.session_state['nav'] = 'home'
if 'step' not in st.session_state: st.session_state['step'] = 1

def navegar(destino):
    st.session_state['nav'] = destino
    st.session_state['step'] = 1
    st.rerun()

# --- 6. ESTRUTURA (SEM COLUNAS LATERAIS QUE ESPREMEM O MOBILE) ---
# Removemos as colunas laterais. O CSS (.app-card) cuida da centralização agora.

st.markdown('<div class="app-card">', unsafe_allow_html=True)

# LOGO
st.markdown(f"""
    <div class="logo-text">Reclama<span class="logo-dot">.Ai</span></div>
    <div class="sub-text">Sua defesa automática e inteligente</div>
""", unsafe_allow_html=True)

# === TELA 1: HOME ===
if st.session_state['nav'] == 'home':
    
    # Linha 1: Consumidor
    c1, c2 = st.columns([1, 3])
    with c1:
        st.markdown('<div class="icon-box"><img src="https://cdn-icons-png.flaticon.com/512/3144/3144456.png" class="icon-img"></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("### Consumidor")
        st.markdown("Problemas com Bancos, Voos e Compras.")
        if st.button("Começar ➝", key="btn_c", type="primary"): navegar('consumidor')

    st.markdown("<hr style='margin: 20px 0; border:none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Linha 2: Trânsito
    c3, c4 = st.columns([1, 3])
    with c3:
        st.markdown('<div class="icon-box"><img src="https://cdn-icons-png.flaticon.com/512/2554/2554936.png" class="icon-img"></div>', unsafe_allow_html=True)
    with c4:
        st.markdown("### Trânsito")
        st.markdown("Recurso de Multas e CNH.")
        if st.button("Começar ➝", key="btn_t", type="primary"): navegar('transito')

    st.markdown("<hr style='margin: 20px 0; border:none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Linha 3: Suporte
    c5, c6 = st.columns([1, 3])
    with c5:
        st.markdown('<div class="icon-box"><img src="https://cdn-icons-png.flaticon.com/512/4233/4233830.png" class="icon-img"></div>', unsafe_allow_html=True)
    with c6:
        st.markdown("### Consultoria Pro")
        st.markdown("Fale com nossos especialistas.")
        if st.button("Falar Agora", key="btn_s", type="secondary"): navegar('suporte')

# === TELA WIZARD ===
elif st.session_state['nav'] in ['consumidor', 'transito']:
    label = "Consumidor" if st.session_state['nav'] == 'consumidor' else "Trânsito"
    
    st.markdown(f"<div style='color:#10B981; font-weight:700; font-size:12px; margin-bottom:5px; text-transform:uppercase; text-align:center;'>PASSO {st.session_state['step']} DE 3 • {label}</div>", unsafe_allow_html=True)
    st.progress(st.session_state['step']/3)
    st.write("")

    if st.session_state['step'] == 1:
        st.markdown("### Seus Dados")
        st.session_state['nome'] = st.text_input("Nome Completo", value=st.session_state.get('nome',''))
        st.session_state['doc'] = st.text_input("CPF ou CNH", value=st.session_state.get('doc',''))
        
        st.write("")
        cb1, cb2 = st.columns(2)
        with cb1: 
            if st.button("Cancelar", type="secondary"): navegar('home')
        with cb2: 
            if st.button("Continuar", type="primary"):
                if st.session_state['nome']:
                    st.session_state['step'] = 2
                    st.rerun()
                else: st.warning("Preencha seu nome.")

    elif st.session_state['step'] == 2:
        st.markdown("### Detalhes")
        if st.session_state['nav'] == 'consumidor':
            st.session_state['alvo'] = st.text_input("Empresa Reclamada", value=st.session_state.get('alvo',''))
            st.session_state['tipo'] = st.selectbox("Motivo", ["Cobrança Indevida", "Voo Atrasado", "Produto Defeituoso", "Outro"])
        else:
            st.session_state['alvo'] = st.selectbox("Órgão", ["Detran", "PRF", "Municipal"])
            st.session_state['tipo'] = st.selectbox("Infração", ["Velocidade", "Sinal Vermelho", "Lei Seca", "Estacionamento"])
            st.session_state['placa'] = st.text_input("Placa", value=st.session_state.get('placa',''))

        st.write("")
        cb1, cb2 = st.columns(2)
        with cb1: 
            if st.button("Voltar", type="secondary"): 
                st.session_state['step'] = 1
                st.rerun()
        with cb2: 
            if st.button("Continuar", type="primary"):
                if st.session_state['alvo']:
                    st.session_state['step'] = 3
                    st.rerun()
                else: st.warning("Preencha os dados.")

    elif st.session_state['step'] == 3:
        st.markdown("### Relato")
        st.info("Descreva o problema. A IA fará o resto.")
        st.session_state['relato'] = st.text_area("", height=150, placeholder="Digite aqui...")
        
        st.write("")
        if st.button("✨ GERAR DOCUMENTO", type="primary"):
            if not st.session_state['relato']:
                st.warning("Escreva o relato.")
            else:
                with st.spinner("IA Redigindo..."):
                    ctx = "CDC" if st.session_state['nav'] == 'consumidor' else "CTB"
                    p = f"Aja como advogado especialista em {ctx}. Redija documento formal. Cliente: {st.session_state['nome']}, Doc: {st.session_state['doc']}. Contra: {st.session_state['alvo']}. Caso: {st.session_state['tipo']}. Detalhes: {st.session_state['relato']}."
                    try:
                        txt = modelo.generate_content(p).text if IA_DISPONIVEL else "Erro IA"
                        st.success("Sucesso!")
                        st.markdown(gerar_pdf_download(txt, "ReclamaAi_Doc"), unsafe_allow_html=True)
                    except: st.error("Erro técnico.")
        
        st.write("")
        if st.button("Início", type="secondary"): navegar('home')

# === SUPORTE ===
elif st.session_state['nav'] == 'suporte':
    st.markdown("### Contato")
    c_nome = st.text_input("Nome")
    c_contato = st.text_input("WhatsApp / Email")
    c_msg = st.text_area("Mensagem", height=100)
    
    st.write("")
    if st.button("Enviar", type="primary"):
        if enviar_email_ticket(c_nome, c_contato, c_msg): st.success("Enviado!")
        else: st.error("Erro no envio.")
    if st.button("Voltar", type="secondary"): navegar('home')

st.markdown('</div>', unsafe_allow_html=True) 

st.markdown("""
<div style="text-align:center; color:#9CA3AF; font-size:11px; margin-top:20px;">
    Operado por CNPJ: 58.612.257/0001-84
</div>
""", unsafe_allow_html=True)