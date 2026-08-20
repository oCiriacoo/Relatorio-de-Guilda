import streamlit as st
import sqlite3
import os
import urllib.request
import pandas as pd
import base64
from datetime import datetime
from fpdf import FPDF

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
    "inner_fire": "https://wow.zamimg.com/images/wow/icons/medium/spell_holy_innerfire.jpg"
}

# SEGREGANDO OS ÍCONES
OPCOES_ICONES_BUFFS = {
    "Nenhum": "", "Sombra/Achilles": "sombra", "Vigor": "vigor", "Espírito": "esp", "Fogo Interior": "inner_fire",
    "Mago (Int)": "mage_icon", "Bruxo (Curse)": "curse_pink", "Bruxo (Orbe)": "orb_roxo", "Xamã (Raio)": "raio", 
    "Xamã (Totem)": "totem_azul", "Pala (Reis)": "kings", "Pala (Sabedoria)": "wisdom", "Pala (Poder)": "might", 
    "Pala (Salvação)": "salv", "Caçador (MD)": "md", "Mago (Sheep)": "sheep"
}

OPCOES_ICONES_TARGET_MARKS = {
    "Nenhum": "", "Caveira": "caveira", "Xis": "xis", "Quadrado": "quadrado", "Triângulo": "triangulo", "Lua": "lua", "Diamante": "diamante"
}

# Combinação total (usada no PDF e nos Tanks)
OPCOES_ICONES_COMBINED = {**OPCOES_ICONES_BUFFS, **OPCOES_ICONES_TARGET_MARKS}

OPCOES_GRUPOS = ["", "1", "2", "3", "4", "5", "1-2", "3-4", "4-5", "1-2-3", "1 a 5", "MAIN TANK", "OFF TANK", "TRASH + BOSS"]

QTD_BOSSES = {
    "Karazhan": 11, "Gruul's Lair": 2, "Magtheridon's Lair": 1, "Serpentshrine Cavern": 6, "The Eye (TK)": 4,
    "Mount Hyjal": 5, "Black Temple": 9, "Zul'Aman": 6, "Sunwell Plateau": 6, "Naxxramas": 15, "Sartharion (OS)": 1,
    "Malygos (EoE)": 1, "Ulduar": 14, "Icecrown Citadel": 12
}

LISTA_RAIDES = list(QTD_BOSSES.keys())
LISTA_ENCANTAMENTOS = ["🛡️ Ombros", "🧥 Capa", "👕 Peito", "💪 Braçadeiras", "🧤 Luvas", "👖 Calças", "👢 Botas", "⚔️ Arma principal", "🗡️ Arma secundária", "🛡️ Escudo", "🏹 Longo alcance"]

TRANSPARENT_B64 = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
PASTA_ICONES = "icones_web"
os.makedirs(PASTA_ICONES, exist_ok=True)

# ==========================================
# DOWNLOAD ROBUSTO DE ÍCONES (COM PROXY BLINDADO)
# ==========================================
def obter_url_icone(chave):
    if not chave: return ""
    if chave in CLASSES_WOW: return CLASSES_WOW[chave]["url"]
    if chave in ICONES_TATICAS: return ICONES_TATICAS[chave]
    return ""

def baixar_icone(chave, url):
    if not url: return None
    caminho = os.path.join(PASTA_ICONES, f"{chave}.jpg")
    
    if os.path.exists(caminho):
        if os.path.getsize(caminho) < 200:
            os.remove(caminho)
        else:
            with open(caminho, "rb") as f_check:
                head = f_check.read(30).lower()
                if b"<html" in head or b"<!doc" in head:
                    os.remove(caminho)
    
    if os.path.exists(caminho):
        return caminho

    tentativas = [
        f"https://api.allorigins.win/raw?url={url}",
        url
    ]

    for link in tentativas:
        try:
            req = urllib.request.Request(link, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            with urllib.request.urlopen(req, timeout=8) as resposta:
                conteudo = resposta.read()
                if len(conteudo) > 200 and b"<html" not in conteudo[:30].lower():
                    with open(caminho, "wb") as arquivo:
                        arquivo.write(conteudo)
                    return caminho
        except:
            continue
            
    return None

@st.cache_data(show_spinner=False)
def obter_icone_base64(chave):
    url = obter_url_icone(chave)
    if not url: return TRANSPARENT_B64
    
    caminho = baixar_icone(chave, url)
    
    if caminho and os.path.exists(caminho):
        try:
            with open(caminho, "rb") as arquivo:
                encoded = base64.b64encode(arquivo.read()).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded}"
        except Exception: pass
        
    return TRANSPARENT_B64

