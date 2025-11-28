import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURAÇÃO (MODO WIDE MAS COM CONTROLE) ---
st.set_page_config(page_title="Reclama.Ai", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

# --- CONEXÕES ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    modelo = genai.GenerativeModel('gemini-1.5-flash')
    IA_DISPONIVEL = True
except: IA_DISPONIVEL = False

try:
    EMAIL_USER = st.secrets["EMAIL_USER"]
    EMAIL_PASS = st.secrets["EMAIL_PASSWORD"]
    EMAIL_DISPONIVEL = True
except: EMAIL_DISPONIVEL = False

# --- PDF E EMAIL ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Reclama.Ai', 0, 1, 'L')
        self.line(10, 20, 200, 20)
        self.ln(10)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Gerado via Reclama.Ai - CNPJ 58.612.257/0001-84', 0, 0, 'C')

def gerar_pdf_download(texto, nome):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 7, texto.encode('latin-1', 'replace').decode('latin-1'))
    b64 = base64.b64encode(pdf.output(dest='S').encode('latin-1')).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{nome}.pdf" style="text-decoration:none;"><div style="background-color:#10B981; color:white; padding:15px; border-radius:12px; text-align:center; font-weight:bold; margin-top:20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">📥 BAIXAR PDF AGORA</div></a>'

def enviar_ticket(nome, contato, problema):
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

