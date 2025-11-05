
import streamlit as st
import pandas as pd
from fila import mm1, mmc, calc_from_jmeter_csv, QueueInputError

st.set_page_config(page_title="Calculadora de Filas (M/M/1 e M/M/c)", layout="centered")
st.title("Calculadora de Métricas de Teoria das Filas")
st.caption("Opção 2 — Ferramenta para calcular métricas a partir de entradas do sistema (com suporte a CSV do JMeter).")

with st.expander("📘 Como usar", expanded=False):
    st.markdown("""
    **Entradas possíveis**:
    - Informe diretamente λ (taxa de chegada) e μ (taxa de serviço por servidor), ou
    - Faça upload de um **CSV do JMeter** para estimar automaticamente λ e μ:
      - λ = N / duração (s), usando `timeStamp` (ms)
      - μ = 1 / média(`elapsed`) (s)
    **Modelos**: M/M/1 e M/M/c (Erlang-C)
    """)

tab1, tab2 = st.tabs(["Entradas Diretas", "A partir de CSV do JMeter"])

with tab1:
    st.subheader("Entradas Diretas")
    model = st.selectbox("Modelo", ["M/M/1", "M/M/c"])
    col1, col2 = st.columns(2)
    with col1:
        lam = st.number_input("λ (taxa de chegada, por segundo)", min_value=0.0, value=2.0, step=0.1, format="%.4f")
    with col2:
        mu = st.number_input("μ (taxa de serviço por servidor, por segundo)", min_value=0.0, value=5.0, step=0.1, format="%.4f")

    c = 1
    if model == "M/M/c":
        c = st.number_input("c (nº de servidores)", min_value=1, value=2, step=1)

    if st.button("Calcular (Entradas Diretas)"):
        try:
            if model == "M/M/1":
                res = mm1(lam, mu)
            else:
                res = mmc(lam, mu, c)
            st.success("Cálculo realizado com sucesso.")
            st.json(res)
        except QueueInputError as e:
            st.error(str(e))

with tab2:
    st.subheader("Estimativa a partir de CSV do JMeter")
    up = st.file_uploader("Envie o CSV (Simple Data Writer do JMeter)", type=["csv"])
    model2 = st.selectbox("Modelo (CSV)", ["M/M/1", "M/M/c"])
    c2 = 1
    if model2 == "M/M/c":
        c2 = st.number_input("c (nº de servidores) — CSV", min_value=1, value=2, step=1, key="c_csv")

    if up is not None:
        try:
            df = pd.read_csv(up)
            lam_csv, mu_csv, N, duration_s, avg_ms = calc_from_jmeter_csv(df)
            st.write(f"**N** = {N} | **Duração (s)** ≈ {duration_s:.2f} | **λ (req/s)** ≈ {lam_csv:.4f}")
            st.write(f"**Média elapsed (ms)** ≈ {avg_ms:.2f} | **μ (req/s)** ≈ {mu_csv:.4f}")

            if st.button("Calcular (CSV)"):
                if model2 == "M/M/1":
                    res = mm1(lam_csv, mu_csv)
                else:
                    res = mmc(lam_csv, mu_csv, c2)
                st.success("Cálculo realizado com sucesso a partir do CSV.")
                st.json(res)

        except Exception as e:
            st.error(f"Erro ao processar CSV: {e}")
