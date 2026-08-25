import streamlit as st
import sqlite3
import os
import urllib.request
import pandas as pd
import base64
from datetime import datetime
from fpdf import FPDF

# A LINHA MÁGICA QUE RESOLVE O PROBLEMA DAS TABELAS:
_ = pd.set_option('display.max_colwidth', None)

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
    "curse_pink": "https://wow.zamimg.com/images/wow/icons/medium/spell_shadow_unholyicons.jpg",
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
    # Os novos adicionados (O sistema vai puxar todos direto da sua pasta local):
    "shadow_prot": "", "light": "", "sanc": "", "trap": "", "blind": "", "banish": "", "shackle": ""
}

OPCOES_ICONES_BUFFS = {
    "Nenhum": "", 
    "Vigor": "vigor", 
    "Espírito": "esp", 
    "Fogo Interior": "inner_fire",
    "Proteção Sombras": "shadow_prot",
    "Mago (Int)": "mage_icon", 
    "Bruxo (Curse)": "curse_pink", 
    "Bruxo (Orbe)": "orb_roxo", 
    "Bruxo (Banir)": "banish",
    "Xamã (Raio)": "raio", 
    "Pala (Reis)": "kings", 
    "Pala (Sabedoria)": "wisdom", 
    "Pala (Poder)": "might", 
    "Pala (Salvação)": "salv", 
    "Pala (Luz)": "light",
    "Pala (Santuário)": "sanc",
    "Caçador (MD)": "md", 
    "Caçador (Armadilha)": "trap",
    "Mago (Sheep)": "sheep",
    "Ladino (Blind)": "blind",
    "Sacerdote (Shackle)": "shackle"
}

OPCOES_ICONES_TARGET_MARKS = {
    "Nenhum": "", "Caveira": "caveira", "Xis": "xis", "Quadrado": "quadrado", "Triângulo": "triangulo", "Lua": "lua", "Diamante": "diamante"
}

OPCOES_ICONES_COMBINED = {**OPCOES_ICONES_BUFFS, **OPCOES_ICONES_TARGET_MARKS}

OPCOES_GRUPOS = ["", "1", "2", "3", "4", "5", "1-2", "3-4", "4-5", "1-2-3", "1 a 5", "MAIN TANK", "OFF TANK", "TRASH + BOSS"]

QTD_BOSSES = {
    "Hyjal": 5, 
    "Black Temple": 9, 
    "SCC + TK + GRULL": 12, 
    "SUENWEL": 6
}

LISTA_RAIDES = list(QTD_BOSSES.keys())
LISTA_ENCANTAMENTOS = ["🛡 Ombros", "🧥 Capa", "👕 Peito", "💪 Braçadeiras", "🧤 Luvas", "👖 Calças", "👢 Botas", "⚔️ Arma principal", "🗡 Arma secundária", "🛡 Escudo", "🏹 Longo alcance"]

# Definindo as duas pastas separadas!
PASTA_CLASSES = "icones_classes"
PASTA_TATICAS = "icones_taticas"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_CLASSES = os.path.join(BASE_DIR, PASTA_CLASSES)
CAMINHO_TATICAS = os.path.join(BASE_DIR, PASTA_TATICAS)

os.makedirs(CAMINHO_CLASSES, exist_ok=True)
os.makedirs(CAMINHO_TATICAS, exist_ok=True)

TRANSPARENT_B64 = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
# ==========================================
# FUNÇÕES DE SUPORTE E ÍCONES (SISTEMA DE DUAS PASTAS)
# ==========================================
def obter_url_icone(chave):
    if not chave: return ""
    if chave in CLASSES_WOW: return CLASSES_WOW[chave]["url"]
    if chave in ICONES_TATICAS: return ICONES_TATICAS[chave]
    return ""

def garantir_icone_local(chave, tipo="tatica"):
    if not chave: return None
    
    # O código agora escolhe a pasta certa dependendo de quem chamou!
    pasta_alvo = CAMINHO_CLASSES if tipo == "classe" else CAMINHO_TATICAS
    extensoes = [".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"]
    
    # 1. Procura o nome exato
    for ext in extensoes:
        caminho_local = os.path.join(pasta_alvo, f"{chave}{ext}")
        if os.path.exists(caminho_local):
            return caminho_local
            
    # 2. Ignora maiúsculas/minúsculas no Linux da nuvem
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
    
    # Avisamos a função para puxar o ícone da pasta de classes!
    img_src = obter_icone_base64(nome_classe, tipo="classe")
    ref_attr = 'referrerpolicy="no-referrer"' if img_src.startswith("http") else ""
    
    return f'<div style="display:flex;align-items:center;gap:8px;height:{tamanho + 4}px;"><img src="{img_src}" width="{tamanho}" height="{tamanho}" style="border-radius:4px;object-fit:cover;flex-shrink:0;" {ref_attr}><span style="color:{cor};font-weight:bold;">{nome_classe}</span></div>'