# --- CSS (DESIGN RESPONSIVO REAL) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    .stApp { background-color: #F8FAFC; font-family: 'Plus Jakarta Sans', sans-serif; }
    header, footer, #MainMenu {visibility: hidden;}
    
    /* CARD PRINCIPAL */
    .main-card {
        background: white; padding: 30px; border-radius: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        max-width: 600px; margin: 0 auto; /* Centraliza e limita largura no PC */
    }
    
    /* HEADER */
    .brand-area { text-align: center; margin-bottom: 40px; margin-top: 20px; }
    .brand-text { font-size: 32px; font-weight: 800; color: #0F172A; letter-spacing: -1px; }
    .brand-dot { color: #10B981; }
    .brand-sub { color: #64748B; font-size: 15px; }

    /* BOTÕES GRANDES (MENU) */
    .menu-btn {
        display: block; width: 100%; background: white; border: 1px solid #E2E8F0;
        border-radius: 16px; padding: 20px; margin-bottom: 15px; text-align: left;
        transition: 0.2s; cursor: pointer; color: #0F172A; text-decoration: none;
    }
    .menu-btn:hover { border-color: #10B981; background: #F0FDF4; }
    .btn-icon { font-size: 24px; margin-bottom: 5px; display: block; }
    .btn-title { font-weight: 700; font-size: 18px; display: block; }
    .btn-desc { font-size: 13px; color: #64748B; font-weight: 400; }

    /* BOTÕES DE AÇÃO */
    div.stButton > button {
        width: 100%; height: 50px; border-radius: 12px; font-weight: 600; border: none;
        background-color: #0F172A; color: white;
    }
    div.stButton > button:hover { background-color: #10B981; }
    
    /* BOTÃO SECUNDÁRIO */
    button[kind="secondary"] { background-color: white; color: #64748B; border: 1px solid #E2E8F0; }

    /* TEXT INPUTS */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: white; border: 1px solid #E2E8F0; border-radius: 10px; color: #0F172A;
    }
</style>
""", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
if 'nav' not in st.session_state: st.session_state['nav'] = 'home'
if 'step' not in st.session_state: st.session_state['step'] = 1

def nav(destino):
    st.session_state['nav'] = destino
    st.session_state['step'] = 1
    st.rerun()

# --- LOGO (SEMPRE VISÍVEL) ---
st.markdown("""
<div class="brand-area">
    <div class="brand-text">Reclama<span class="brand-dot">.Ai</span></div>
    <div class="brand-sub">Sua defesa automática</div>
</div>
""", unsafe_allow_html=True)

# --- CONTAINER CENTRAL ---
col_esq, col_centro, col_dir = st.columns([1, 10, 1]) # Ocupa quase tudo no celular, centraliza no PC

with col_centro:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    # === HOME (MENU VERTICAL - MELHOR PARA CELULAR) ===
    if st.session_state['nav'] == 'home':
        st.write("### Selecione uma opção:")
        st.write("")
        
        # Botões manuais usando st.button com container para simular card
        c1 = st.container(border=True)
        c1.markdown("#### 🛒 Consumidor")
        c1.caption("Bancos, Voos, Compras e Serviços.")
        if c1.button("Começar Defesa", key="b1"): nav('consumidor')
        
        st.write("")
        
        c2 = st.container(border=True)
        c2.markdown("#### 🚦 Trânsito")
        c2.caption("Recurso de Multas e CNH.")
        if c2.button("Começar Recurso", key="b2"): nav('transito')
        
        st.write("")
        st.markdown("---")
        st.write("")
        
        if st.button("Falar com Especialistas", type="secondary"): nav('suporte')

    # === WIZARD (FORMULÁRIOS) ===
    elif st.session_state['nav'] in ['consumidor', 'transito']:
        label = "Consumidor" if st.session_state['nav'] == 'consumidor' else "Trânsito"
        
        # Header do Wizard
        st.caption(f"PASSO {st.session_state['step']} DE 3 • {label.upper()}")
        st.progress(st.session_state['step']/3)
        st.write("")

        # PASSO 1
        if st.session_state['step'] == 1:
            st.markdown("### Seus Dados")
            st.session_state['nome'] = st.text_input("Nome Completo", value=st.session_state.get('nome',''))
            st.session_state['doc'] = st.text_input("CPF ou CNH", value=st.session_state.get('doc',''))
            
            st.write("")
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1: 
                if st.button("Cancelar", type="secondary"): nav('home')
            with c_btn2: 
                if st.button("Continuar"):
                    if st.session_state['nome']:
                        st.session_state['step'] = 2
                        st.rerun()
                    else: st.warning("Preencha seu nome.")

        # PASSO 2
        elif st.session_state['step'] == 2:
            st.markdown("### Detalhes")
            if st.session_state['nav'] == 'consumidor':
                st.session_state['alvo'] = st.text_input("Empresa", value=st.session_state.get('alvo',''))
                st.session_state['tipo'] = st.selectbox("Motivo", ["Cobrança Indevida", "Voo Atrasado", "Produto Defeituoso", "Outro"])
            else:
                st.session_state['alvo'] = st.selectbox("Órgão", ["Detran", "PRF", "Municipal"])
                st.session_state['tipo'] = st.selectbox("Infração", ["Velocidade", "Sinal Vermelho", "Lei Seca", "Estacionamento"])
                st.session_state['placa'] = st.text_input("Placa", value=st.session_state.get('placa',''))

            st.write("")
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1: 
                if st.button("Voltar", type="secondary"): 
                    st.session_state['step'] = 1
                    st.rerun()
            with c_btn2: 
                if st.button("Continuar"):
                    if st.session_state['alvo']:
                        st.session_state['step'] = 3
                        st.rerun()
                    else: st.warning("Preencha os dados.")

        # PASSO 3
        elif st.session_state['step'] == 3:
            st.markdown("### O Relato")
            st.info("Descreva o problema. A IA fará o resto.")
            st.session_state['relato'] = st.text_area("", height=150, placeholder="Digite aqui...")
            
            st.write("")
            if st.button("✨ GERAR PDF"):
                if not st.session_state['relato']:
                    st.warning("Escreva o relato.")
                else:
                    with st.spinner("Gerando documento..."):
                        ctx = "CDC" if st.session_state['nav'] == 'consumidor' else "CTB"
                        p = f"Aja como advogado ({ctx}). Documento formal. Cliente: {st.session_state['nome']}, Doc: {st.session_state['doc']}. Contra: {st.session_state['alvo']}. Caso: {st.session_state['tipo']}. Detalhes: {st.session_state['relato']}."
                        try:
                            txt = modelo.generate_content(p).text if IA_DISPONIVEL else "Erro IA"
                            st.success("Sucesso!")
                            st.markdown(gerar_pdf_download(txt, "ReclamaAi_Doc"), unsafe_allow_html=True)
                        except: st.error("Erro técnico.")
            
            st.write("")
            if st.button("Início", type="secondary"): nav('home')

    # === SUPORTE ===
    elif st.session_state['nav'] == 'suporte':
        st.markdown("### Contato")
        c_nome = st.text_input("Nome")
        c_contato = st.text_input("WhatsApp / Email")
        c_msg = st.text_area("Mensagem", height=100)
        
        st.write("")
        if st.button("Enviar"):
            if enviar_email_ticket(c_nome, c_contato, c_msg): st.success("Enviado!")
            else: st.error("Erro no envio.")
        if st.button("Voltar", type="secondary"): nav('home')

    st.markdown('</div>', unsafe_allow_html=True)

# RODAPÉ
st.markdown("""
<div style="text-align:center; color:#9CA3AF; font-size:11px; margin-top:30px;">
    Operado por CNPJ: 58.612.257/0001-84<br>Não substitui advogado.
</div>
""", unsafe_allow_html=True)