def html_classe(nome_classe, tamanho=24):
    dados = CLASSES_WOW.get(nome_classe)
    if not dados: return nome_classe
    cor = dados["cor"]
    img_b64 = obter_icone_base64(nome_classe)
    return f'<div style="display:flex;align-items:center;gap:8px;height:{tamanho + 4}px;"><img src="{img_b64}" width="{tamanho}" height="{tamanho}" style="border-radius:4px;object-fit:cover;flex-shrink:0;"><span style="color:{cor};font-weight:bold;">{nome_classe}</span></div>'

# ==========================================
# BANCO DE DADOS
# ==========================================
def conectar_banco():
    conn = sqlite3.connect("guilda_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_raides (
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
# GERADORES DE PDF
# ==========================================
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
    pdf = PDFCore()
    pdf.add_page()
    pdf.ln(32)
    pdf.set_font("helvetica", "B", 15)
    pdf.set_text_color(212, 175, 55)
    pdf.cell(0, 8, "CORE RENEGADOS - RELATORIO DE RAIDE", 0, 1, "C")
    pdf.set_font("helvetica", "I", 10)
    pdf.set_text_color(200, 200, 200)
    pdf.cell(0, 5, f"Raide: {nome_raide} | Data: {data_raide}", 0, 1, "C")
    pdf.ln(8)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(31, 111, 235)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(65, 8, "Jogador", 1, 0, "L", True)
    pdf.cell(45, 8, "Classe", 1, 0, "L", True)
    pdf.cell(35, 8, "Pontos", 1, 0, "C", True)
    pdf.cell(45, 8, "Status", 1, 1, "C", True)
    pdf.set_font("helvetica", "", 10)
    fill = False
    for _, row in df_resultados.iterrows():
        pdf.set_fill_color(33, 38, 45) if fill else pdf.set_fill_color(22, 27, 34)
        status_txt = str(row["status"])
        if "PREPARADO" in status_txt and "NÃO" not in status_txt: pdf.set_text_color(86, 211, 100)
        elif "ATENÇÃO" in status_txt: pdf.set_text_color(227, 179, 65)
        else: pdf.set_text_color(248, 81, 73)
        pdf.cell(65, 7, str(row["jogador"]), 1, 0, "L", True)
        pdf.cell(45, 7, str(row["classe"]), 1, 0, "L", True)
        pdf.set_text_color(240, 246, 252)
        pdf.cell(35, 7, f'{row["pontuacao"]} ({row["porcentagem"]})', 1, 0, "C", True)
        pdf.cell(45, 7, status_txt, 1, 1, "C", True)
        fill = not fill
    return bytes(pdf.output())

def gerar_pdf_individual(nome_raide, data_raide, row):
    pdf = PDFCore()
    pdf.add_page()
    pdf.ln(32)
    pdf.set_font("helvetica", "B", 15)
    pdf.set_text_color(212, 175, 55)
    pdf.cell(0, 8, "CORE RENEGADOS - DESEMPENHO INDIVIDUAL", 0, 1, "C")
    pdf.set_font("helvetica", "I", 10)
    pdf.set_text_color(200, 200, 200)
    pdf.cell(0, 5, f"Raide: {nome_raide} | Data: {data_raide}", 0, 1, "C")
    pdf.ln(12)
    pdf.set_fill_color(33, 38, 45)
    pdf.set_draw_color(212, 175, 55)
    pdf.rect(20, pdf.get_y(), 170, 55, "DF")
    pdf.set_xy(25, pdf.get_y() + 5)
    pdf.set_font("helvetica", "B", 13)
    pdf.set_text_color(212, 175, 55)
    pdf.cell(0, 8, f"Jogador: {row['jogador']}", 0, 1, "L")
    pdf.set_x(25)
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(240, 246, 252)
    pdf.cell(0, 7, f"Classe: {row['classe']}", 0, 1, "L")
    pdf.set_x(25)
    pdf.cell(0, 7, f"Pontuacao Final: {row['pontuacao']} pontos", 0, 1, "L")
    pdf.set_x(25)
    pdf.cell(0, 7, f"Aproveitamento Geral: {row['porcentagem']}", 0, 1, "L")
    pdf.set_x(25)
    status_txt = str(row["status"])
    if "PREPARADO" in status_txt and "NÃO" not in status_txt: pdf.set_text_color(86, 211, 100)
    elif "ATENÇÃO" in status_txt: pdf.set_text_color(227, 179, 65)
    else: pdf.set_text_color(248, 81, 73)
    pdf.cell(0, 7, f"Status de Preparacao: {status_txt}", 0, 1, "L")
    return bytes(pdf.output())

def get_icon_name(val):
    for k, v in OPCOES_ICONES_COMBINED.items():
        if v == val and k != "Nenhum": return k
    return ""


# ==========================================
# CABEÇALHO DA PÁGINA
# ==========================================
col_img, col_tit = st.columns([1, 8])
with col_img:
    if os.path.exists("logo_guilda.jpg"): st.image("logo_guilda.jpg", width=70)
    elif os.path.exists("logo_guilda.png"): st.image("logo_guilda.png", width=70)
with col_tit:
    st.markdown("<h1 style='color:#d4af37; margin-bottom:0px; padding-top:5px; font-size:26px;'>🛡️ CORE RENEGADOS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e; font-size:13px; margin-top:-5px;'>SISTEMA DE GESTÃO E PREPARAÇÃO DE RAIDE</p>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Dashboard", "👥 Gerenciar Jogadores", "⚔️ Nova Raide", "📊 Relatórios de Raide", "📝 Táticas e Buffs"])

