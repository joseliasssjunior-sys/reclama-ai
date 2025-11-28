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
    page_title="Reclama.Ai | Defesa Automática",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CONFIGURAÇÕES TÉCNICAS ---
# Tenta carregar as chaves secretas. Se não tiver, o app roda em "modo visual" (sem IA/Email)
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

# --- 3. FUNÇÕES AUXILIARES (PDF e E-mail) ---
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
        self.cell(0, 10, f'Gerado via Reclama.Ai - Operado por CNPJ 58.612.257/0001-84', 0, 0, 'C')

def gerar_pdf_download(texto_final, nome_arquivo):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    # Tratamento simples para caracteres especiais no PDF
    texto_seguro = texto_final.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, texto_seguro)
    pdf_output = pdf.output(dest='S').encode('latin-1')
    b64 = base64.b64encode(pdf_output).decode()
    # Botão de Download estilizado
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{nome_arquivo}.pdf" style="text-decoration:none;"><div style="background-color:#10B981; color:white; padding:15px; border-radius:8px; text-align:center; font-weight:bold; margin-top:15px; box-shadow: 0 4px 10px rgba(16,185,129,0.2);">📥 BAIXAR DOCUMENTO (PDF)</div></a>'

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

# --- 4. CSS PREMIUM (ESTILO MANUS/LOVABLE) ---
def inject_custom_css():
    st.markdown("""
    <style>
        /* Importa a fonte Plus Jakarta Sans (Moderna e Tech) */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700&display=swap');
        
        /* FUNDO GERAL (Cinza Suave) */
        .stApp { background-color: #F3F4F6; font-family: 'Plus Jakarta Sans', sans-serif; }
        #MainMenu, footer, header {visibility: hidden;}
        
        /* O "CARD" BRANCO CENTRALIZADO */
        .app-card {
            background-color: #FFFFFF;
            padding: 50px;
            border-radius: 24px;
            box-shadow: 0 20px 40px -10px rgba(0,0,0,0.08); /* Sombra suave */
            border: 1px solid #FFFFFF;
            max-width: 900px;
            margin: 40px auto; /* Centraliza horizontalmente */
        }

        /* HEADER E LOGO */
        .logo-text { font-size: 32px; font-weight: 800; color: #111827; letter-spacing: -1px; text-align: center; margin-bottom: 5px; }
        .logo-dot { color: #10B981; }
        .sub-text { text-align: center; color: #6B7280; font-size: 16px; margin-bottom: 40px; }

        /* ÍCONES (Imagens PNG) */
        .icon-box {
            display: flex; justify-content: center; margin-bottom: 15px;
        }
        .icon-img {
            width: 64px; height: 64px; opacity: 0.9; transition: 0.3s;
        }
        
        /* TEXTOS */
        h3 { font-size: 20px !important; font-weight: 700 !important; color: #111827 !important; margin-top: 0 !important; }
        p { color: #6B7280 !important; font-size: 15px !important; }

        /* BOTÕES PERSONALIZADOS */
        div.stButton > button {
            width: 100%; height: 50px; border-radius: 10px; font-weight: 600; border: none; transition: 0.2s;
        }
        
        /* Botão Primário (Escuro) */
        button[kind="primary"] { background-color: #111827; color: white; } 
        button[kind="primary"]:hover { background-color: #10B981; transform: translateY(-2px); }
        
        /* Botão Secundário (Claro) */
        button[kind="secondary"] { background-color: white; color: #374151; border: 1px solid #E5E7EB; }
        button[kind="secondary"]:hover { border-color: #111827; color: #111827; }

        /* INPUTS LIMPOS */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 10px; padding: 10px; color: #111827;
        }
        .stTextInput input:focus { border-color: #10B981; background-color: white; }

        /* Ajuste de espaçamento do Streamlit */
        div[data-testid="stVerticalBlock"] { gap: 1rem; }
        
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

# --- 6. ESTRUTURA VISUAL (CENTRALIZADA) ---
# Usamos colunas para criar margens laterais e deixar o conteúdo no meio
c_esq, c_meio, c_dir = st.columns([1, 2, 1])

with c_meio:
    # TUDO ACONTECE DENTRO DESTE CARD BRANCO
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    
    # LOGO
    st.markdown(f"""
        <div class="logo-text">Reclama<span class="logo-dot">.Ai</span></div>
        <div class="sub-text">Inteligência Jurídica Automática</div>
    """, unsafe_allow_html=True)

    # === TELA 1: HOME (MENU COM ÍCONES REAIS) ===
    if st.session_state['nav'] == 'home':
        
        # LINHA 1: CONSUMIDOR
        c1, c2 = st.columns([1, 3])
        with c1:
            # Ícone Sacola de Compras
            st.markdown('<div class="icon-box"><img src="https://cdn-icons-png.flaticon.com/512/3144/3144456.png" class="icon-img"></div>', unsafe_allow_html=True)
        with c2:
            st.markdown("### Consumidor")
            st.markdown("Problemas com Bancos, Voos, Compras e Serviços.")
            if st.button("Criar Reclamação ➝", key="btn_c", type="primary"): navegar('consumidor')

        st.markdown("<hr style='margin: 30px 0; border:none; border-top: 1px solid #F3F4F6;'>", unsafe_allow_html=True)

        # LINHA 2: TRÂNSITO
        c3, c4 = st.columns([1, 3])
        with c3:
            # Ícone Carro/Escudo
            st.markdown('<div class="icon-box"><img src="https://cdn-icons-png.flaticon.com/512/2554/2554936.png" class="icon-img"></div>', unsafe_allow_html=True)
        with c4:
            st.markdown("### Trânsito")
            st.markdown("Recurso de Multas, CNH e Lei Seca.")
            if st.button("Criar Recurso ➝", key="btn_t", type="primary"): navegar('transito')

        st.markdown("<hr style='margin: 30px 0; border:none; border-top: 1px solid #F3F4F6;'>", unsafe_allow_html=True)

        # LINHA 3: SUPORTE
        c5, c6 = st.columns([1, 3])
        with c5:
            # Ícone Atendente
            st.markdown('<div class="icon-box"><img src="https://cdn-icons-png.flaticon.com/512/4233/4233830.png" class="icon-img"></div>', unsafe_allow_html=True)
        with c6:
            st.markdown("### Consultoria Pro")
            st.markdown("Casos complexos? Fale com especialistas.")
            if st.button("Entrar em Contato", key="btn_s", type="secondary"): navegar('suporte')

    # === TELA WIZARD (FORMULÁRIOS PASSO A PASSO) ===
    elif st.session_state['nav'] in ['consumidor', 'transito']:
        label = "Defesa do Consumidor" if st.session_state['nav'] == 'consumidor' else "Defesa de Trânsito"
        
        # Barra de Progresso e Título
        st.markdown(f"<div style='color:#10B981; font-weight:700; font-size:12px; margin-bottom:5px; text-transform:uppercase;'>{label} • Passo {st.session_state['step']} de 3</div>", unsafe_allow_html=True)
        st.progress(st.session_state['step']/3)
        st.write("")

        # PASSO 1: DADOS PESSOAIS
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

        # PASSO 2: DETALHES
        elif st.session_state['step'] == 2:
            st.markdown("### Detalhes do Caso")
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

        # PASSO 3: RELATO E GERAÇÃO
        elif st.session_state['step'] == 3:
            st.markdown("### O Relato")
            st.info("Descreva o que houve. A IA escreverá o juridiquês.")
            st.session_state['relato'] = st.text_area("", height=150, placeholder="Ex: Recebi uma cobrança no dia...")
            
            st.write("")
            if st.button("✨ GERAR DOCUMENTO AGORA", type="primary"):
                if not st.session_state['relato']:
                    st.warning("Escreva o relato.")
                else:
                    with st.spinner("IA Redigindo..."):
                        ctx = "CDC" if st.session_state['nav'] == 'consumidor' else "CTB"
                        p = f"Aja como advogado especialista em {ctx}. Redija documento formal. Cliente: {st.session_state['nome']}. Contra: {st.session_state['alvo']}. Caso: {st.session_state['tipo']}. Detalhes: {st.session_state['relato']}."
                        try:
                            if IA_DISPONIVEL:
                                txt = modelo.generate_content(p).text
                                st.success("Sucesso!")
                                st.markdown(gerar_pdf_download(txt, "ReclamaAi_Doc"), unsafe_allow_html=True)
                            else:
                                st.error("Erro: Configure a chave da IA no secrets.toml")
                        except Exception as e:
                            st.error(f"Erro técnico: {e}")
            
            st.write("")
            if st.button("Início", type="secondary"): navegar('home')

    # === TELA SUPORTE ===
    elif st.session_state['nav'] == 'suporte':
        st.markdown("### Fale com Especialistas")
        c_nome = st.text_input("Nome")
        c_contato = st.text_input("WhatsApp / Email")
        c_msg = st.text_area("Mensagem", height=100)
        
        st.write("")
        if st.button("Enviar", type="primary"):
            if enviar_email_ticket(c_nome, c_contato, c_msg): st.success("Enviado!")
            else: st.error("Erro ao enviar. Verifique configurações de e-mail.")
        if st.button("Voltar", type="secondary"): navegar('home')

    # FIM DO CARD BRANCO
    st.markdown('</div>', unsafe_allow_html=True) 

# RODAPÉ FORA DO CARD
st.markdown("""
<div style="text-align:center; color:#9CA3AF; font-size:12px; margin-top:20px;">
    Operado por CNPJ: 58.612.257/0001-84<br>CNAE 82.19-9-99
</div>
""", unsafe_allow_html=True)