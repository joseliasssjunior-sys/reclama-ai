import streamlit as st
import time
import google.generativeai as genai
from datetime import datetime
from fpdf import FPDF
import base64

# --- 1. CONFIGURAÇÃO GERAL ---
st.set_page_config(
    page_title="Reclama.Ai | Sua defesa automática",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CONFIGURAÇÃO IA ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    modelo = genai.GenerativeModel('gemini-1.5-flash')
    IA_DISPONIVEL = True
except:
    IA_DISPONIVEL = False

# --- 3. SISTEMA DE PDF (FPDF) ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 100, 0) # Verde Escuro
        self.cell(0, 10, 'Reclama.Ai', 0, 1, 'L')
        self.set_font('Arial', '', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Documento gerado por Inteligência Artificial', 0, 1, 'L')
        self.ln(10)
        self.line(10, 25, 200, 25) # Linha horizontal

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Gerado em {datetime.now().strftime("%d/%m/%Y")} via Reclama.Ai', 0, 0, 'C')

def gerar_pdf_download(texto_final, nome_arquivo):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    # Tratamento básico de caracteres para PDF
    texto_seguro = texto_final.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, texto_seguro)
    
    # Gerar botão de download
    pdf_output = pdf.output(dest='S').encode('latin-1')
    b64 = base64.b64encode(pdf_output).decode()
    href = f'''
    <a href="data:application/octet-stream;base64,{b64}" download="{nome_arquivo}.pdf" style="text-decoration:none;">
        <div style="background-color:#10B981; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; font-size:18px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            ⬇️ BAIXAR PDF PRONTO
        </div>
    </a>
    '''
    return href

# --- 4. DESIGN (CSS RECLAMA.AI) ---
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;600&display=swap');
        
        :root {
            --brand-dark: #0F172A;
            --brand-green: #10B981; /* Verde Tech */
            --bg-gray: #F8FAFC;
        }

        .stApp { background-color: var(--bg-gray); font-family: 'Inter', sans-serif; }
        #MainMenu, footer, header {visibility: hidden;}
        
        /* HEADER */
        .header-container {
            display: flex; justify-content: space-between; align-items: center;
            padding: 20px 0; margin-bottom: 40px; border-bottom: 1px solid #E2E8F0;
        }
        .logo-text {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 28px; font-weight: 700; color: var(--brand-dark); letter-spacing: -1px;
        }
        .logo-ai { color: var(--brand-green); }
        .tagline { font-size: 14px; color: #64748B; font-weight: 500; }

        /* CARDS DE SELEÇÃO */
        .choice-card {
            background: white; border: 1px solid #E2E8F0; border-radius: 16px;
            padding: 30px; text-align: center; cursor: pointer; transition: all 0.3s ease;
            height: 100%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
        }
        .choice-card:hover {
            transform: translateY(-5px); border-color: var(--brand-green);
            box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.1);
        }
        .emoji-icon { font-size: 48px; margin-bottom: 15px; }
        .card-h { font-weight: 700; font-size: 20px; color: var(--brand-dark); margin-bottom: 8px; }
        .card-p { color: #64748B; font-size: 14px; line-height: 1.5; }

        /* FORMULÁRIO */
        .form-box {
            background: white; padding: 40px; border-radius: 20px;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); border: 1px solid #E2E8F0;
        }
        .section-title {
            font-family: 'Space Grotesk', sans-serif; font-size: 18px; font-weight: 700;
            color: var(--brand-dark); margin-bottom: 20px; margin-top: 10px;
            border-left: 4px solid var(--brand-green); padding-left: 10px;
        }

        /* BOTÃO PRINCIPAL */
        div.stButton > button {
            background-color: var(--brand-dark); color: white; border-radius: 8px;
            height: 50px; font-weight: 600; border: none; transition: 0.3s;
        }
        div.stButton > button:hover {
            background-color: var(--brand-green); color: white;
        }
        
        /* BOTÃO SECUNDÁRIO (VOLTAR) */
        button[kind="secondary"] {
            background-color: transparent; color: #64748B; border: 1px solid #CBD5E1;
        }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# --- 5. LÓGICA DE NAVEGAÇÃO ---
if 'nav' not in st.session_state:
    st.session_state['nav'] = 'home'

def navegar(destino):
    st.session_state['nav'] = destino
    st.rerun()

# --- HEADER (IGUAL EM TODAS AS PÁGINAS) ---
c_h1, c_h2 = st.columns([1,1])
with c_h1:
    st.markdown("""
    <div class="header-container">
        <div>
            <span class="logo-text">Reclama<span class="logo-ai">.Ai</span></span>
            <div class="tagline">Inteligência Jurídica ao seu alcance</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with c_h2:
    if st.session_state['nav'] != 'home':
        # Botão voltar alinhado à direita
        st.write("")
        col_v1, col_v2 = st.columns([4,1])
        with col_v2:
            if st.button("⬅ Voltar"): navegar('home')

# --- CONTEÚDO ---

# === TELA 1: HOME ===
if st.session_state['nav'] == 'home':
    st.markdown("<h1 style='text-align:center; font-family:Space Grotesk; font-size:42px; margin-bottom:10px;'>O que vamos resolver hoje?</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#64748B; margin-bottom:50px;'>Selecione a categoria para nossa IA preparar sua defesa.</p>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div class="choice-card">
            <div class="emoji-icon">🛒</div>
            <div class="card-h">Consumidor</div>
            <div class="card-p">Voos, compras online, bancos, planos de saúde e serviços.</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("Abrir Reclamação"): navegar('consumidor')

    with c2:
        st.markdown("""
        <div class="choice-card">
            <div class="emoji-icon">🚦</div>
            <div class="card-h">Multas de Trânsito</div>
            <div class="card-p">Recursos para Lei Seca, velocidade, sinal vermelho e estacionamento.</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("Gerar Recurso"): navegar('transito')

    with c3:
        st.markdown("""
        <div class="choice-card">
            <div class="emoji-icon">⚖️</div>
            <div class="card-h">Consultoria Pro</div>
            <div class="card-p">Casos complexos que precisam de análise humana detalhada.</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        # Link para seu WhatsApp
        st.link_button("Falar com Dr. Joselias", "https://wa.me/5598991113034")

# === TELA 2: CONSUMIDOR ===
elif st.session_state['nav'] == 'consumidor':
    st.markdown("<h2 style='text-align:center;'>🛒 Defesa do Consumidor</h2>", unsafe_allow_html=True)
    st.write("")
    
    with st.container():
        st.markdown('<div class="form-box">', unsafe_allow_html=True)
        
        c_a, c_b = st.columns(2)
        with c_a:
            nome = st.text_input("Seu Nome")
            cpf = st.text_input("CPF")
        with c_b:
            empresa = st.text_input("Empresa Reclamada")
            cnpj = st.text_input("CNPJ (Opcional)")
            
        st.markdown('<div class="section-title">O Problema</div>', unsafe_allow_html=True)
        tipo = st.selectbox("Categoria", ["Voo Atrasado/Cancelado", "Cobrança Indevida", "Produto com Defeito", "Não Entrega", "Plano de Saúde", "Outros"])
        
        relato = st.text_area("Descreva o que aconteceu (detalhes, datas, valores)", height=150)
        pedido = st.text_input("O que você quer?", placeholder="Ex: Devolução do valor em dobro e indenização")
        
        st.write("")
        if st.button("⚡ GERAR MINUTA PDF", type="primary"):
            if not nome or not empresa or not relato:
                st.warning("Preencha Nome, Empresa e Relato.")
            else:
                with st.spinner("Reclama.Ai analisando jurisprudência..."):
                    prompt = f"""
                    Aja como advogado especialista em CDC. Crie uma NOTIFICAÇÃO EXTRAJUDICIAL.
                    Cliente: {nome}, CPF {cpf}. Contra: {empresa}.
                    Caso ({tipo}): {relato}. Pedido: {pedido}.
                    Fundamente com artigos do CDC e tom firme.
                    """
                    try:
                        texto = modelo.generate_content(prompt).text if IA_DISPONIVEL else "Texto Simulado (Configure a API Key)."
                        st.success("Documento Pronto!")
                        st.markdown(gerar_pdf_download(texto, "Reclamacao_Consumidor"), unsafe_allow_html=True)
                    except: st.error("Erro ao conectar com a IA.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# === TELA 3: TRÂNSITO ===
elif st.session_state['nav'] == 'transito':
    st.markdown("<h2 style='text-align:center;'>🚗 Recurso de Multas</h2>", unsafe_allow_html=True)
    st.write("")

    with st.container():
        st.markdown('<div class="form-box">', unsafe_allow_html=True)
        
        c_t1, c_t2 = st.columns(2)
        with c_t1:
            condutor = st.text_input("Nome do Condutor")
            cnh = st.text_input("CNH")
            placa = st.text_input("Placa do Veículo")
        with c_t2:
            modelo_veiculo = st.text_input("Modelo do Veículo")
            renavam = st.text_input("Renavam")
            
        st.markdown('<div class="section-title">A Infração</div>', unsafe_allow_html=True)
        orgao = st.selectbox("Órgão", ["DETRAN", "PRF", "DNIT", "Municipal"])
        infracao = st.selectbox("Tipo", ["Velocidade", "Sinal Vermelho", "Estacionamento", "Lei Seca", "Capacete/Cinto", "Outros"])
        auto = st.text_input("Número do Auto de Infração")
        
        defesa = st.text_area("Seus Argumentos (Por que anular?)", height=100, placeholder="Ex: A placa estava encoberta; Não fui notificado no prazo...")
        
        st.write("")
        if st.button("⚡ GERAR RECURSO PDF", type="primary"):
            if not condutor or not placa:
                st.warning("Preencha dados do condutor e veículo.")
            else:
                with st.spinner("Reclama.Ai consultando o CTB..."):
                    prompt = f"""
                    Aja como especialista em Trânsito. Redija uma DEFESA PRÉVIA para o {orgao}.
                    Condutor: {condutor}, CNH {cnh}. Veículo: {modelo_veiculo}, Placa {placa}.
                    Multa: {infracao}. Auto: {auto}.
                    Defesa: {defesa}.
                    Cite artigos técnicos do CTB e Resoluções do CONTRAN para pedir anulação.
                    """
                    try:
                        texto = modelo.generate_content(prompt).text if IA_DISPONIVEL else "Texto Simulado."
                        st.success("Recurso Pronto!")
                        st.markdown(gerar_pdf_download(texto, "Recurso_Multa"), unsafe_allow_html=True)
                    except: st.error("Erro na IA.")

        st.markdown('</div>', unsafe_allow_html=True)

# --- RODAPÉ BLINDADO ---
st.markdown("""
<div style="text-align:center; margin-top:50px; color:#94A3B8; font-size:12px; line-height: 1.6; border-top:1px solid #E2E8F0; padding-top:20px;">
    <b>Reclama.Ai</b> © 2025 - Todos os direitos reservados.<br>
    Operado por CNPJ: 58.612.257/0001-84 | São Luís - MA<br>
    <br>
    <i>Isenção de Responsabilidade: Esta plataforma é uma ferramenta tecnológica para automação de documentos (CNAE 82.19-9-99).<br>
    Não prestamos consultoria jurídica privativa de advocacia. Para casos complexos, consulte um advogado.</i>
</div>
""", unsafe_allow_html=True)