# ==========================================
# ABA 1: DASHBOARD
# ==========================================
with tab1:
    st.subheader("📊 Visão Geral da Guilda")
    membros_df = obter_membros()
    conn = sqlite3.connect("guilda_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT data_registro || nome_raide) FROM historico_raides")
    total_raides = cursor.fetchone()[0] or 0
    cursor.execute("SELECT AVG(pontuacao) FROM historico_raides")
    media_pontos = cursor.fetchone()[0]
    media_geral = f"{(media_pontos / 32) * 100:.1f}%" if media_pontos else "0.0%"
    ranking_df = pd.read_sql("SELECT jogador, classe, AVG(pontuacao) AS media FROM historico_raides GROUP BY jogador ORDER BY media DESC", conn)
    conn.close()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Membros", len(membros_df))
    col2.metric("Raides Registradas", total_raides)
    col3.metric("Prep. Média da Guilda", media_geral)
    st.markdown("---")
    st.subheader("🏆 Ranking de Preparação dos Jogadores")

    if ranking_df.empty:
        st.info("Nenhum dado de raide registrado ainda.")
    else:
        ranking_formatado = []
        for _, row in ranking_df.iterrows():
            pct = (row["media"] / 32) * 100
            ranking_formatado.append({
                "Jogador": row["jogador"],
                "Classe": html_classe(row["classe"], 20),
                "Média Histórica": f"{pct:.1f}%"
            })
        df_rank_final = pd.DataFrame(ranking_formatado)
        st.markdown(df_rank_final.to_html(escape=False, index=False), unsafe_allow_html=True)

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

