import streamlit as st
import os
import urllib.request
import pandas as pd
import base64
from datetime import datetime
from fpdf import FPDF
import psycopg2
import warnings

# Tira os avisos chatos do Pandas
warnings.filterwarnings('ignore', message=".*pandas only supports SQLAlchemy.*")
_ = pd.set_option('display.max_colwidth', None)

# ==========================================
# ⚠️ COLE AQUI O LINK DO SEU SUPABASE ENTRE AS ASPAS:
# ==========================================
DB_URL = "postgresql://postgres.vrsbibaacisypceslzam:Renegados2026@aws-0-us-east-2.pooler.supabase.com:6543/postgres"

def get_conexao():
    return psycopg2.connect(DB_URL)

# ==========================================
# CONFIGURAÇÃO DA PÁGINA E ESTILO
# ==========================================
st.set_page_config(
    page_title="Core Renegados - Sistema Web",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
.main { background-color: #0d1117; }
h1, h2, h3 { color: #d4af37 !important; }
.tactics-box { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 15px; }
.tatica-header { background-color: #0b3d60; color: #ffffff; padding: 10px 16px; font-weight: 800; border-radius: 5px; font-size: 15px; margin-top: 20px; margin-bottom: 10px; letter-spacing: 1px; text-transform: uppercase; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
div[data-baseweb="select"] { margin-bottom: 0px; }
div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] { margin-bottom: 2px; }
div[data-testid="stMultiSelect"] { margin-bottom: 0px; }
.stButton button { min-height: 38px; }
hr { margin-top: 5px !important; margin-bottom: 5px !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CONSTANTES E ÍCONES
# ==========================================
CLASSES_WOW = {
    "Guerreiro": {"cor": "#C69B6D", "url": "https://wow.zamimg.com/images/wow/icons/medium/classicon_warrior.jpg"},
    "Paladino": {"cor": "#F48CBA", "url": "https://wow.zamimg.com/images/wow/icons/medium/classicon_paladin.jpg"},
    "Caçador": {"cor": "#ABD473", "url": "https://wow.zamimg.com/images/wow/icons/medium/classicon_hunter.jpg"},
    "Ladino": {"cor": "#FFF468", "url": "https://wow.zamimg.com/images/wow/icons/medium/classicon_rogue.jpg"},
    "Sacerdote": {"cor": "#FFFFFF", "url": "https://wow.zamimg.com/images/wow/icons/medium/classicon_priest.jpg"},
    "Mago": {"cor": "#3FC7EB", "url": "https://wow.zamimg.com/images/wow/icons/medium/classicon_mage.jpg"},
    "Bruxo": {"cor": "#8787ED", "url": "https://wow.zamimg.com/images/wow/icons/medium/classicon_warlock.jpg"},
    "Xamã": {"cor": "#0070DE", "url": "https://wow.zamimg.com/images/wow/icons/medium/classicon_shaman.jpg"},
    "Druida": {"cor": "#FF7C0A", "url": "https://wow.zamimg.com/images/wow/icons/medium/classicon_druid.jpg"}
}

ICONES_TATICAS = {
    "sombra": "https://wow.zamimg.com/images/wow/icons/medium/spell_shadow_curseofachilles.jpg",
    "vigor": "https://wow.zamimg.com/images/wow/icons/medium/spell_holy_wordfortitude.jpg",
    "esp": "https://wow.zamimg.com/images/wow/icons/medium/spell_holy_divinespirit.jpg",
    "mage_icon": "https://wow.zamimg.com/images/wow/icons/medium/spell_holy_magicalvision.jpg",
    "curse_pink": "https://wow.wowhead.com/images/wow/icons/medium/spell_shadow_unholyicons.jpg",
    "raio": "https://wow.zamimg.com/images/wow/icons/medium/spell_nature_lightning.jpg",
    "totem_azul": "https://wow.zamimg.com/images/wow/icons/medium/spell_nature_manaregentotem.jpg",
    "kings": "https://wow.zamimg.com/images/wow/icons/medium/spell_magic_greaterblessingofkings.jpg",
    "wisdom": "https://wow.zamimg.com/images/wow/icons/medium/spell_holy_prayerofhealing.jpg",
    "might": "https://wow.zamimg.com/images/wow/icons/medium/spell_holy_greaterblessingofmight.jpg",
    "salv": "https://wow.zamimg.com/images/wow/icons/medium/spell_holy_greaterblessingofsalvation.jpg",
    "orb_roxo": "https://wow.zamimg.com/images/wow/icons/medium/spell_shadow_curseofsargeras.jpg",
    "caveira": "https://wow.zamimg.com/images/wow/icons/medium/ui_raidtargetingicon_8.jpg",
    "xis": "https://wow.zamimg.com/images/wow/icons/medium/ui_raidtargetingicon_7.jpg",
    "quadrado": "https://wow.zamimg.com/images/wow/icons/medium/ui_raidtargetingicon_6.jpg",
    "triangulo": "https://wow.zamimg.com/images/wow/icons/medium/ui_raidtargetingicon_4.jpg",
    "lua": "https://wow.zamimg.com/images/wow/icons/medium/ui_raidtargetingicon_5.jpg",
    "diamante": "https://wow.zamimg.com/images/wow/icons/medium/ui_raidtargetingicon_3.jpg",
    "md": "https://wow.zamimg.com/images/wow/icons/medium/ability_hunter_misdirection.jpg",
    "sheep": "https://wow.zamimg.com/images/wow/icons/medium/spell_nature_polymorph.jpg",
    "inner_fire": "https://wow.zamimg.com/images/wow/icons/medium/spell_holy_innerfire.jpg",
    "shadow_prot": "", "light": "", "sanc": "", "trap": "", "blind": "", "banish": "", "shackle": ""
}

OPCOES_ICONES_BUFFS = {
    "Nenhum": "", "Vigor": "vigor", "Espírito": "esp", "Fogo Interior": "inner_fire",
    "Proteção Sombras": "shadow_prot", "Mago (Int)": "mage_icon", "Bruxo (Curse)": "curse_pink", 
    "Bruxo (Orbe)": "orb_roxo", "Bruxo (Banir)": "banish", "Xamã (Raio)": "raio", 
    "Pala (Reis)": "kings", "Pala (Sabedoria)": "wisdom", "Pala (Poder)": "might", 
    "Pala (Salvação)": "salv", "Pala (Luz)": "light", "Pala (Santuário)": "sanc",
    "Caçador (MD)": "md", "Caçador (Armadilha)": "trap", "Mago (Sheep)": "sheep",
    "Ladino (Blind)": "blind", "Sacerdote (Shackle)": "shackle"
}

OPCOES_ICONES_TARGET_MARKS = {
    "Nenhum": "", "Caveira": "caveira", "Xis": "xis", "Quadrado": "quadrado", "Triângulo": "triangulo", "Lua": "lua", "Diamante": "diamante"
}

OPCOES_ICONES_COMBINED = {**OPCOES_ICONES_BUFFS, **OPCOES_ICONES_TARGET_MARKS}
OPCOES_GRUPOS = ["", "1", "2", "3", "4", "5", "1-2", "3-4", "4-5", "1-2-3", "1 a 5", "MAIN TANK", "OFF TANK", "TRASH + BOSS"]
QTD_BOSSES = {"Hyjal": 5, "Black Temple": 9, "SCC + TK + GRULL": 12, "SUENWEL": 6}
LISTA_RAIDES = list(QTD_BOSSES.keys())
LISTA_ENCANTAMENTOS = ["🛡 Ombros", "🧥 Capa", "👕 Peito", "💪 Braçadeiras", "🧤 Luvas", "👖 Calças", "👢 Botas", "⚔️ Arma principal", "🗡 Arma secundária", "🛡 Escudo", "🏹 Longo alcance"]

PASTA_CLASSES = "icones_classes"
PASTA_TATICAS = "icones_taticas"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_CLASSES = os.path.join(BASE_DIR, PASTA_CLASSES)
CAMINHO_TATICAS = os.path.join(BASE_DIR, PASTA_TATICAS)

os.makedirs(CAMINHO_CLASSES, exist_ok=True)
os.makedirs(CAMINHO_TATICAS, exist_ok=True)
TRANSPARENT_B64 = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"

# ==========================================
# FUNÇÕES DE SUPORTE E ÍCONES 
# ==========================================
def obter_url_icone(chave):
    if not chave: return ""
    if chave in CLASSES_WOW: return CLASSES_WOW[chave]["url"]
    if chave in ICONES_TATICAS: return ICONES_TATICAS[chave]
    return ""

def garantir_icone_local(chave, tipo="tatica"):
    if not chave: return None
    pasta_alvo = CAMINHO_CLASSES if tipo == "classe" else CAMINHO_TATICAS
    extensoes = [".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"]
    for ext in extensoes:
        caminho_local = os.path.join(pasta_alvo, f"{chave}{ext}")
        if os.path.exists(caminho_local):
            return caminho_local
    try:
        arquivos_na_pasta = os.listdir(pasta_alvo)
        chave_lower = chave.lower()
        for arq in arquivos_na_pasta:
            if arq.rsplit('.', 1)[0].lower() == chave_lower:
                return os.path.join(pasta_alvo, arq)
    except Exception:
        pass
    return None

def obter_icone_base64(chave, tipo="tatica"):
    caminho = garantir_icone_local(chave, tipo)
    if caminho:
        try:
            with open(caminho, "rb") as arquivo:
                encoded = base64.b64encode(arquivo.read()).decode("utf-8")
            mime_type = "image/png" if caminho.lower().endswith(".png") else "image/jpeg"
            return f"data:{mime_type};base64,{encoded}"
        except Exception: pass
    url = obter_url_icone(chave)
    if url: return url
    return TRANSPARENT_B64

def html_classe(nome_classe, tamanho=24):
    dados = CLASSES_WOW.get(nome_classe)
    if not dados: return nome_classe
    cor = dados["cor"]
    img_src = obter_icone_base64(nome_classe, tipo="classe")
    ref_attr = 'referrerpolicy="no-referrer"' if img_src.startswith("http") else ""
    return f'<div style="display:flex;align-items:center;gap:8px;height:{tamanho + 4}px;"><img src="{img_src}" width="{tamanho}" height="{tamanho}" style="border-radius:4px;object-fit:cover;flex-shrink:0;" {ref_attr}><span style="color:{cor};font-weight:bold;">{nome_classe}</span></div>'

# ==========================================
# BANCO DE DADOS SUPABASE (POSTGRESQL) - TURBINADO 🚀
# ==========================================

# 1. A linha mágica que faz o sistema checar/criar tabelas apenas UMA VEZ ao ligar
@st.cache_resource 
def conectar_banco():
    conn = get_conexao()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_raides (
            id SERIAL PRIMARY KEY, data_registro TEXT, nome_raide TEXT, jogador TEXT, classe TEXT,
            boss TEXT, flask TEXT, comida TEXT, presenca TEXT, ausentes TEXT, pontuacao INTEGER, porcentagem TEXT, status TEXT
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS membros (id SERIAL PRIMARY KEY, nome TEXT UNIQUE, classe TEXT, funcao TEXT)")
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM membros")
    if cursor.fetchone()[0] == 0:
        membros_iniciais = [
            ("Merenguinha", "Druida", "Tank"), ("Sliws", "Paladino", "Healer"), ("Rubro", "Guerreiro", "Tank"), ("KEVÃO", "Guerreiro", "DPS"),
            ("Flockk", "Druida", "DPS"), ("korthak", "Druida", "DPS"), ("Cybercat", "Druida", "Healer"), ("Clorofila", "Paladino", "DPS"),
            ("Kishin", "Paladino", "Healer"), ("Kastten", "Ladino", "DPS"), ("Kiss/Pantera", "Caçador", "DPS"), ("JeffHunter/Shans", "Caçador", "DPS"),
            ("Pivetona", "Caçador", "DPS"), ("Velhanoite", "Sacerdote", "Healer"), ("song", "Sacerdote", "DPS"), ("Domjr", "Mago", "DPS"),
            ("Shura", "Mago", "DPS"), ("Limaman", "Mago", "DPS"), ("Viviornitier", "Bruxo", "DPS"), ("Drakir", "Bruxo", "DPS"),
            ("Belerof", "Xamã", "DPS"), ("Moondin", "Xamã", "Healer"), ("Toitio", "Xamã", "Healer"), ("Elöhim", "Xamã", "DPS"),
            ("Trakina", "Xamã", "DPS"), ("Kdan", "Mago", "DPS"), ("Polvão", "Bruxo", "DPS")
        ]
        cursor.executemany("INSERT INTO membros (nome, classe, funcao) VALUES (%s, %s, %s) ON CONFLICT (nome) DO NOTHING", membros_iniciais)
        conn.commit()
    cursor.close()
    conn.close()
    return True

_ = conectar_banco()

# 2. A linha mágica que guarda os jogadores na memória por 15 segundos!
@st.cache_data(ttl=15) 
def obter_membros():
    conn = get_conexao()
    df = pd.read_sql("SELECT * FROM membros ORDER BY nome ASC", conn)
    conn.close()
    return df

# ==========================================
# GERADORES DE PDF CORRIGIDOS (BLINDAGEM CONTRA CORRUPÇÃO)
# ==========================================
def sanitizar_texto(texto):
    if not texto or pd.isna(texto): return ""
    txt = str(texto)
    replaces = {"’": "'", "`": "'", "º": "o", "ª": "a", "🛡": "", "🧥": "", "👕": "", "💪": "", "🧤": "", "👖": "", "👢": "", "⚔️": "", "🗡": "", "🏹": "", "⭐": "", "️": ""}
    for k, v in replaces.items(): txt = txt.replace(k, v)
    return txt.encode("latin-1", "ignore").decode("latin-1").strip()

def pdf_para_bytes(pdf):
    try:
        saida = pdf.output(dest='S')
        if isinstance(saida, str): return saida.encode('latin-1', 'ignore')
        return bytes(saida)
    except: pass
    try:
        saida = pdf.output()
        if isinstance(saida, str): return saida.encode('latin-1', 'ignore')
        return bytes(saida)
    except: return b""

class PDFCore(FPDF):
    def header(self):
        self.set_fill_color(22, 27, 34)
        self.rect(0, 0, 210, 297, "F")
        self.set_draw_color(212, 175, 55)
        self.set_line_width(1)
        self.rect(8, 8, 194, 281)
        if os.path.exists("logo_guilda.jpg"): self.image("logo_guilda.jpg", x=90, y=12, w=30)
        elif os.path.exists("logo_guilda.png"): self.image("logo_guilda.png", x=90, y=12, w=30)

    def footer(self):
        self.set_y(-18)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "Core Renegados - Sistema Oficial de Gestao", 0, 0, "C")

def gerar_pdf_geral(nome_raide, data_raide, df_resultados):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    
    nome_raide_limpo = sanitizar_texto(nome_raide)
    data_raide_limpa = sanitizar_texto(data_raide)
    
    pdf.set_fill_color(20, 20, 20)
    pdf.rect(10, 10, 277, 22, "F")
    pdf.set_xy(15, 13)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(140, 8, "RELATORIO DE PREPARACAO PARA ATAQUE", 0, 1, "L")
    pdf.set_xy(15, 21)
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(200, 200, 200)
    pdf.cell(140, 6, f"Data/Horario: {data_raide_limpa} | Raide: {nome_raide_limpo}", 0, 1, "L")
    
    qtd_prep = len(df_resultados[df_resultados['status'].astype(str).str.contains("PREPARADO", na=False) & ~df_resultados['status'].astype(str).str.contains("NÃO|NAO", na=False)])
    qtd_atencao = len(df_resultados[df_resultados['status'].astype(str).str.contains("ATENÇÃO|ATENCAO", na=False)])
    qtd_nao = len(df_resultados[df_resultados['status'].astype(str).str.contains("NÃO|NAO", na=False)])
    total = len(df_resultados)
    
    pdf.set_xy(155, 13)
    pdf.set_font("helvetica", "B", 8)
    pdf.set_fill_color(50, 50, 50)
    pdf.cell(30, 6, "JOGADORES", 1, 0, "C", True)
    pdf.cell(30, 6, "PREPARADOS", 1, 0, "C", True)
    pdf.cell(30, 6, "ATENCAO", 1, 0, "C", True)
    pdf.cell(35, 6, "NAO PREPARADOS", 1, 1, "C", True)
    pdf.set_xy(155, 19)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(30, 9, str(total), 1, 0, "C", True)
    pdf.set_fill_color(198, 239, 206); pdf.set_text_color(0, 97, 0)
    pdf.cell(30, 9, str(qtd_prep), 1, 0, "C", True)
    pdf.set_fill_color(255, 235, 156); pdf.set_text_color(156, 101, 0)
    pdf.cell(30, 9, str(qtd_atencao), 1, 0, "C", True)
    pdf.set_fill_color(255, 199, 206); pdf.set_text_color(156, 0, 6)
    pdf.cell(35, 9, str(qtd_nao), 1, 1, "C", True)
    pdf.ln(8)
    
    pdf.set_fill_color(30, 30, 30)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(64, 6, "DADOS DO JOGADOR", 1, 0, "C", True)
    pdf.cell(72, 6, "ITENS OBRIGATORIOS", 1, 0, "C", True)
    pdf.cell(83, 6, "ENCANTAMENTOS AUSENTES", 1, 0, "C", True)
    pdf.cell(26, 6, "PONTOS", 1, 0, "C", True)
    pdf.cell(32, 6, "STATUS", 1, 1, "C", True)
    
    pdf.set_fill_color(15, 15, 15)
    pdf.set_font("helvetica", "B", 7)
    w = [8, 36, 20, 18, 18, 18, 18, 83, 13, 13, 32]
    h_cols = ["#", "Jogador", "Classe", "Boss", "Frasco", "Comida", "Pres.", "Itens Ausentes", "Total", "%", "Situacao"]
    for i in range(len(w)): pdf.cell(w[i], 6, h_cols[i], 1, 0, "C", True)
    pdf.ln()
    
    pdf.set_font("helvetica", "", 7)
    row_h = 5.3
    MAPA_ENC = {"🛡": "Ombros", "🧥": "Capa", "👕": "Peito", "💪": "Bracadeiras", "🧤": "Luvas", "👖": "Calcas", "👢": "Botas", "⚔": "Arma Prin.", "🗡": "Arma Sec.", "🏹": "Ranged"}
    
    for idx, row in df_resultados.iterrows():
        st_raw = sanitizar_texto(row["status"]).upper()
        if "NAO" in st_raw or "NÃO" in st_raw: pdf.set_fill_color(255, 199, 206)
        else: pdf.set_fill_color(*(245, 245, 245) if idx % 2 == 0 else (255, 255, 255))
            
        pdf.set_text_color(0, 0, 0)
        pdf.cell(w[0], row_h, str(idx+1), 1, 0, "C", True)
        jogador_nome = sanitizar_texto(row["jogador"]).replace("*", "").strip()
        if str(row["porcentagem"]) == "100%": pdf.set_font("helvetica", "B", 7); pdf.set_text_color(0, 100, 0)
        else: pdf.set_font("helvetica", "", 7); pdf.set_text_color(0, 0, 0)
        pdf.cell(w[1], row_h, jogador_nome, 1, 0, "L", True)
        
        pdf.set_font("helvetica", "", 7); pdf.set_text_color(0, 0, 0)
        x_classe, y_classe = pdf.get_x(), pdf.get_y()
        classe_str = sanitizar_texto(row["classe"])
        caminho_icone = garantir_icone_local(classe_str, "classe")
        if caminho_icone and os.path.exists(caminho_icone):
            try: pdf.image(caminho_icone, x=x_classe + 2, y=y_classe + 0.9, w=3.5, h=3.5)
            except Exception: pass
        pdf.cell(w[2], row_h, "      " + classe_str, 1, 0, "L", True)
        pdf.cell(w[3], row_h, sanitizar_texto(row["boss"]), 1, 0, "C", True)
        pdf.cell(w[4], row_h, sanitizar_texto(row["flask"]), 1, 0, "C", True)
        pdf.cell(w[5], row_h, sanitizar_texto(row["comida"]), 1, 0, "C", True)
        pdf.cell(w[6], row_h, sanitizar_texto(row["presenca"]), 1, 0, "C", True)
        
        aus_txt = str(row["ausentes"]) if pd.notna(row["ausentes"]) else "-"
        for k, v in MAPA_ENC.items(): aus_txt = aus_txt.replace(k, v)
        aus_txt = sanitizar_texto(aus_txt)
        if aus_txt and aus_txt != "-": pdf.set_text_color(220, 0, 0)
        pdf.cell(w[7], row_h, aus_txt, 1, 0, "L", True)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(w[8], row_h, sanitizar_texto(row["pontuacao"]), 1, 0, "C", True)
        
        if str(row["porcentagem"]) == "100%": pdf.set_font("helvetica", "B", 7); pdf.set_text_color(0, 100, 0)
        pdf.cell(w[9], row_h, sanitizar_texto(row["porcentagem"]), 1, 0, "C", True)
        pdf.set_font("helvetica", "", 7); pdf.set_text_color(0, 0, 0)
        
        if "PREPARADO" in st_raw and "NAO" not in st_raw and "NÃO" not in st_raw: pdf.set_fill_color(198, 239, 206); pdf.set_text_color(0, 97, 0)
        elif "ATENCAO" in st_raw or "ATENÇÃO" in st_raw: pdf.set_fill_color(255, 235, 156); pdf.set_text_color(156, 101, 0)
        else: pdf.set_fill_color(255, 199, 206); pdf.set_text_color(156, 0, 6)
        pdf.set_font("helvetica", "B", 7)
        pdf.cell(w[10], row_h, st_raw, 1, 1, "C", True)
        pdf.set_font("helvetica", "", 7)
    return pdf_para_bytes(pdf)

def gerar_pdf_individual(nome_raide, data_raide, row):
    pdf = PDFCore()
    pdf.add_page()
    pdf.ln(32)
    pdf.set_font("helvetica", "B", 15)
    pdf.set_text_color(212, 175, 55)
    pdf.cell(0, 8, "CORE RENEGADOS - DESEMPENHO INDIVIDUAL", 0, 1, "C")
    pdf.set_font("helvetica", "I", 10)
    pdf.set_text_color(200, 200, 200)
    pdf.cell(0, 5, sanitizar_texto(f"Raid: {nome_raide} | Data: {data_raide}"), 0, 1, "C")
    pdf.ln(12)
    pdf.set_fill_color(33, 38, 45)
    pdf.set_draw_color(212, 175, 55)
    pdf.rect(20, pdf.get_y(), 170, 55, "DF")
    pdf.set_xy(25, pdf.get_y() + 5)
    pdf.set_font("helvetica", "B", 13)
    pdf.set_text_color(212, 175, 55)
    pdf.cell(0, 8, sanitizar_texto(f"Jogador: {row['jogador']}"), 0, 1, "L")
    pdf.set_x(25)
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(240, 246, 252)
    pdf.cell(0, 7, sanitizar_texto(f"Classe: {row['classe']}"), 0, 1, "L")
    pdf.set_x(25)
    pdf.cell(0, 7, sanitizar_texto(f"Pontuacao Final: {row['pontuacao']} pontos"), 0, 1, "L")
    pdf.set_x(25)
    pdf.cell(0, 7, sanitizar_texto(f"Aproveitamento Geral: {row['porcentagem']}"), 0, 1, "L")
    pdf.set_x(25)
    status_txt = sanitizar_texto(str(row["status"]))
    if "PREPARADO" in status_txt and "NÃO" not in status_txt and "NAO" not in status_txt: pdf.set_text_color(86, 211, 100)
    elif "ATENÇÃO" in status_txt or "ATENCAO" in status_txt: pdf.set_text_color(227, 179, 65)
    else: pdf.set_text_color(248, 81, 73)
    pdf.cell(0, 7, f"Status de Preparacao: {status_txt}", 0, 1, "L")
    return pdf_para_bytes(pdf)

class PDFTaticas(FPDF):
    def header(self):
        self.set_fill_color(70, 70, 70) 
        self.rect(0, 0, 210, 297, "F")

def gerar_pdf_taticas(dados, player_classes):
    pdf = PDFTaticas()
    pdf.add_page()
    pdf.set_y(15)
    pdf.set_font("helvetica", "B", 18)
    pdf.set_fill_color(11, 77, 140) 
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "MATA BOSS WIPE TRASH", 1, 1, "C", True)
    pdf.ln(10)

    def get_class_color(player_name):
        if not player_name or player_name not in player_classes: return (255, 255, 255) 
        c = player_classes[player_name]
        cores = {"Guerreiro": (198, 155, 109), "Paladino": (244, 140, 186), "Caçador": (171, 212, 115), "Ladino": (255, 244, 104), "Sacerdote": (255, 255, 255), "Mago": (63, 199, 235), "Bruxo": (148, 130, 201), "Xamã": (0, 112, 222), "Druida": (255, 124, 10)}
        return cores.get(c, (255, 255, 255))

    row_h, icon_sz = 7, 6
    def desenhar_cabecalho(texto, start_x, larg_total):
        pdf.set_xy(start_x, pdf.get_y()); pdf.set_font("helvetica", "B", 12); pdf.set_fill_color(11, 77, 140); pdf.set_text_color(255, 255, 255); pdf.cell(larg_total, 8, texto, 1, 1, "C", True)

    def desenhar_linha(items, start_x):
        pdf.set_xy(start_x, pdf.get_y())
        start_y, x_atual = pdf.get_y(), start_x
        pdf.set_draw_color(0, 0, 0); pdf.set_line_width(0.5); pdf.set_font("helvetica", "B", 10)
        
        for (tipo, val, larg, extra) in items:
            if tipo == "img":
                pdf.set_fill_color(150, 150, 150) 
                pdf.rect(x_atual, start_y, larg, row_h, "DF")
                if val:
                    caminho = garantir_icone_local(val, "tatica")
                    if caminho and os.path.exists(caminho):
                        try: pdf.image(caminho, x=x_atual + (larg/2) - (icon_sz/2), y=start_y + (row_h/2) - (icon_sz/2), w=icon_sz, h=icon_sz)
                        except Exception: pass
            elif tipo == "txt":
                if extra == "player" and val: r,g,b = get_class_color(val); pdf.set_fill_color(r, g, b); pdf.set_text_color(0, 0, 0)
                elif extra == "group" and val: pdf.set_fill_color(200, 200, 200); pdf.set_text_color(0, 0, 0)
                else: pdf.set_fill_color(255, 255, 255); pdf.set_text_color(0, 0, 0)
                pdf.set_xy(x_atual, start_y)
                pdf.cell(larg, row_h, sanitizar_texto(val), 1, 0, "C", True)
            x_atual += larg
        pdf.set_xy(start_x, start_y + row_h)

    linhas_buffs = []
    for r in range(1, 10):
        b1, b2, grp, p1, atr, p2, b3 = dados.get(f"b_r{r}_0",""), dados.get(f"b_r{r}_1",""), dados.get(f"b_r{r}_2",""), dados.get(f"b_r{r}_3",""), dados.get(f"b_r{r}_4",""), dados.get(f"b_r{r}_5",""), dados.get(f"b_r{r}_6","")
        if b1 or b2 or grp or p1 or atr or p2 or b3: linhas_buffs.append([("img", b1, 8, None), ("img", b2, 8, None), ("txt", grp, 16, "group"), ("txt", p1, 45, "player"), ("img", atr, 8, None), ("txt", p2, 45, "player"), ("img", b3, 8, None)])
    largura_buffs = 138; start_x_buffs = (210 - largura_buffs) / 2
    if linhas_buffs:
        desenhar_cabecalho("Buffs and Assignments", start_x_buffs, largura_buffs)
        for l in linhas_buffs: desenhar_linha(l, start_x_buffs)
        pdf.ln(8)

    linhas_tanks = []
    for r in range(1, 7):
        b1, b2, p1, p2, mald, p3, b3 = dados.get(f"t_r{r}_0",""), dados.get(f"t_r{r}_1",""), dados.get(f"t_r{r}_2",""), dados.get(f"t_r{r}_3",""), dados.get(f"t_r{r}_4",""), dados.get(f"t_r{r}_5",""), dados.get(f"t_r{r}_6","")
        if b1 or b2 or p1 or p2 or mald or p3 or b3: linhas_tanks.append([("img", b1, 8, None), ("img", b2, 8, None), ("txt", p1, 35, "player"), ("txt", p2, 35, "player"), ("img", mald, 8, None), ("txt", p3, 35, "player"), ("img", b3, 8, None)])
    largura_tanks = 137; start_x_tanks = (210 - largura_tanks) / 2
    if linhas_tanks:
        desenhar_cabecalho("Tanks, Sheep & Debuffs", start_x_tanks, largura_tanks)
        for l in linhas_tanks: desenhar_linha(l, start_x_tanks)
        pdf.ln(8)

    linhas_md = []
    for r in range(1, 3):
        ic, p1, g1, g2 = dados.get(f"m_r{r}_0",""), dados.get(f"m_r{r}_1",""), dados.get(f"m_r{r}_2",""), dados.get(f"m_r{r}_3","")
        if ic or p1 or g1 or g2: linhas_md.append([("img", ic, 10, None), ("txt", p1, 40, "player"), ("txt", g1, 40, "group"), ("txt", g2, 40, "group")])
    largura_md = 130; start_x_md = (210 - largura_md) / 2
    if linhas_md:
        desenhar_cabecalho("MD Trash - Boss + Trash", start_x_md, largura_md)
        for l in linhas_md: desenhar_linha(l, start_x_md)

    return pdf_para_bytes(pdf)

# ==========================================
# CABEÇALHO DA PÁGINA
# ==========================================
col_img, col_tit = st.columns([1, 8])
with col_img:
    if os.path.exists("logo_guilda.jpg"): st.image("logo_guilda.jpg", width=70)
    elif os.path.exists("logo_guilda.png"): st.image("logo_guilda.png", width=70)
with col_tit:
    st.markdown("<h1 style='color:#d4af37; margin-bottom:0px; padding-top:5px; font-size:26px;'>🛡️ CORE RENEGADOS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e; font-size:13px; margin-top:-5px;'>SISTEMA DE GESTÃO E PREPARAÇÃO DE RAID</p>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Dashboard", "👥 Gerenciar Jogadores", "⚔️ Nova Raide", "📊 Relatórios de Raide", "📝 Táticas e Buffs"])

# ==========================================
# ABA 1: DASHBOARD
# ==========================================
with tab1:
    st.subheader("📊 Visão Geral da Guilda e Desempenho")
    
    conn = get_conexao()
    df_hist = pd.read_sql("SELECT * FROM historico_raides", conn)
    membros_df = pd.read_sql("SELECT * FROM membros", conn)
    conn.close()

    total_membros = len(membros_df) if not membros_df.empty else 0
    total_raides = df_hist["data_registro"].nunique() if not df_hist.empty else 0
    
    if not df_hist.empty:
        df_hist["pct_num"] = df_hist["porcentagem"].astype(str).str.replace("%", "").str.strip().astype(float)
        prep_media = f"{df_hist['pct_num'].mean():.1f}%"
    else:
        prep_media = "0%"

    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.metric("Total de Membros", total_membros)
    c_m2.metric("Raides Registradas", total_raides)
    c_m3.metric("Prep. Média da Guilda", prep_media)
    st.markdown("---")

    if df_hist.empty:
        st.info("ℹ️ Ainda não há dados de raides suficientes para gerar os gráficos. Registre uma nova raide na Aba 3!")
    else:
        c_pizza, c_rank = st.columns(2)
        with c_pizza:
            st.markdown("### 🥧 Proporção de Presença nas Raids")
            st.caption("Distribuição geral de comparência (Presentes vs Ausentes/Faltas).")
            # Correção vital do BUG da pizza: "startswith" no lugar de "in"
            df_hist["status_presenca"] = df_hist["presenca"].apply(lambda x: "Presente" if str(x).startswith("1") else "Ausente")
            df_pie = df_hist["status_presenca"].value_counts().reset_index()
            df_pie.columns = ["Status", "Quantidade"]
            
            import altair as alt
            pie_chart = alt.Chart(df_pie).mark_arc(innerRadius=60).encode(
                theta=alt.Theta(field="Quantidade", type="quantitative"),
                color=alt.Color(field="Status", type="nominal", scale=alt.Scale(domain=["Presente", "Ausente"], range=["#238636", "#da3633"])),
                tooltip=["Status", "Quantidade"]
            ).properties(height=200)
            
            st.altair_chart(pie_chart, use_container_width=True)
            status_filtro = st.radio("🔍 Ver lista de:", ["Nenhum", "Presente", "Ausente"], horizontal=True, key="filtro_status_pizza_v2")
            if status_filtro != "Nenhum":
                df_filtrado = df_hist[df_hist["status_presenca"] == status_filtro][["data_registro", "nome_raide", "jogador"]].drop_duplicates()
                if not df_filtrado.empty:
                    st.dataframe(df_filtrado.rename(columns={"data_registro": "Data/Horário", "nome_raide": "Raide", "jogador": "Jogador"}), use_container_width=True, hide_index=True, height=130)
                else:
                    st.info("Nenhum registro encontrado.")
            
        with c_rank:
            st.markdown("### 🏆 Ranking Histórico de Preparação")
            st.caption("Média histórica de preparação por jogador.")
            df_ranking = df_hist.groupby(["jogador", "classe"])["pct_num"].mean().reset_index().sort_values(by="pct_num", ascending=False).reset_index(drop=True)
            
            ranking_formatado = []
            for _, row in df_ranking.iterrows():
                classe_nome = str(row["classe"]) if pd.notna(row["classe"]) else "-"
                _ = ranking_formatado.append({"Jogador": row["jogador"], "Classe": html_classe(classe_nome, 20), "Média": f"{row['pct_num']:.1f}%"})
                
            tabela_rank_html = pd.DataFrame(ranking_formatado).to_html(escape=False, index=False).replace('<table', '<table style="width: 100%; text-align: left; border-collapse: collapse;"')
            st.markdown(f'<div style="height: 330px; overflow-y: auto; border: 1px solid #30363d; border-radius: 6px; padding: 4px; background-color: #0d1117;">{tabela_rank_html}</div>', unsafe_allow_html=True)

        st.markdown("---")
        c_g1, c_g2 = st.columns(2)
        with c_g1:
            st.markdown("### ⚠️ Encantamentos Mais Ausentes")
            st.caption("Quais partes de equipamento o core mais esquece de encantar.")
            todos_ausentes = [i for aus in df_hist["ausentes"].dropna() if aus and aus != "-" for i in [item.strip() for item in str(aus).split(",")] if i and i != "-"]
            if todos_ausentes:
                df_aus_count = pd.DataFrame(todos_ausentes, columns=["Encantamento"]).value_counts().reset_index()
                df_aus_count.columns = ["Encantamento", "Total Ausências"]
                st.bar_chart(df_aus_count.set_index("Encantamento"), height=260, color="#da3633")
            else:
                st.success("🎉 Nenhum encantamento ausente registrado nas raides até o momento!")
            
        with c_g2:
            st.markdown("### 🧪 Média de Flasks e Comida")
            st.caption("Acompanhamento da regularidade de consumíveis por sessão.")
            def extrair_num(val):
                try: return float(str(val).split("/")[0])
                except: return 0.0
            df_hist_cons = df_hist.copy()
            df_hist_cons["flask_num"] = df_hist_cons["flask"].apply(extrair_num)
            df_hist_cons["comida_num"] = df_hist_cons["comida"].apply(extrair_num)
            df_consumo = df_hist_cons.groupby("data_registro")[["flask_num", "comida_num"]].mean().reset_index().rename(columns={"data_registro": "Raide/Data", "flask_num": "Flasks", "comida_num": "Comida"}).set_index("Raide/Data")
            st.line_chart(df_consumo, height=260, color=["#1f6feb", "#e3b341"])

# ==========================================
# ABA 2: GERENCIAR JOGADORES
# ==========================================
with tab2:
    st.subheader("👥 Gestão de Membros do Core")
    with st.expander("➕ Adicionar Novo Membro"):
        with st.form("form_add", clear_on_submit=True):
            novo_nome = st.text_input("Nome do Jogador")
            nova_classe = st.selectbox("Classe", list(CLASSES_WOW.keys()))
            nova_funcao = st.selectbox("Função", ["Tank", "Healer", "DPS"])
            if st.form_submit_button("Salvar Membro"):
                if novo_nome:
                    try:
                        conn = get_conexao()
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO membros (nome, classe, funcao) VALUES (%s, %s, %s)", (novo_nome, nova_classe, nova_funcao))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success(f"Jogador {novo_nome} adicionado!")
                        st.rerun()
                    except: st.error("Erro: Já existe um jogador com este nome!")
                else: st.warning("Insira um nome válido.")
    st.markdown("---")
    membros = obter_membros()
    for _, row in membros.iterrows():
        c_nome, c_classe, c_func, c_edit, c_del = st.columns([3, 2, 2, 1.5, 1.5])
        c_nome.markdown(f'<div style="height:42px; display:flex; align-items:center; font-size:16px;">{row["nome"]}</div>', unsafe_allow_html=True)
        c_classe.markdown(html_classe(row["classe"], 28), unsafe_allow_html=True)
        c_func.markdown(f'<div style="height:42px; display:flex; align-items:center; font-size:16px;">{row["funcao"]}</div>', unsafe_allow_html=True)
        with c_edit:
            with st.popover("✏️ Editar"):
                with st.form(f"edit_{row['id']}"):
                    e_nome = st.text_input("Nome", value=row["nome"])
                    classes_lista = list(CLASSES_WOW.keys())
                    e_classe = st.selectbox("Classe", classes_lista, index=classes_lista.index(row["classe"]) if row["classe"] in classes_lista else 0)
                    funcoes = ["Tank", "Healer", "DPS"]
                    e_funcao = st.selectbox("Função", funcoes, index=funcoes.index(row["funcao"]) if row["funcao"] in funcoes else 0)
                    if st.form_submit_button("Salvar Alterações"):
                        conn = get_conexao()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE membros SET nome=%s, classe=%s, funcao=%s WHERE id=%s", (e_nome, e_classe, e_funcao, row["id"]))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success("Atualizado!")
                        st.rerun()
        if c_del.button("🗑️ Excluir", key=f"del_{row['id']}"):
            conn = get_conexao()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM membros WHERE id=%s", (row["id"],))
            conn.commit()
            cursor.close()
            conn.close()
            st.rerun()

# ==========================================
# ABA 3: NOVA RAIDE
# ==========================================
with tab3:
    st.subheader("⚔️ Registrar Nova Raid")

    if "etapa_raide" not in st.session_state: st.session_state.etapa_raide = 1
    if st.session_state.etapa_raide == 2 and not all(k in st.session_state for k in ["raide_data_base", "raide_nome", "raide_jogadores", "raide_bosses"]):
        st.session_state.etapa_raide = 1
        st.rerun()

    def resetar_raide(): st.session_state.etapa_raide = 1

    if st.session_state.etapa_raide == 1:
        st.markdown("### 1️⃣ Seleção do Core e Horário de Início")
        c_data, c_inicio, c_raide = st.columns(3)
        with c_data: data_input = st.date_input("Data da Raid", datetime.today())
        with c_inicio: hora_inicio = st.time_input("Horário de Início", datetime.strptime("20:00", "%H:%M").time())
        with c_raide: raide_input = st.selectbox("Qual Raid ?", LISTA_RAIDES)
            
        membros_df = obter_membros()
        todos_jogadores = membros_df["nome"].tolist() if not membros_df.empty else []
        jogadores_selecionados = st.multiselect("Selecione quem vai participar:", todos_jogadores, default=todos_jogadores)
        
        if st.button("🚀 Confirmar Core e Gerar Tabela", type="primary", use_container_width=True):
            if not jogadores_selecionados: st.warning("⚠️ Selecione pelo menos um jogador para prosseguir!")
            else:
                st.session_state.raide_data_base = data_input.strftime('%d/%m/%Y')
                st.session_state.raide_hora_inicio = hora_inicio.strftime('%H:%M')
                st.session_state.raide_nome = raide_input
                st.session_state.raide_jogadores = jogadores_selecionados
                st.session_state.raide_bosses = QTD_BOSSES[raide_input]
                st.session_state.etapa_raide = 2
                st.rerun()

    elif st.session_state.etapa_raide == 2:
        boss_total = st.session_state.raide_bosses
        st.markdown(f"### 2️⃣ Preenchimento: {st.session_state.raide_nome} ({st.session_state.raide_data_base}) — Total de Bosses: {boss_total}")
        st.info("Todos iniciam como presentes. Desmarque os ausentes para zerar. 0 ausências = **+5 pontos de Bônus (Total: 45 Pontos)**.")
        
        # O NOVO CAMPO DE BUSCA INTELIGENTE
        busca = st.text_input("🔍 Buscar jogador específico (ao digitar, ele irá para o topo da lista):", "")
        st.button("🔙 Voltar para a Seleção de Jogadores", on_click=resetar_raide)
        st.markdown("---")
        
        opcoes_boss = [f"{i}/{boss_total}" for i in range(boss_total, -1, -1)]
        opcoes_flask_comida = [f"{i}/10" for i in range(10, -1, -1)]
        membros_df = obter_membros()
        player_classes = dict(zip(membros_df["nome"], membros_df["classe"])) if not membros_df.empty else {}
        resultados_inputs = {}
        
        c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1, 1.2, 1.2, 1.2, 2.5])
        c1.write("**Jogador / Classe**"); c2.write("**Pres.**"); c3.write("**Bosses**"); c4.write("**Flasks**"); c5.write("**Comida**"); c6.write("**Encantamentos Ausentes**")
        
        # A mágica da ordenação: Quem você busca sobe pro topo da tela na mesma hora
        jogadores_exibicao = st.session_state.raide_jogadores
        if busca:
            jogadores_exibicao = sorted(jogadores_exibicao, key=lambda j: 0 if busca.lower() in j.lower() else 1)
        
        for jogador in jogadores_exibicao:
            classe_jogador = player_classes.get(jogador, "-")
            
            # Destaca de leve o fundo de quem foi buscado
            if busca and busca.lower() in jogador.lower():
                st.markdown(f"<div style='background-color: rgba(212, 175, 55, 0.1); padding: 5px; border-radius: 5px;'>", unsafe_allow_html=True)
            
            c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1, 1.2, 1.2, 1.2, 2.5])
            with c1: st.markdown(f"<div style='font-weight:bold; font-size:14px; margin-bottom:2px;'>{jogador}</div>" + html_classe(classe_jogador, 18), unsafe_allow_html=True)
            with c2: pres = st.checkbox("", value=True, key=f"pres_{jogador}")
            is_disabled = not pres
            with c3: boss_sel = st.selectbox("", opcoes_boss, index=0, key=f"boss_{jogador}", disabled=is_disabled, label_visibility="collapsed")
            with c4: flask_sel = st.selectbox("", opcoes_flask_comida, index=0, key=f"flask_{jogador}", disabled=is_disabled, label_visibility="collapsed")
            with c5: comida_sel = st.selectbox("", opcoes_flask_comida, index=0, key=f"comida_{jogador}", disabled=is_disabled, label_visibility="collapsed")
            with c6: encants = st.multiselect("", LISTA_ENCANTAMENTOS, key=f"encant_{jogador}", disabled=is_disabled, label_visibility="collapsed")
            resultados_inputs[jogador] = {"pres": pres, "boss": boss_sel, "flask": flask_sel, "comida": comida_sel, "encants": encants, "classe": classe_jogador}
            
            if busca and busca.lower() in jogador.lower():
                st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("---")
        if st.button("💾 Encerrar Raid e Salvar Relatório", type="primary", use_container_width=True):
            hora_fim_automatica = datetime.now().strftime('%H:%M')
            data_final_completa = f"{st.session_state.raide_data_base} ({st.session_state.raide_hora_inicio} - {hora_fim_automatica})"
            conn = get_conexao()
            cursor = conn.cursor()
            
            for jogador, dados in resultados_inputs.items():
                pres_val = 1 if dados["pres"] else 0
                if pres_val == 0:
                    total_pontos, porcentagem, status = 0, "0%", "NÃO PREPARADO"
                    str_boss, str_flask, str_comida, str_ausentes = f"0/{boss_total}", "0/10", "0/10", "-"
                else:
                    boss_val = int(dados["boss"].split("/")[0])
                    flask_val = int(dados["flask"].split("/")[0])
                    comida_val = int(dados["comida"].split("/")[0])
                    qtd_ausentes = len(dados["encants"])
                    
                    # NOVA MATEMÁTICA: Se faltar 1 encante, ZERA a nota de encantamento (0). Se tiver tudo, ganha 15!
                    p_boss = (boss_val / boss_total) * 10
                    p_flask = (flask_val / 10) * 10
                    p_comida = (comida_val / 10) * 10
                    p_encant = 15 if qtd_ausentes == 0 else 0
                    
                    total_pontos = round(p_boss + p_flask + p_comida + p_encant)
                    
                    pct = (total_pontos / 45) * 100
                    porcentagem = f"{int(pct)}%"
                    if pct == 100: status = "PREPARADO"
                    elif pct >= 50: status = "ATENÇÃO"
                    else: status = "NÃO PREPARADO"
                    
                    str_ausentes = ", ".join(dados["encants"]) if qtd_ausentes > 0 else "-"
                    str_boss, str_flask, str_comida = dados['boss'], dados['flask'], dados['comida']
                    
                cursor.execute('''
                    INSERT INTO historico_raides (data_registro, nome_raide, jogador, classe, boss, flask, comida, presenca, ausentes, pontuacao, porcentagem, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (data_final_completa, st.session_state.raide_nome, jogador, dados["classe"], str_boss, str_flask, str_comida, f"{pres_val}/1", str_ausentes, total_pontos, porcentagem, status))
                      
            conn.commit()
            cursor.close()
            conn.close()
            st.session_state.etapa_raide = 1
            st.success(f"✅ Raid salva com sucesso! Encerrada às {hora_fim_automatica}.")
            st.balloons()

# ==========================================
# ABA 4: RELATÓRIOS 
# ==========================================
with tab4:
    st.subheader("📊 Relatórios e Histórico de Raids")
    conn = get_conexao()
    cursor = conn.cursor()
    
    # === A CORREÇÃO ENTRA AQUI: A BUSCA ADAPTADA PARA POSTGRESQL ===
    cursor.execute("SELECT data_registro, nome_raide FROM historico_raides GROUP BY data_registro, nome_raide ORDER BY MAX(id) DESC")
    
    raides_salvas = cursor.fetchall()
    cursor.close()
    conn.close()

    if not raides_salvas: st.info("Nenhuma raide registrada.")
    else:
        escolha = st.selectbox("Selecione a Raid no Histórico", [f"{d} | {n}" for d, n in raides_salvas])
        data_sel, nome_sel = escolha.split(" | ", 1)
        st.markdown(f"**Raide selecionada:** `{nome_sel}` — **Horário/Data:** `{data_sel}`")
        
        with st.expander("⚙️ Gerenciar Raid (Excluir do Histórico)"):
            st.warning("⚠️ Atenção: A exclusão é permanente.")
            senha_input = st.text_input("Digite a senha de administrador:", type="password", key=f"senha_exc_{data_sel}_{nome_sel}")
            if st.button("🚨 Confirmar Exclusão Permanente", key=f"btn_exc_{data_sel}_{nome_sel}", type="primary"):
                if senha_input == "Renegados2026":
                    conn = get_conexao()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM historico_raides WHERE data_registro = %s AND nome_raide = %s", (data_sel, nome_sel))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success("✅ Raid excluída com sucesso!")
                    st.rerun()
                else: st.error("❌ Senha incorreta!")
                    
        st.markdown("---")
        conn = get_conexao()
        df = pd.read_sql("SELECT jogador, classe, boss, flask, comida, presenca, ausentes, pontuacao, porcentagem, status FROM historico_raides WHERE data_registro=%s AND nome_raide=%s", conn, params=(data_sel, nome_sel)).fillna("-")
        conn.close()

        c_m1, c_m2, c_m3 = st.columns(3)
        c_m1.metric("🟢 Preparados", len(df[df["status"] == "PREPARADO"]))
        c_m2.metric("🟡 Atenção", len(df[df["status"] == "ATENÇÃO"]))
        c_m3.metric("🔴 Não Preparados", len(df[df["status"] == "NÃO PREPARADO"]))
        st.markdown("---")
        
        relatorio_formatado = []
        for _, row in df.iterrows():
            classe_nome = str(row["classe"]) if pd.notna(row["classe"]) else "-"
            jogador_nome = f"⭐ {row['jogador']}" if str(row["porcentagem"]) == "100%" else row["jogador"]
            
            st_txt = str(row["status"])
            if "PREPARADO" in st_txt and "NÃO" not in st_txt: status_html = f"<span style='color: #4CAF50; font-weight: bold;'>🟢 {st_txt}</span>"
            elif "ATENÇÃO" in st_txt: status_html = f"<span style='color: #FFC107; font-weight: bold;'>🟡 {st_txt}</span>"
            else: status_html = f"<span style='color: #F44336; font-weight: bold;'>🔴 {st_txt}</span>"
            
            _ = relatorio_formatado.append({
                "Jogador": jogador_nome, "Classe": html_classe(classe_nome, 20), "Boss": row["boss"], "Flask": row["flask"],
                "Comida": row["comida"], "Pres.": row["presenca"], "Ausências de Magías": row["ausentes"], "Pts": row["pontuacao"],
                "Média": row["porcentagem"], "Status": status_html
            })
            
        def destacar_nao_preparados(row): return ['background-color: rgba(244, 67, 54, 0.15); border-bottom: 1px solid #F44336;'] * len(row) if '🔴' in str(row['Status']) else [''] * len(row)
            
        tabela_html = pd.DataFrame(relatorio_formatado).style.apply(destacar_nao_preparados, axis=1).hide(axis="index").to_html(escape=False).replace('<table', '<table style="width: 100%; text-align: left; border-collapse: collapse;"')
        st.markdown(tabela_html, unsafe_allow_html=True)
        st.markdown("---")
        
        c_btn1, c_sel, c_btn2 = st.columns([1, 1, 1])
        nome_arquivo_seguro = "".join(c for c in nome_sel if c.isalnum() or c in " _-").replace(" ", "_")
        
        with c_btn1:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            st.download_button("📥 Baixar Relatório Geral (Dashboard PDF)", data=gerar_pdf_geral(nome_sel, data_sel, df), file_name=f"Relatorio_{nome_arquivo_seguro}.pdf", mime="application/pdf", use_container_width=True)
            
        jogadores_lista = df["jogador"].tolist()
        with c_sel: jogador_escolhido = st.selectbox("Selecionar Jogador (Para PDF Individual)", jogadores_lista) if jogadores_lista else None
        with c_btn2:
            if jogador_escolhido:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                jogador_arquivo_seguro = "".join(c for c in jogador_escolhido if c.isalnum() or c in " _-").replace(" ", "_")
                st.download_button(f"📥 Baixar PDF Individual ({jogador_escolhido})", data=gerar_pdf_individual(nome_sel, data_sel, df[df["jogador"] == jogador_escolhido].iloc[0]), file_name=f"Desempenho_{jogador_arquivo_seguro}.pdf", mime="application/pdf", use_container_width=True)

# ==========================================
# ABA 5: TÁTICAS E BUFFS
# ==========================================
def draw_dynamic_row(key_prefix, c_sizes, defaults, list_players, dados_tatica, icon_options_dict):
    cols = st.columns(c_sizes)
    for i in range(len(c_sizes)):
        with cols[i]:
            key = f"{key_prefix}_{i}"
            is_icon_col = (key_prefix.startswith(("b_", "t_")) and i in [0, 1, 4, 6]) or (key_prefix.startswith("m_") and i == 0)
            if is_icon_col:
                idx_default = list(icon_options_dict.values()).index(defaults[i]) if defaults[i] in icon_options_dict.values() else 0
                escolha = st.selectbox("", list(icon_options_dict.keys()), index=idx_default, key=key, label_visibility="collapsed")
                img_key = icon_options_dict[escolha]
                dados_tatica[key] = img_key
                if img_key: st.markdown(f'<div style="display:flex; justify-content:center; height:38px;"><img src="{obter_icone_base64(img_key, tipo="tatica")}" width="36" height="36" style="border:1px solid #555; border-radius:4px;"></div>', unsafe_allow_html=True)
                else: st.markdown("<div style='height:38px;'></div>", unsafe_allow_html=True)
            elif key_prefix.startswith("b_") and i == 2 or key_prefix.startswith("m_") and i in [2, 3]:
                idx_default = OPCOES_GRUPOS.index(defaults[i]) if defaults[i] in OPCOES_GRUPOS else 0
                dados_tatica[key] = st.selectbox("", OPCOES_GRUPOS, index=idx_default, key=key, label_visibility="collapsed")
            else:
                idx_default = list_players.index(defaults[i]) if defaults[i] in list_players else 0
                dados_tatica[key] = st.selectbox("", list_players, index=idx_default, key=key, label_visibility="collapsed")
    return ""

with tab5:
    membros_df = obter_membros()
    opcoes_players = [""] + membros_df["nome"].tolist() if not membros_df.empty else ["Nenhum jogador"]
    player_classes = dict(zip(membros_df["nome"], membros_df["classe"]))
    dados_tatica = {}

    st.markdown('<div class="tatica-header">🔮 Buffs and Assignments</div>', unsafe_allow_html=True)
    c_sizes_buffs = [1.2, 1.2, 1.5, 3.5, 1.2, 3.5, 1.2]
    defaults_buffs = [
        ["sombra", "vigor", "1-2-3", "", "mage_icon", "", ""], ["sombra", "vigor", "4-5", "", "mage_icon", "", ""],
        ["", "esp", "1 a 5", "", "mage_icon", "", ""], ["curse_pink", "", "1 a 5", "", "raio", "", ""],
        ["", "", "", "", "raio", "", ""], ["", "", "", "", "raio", "", ""],
        ["totem_azul", "", "1-2", "", "kings", "", "wisdom"], ["totem_azul", "", "3-4", "", "kings", "", "might"], ["totem_azul", "", "5", "", "kings", "", "salv"]
    ]
    for r, default in enumerate(defaults_buffs):
        draw_dynamic_row(f"b_r{r+1}", c_sizes_buffs, default, opcoes_players, dados_tatica, icon_options_dict=OPCOES_ICONES_BUFFS)
        if r in [2, 5]: st.markdown('<hr style="border-color:#333; margin-top:8px; margin-bottom:8px;">', unsafe_allow_html=True)

    st.markdown('<div class="tatica-header">🛡️ Tanks, Sheep & Debuffs</div>', unsafe_allow_html=True)
    c_sizes_tanks = [1.2, 1.2, 3.5, 3.5, 1.2, 3.5, 1.2]
    defaults_tanks = [["caveira", "", "", "", "", "", ""], ["xis", "", "", "", "orb_roxo", "", ""], ["quadrado", "", "", "", "orb_roxo", "", ""], ["triangulo", "", "", "", "", "", ""], ["lua", "", "", "", "", "", ""], ["diamante", "", "", "", "", "", ""]]
    for r, default in enumerate(defaults_tanks): draw_dynamic_row(f"t_r{r+1}", c_sizes_tanks, default, opcoes_players, dados_tatica, icon_options_dict=OPCOES_ICONES_COMBINED)

    st.markdown('<div class="tatica-header">🏹 MD Trash - Boss + Trash</div>', unsafe_allow_html=True)
    c_sizes_md = [1.2, 3.5, 3.5, 3.5]
    defaults_md = [["caveira", "", "MAIN TANK", "TRASH + BOSS"], ["xis", "", "OFF TANK", "TRASH + BOSS"]]
    for r, default in enumerate(defaults_md): draw_dynamic_row(f"m_r{r+1}", c_sizes_md, default, opcoes_players, dados_tatica, icon_options_dict=OPCOES_ICONES_TARGET_MARKS)

    st.markdown('<hr style="border-color:#333; margin-top:15px; margin-bottom:15px;">', unsafe_allow_html=True)
    st.download_button("📥 Gerar e Baixar PDF com Táticas de Boss", data=gerar_pdf_taticas(dados_tatica, player_classes), file_name=f"Taticas_Mata_Boss_{datetime.now().strftime('%d-%m-%Y')}.pdf", mime="application/pdf", type="primary", use_container_width=True)
