
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="SmartQuant",
    page_icon="📊",
    layout="wide"
)

st.title("📊 SmartQuant")
st.subheader("Plataforma de análise quantitativa")

st.info("Ambiente de simulação. Não realiza apostas nem transações financeiras reais.")

st.sidebar.header("Configurações")

modo = st.sidebar.selectbox(
    "Fonte de dados",
    ["Dados de demonstração", "Importar CSV/Excel", "Entrada manual"]
)

def gerar_dados():
    np.random.seed(42)
    datas = pd.date_range("2025-01-01", periods=250)
    precos = 100 * np.cumprod(1 + np.random.normal(0.0005, 0.015, 250))
    return pd.DataFrame({"Data": datas, "Preço": precos})

df = None

if modo == "Dados de demonstração":
    df = gerar_dados()

elif modo == "Importar CSV/Excel":
    ficheiro = st.file_uploader(
        "Carregar ficheiro",
        type=["csv", "xlsx"]
    )
    if ficheiro:
        try:
            if ficheiro.name.endswith(".csv"):
                df = pd.read_csv(ficheiro)
            else:
                df = pd.read_excel(ficheiro)
        except Exception as e:
            st.error(f"Erro ao importar: {e}")

elif modo == "Entrada manual":
    dados = st.text_area(
        "Introduza os preços separados por vírgulas",
        "100,102,101,104,106,103,108,110,109,113"
    )
    try:
        precos = [float(x.strip()) for x in dados.split(",")]
        df = pd.DataFrame({
            "Data": range(1, len(precos) + 1),
            "Preço": precos
        })
    except ValueError:
        st.error("Introduza apenas números separados por vírgulas.")

if df is not None:
    if modo != "Dados de demonstração":
        coluna = st.selectbox("Escolha a coluna dos preços", df.columns)
        df = df.copy()
        df["Preço"] = pd.to_numeric(df[coluna], errors="coerce")
        df = df.dropna(subset=["Preço"])

    if len(df) < 3:
        st.warning("Introduza pelo menos 3 preços.")
        st.stop()

    df = df.reset_index(drop=True)

    st.header("Análise de mercado")

    periodo_curto = st.slider("Média móvel curta", 2, 30, 5)
    periodo_longo = st.slider("Média móvel longa", 5, 100, 20)

    df["MM Curta"] = df["Preço"].rolling(periodo_curto).mean()
    df["MM Longa"] = df["Preço"].rolling(periodo_longo).mean()

    df["Sinal"] = np.where(
        df["MM Curta"] > df["MM Longa"], 1, 0
    )

    df["Retorno"] = df["Preço"].pct_change().fillna(0)
    df["Estratégia"] = (
        df["Sinal"].shift(1).fillna(0) * df["Retorno"]
    )

    retorno = (1 + df["Estratégia"]).prod() - 1
    retorno_mercado = (1 + df["Retorno"]).prod() - 1

    patrimonio = (1 + df["Estratégia"]).cumprod()
    drawdown = (patrimonio / patrimonio.cummax()) - 1
    queda_maxima = drawdown.min()

    c1, c2, c3 = st.columns(3)

    c1.metric("Retorno simulado", f"{retorno * 100:.2f}%")
    c2.metric("Retorno do mercado", f"{retorno_mercado * 100:.2f}%")
    c3.metric("Queda máxima", f"{queda_maxima * 100:.2f}%")

    st.subheader("Evolução dos preços")
    st.line_chart(df.set_index("Data")[["Preço"]])

    st.subheader("Estratégia de médias móveis")
    st.line_chart(
        df.set_index("Data")[["MM Curta", "MM Longa"]]
    )

    st.subheader("Histórico de simulação")
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "Descarregar resultados CSV",
        df.to_csv(index=False).encode("utf-8"),
        "smartquant_resultados.csv",
        "text/csv"
    )

st.divider()
st.caption("SmartQuant © 2026 | Ferramenta experimental de análise e simulação.")