# =========================================================
# ABA 3 - NOVA RAIDE
# =========================================================
with tab3:
    st.subheader("⚔️ Registro de Raide")

    if "raide_iniciada" not in st.session_state:
        st.session_state.raide_iniciada = False

    if not st.session_state.raide_iniciada:
        c_r1, c_r2 = st.columns(2)
        raide_escolhida = c_r1.selectbox("Selecione a Raide", LISTA_RAIDES)
        dia_escolhido = c_r2.selectbox("Dia da Raide", ["1º Dia", "2º Dia", "3º Dia", "Outro"])

        if st.button("🚀 Iniciar Raide", type="primary", use_container_width=True):
            st.session_state.raide_iniciada = True
            st.session_state.raide_base = raide_escolhida
            st.session_state.nome_raide_ativa = f"{raide_escolhida} ({dia_escolhido})"

            for key in list(st.session_state.keys()):
                if key.startswith(("pres_", "at_", "el_", "co_", "en_")):
                    del st.session_state[key]
            st.rerun()

    else:
        max_bosses = QTD_BOSSES.get(st.session_state.raide_base, 10)
        
        st.markdown(
            f"""
            <div style="background-color:#161b22; border:1px solid #30363d; border-radius:8px; padding:12px 16px; margin-bottom:12px;">
                <span style="color:#8b949e; font-size:13px;">RAIDE EM ANDAMENTO (Bosses: {max_bosses} | Flask e Comida: 10/10)</span><br>
                <span style="color:#d4af37; font-size:21px; font-weight:bold;">⚔️ {st.session_state.nome_raide_ativa}</span>
            </div>
            """, unsafe_allow_html=True
        )

        st.info("💡 Marque ☑ Presente ao lado do jogador para liberar os menus. Encantamentos ausentes subtraem pontos da média final!")

        membros = obter_membros()
        dados_checkin = []
        
        opcoes_boss = [f"{i}/{max_bosses}" for i in range(max_bosses + 1)]
        opcoes_flask_comida = [f"{i}/10" for i in range(11)]

        h_nome, h_pres, h_boss, h_flask, h_comida, h_enc = st.columns([3.5, 1.2, 1.1, 1.1, 1.1, 2.8])
        h_nome.markdown("<b>JOGADOR</b>", unsafe_allow_html=True)
        h_pres.markdown("<b>PRES.</b>", unsafe_allow_html=True)
        h_boss.markdown("<b>BOSS</b>", unsafe_allow_html=True)
        h_flask.markdown("<b>FLASK</b>", unsafe_allow_html=True)
        h_comida.markdown("<b>COMIDA</b>", unsafe_allow_html=True)
        h_enc.markdown("<b>ENCANT. FALTANDO (-1 PT)</b>", unsafe_allow_html=True)
        st.markdown('<hr style="margin:5px 0 8px 0; border:0; border-top:1px solid #30363d;">', unsafe_allow_html=True)

        for idx, m in membros.iterrows():
            c_info, c_pres, c_at, c_el, c_co, c_en = st.columns([3.5, 1.2, 1.1, 1.1, 1.1, 2.8])
            
            c_info.markdown(html_classe(m["classe"], 30).replace("<div>", f"<div style='margin-top:-6px; font-size:14px; line-height:1.2;'><span style='color:#f0f6fc;'>{m['nome']}</span><br>"), unsafe_allow_html=True)

            presente = c_pres.checkbox("Presente", value=False, key=f"pres_{m['id']}", label_visibility="collapsed")

            ativ = c_at.selectbox("Boss", opcoes_boss, index=max_bosses, key=f"at_{m['id']}", disabled=not presente, label_visibility="collapsed")
            elixir = c_el.selectbox("Flask", opcoes_flask_comida, index=10, key=f"el_{m['id']}", disabled=not presente, label_visibility="collapsed")
            comida = c_co.selectbox("Comida", opcoes_flask_comida, index=10, key=f"co_{m['id']}", disabled=not presente, label_visibility="collapsed")
            encantamentos = c_en.multiselect("Encantamentos", LISTA_ENCANTAMENTOS, key=f"en_{m['id']}", placeholder=("Ausentes..." if presente else "Jogador ausente"), disabled=not presente, label_visibility="collapsed")

            if presente:
                c_pres.markdown("<div style='color:#56d364; font-size:11px; font-weight:bold; margin-top:-8px;'>✓ PRESENTE</div>", unsafe_allow_html=True)
            else:
                c_pres.markdown("<div style='color:#f85149; font-size:11px; font-weight:bold; margin-top:-8px;'>✕ AUSENTE</div>", unsafe_allow_html=True)

            dados_checkin.append({
                "nome": m["nome"], "classe": m["classe"], "presente": presente,
                "ativ": ativ, "elixir": elixir, "comida": comida, "encantamentos": encantamentos
            })

            if idx < len(membros) - 1:
                st.markdown('<hr style="margin:4px 0; border:0; border-top:1px solid #30363d;">', unsafe_allow_html=True)

        st.markdown('<hr style="margin:12px 0;">', unsafe_allow_html=True)
        col_b1, col_b2 = st.columns([4, 1])

        if col_b1.button("💾 SALVAR REGISTRO COMPLETO DA RAIDE", type="primary", use_container_width=True):
            try:
                conn = sqlite3.connect("guilda_database.db")
                cursor = conn.cursor()
                data_hoje = datetime.now().strftime("%d/%m/%Y")
                
                max_pts_possiveis = max_bosses + 10 + 10 + 2

                for reg in dados_checkin:
                    if not reg["presente"]:
                        total_pts = 0
                        pct = 0
                        status = "NÃO PREPARADO"
                        boss_val, flask_val, comida_val, pres_val, ausentes_val = "-", "-", "-", "0/2", "-"
                    else:
                        p_ativ = int(reg["ativ"].split("/")[0])     
                        p_eli = int(reg["elixir"].split("/")[0])    
                        p_com = int(reg["comida"].split("/")[0])    
                        p_pre = 2                                   
                        
                        pts_punicao = len(reg["encantamentos"])
                        
                        total_pts = (p_ativ + p_eli + p_com + p_pre) - pts_punicao
                        if total_pts < 0: total_pts = 0
                        
                        pct = (total_pts / max_pts_possiveis) * 100

                        if pct >= 75: status = "PREPARADO"
                        elif pct >= 50: status = "ATENÇÃO"
                        else: status = "NÃO PREPARADO"

                        boss_val = reg["ativ"]
                        flask_val = reg["elixir"]
                        comida_val = reg["comida"]
                        pres_val = "2/2"
                        ausentes_val = " ".join([e.split()[0] for e in reg["encantamentos"]]) if reg["encantamentos"] else "-"

                    cursor.execute("""
                        INSERT INTO historico_raides
                        (data_registro, nome_raide, jogador, classe, boss, flask, comida, presenca, ausentes, pontuacao, porcentagem, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        data_hoje, st.session_state.nome_raide_ativa, reg["nome"], reg["classe"],
                        boss_val, flask_val, comida_val, pres_val, ausentes_val,
                        total_pts, f"{int(pct)}%", status
                    ))

                conn.commit()
                conn.close()
                st.success("✅ Raide salva com sucesso!")
                st.session_state.raide_iniciada = False
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar a raide: {e}")

        if col_b2.button("❌ Cancelar", use_container_width=True):
            st.session_state.raide_iniciada = False
            for key in list(st.session_state.keys()):
                if key.startswith(("pres_", "at_", "el_", "co_", "en_")):
                    del st.session_state[key]
            st.rerun()

# ==========================================
# ABA 4: RELATÓRIOS (CORRIGIDO SEM "NONE")
# ==========================================
with tab4:
    st.subheader("📊 Relatórios e Histórico de Raides")
    conn = sqlite3.connect("guilda_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT data_registro, nome_raide FROM historico_raides ORDER BY id DESC")
    raides_salvas = cursor.fetchall()
    conn.close()

    if not raides_salvas:
        st.info("Nenhuma raide registrada.")
    else:
        escolha = st.selectbox("Selecione a Raide no Histórico", [f"{d} - {n}" for d, n in raides_salvas])
        data_sel, nome_sel = escolha.split(" - ", 1)
        
        conn = sqlite3.connect("guilda_database.db")
        df = pd.read_sql("""
            SELECT jogador, classe, boss, flask, comida, presenca, ausentes, pontuacao, porcentagem, status 
            FROM historico_raides WHERE data_registro=? AND nome_raide=?
        """, conn, params=(data_sel, nome_sel))
        conn.close()

        # Substituição segura de valores vazios sem retornar 'None' na tela
        df = df.fillna("-")

        c1, c2, c3 = st.columns(3)
        c1.metric("🟢 Preparados", len(df[df["status"] == "PREPARADO"]))
        c2.metric("🟡 Atenção", len(df[df["status"] == "ATENÇÃO"]))
        c3.metric("🔴 Não Preparados", len(df[df["status"] == "NÃO PREPARADO"]))
        st.markdown("---")

        col_pdf1, col_pdf2 = st.columns(2)
        with col_pdf1:
            _ = st.download_button(
                "📥 Baixar Relatório Geral (PDF)", 
                data=gerar_pdf_geral(nome_sel, data_sel, df), 
                file_name=f"Relatorio_{nome_sel.replace(' ', '_')}.pdf", 
                mime="application/pdf", 
                use_container_width=True
            )
        with col_pdf2:
            jogadores_lista = df["jogador"].tolist()
            if jogadores_lista:
                jogador_escolhido = st.selectbox("Selecionar Jogador", jogadores_lista)
                _ = st.download_button(
                    f"📥 Baixar PDF Individual ({jogador_escolhido})", 
                    data=gerar_pdf_individual(nome_sel, data_sel, df[df["jogador"] == jogador_escolhido].iloc[0]), 
                    file_name=f"Desempenho_{jogador_escolhido}.pdf", 
                    mime="application/pdf", 
                    use_container_width=True
                )
        
        st.markdown("---")
        
        relatorio_formatado = []
        for _, row in df.iterrows():
            classe_nome = str(row["classe"]) if pd.notna(row["classe"]) else "-"
            relatorio_formatado.append({
                "Jogador": row["jogador"],
                "Classe": html_classe(classe_nome, 20),
                "Boss": row["boss"],
                "Flask": row["flask"],
                "Comida": row["comida"],
                "Pres.": row["presenca"],
                "Ausências": row["ausentes"],
                "Pts": row["pontuacao"],
                "Média": row["porcentagem"],
                "Status": row["status"]
            })
        
        df_final_rel = pd.DataFrame(relatorio_formatado)
        st.markdown(df_final_rel.to_html(escape=False, index=False), unsafe_allow_html=True)

# ==========================================
# FUNÇÃO DINÂMICA DAS TÁTICAS
# ==========================================
def draw_dynamic_row(key_prefix, c_sizes, defaults, list_players, dados_tatica, icon_options_dict):
    cols = st.columns(c_sizes)
    for i in range(len(c_sizes)):
        with cols[i]:
            key = f"{key_prefix}_{i}"
            is_icon_col = False
            if len(c_sizes) == 7 and i in [0, 1, 4, 6]: is_icon_col = True
            elif len(c_sizes) == 5 and i in [0, 4]: is_icon_col = True
            elif len(c_sizes) == 4 and i == 0: is_icon_col = True

            if is_icon_col:
                idx_default = list(icon_options_dict.values()).index(defaults[i]) if defaults[i] in icon_options_dict.values() else 0
                escolha = st.selectbox("", list(icon_options_dict.keys()), index=idx_default, key=key, label_visibility="collapsed")
                img_key = icon_options_dict[escolha]
                dados_tatica[key] = img_key

                if img_key:
                    img_b64 = obter_icone_base64(img_key)
                    st.markdown(f'<div style="display:flex; justify-content:center; height:38px;"><img src="{img_b64}" width="36" height="36" style="border:1px solid #555; border-radius:4px;"></div>', unsafe_allow_html=True)
                else:
                    st.markdown("<div style='height:38px;'></div>", unsafe_allow_html=True)
            elif (len(c_sizes) == 7 and i == 2) or (len(c_sizes) == 4 and i in [2, 3]):
                idx_default = OPCOES_GRUPOS.index(defaults[i]) if defaults[i] in OPCOES_GRUPOS else 0
                escolha = st.selectbox("", OPCOES_GRUPOS, index=idx_default, key=key, label_visibility="collapsed")
                dados_tatica[key] = escolha
            else:
                idx_default = list_players.index(defaults[i]) if defaults[i] in list_players else 0
                escolha = st.selectbox("", list_players, index=idx_default, key=key, label_visibility="collapsed")
                dados_tatica[key] = escolha

# ==========================================
# ABA 5: TÁTICAS E BUFFS
# ==========================================
with tab5:
    membros_df = obter_membros()
    opcoes_players = [""] + membros_df["nome"].tolist() if not membros_df.empty else ["Nenhum jogador"]
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
        _ = draw_dynamic_row(f"b_r{r+1}", c_sizes_buffs, default, opcoes_players, dados_tatica, icon_options_dict=OPCOES_ICONES_BUFFS)
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
        _ = draw_dynamic_row(f"t_r{r+1}", c_sizes_tanks, default, opcoes_players, dados_tatica, icon_options_dict=OPCOES_ICONES_COMBINED)

    st.markdown('<div class="tatica-header">🏹 MD Trash - Boss + Trash</div>', unsafe_allow_html=True)
    c_sizes_md = [1.2, 3.5, 3.5, 3.5]
    defaults_md = [
        ["caveira", "", "MAIN TANK", "TRASH + BOSS"], ["xis", "", "OFF TANK", "TRASH + BOSS"]
    ]
    for r, default in enumerate(defaults_md):
        _ = draw_dynamic_row(f"m_r{r+1}", c_sizes_md, default, opcoes_players, dados_tatica, icon_options_dict=OPCOES_ICONES_TARGET_MARKS)

    st.markdown('<hr style="border-color:#333; margin-top:15px; margin-bottom:15px;">', unsafe_allow_html=True)
    _ = st.download_button("📥 Gerar e Baixar PDF com Táticas de Boss", data=gerar_pdf_taticas(dados_tatica), file_name=f"Taticas_Mata_Boss_{datetime.now().strftime('%d-%m-%Y')}.pdf", mime="application/pdf", type="primary", use_container_width=True)
