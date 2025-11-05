
# Ferramenta de Cálculo de Métricas de Teoria das Filas (Opção 2)

Este projeto implementa uma calculadora de métricas **M/M/1** e **M/M/c (Erlang‑C)**, com duas formas de uso:
1) **Entradas diretas:** informar λ e μ e obter as métricas.
2) **A partir de CSV do JMeter:** estimar λ e μ automaticamente e calcular as métricas.

## Como executar (Streamlit)
```bash
pip install streamlit pandas
streamlit run app.py
```
Abra o link local no navegador, escolha o modelo e:
- informe λ e μ diretamente, ou
- envie um CSV do **Simple Data Writer do JMeter** (com colunas `timeStamp` e `elapsed`).

## Como estimamos λ e μ a partir do JMeter
- λ (taxa de chegada) = **N / duração (s)**, onde:
  - `N` é o número de linhas do CSV (amostras),
  - `duração (s)` = (`max(timeStamp)` − `min(timeStamp)`) / 1000
- μ (taxa de serviço) ≈ **1 / média(elapsed_s)**, onde `elapsed_s` = `elapsed_ms` / 1000

> Observação: quando o sistema está no limite (muito carregado), μ estimado por `1/avg_elapsed` tende a ser conservador. Em cargas leves, usar o Throughput do Summary Report também é aceitável como estimativa de μ.

## Métricas retornadas
### M/M/1
- ρ = λ/μ
- L = ρ / (1 − ρ)
- Lq = ρ² / (1 − ρ)
- W = 1 / (μ − λ)
- Wq = λ / (μ(μ − λ))
- P0 = 1 − ρ

### M/M/c (Erlang‑C)
- ρ = (λ / μ) / c
- P0 (prob. de sistema vazio), Pw (prob. de esperar)
- Lq, Wq, W, L

## Estrutura
- `fila.py` — biblioteca com `mm1`, `mmc`, `calc_from_jmeter_csv`.
- `app.py` — UI Streamlit.
- `README.md` — instruções.