# ==========================================
def conectar_banco():
    conn = sqlite3.connect("guilda_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_raids (
            id INTEGER PRIMARY KEY AUTOINCREMENT, data_registro TEXT, nome_raide TEXT, jogador TEXT, classe TEXT,
            boss TEXT, flask TEXT, comida TEXT, presenca TEXT, ausentes TEXT, pontuacao INTEGER, porcentagem TEXT, status TEXT
        )
    """)
    colunas_novas = ["boss", "flask", "comida", "presenca", "ausentes"]
    for col in colunas_novas:
        try: cursor.execute(f"ALTER TABLE historico_raides ADD COLUMN {col} TEXT")
        except: pass 

    cursor.execute("CREATE TABLE IF NOT EXISTS membros (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE, classe TEXT, funcao TEXT)")
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
        cursor.executemany("INSERT OR IGNORE INTO membros (nome, classe, funcao) VALUES (?, ?, ?)", membros_iniciais)
        conn.commit()
    conn.close()

_ = conectar_banco()

def obter_membros():
    conn = sqlite3.connect("guilda_database.db")
    df = pd.read_sql("SELECT * FROM membros ORDER BY nome ASC", conn)
    conn.close()
    return df

# ==========================================
# GERADORES DE PDF CORRIGIDOS (BLINDAGEM CONTRA CORRUPÇÃO)
# ==========================================
def sanitizar_texto(texto):
    if texto is None:
        return ""
    txt = str(texto)
    # Substitui caracteres problemáticos comuns no Windows/Wow
    txt = txt.replace("’", "'").replace("`", "'").replace("º", "o").replace("ª", "a")
    return txt.encode("latin-1", "replace").decode("latin-1")

def pdf_para_bytes(pdf):
    # FPDF2 nativo para bytes
    try:
        return bytes(pdf.output())
    except Exception:
        out = pdf.output()
        if isinstance(out, (bytes, bytearray)):
            return bytes(out)
        return str(out).encode("latin-1", "replace")

class PDFCore(FPDF):
    def header(self):
        self.set_fill_color(22, 27, 34)
        self.rect(0, 0, 210, 297, "F")
        self.set_draw_color(212, 175, 55)
        self.set_line_width(1)
        self.rect(8, 8, 194, 281)
        if os.path.exists("logo_guilda.jpg"):
            self.image("logo_guilda.jpg", x=90, y=12, w=30)
        elif os.path.exists("logo_guilda.png"):
            self.image("logo_guilda.png", x=90, y=12, w=30)

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
    
    # Cabeçalho Escuro
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
    
    # Resumo
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
    
    # Cabeçalho Tabela
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
    h_cols = ["#", "Jogador", "Classe", "Buff", "Frasco", "Comida", "Pres.", "Detalhes", "Total", "%", "Situacao"]
    for i in range(len(w)):
        pdf.cell(w[i], 6, h_cols[i], 1, 0, "C", True)
    pdf.ln()
    
    pdf.set_font("helvetica", "", 7)
    row_h = 5.3
    
    MAPA_ENC = {
        "🛡": "Ombros", "🧥": "Capa", "👕": "Peito", "💪": "Bracadeiras",
        "🧤": "Luvas", "👖": "Calcas", "👢": "Botas", "⚔": "Arma Prin.",
        "🗡": "Arma Sec.", "🏹": "Ranged"
    }
    
    for idx, row in df_resultados.iterrows():
        st_raw = sanitizar_texto(row["status"]).upper()
        
        if "NAO" in st_raw or "NÃO" in st_raw:
            pdf.set_fill_color(255, 199, 206)
        else:
            fill_color = (245, 245, 245) if idx % 2 == 0 else (255, 255, 255)
            pdf.set_fill_color(*fill_color)
            
        pdf.set_text_color(0, 0, 0)
        pdf.cell(w[0], row_h, str(idx+1), 1, 0, "C", True)
        
        jogador_nome = sanitizar_texto(row["jogador"]).replace("*", "").strip()
        if str(row["porcentagem"]) == "100%":
            pdf.set_font("helvetica", "B", 7)
            pdf.set_text_color(0, 100, 0)
        else:
            pdf.set_font("helvetica", "", 7)
            pdf.set_text_color(0, 0, 0)
            
        pdf.cell(w[1], row_h, jogador_nome, 1, 0, "L", True)
        
        pdf.set_font("helvetica", "", 7)
        pdf.set_text_color(0, 0, 0)
        
        # Classe com ícone
        x_classe = pdf.get_x()
        y_classe = pdf.get_y()
        classe_str = sanitizar_texto(row["classe"])
        caminho_icone = garantir_icone_local(classe_str, "classe")
        if caminho_icone and os.path.exists(caminho_icone):
            try:
                pdf.image(caminho_icone, x=x_classe + 2, y=y_classe + 0.9, w=3.5, h=3.5)
            except Exception:
                pass
        pdf.cell(w[2], row_h, "      " + classe_str, 1, 0, "L", True)
        
        pdf.cell(w[3], row_h, sanitizar_texto(row["boss"]), 1, 0, "C", True)
        pdf.cell(w[4], row_h, sanitizar_texto(row["flask"]), 1, 0, "C", True)
        pdf.cell(w[5], row_h, sanitizar_texto(row["comida"]), 1, 0, "C", True)
        pdf.cell(w[6], row_h, sanitizar_texto(row["presenca"]), 1, 0, "C", True)
        
        # Ausências
        aus_txt = str(row["ausentes"]) if pd.notna(row["ausentes"]) else "-"
        for k, v in MAPA_ENC.items():
            aus_txt = aus_txt.replace(k, v)
        aus_txt = sanitizar_texto(aus_txt)
        
        if aus_txt and aus_txt != "-":
            pdf.set_text_color(220, 0, 0)
        pdf.cell(w[7], row_h, aus_txt, 1, 0, "L", True)
        pdf.set_text_color(0, 0, 0)
        
        pdf.cell(w[8], row_h, sanitizar_texto(row["pontuacao"]), 1, 0, "C", True)
        
        if str(row["porcentagem"]) == "100%":
            pdf.set_font("helvetica", "B", 7)
            pdf.set_text_color(0, 100, 0)
        pdf.cell(w[9], row_h, sanitizar_texto(row["porcentagem"]), 1, 0, "C", True)
        pdf.set_font("helvetica", "", 7)
        pdf.set_text_color(0, 0, 0)
        
        if "PREPARADO" in st_raw and "NAO" not in st_raw and "NÃO" not in st_raw:
            pdf.set_fill_color(198, 239, 206); pdf.set_text_color(0, 97, 0)
        elif "ATENCAO" in st_raw or "ATENÇÃO" in st_raw:
            pdf.set_fill_color(255, 235, 156); pdf.set_text_color(156, 101, 0)
        else:
            pdf.set_fill_color(255, 199, 206); pdf.set_text_color(156, 0, 6)
            
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
    if "PREPARADO" in status_txt and "NÃO" not in status_txt and "NAO" not in status_txt:
        pdf.set_text_color(86, 211, 100)
    elif "ATENÇÃO" in status_txt or "ATENCAO" in status_txt:
        pdf.set_text_color(227, 179, 65)
    else:
        pdf.set_text_color(248, 81, 73)
    pdf.cell(0, 7, f"Status de Preparacao: {status_txt}", 0, 1, "L")
    return pdf_para_bytes(pdf)

# ==========================================
# PDF DE TÁTICAS (CORRIGIDO E BLINDADO)
# ==========================================
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
        if not player_name or player_name not in player_classes:
            return (255, 255, 255) 
        c = player_classes[player_name]
        cores = {
            "Guerreiro": (198, 155, 109),
            "Paladino": (244, 140, 186),
            "Caçador": (171, 212, 115),
            "Ladino": (255, 244, 104),
            "Sacerdote": (255, 255, 255),
            "Mago": (63, 199, 235),
            "Bruxo": (148, 130, 201),
            "Xamã": (0, 112, 222),
            "Druida": (255, 124, 10)
        }
        return cores.get(c, (255, 255, 255))

    row_h = 7
    icon_sz = 6
    
    def desenhar_cabecalho(texto, start_x, larg_total):
        pdf.set_xy(start_x, pdf.get_y())
        pdf.set_font("helvetica", "B", 12)
        pdf.set_fill_color(11, 77, 140) 
        pdf.set_text_color(255, 255, 255)
        pdf.cell(larg_total, 8, texto, 1, 1, "C", True)

    def desenhar_linha(items, start_x):
        pdf.set_xy(start_x, pdf.get_y())
        start_y = pdf.get_y()
        x_atual = start_x
        
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.5)
        pdf.set_font("helvetica", "B", 10)
        
        for (tipo, val, larg, extra) in items:
            if tipo == "img":
                pdf.set_fill_color(150, 150, 150) 
                pdf.rect(x_atual, start_y, larg, row_h, "DF")
                if val:
                    caminho = garantir_icone_local(val, "tatica")
                    if caminho and os.path.exists(caminho):
                        try:
                            img_x = x_atual + (larg / 2) - (icon_sz / 2)
                            img_y = start_y + (row_h / 2) - (icon_sz / 2)
                            pdf.image(caminho, x=img_x, y=img_y, w=icon_sz, h=icon_sz)
                        except Exception:
                            pass
            elif tipo == "txt":
                if extra == "player" and val:
                    r, g, b = get_class_color(val)
                    pdf.set_fill_color(r, g, b)
                    pdf.set_text_color(0, 0, 0) 
                elif extra == "group" and val:
                    pdf.set_fill_color(200, 200, 200) 
                    pdf.set_text_color(0, 0, 0)
                else:
                    pdf.set_fill_color(255, 255, 255)
                    pdf.set_text_color(0, 0, 0)
                
                pdf.set_xy(x_atual, start_y)
                safe_val = sanitizar_texto(val) 
                pdf.cell(larg, row_h, safe_val, 1, 0, "C", True)
                
            x_atual += larg
        pdf.set_xy(start_x, start_y + row_h)

    # 1. BUFFS
    linhas_buffs = []
    for r in range(1, 10):
        b1 = dados.get(f"b_r{r}_0", "")
        b2 = dados.get(f"b_r{r}_1", "")
        grp = dados.get(f"b_r{r}_2", "")
        p1 = dados.get(f"b_r{r}_3", "")
        atr = dados.get(f"b_r{r}_4", "")
        p2 = dados.get(f"b_r{r}_5", "")
        b3 = dados.get(f"b_r{r}_6", "")
        if b1 or b2 or grp or p1 or atr or p2 or b3:
            linhas_buffs.append([
                ("img", b1, 8, None), ("img", b2, 8, None), ("txt", grp, 16, "group"),
                ("txt", p1, 45, "player"), ("img", atr, 8, None), ("txt", p2, 45, "player"), ("img", b3, 8, None)
            ])
    
    largura_buffs = 8+8+16+45+8+45+8 
    start_x_buffs = (210 - largura_buffs) / 2
    
    if linhas_buffs:
        desenhar_cabecalho("Buffs and Assignments", start_x_buffs, largura_buffs)
        for l in linhas_buffs:
            desenhar_linha(l, start_x_buffs)
        pdf.ln(8)

    # 2. TANKS
    linhas_tanks = []
    for r in range(1, 7):
        b1 = dados.get(f"t_r{r}_0", "")
        b2 = dados.get(f"t_r{r}_1", "")
        p1 = dados.get(f"t_r{r}_2", "")
        p2 = dados.get(f"t_r{r}_3", "")
        mald = dados.get(f"t_r{r}_4", "")
        p3 = dados.get(f"t_r{r}_5", "")
        b3 = dados.get(f"t_r{r}_6", "")
        if b1 or b2 or p1 or p2 or mald or p3 or b3:
            linhas_tanks.append([
                ("img", b1, 8, None), ("img", b2, 8, None), ("txt", p1, 35, "player"), 
                ("txt", p2, 35, "player"), ("img", mald, 8, None), ("txt", p3, 35, "player"), ("img", b3, 8, None)
            ])
    
    largura_tanks = 8+8+35+35+8+35+8 
    start_x_tanks = (210 - largura_tanks) / 2
    
    if linhas_tanks:
        desenhar_cabecalho("Tanks, Sheep & Debuffs", start_x_tanks, largura_tanks)
        for l in linhas_tanks:
            desenhar_linha(l, start_x_tanks)
        pdf.ln(8)

    # 3. MD TRASH
    linhas_md = []
    for r in range(1, 3):
        ic = dados.get(f"m_r{r}_0", "")
        p1 = dados.get(f"m_r{r}_1", "")
        g1 = dados.get(f"m_r{r}_2", "")
        g2 = dados.get(f"m_r{r}_3", "")
        if ic or p1 or g1 or g2:
            linhas_md.append([
                ("img", ic, 10, None), ("txt", p1, 40, "player"), ("txt", g1, 40, "group"), ("txt", g2, 40, "group")
            ])
            
    largura_md = 10+40+40+40 
    start_x_md = (210 - largura_md) / 2
    
    if linhas_md:
        desenhar_cabecalho("MD Trash - Boss + Trash", start_x_md, largura_md)
        for l in linhas_md:
            desenhar_linha(l, start_x_md)

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
# ABA 1: DASHBOARD COM GRÁFICO DE PIZZA E RANKING COM ROLAGEM INTERNA
# ==========================================
with tab1:
    st.subheader("📊 Visão Geral da Guilda e Desempenho")
    
    conn = sqlite3.connect("guilda_database.db")
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

    # --- MÉTRICAS DO TOPO ---
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        st.metric("Total de Membros", total_membros)
    with c_m2:
        st.metric("Raids Registradas", total_raides)
    with c_m3:
        st.metric("Prep. Média da Guilda", prep_media)
        
    st.markdown("---")

    if df_hist.empty:
        st.info("ℹ️ Ainda não há dados de raides suficientes para gerar os gráficos. Registre uma nova raide na Aba 3!")
    else:
        # ==========================================
        # LINHA 1: GRÁFICO DE PIZZA (PRESENÇA) LADO A LADO COM O RANKING (ROLAGEM INTERNA)
        # ==========================================
        c_pizza, c_rank = st.columns(2)
        
       # ==========================================
        # LINHA 1: GRÁFICO DE PIZZA (PRESENÇA) LADO A LADO COM O RANKING (ROLAGEM INTERNA)
        # ==========================================
        c_pizza, c_rank = st.columns(2)
        
        with c_pizza:
            st.markdown("### 🥧 Proporção de Presença nas Raids")
            st.caption("Distribuição geral de comparência (Presentes vs Ausentes/Faltas).")
            
            # Prepara dados para o gráfico de pizza/rosca
            df_hist["status_presenca"] = df_hist["presenca"].apply(lambda x: "Presente" if "1" in str(x) else "Ausente")
            df_pie = df_hist["status_presenca"].value_counts().reset_index()
            df_pie.columns = ["Status", "Quantidade"]
            
            import altair as alt
            pie_chart = alt.Chart(df_pie).mark_arc(innerRadius=60).encode(
                theta=alt.Theta(field="Quantidade", type="quantitative"),
                color=alt.Color(field="Status", type="nominal", scale=alt.Scale(domain=["Presente", "Ausente"], range=["#238636", "#da3633"])),
                tooltip=["Status", "Quantidade"]
            ).properties(height=200)
            
            st.altair_chart(pie_chart, use_container_width=True)
            
            # Seletor rápido e blindado para exibir os nomes instantaneamente
            status_filtro = st.radio("🔍 Ver lista de:", ["Nenhum", "Presente", "Ausente"], horizontal=True, key="filtro_status_pizza")
            
            if status_filtro != "Nenhum":
                df_filtrado = df_hist[df_hist["status_presenca"] == status_filtro][["data_registro", "nome_raide", "jogador"]].drop_duplicates()
                if not df_filtrado.empty:
                    df_exibicao = df_filtrado.rename(columns={"data_registro": "Data/Horário", "nome_raide": "Raide", "jogador": "Jogador"})
                    st.dataframe(df_exibicao, use_container_width=True, hide_index=True, height=130)
                else:
                    st.info("Nenhum registro encontrado.")
            
        with c_rank:
            st.markdown("### 🏆 Ranking Histórico de Preparação")
            st.caption("Média histórica de preparação por jogador.")
            
            df_ranking = df_hist.groupby(["jogador", "classe"])["pct_num"].mean().reset_index()
            df_ranking = df_ranking.sort_values(by="pct_num", ascending=False).reset_index(drop=True)
            
            ranking_formatado = []
            for _, row in df_ranking.iterrows():
                classe_nome = str(row["classe"]) if pd.notna(row["classe"]) else "-"
                _ = ranking_formatado.append({
                    "Jogador": row["jogador"],
                    "Classe": html_classe(classe_nome, 20),
                    "Média": f"{row['pct_num']:.1f}%"
                })
                
            df_final_rank = pd.DataFrame(ranking_formatado)
            tabela_rank_html = df_final_rank.to_html(escape=False, index=False)
            tabela_rank_html = tabela_rank_html.replace('<table', '<table style="width: 100%; text-align: left; border-collapse: collapse;"')
            
            # Caixa com altura fixa e rolagem interna ativada (Overflow Y)
            st.markdown(f"""
                <div style="height: 330px; overflow-y: auto; border: 1px solid #30363d; border-radius: 6px; padding: 4px; background-color: #0d1117;">
                    {tabela_rank_html}
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # ==========================================
        # LINHA 2: GRÁFICOS DE DESEMPENHO POR INSTÂNCIA E INDIVIDUAL
        # ==========================================
        c_g1, c_g2 = st.columns(2)
        
        with c_g1:
            st.markdown("### 🏰 Desempenho por Instância")
            st.caption("Comparativo da média de pontos obtidos em cada tipo de raide.")
            
            df_raide_perf = df_hist.groupby("nome_raide")["pontuacao"].mean().reset_index()
            df_raide_perf = df_raide_perf.rename(columns={"nome_raide": "Raide", "pontuacao": "Média de Pontos"})
            df_raide_perf = df_raide_perf.set_index("Raide")
            
            st.bar_chart(df_raide_perf, color="#1f6feb")
            
        with c_g2:
            st.markdown("### 👤 Histórico Individual por Jogador")
            st.caption("Acompanhe a evolução de preparação de um membro específico.")
            
            lista_jogadores_hist = sorted(df_hist["jogador"].unique().tolist())
            jogador_selecionado = st.selectbox("Selecione o Jogador", lista_jogadores_hist, key="dash_jogador_sel")
            
            df_jogador = df_hist[df_hist["jogador"] == jogador_selecionado].copy()
            if not df_jogador.empty:
                df_jogador = df_jogador[["data_registro", "pontuacao"]].rename(columns={"data_registro": "Raide", "pontuacao": "Pontos"})
                df_jogador = df_jogador.set_index("Raide")
                st.line_chart(df_jogador, color="#238636")
            else:
                st.info("Sem registros para este jogador.")

        st.markdown("---")
        
# ==========================================
# ABA 1: DASHBOARD UNIFICADO (PIZZA + RANKING + AUSÊNCIAS + CONSUMÍVEIS)
# ==========================================
with tab1:
    st.subheader("📊 Visão Geral da Guilda e Desempenho")
    
    conn = sqlite3.connect("guilda_database.db")
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

    # --- MÉTRICAS DO TOPO ---
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        st.metric("Total de Membros", total_membros)
    with c_m2:
        st.metric("Raides Registradas", total_raides)
    with c_m3:
        st.metric("Prep. Média da Guilda", prep_media)
        
    st.markdown("---")

    if df_hist.empty:
        st.info("ℹ️ Ainda não há dados de raides suficientes para gerar os gráficos. Registre uma nova raide na Aba 3!")
    else:
        # ==========================================
        # LINHA 1: GRÁFICO DE PIZZA (PRESENÇA) + RANKING COM ROLAGEM
        # ==========================================
        c_pizza, c_rank = st.columns(2)
        
        with c_pizza:
            st.markdown("### 🥧 Proporção de Presença nas Raids")
            st.caption("Distribuição geral de comparência (Presentes vs Ausentes/Faltas).")
            
            df_hist["status_presenca"] = df_hist["presenca"].apply(lambda x: "Presente" if "1" in str(x) else "Ausente")
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
                    df_exibicao = df_filtrado.rename(columns={"data_registro": "Data/Horário", "nome_raide": "Raide", "jogador": "Jogador"})
                    st.dataframe(df_exibicao, use_container_width=True, hide_index=True, height=130)
                else:
                    st.info("Nenhum registro encontrado.")
            
        with c_rank:
            st.markdown("### 🏆 Ranking Histórico de Preparação")
            st.caption("Média histórica de preparação por jogador.")
            
            df_ranking = df_hist.groupby(["jogador", "classe"])["pct_num"].mean().reset_index()
            df_ranking = df_ranking.sort_values(by="pct_num", ascending=False).reset_index(drop=True)
            
            ranking_formatado = []
            for _, row in df_ranking.iterrows():
                classe_nome = str(row["classe"]) if pd.notna(row["classe"]) else "-"
                _ = ranking_formatado.append({
                    "Jogador": row["jogador"],
                    "Classe": html_classe(classe_nome, 20),
                    "Média": f"{row['pct_num']:.1f}%"
                })
                
            df_final_rank = pd.DataFrame(ranking_formatado)
            tabela_rank_html = df_final_rank.to_html(escape=False, index=False)
            tabela_rank_html = tabela_rank_html.replace('<table', '<table style="width: 100%; text-align: left; border-collapse: collapse;"')
            
            st.markdown(f"""
                <div style="height: 330px; overflow-y: auto; border: 1px solid #30363d; border-radius: 6px; padding: 4px; background-color: #0d1117;">
                    {tabela_rank_html}
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # ==========================================
        # LINHA 2: ENCANTAMENTOS AUSENTES VS MÉDIA DE FLASKS/COMIDA
        # ==========================================
        c_g1, c_g2 = st.columns(2)
        
        with c_g1:
            st.markdown("### ⚠️ Encantamentos Mais Ausentes (Geral)")
            st.caption("Quais partes de equipamento o core mais esquece de encantar.")
            
            todos_ausentes = []
            for aus in df_hist["ausentes"].dropna():
                if aus and aus != "-":
                    itens = [item.strip() for item in str(aus).split(",")]
                    for item in itens:
                        if item and item != "-":
                            todos_ausentes.append(item)
                            
            if todos_ausentes:
                df_aus_count = pd.DataFrame(todos_ausentes, columns=["Encantamento"]).value_counts().reset_index()
                df_aus_count.columns = ["Encantamento", "Total Ausências"]
                df_aus_count = df_aus_count.set_index("Encantamento")
                st.bar_chart(df_aus_count, height=260, color="#da3633")
            else:
                st.success("🎉 Nenhum encantamento ausente registrado nas raides até o momento!")
            
        with c_g2:
            st.markdown("### 🧪 Média de Flasks e Comida por Raide")
            st.caption("Acompanhamento da regularidade de consumíveis por sessão.")
            
            def extrair_num(val):
                try:
                    return float(str(val).split("/")[0])
                except:
                    return 0.0
                    
            df_hist_cons = df_hist.copy()
            df_hist_cons["flask_num"] = df_hist_cons["flask"].apply(extrair_num)
            df_hist_cons["comida_num"] = df_hist_cons["comida"].apply(extrair_num)
            
            df_consumo = df_hist_cons.groupby("data_registro")[["flask_num", "comida_num"]].mean().reset_index()
            df_consumo = df_consumo.rename(columns={"data_registro": "Raide/Data", "flask_num": "Flasks", "comida_num": "Comida"})
            df_consumo = df_consumo.set_index("Raide/Data")
            
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
                        conn = sqlite3.connect("guilda_database.db")
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO membros (nome, classe, funcao) VALUES (?, ?, ?)", (novo_nome, nova_classe, nova_funcao))
                        conn.commit()
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
                        conn = sqlite3.connect("guilda_database.db")
                        cursor = conn.cursor()
                        cursor.execute("UPDATE membros SET nome=?, classe=?, funcao=? WHERE id=?", (e_nome, e_classe, e_funcao, row["id"]))
                        conn.commit()
                        conn.close()
                        st.success("Atualizado!")
                        st.rerun()
        if c_del.button("🗑️ Excluir", key=f"del_{row['id']}"):
            conn = sqlite3.connect("guilda_database.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM membros WHERE id=?", (row["id"],))
            conn.commit()
            conn.close()
            st.rerun()

# ==========================================
# ABA 3: NOVA RAIDE (COM BLINDAGEM DE SESSÃO)
# ==========================================
with tab3:
    st.subheader("⚔️ Registrar Nova Raid")

    if "etapa_raide" not in st.session_state:
        st.session_state.etapa_raide = 1

    # 🛡️ BLINDAGEM DE SEGURANÇA: Se a sessão resetar, volta pra etapa 1 em vez de dar erro
    if st.session_state.etapa_raide == 2 and not all(k in st.session_state for k in ["raide_data_base", "raide_nome", "raide_jogadores", "raide_bosses"]):
        st.session_state.etapa_raide = 1
        st.rerun()

    def resetar_raide():
        st.session_state.etapa_raide = 1

    # ==========================================
    # ETAPA 1: DEFINIR DIA, HORA DE INÍCIO E CORE
    # ==========================================
    if st.session_state.etapa_raide == 1:
        st.markdown("### 1️⃣ Seleção do Core e Horário de Início")
        
        c_data, c_inicio, c_raide = st.columns(3)
        
        with c_data:
            data_input = st.date_input("Data da Raid", datetime.today())
        with c_inicio:
            hora_inicio = st.time_input("Horário de Início", datetime.strptime("20:00", "%H:%M").time())
        with c_raide:
            raide_input = st.selectbox("Qual Raid ?", LISTA_RAIDES)
            
        membros_df = obter_membros()
        todos_jogadores = membros_df["nome"].tolist() if not membros_df.empty else []
        
        jogadores_selecionados = st.multiselect(
            "Selecione quem vai participar (Os não selecionados não aparecerão na tabela):", 
            todos_jogadores, 
            default=todos_jogadores
        )
        
        if st.button("🚀 Confirmar Core e Gerar Tabela", type="primary", use_container_width=True):
            if not jogadores_selecionados:
                st.warning("⚠️ Selecione pelo menos um jogador para prosseguir!")
            else:
                st.session_state.raide_data_base = data_input.strftime('%d/%m/%Y')
                st.session_state.raide_hora_inicio = hora_inicio.strftime('%H:%M')
                st.session_state.raide_nome = raide_input
                st.session_state.raide_jogadores = jogadores_selecionados
                st.session_state.raide_bosses = QTD_BOSSES[raide_input]
                st.session_state.etapa_raide = 2
                st.rerun()

   # ==========================================
    # ETAPA 2: PREENCHIMENTO REATIVO (TODOS MARCADOS POR PADRÃO)
    # ==========================================
    elif st.session_state.etapa_raide == 2:
        boss_total = st.session_state.raide_bosses
        st.markdown(f"### 2️⃣ Preenchimento: {st.session_state.raide_nome} ({st.session_state.raide_data_base}) — Total de Bosses: {boss_total}")
        st.info("Todos iniciam como presentes. Desmarque os ausentes para zerar e bloquear a linha. 0 ausências = **+5 pontos de Bônus (Total: 45 Pontos)**.")
        
        st.button("🔙 Voltar para a Seleção de Jogadores", on_click=resetar_raide)
        st.markdown("---")
        
        opcoes_boss = [f"{i}/{boss_total}" for i in range(boss_total, -1, -1)]
        opcoes_flask_comida = [f"{i}/10" for i in range(10, -1, -1)]
        
        membros_df = obter_membros()
        player_classes = dict(zip(membros_df["nome"], membros_df["classe"])) if not membros_df.empty else {}
        
        resultados_inputs = {}
        
        c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1, 1.2, 1.2, 1.2, 2.5])
        c1.write("**Jogador / Classe**")
        c2.write("**Pres.**")
        c3.write("**Bosses**")
        c4.write("**Flasks**")
        c5.write("**Comida**")
        c6.write("**Encantamentos Ausentes**")
        
        for jogador in st.session_state.raide_jogadores:
            classe_jogador = player_classes.get(jogador, "-")
            
            c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1, 1.2, 1.2, 1.2, 2.5])
            
            with c1:
                html_info = f"<div style='font-weight:bold; font-size:14px; margin-bottom:2px;'>{jogador}</div>" + html_classe(classe_jogador, 18)
                st.markdown(html_info, unsafe_allow_html=True)
                
            with c2:
                # Marcado como True por padrão
                pres = st.checkbox("", value=True, key=f"pres_{jogador}")
                
            is_disabled = not pres
            
            with c3:
                boss_sel = st.selectbox("", opcoes_boss, index=0, key=f"boss_{jogador}", disabled=is_disabled, label_visibility="collapsed")
            with c4:
                flask_sel = st.selectbox("", opcoes_flask_comida, index=0, key=f"flask_{jogador}", disabled=is_disabled, label_visibility="collapsed")
            with c5:
                comida_sel = st.selectbox("", opcoes_flask_comida, index=0, key=f"comida_{jogador}", disabled=is_disabled, label_visibility="collapsed")
            with c6:
                encants = st.multiselect("", LISTA_ENCANTAMENTOS, key=f"encant_{jogador}", disabled=is_disabled, label_visibility="collapsed")
            
            resultados_inputs[jogador] = {
                "pres": pres, 
                "boss": boss_sel, 
                "flask": flask_sel, 
                "comida": comida_sel, 
                "encants": encants,
                "classe": classe_jogador
            }
            
        st.markdown("---")
        salvar_btn = st.button("💾 Encerrar Raid e Salvar Relatório", type="primary", use_container_width=True)
        
        if salvar_btn:
            hora_fim_automatica = datetime.now().strftime('%H:%M')
            data_final_completa = f"{st.session_state.raide_data_base} ({st.session_state.raide_hora_inicio} - {hora_fim_automatica})"
            
            conn = sqlite3.connect("guilda_database.db")
            cursor = conn.cursor()
            
            for jogador, dados in resultados_inputs.items():
                pres_val = 1 if dados["pres"] else 0
                
                if pres_val == 0:
                    total_pontos = 0
                    porcentagem = "0%"
                    status = "NÃO PREPARADO"
                    str_boss = f"0/{boss_total}"
                    str_flask = "0/10"
                    str_comida = "0/10"
                    str_ausentes = "-"
                else:
                    boss_val = int(dados["boss"].split("/")[0])
                    flask_val = int(dados["flask"].split("/")[0])
                    comida_val = int(dados["comida"].split("/")[0])
                    qtd_ausentes = len(dados["encants"])
                    
                    p_boss = (boss_val / boss_total) * 10
                    p_flask = (flask_val / 10) * 10
                    p_comida = (comida_val / 10) * 10
                    p_encant = max(0, 10 - (qtd_ausentes * 2))
                    
                    total_pontos = p_boss + p_flask + p_comida + p_encant
                    
                    if qtd_ausentes == 0:
                        total_pontos += 5 
                        
                    total_pontos = round(total_pontos)
                    pct = (total_pontos / 45) * 100
                    porcentagem = f"{int(pct)}%"
                    
                    if pct == 100: status = "PREPARADO"
                    elif pct >= 50: status = "ATENÇÃO"
                    else: status = "NÃO PREPARADO"
                    
                    str_ausentes = ", ".join(dados["encants"]) if qtd_ausentes > 0 else "-"
                    str_boss = dados['boss']
                    str_flask = dados['flask']
                    str_comida = dados['comida']
                    
                str_presenca = f"{pres_val}/1"
                
                cursor.execute('''
                    INSERT INTO historico_raides (data_registro, nome_raide, jogador, classe, boss, flask, comida, presenca, ausentes, pontuacao, porcentagem, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (data_final_completa, st.session_state.raide_nome, jogador, dados["classe"], 
                      str_boss, str_flask, str_comida, str_presenca, str_ausentes, total_pontos, porcentagem, status))
                      
            conn.commit()
            conn.close()
            
            st.session_state.etapa_raide = 1
            st.success(f"✅ Raid salva com sucesso! Encerrada às {hora_fim_automatica}.")
            st.balloons()
# ==========================================
# ABA 4: RELATÓRIOS (COM OPÇÃO DE EXCLUSÃO PROTEGIDA POR SENHA)
# ==========================================
with tab4:
    st.subheader("📊 Relatórios e Histórico de Raids")
    
    conn = sqlite3.connect("guilda_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT data_registro, nome_raide FROM historico_raides ORDER BY id DESC")
    raides_salvas = cursor.fetchall()
    conn.close()

    if not raides_salvas:
        st.info("Nenhuma raide registrada.")
    else:
        escolha = st.selectbox("Selecione a Raid no Histórico", [f"{d} | {n}" for d, n in raides_salvas])
        data_sel, nome_sel = escolha.split(" | ", 1)
        
        st.markdown(f"**Raide selecionada:** `{nome_sel}` — **Horário/Data:** `{data_sel}`")
        
        # --- BOTÃO DE EXCLUSÃO PROTEGIDO POR SENHA ---
        with st.expander("⚙️ Gerenciar Raid (Excluir do Histórico)"):
            st.warning("⚠️ Atenção: A exclusão é permanente e apagará todos os dados desta sessão de raid.")
            senha_input = st.text_input("Digite a senha de administrador:", type="password", key=f"senha_exc_{data_sel}_{nome_sel}")
            
            if st.button("🚨 Confirmar Exclusão Permanente", key=f"btn_exc_{data_sel}_{nome_sel}", type="primary"):
                # Defina a sua senha aqui ("renegados" por padrão)
                if senha_input == "Renegados2026":
                    conn = sqlite3.connect("guilda_database.db")
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM historico_raides WHERE data_registro = ? AND nome_raide = ?", (data_sel, nome_sel))
                    conn.commit()
                    conn.close()
                    st.success("✅ Raid excluída com sucesso do histórico!")
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta! A exclusão foi cancelada.")
                    
        st.markdown("---")
        
        conn = sqlite3.connect("guilda_database.db")
        df = pd.read_sql("""
            SELECT jogador, classe, boss, flask, comida, presenca, ausentes, pontuacao, porcentagem, status 
            FROM historico_raides WHERE data_registro=? AND nome_raide=?
        """, conn, params=(data_sel, nome_sel))
        conn.close()

        df = df.fillna("-")

        # --- 1. MÉTRICAS NO TOPO ---
        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1:
            st.metric("🟢 Preparados", len(df[df["status"] == "PREPARADO"]))
        with c_m2:
            st.metric("🟡 Atenção", len(df[df["status"] == "ATENÇÃO"]))
        with c_m3:
            st.metric("🔴 Não Preparados", len(df[df["status"] == "NÃO PREPARADO"]))
        
        st.markdown("---")
        
        # --- 2. TABELA EM TELA CHEIA ---
        relatorio_formatado = []
        for _, row in df.iterrows():
            classe_nome = str(row["classe"]) if pd.notna(row["classe"]) else "-"
            
            # --- LÓGICA DA ESTRELA DE BÔNUS ---
            jogador_nome = row["jogador"]
            if str(row["porcentagem"]) == "100%":
                jogador_nome = f"⭐ {jogador_nome}"
            
            # --- LÓGICA DO STATUS (Bolinhas) ---
            status_txt = str(row["status"])
            if "PREPARADO" in status_txt and "NÃO" not in status_txt:
                status_html = f"<span style='color: #4CAF50; font-weight: bold;'>🟢 {status_txt}</span>"
            elif "ATENÇÃO" in status_txt:
                status_html = f"<span style='color: #FFC107; font-weight: bold;'>🟡 {status_txt}</span>"
            else:
                status_html = f"<span style='color: #F44336; font-weight: bold;'>🔴 {status_txt}</span>"
            
            _ = relatorio_formatado.append({
                "Jogador": jogador_nome,
                "Classe": html_classe(classe_nome, 20),
                "Boss": row["boss"],
                "Flask": row["flask"],
                "Comida": row["comida"],
                "Pres.": row["presenca"],
                "Ausências de Magías": row["ausentes"],
                "Pts": row["pontuacao"],
                "Média": row["porcentagem"],
                "Status": status_html
            })
            
        df_final_rel = pd.DataFrame(relatorio_formatado)
        
        # --- PINTAR LINHA INTEIRA DE VERMELHO SE NÃO PREPARADO ---
        def destacar_nao_preparados(row):
            if '🔴' in str(row['Status']):
                return ['background-color: rgba(244, 67, 54, 0.15); border-bottom: 1px solid #F44336;'] * len(row)
            return [''] * len(row)
            
        # O Pandas aplica o estilo de linha antes de converter para HTML
        tabela_html = df_final_rel.style.apply(destacar_nao_preparados, axis=1).hide(axis="index").to_html(escape=False)
        
        tabela_html = tabela_html.replace('<table', '<table style="width: 100%; text-align: left; border-collapse: collapse;"')
        st.markdown(tabela_html, unsafe_allow_html=True)
        
        st.markdown("---")
        
       # --- 3. BARRA DE COMANDOS NA PARTE INFERIOR ---
        c_btn1, c_sel, c_btn2 = st.columns([1, 1, 1])
        
        with c_btn1:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            pdf_geral_bytes = gerar_pdf_geral(nome_sel, data_sel, df)
            st.download_button(
                "📥 Baixar Relatório Geral (Dashboard PDF)", 
                data=pdf_geral_bytes, 
                file_name=f"Relatorio_{nome_sel.replace(' ', '_')}.pdf", 
                mime="application/pdf", 
                use_container_width=True
            )
            
        jogadores_lista = df["jogador"].tolist()
        
        with c_sel:
            jogador_escolhido = st.selectbox("Selecionar Jogador (Para PDF Individual)", jogadores_lista) if jogadores_lista else None
                
        with c_btn2:
            if jogador_escolhido:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                linha_jogador = df[df["jogador"] == jogador_escolhido].iloc[0]
                pdf_indiv_bytes = gerar_pdf_individual(nome_sel, data_sel, linha_jogador)
                st.download_button(
                    f"📥 Baixar PDF Individual ({jogador_escolhido})", 
                    data=pdf_indiv_bytes, 
                    file_name=f"Desempenho_{jogador_escolhido}.pdf", 
                    mime="application/pdf", 
                    use_container_width=True
                )
# ==========================================
# FUNÇÃO DINÂMICA DAS TÁTICAS 
# ==========================================
# ==========================================
# FUNÇÃO DINÂMICA DAS TÁTICAS 
# ==========================================
def draw_dynamic_row(key_prefix, c_sizes, defaults, list_players, dados_tatica, icon_options_dict):
    cols = st.columns(c_sizes)
    for i in range(len(c_sizes)):
        with cols[i]:
            key = f"{key_prefix}_{i}"
            
            is_icon_col = False
            if key_prefix.startswith(("b_", "t_")) and i in [0, 1, 4, 6]:
                is_icon_col = True
            elif key_prefix.startswith("m_") and i == 0:
                is_icon_col = True

            if is_icon_col:
                idx_default = list(icon_options_dict.values()).index(defaults[i]) if defaults[i] in icon_options_dict.values() else 0
                escolha = st.selectbox("", list(icon_options_dict.keys()), index=idx_default, key=key, label_visibility="collapsed")
                img_key = icon_options_dict[escolha]
                dados_tatica[key] = img_key

                if img_key:
                    img_b64 = obter_icone_base64(img_key, tipo="tatica")
                    st.markdown(f'<div style="display:flex; justify-content:center; height:38px;"><img src="{img_b64}" width="36" height="36" style="border:1px solid #555; border-radius:4px;"></div>', unsafe_allow_html=True)
                else:
                    st.markdown("<div style='height:38px;'></div>", unsafe_allow_html=True)
            elif key_prefix.startswith("b_") and i == 2:
                idx_default = OPCOES_GRUPOS.index(defaults[i]) if defaults[i] in OPCOES_GRUPOS else 0
                escolha = st.selectbox("", OPCOES_GRUPOS, index=idx_default, key=key, label_visibility="collapsed")
                dados_tatica[key] = escolha
            elif key_prefix.startswith("m_") and i in [2, 3]:
                idx_default = OPCOES_GRUPOS.index(defaults[i]) if defaults[i] in OPCOES_GRUPOS else 0
                escolha = st.selectbox("", OPCOES_GRUPOS, index=idx_default, key=key, label_visibility="collapsed")
                dados_tatica[key] = escolha
            else:
                idx_default = list_players.index(defaults[i]) if defaults[i] in list_players else 0
                escolha = st.selectbox("", list_players, index=idx_default, key=key, label_visibility="collapsed")
                dados_tatica[key] = escolha
    return "" # ISSO AQUI MATA O "NONE" VERDE DA TELA

# ==========================================
# ABA 5: TÁTICAS E BUFFS
# ==========================================
with tab5:
    membros_df = obter_membros()
    opcoes_players = [""] + membros_df["nome"].tolist() if not membros_df.empty else ["Nenhum jogador"]
    
    # Criamos um dicionário para a função do PDF saber qual cor pintar!
    player_classes = dict(zip(membros_df["nome"], membros_df["classe"]))
    
    dados_tatica = {}

    st.markdown('<div class="tatica-header">🔮 Buffs and Assignments</div>', unsafe_allow_html=True)
    c_sizes_buffs = [1.2, 1.2, 1.5, 3.5, 1.2, 3.5, 1.2]
    defaults_buffs = [
        ["sombra", "vigor", "1-2-3", "", "mage_icon", "", ""],
        ["sombra", "vigor", "4-5", "", "mage_icon", "", ""],
        ["", "esp", "1 a 5", "", "mage_icon", "", ""],
        ["curse_pink", "", "1 a 5", "", "raio", "", ""],
        ["", "", "", "", "raio", "", ""],
        ["", "", "", "", "raio", "", ""],
        ["totem_azul", "", "1-2", "", "kings", "", "wisdom"],
        ["totem_azul", "", "3-4", "", "kings", "", "might"],
        ["totem_azul", "", "5", "", "kings", "", "salv"]
    ]
    for r, default in enumerate(defaults_buffs):
        draw_dynamic_row(f"b_r{r+1}", c_sizes_buffs, default, opcoes_players, dados_tatica, icon_options_dict=OPCOES_ICONES_BUFFS)
        if r in [2, 5]: st.markdown('<hr style="border-color:#333; margin-top:8px; margin-bottom:8px;">', unsafe_allow_html=True)

    st.markdown('<div class="tatica-header">🛡️ Tanks, Sheep & Debuffs</div>', unsafe_allow_html=True)
    c_sizes_tanks = [1.2, 1.2, 3.5, 3.5, 1.2, 3.5, 1.2]
    defaults_tanks = [
        ["caveira", "", "", "", "", "", ""],
        ["xis", "", "", "", "orb_roxo", "", ""],
        ["quadrado", "", "", "", "orb_roxo", "", ""],
        ["triangulo", "", "", "", "", "", ""],
        ["lua", "", "", "", "", "", ""],
        ["diamante", "", "", "", "", "", ""]
    ]
    for r, default in enumerate(defaults_tanks):
        draw_dynamic_row(f"t_r{r+1}", c_sizes_tanks, default, opcoes_players, dados_tatica, icon_options_dict=OPCOES_ICONES_COMBINED)

    st.markdown('<div class="tatica-header">🏹 MD Trash - Boss + Trash</div>', unsafe_allow_html=True)
    c_sizes_md = [1.2, 3.5, 3.5, 3.5]
    defaults_md = [
        ["caveira", "", "MAIN TANK", "TRASH + BOSS"],
        ["xis", "", "OFF TANK", "TRASH + BOSS"]
    ]
    for r, default in enumerate(defaults_md):
        draw_dynamic_row(f"m_r{r+1}", c_sizes_md, default, opcoes_players, dados_tatica, icon_options_dict=OPCOES_ICONES_TARGET_MARKS)

    st.markdown('<hr style="border-color:#333; margin-top:15px; margin-bottom:15px;">', unsafe_allow_html=True)
    st.download_button("📥 Gerar e Baixar PDF com Táticas de Boss", data=gerar_pdf_taticas(dados_tatica, player_classes), file_name=f"Taticas_Mata_Boss_{datetime.now().strftime('%d-%m-%Y')}.pdf", mime="application/pdf", type="primary", use_container_width=True)
