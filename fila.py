
import math

class QueueInputError(ValueError):
    pass

def _validate_rates(lam, mu):
    if lam is None or mu is None:
        raise QueueInputError("λ e μ não podem ser nulos.")
    if lam < 0 or mu <= 0:
        raise QueueInputError("λ deve ser ≥ 0 e μ > 0.")
    return float(lam), float(mu)

def mm1(lam, mu):
    lam, mu = _validate_rates(lam, mu)
    rho = lam / mu
    if rho >= 1:
        return {"rho": rho, "L": float("inf"), "Lq": float("inf"),
                "W": float("inf"), "Wq": float("inf"), "P0": 0.0}
    L = rho / (1 - rho)
    Lq = (rho * rho) / (1 - rho)
    W = 1.0 / (mu - lam)
    Wq = lam / (mu * (mu - lam))
    P0 = 1.0 - rho
    return {"rho": rho, "L": L, "Lq": Lq, "W": W, "Wq": Wq, "P0": P0}

def mmc(lam, mu, c):
    if c is None or c < 1 or int(c) != c:
        raise QueueInputError("c deve ser inteiro >= 1.")
    lam, mu = _validate_rates(lam, mu)
    c = int(c)
    a = lam / mu
    rho = a / c
    if rho >= 1:
        return {"rho": rho, "P0": 0.0, "Pw": 1.0, "Lq": float("inf"),
                "Wq": float("inf"), "W": float("inf"), "L": float("inf")}
    sum_terms = 0.0
    for n in range(c):
        sum_terms += (a ** n) / math.factorial(n)
    last = (a ** c) / (math.factorial(c) * (1 - rho))
    P0 = 1.0 / (sum_terms + last)
    Pw = last * P0
    Lq = ((a ** c) * rho / (math.factorial(c) * (1 - rho) ** 2)) * P0
    Wq = Lq / lam
    W = Wq + 1.0 / mu
    L = lam * W
    return {"rho": rho, "P0": P0, "Pw": Pw, "Lq": Lq, "Wq": Wq, "W": W, "L": L}

def calc_from_jmeter_csv(df, elapsed_col='elapsed', ts_col='timeStamp'):
    import pandas as pd
    if elapsed_col not in df.columns:
        for c in df.columns:
            lc = c.lower()
            if lc == 'elapsed' or 'elapsed' in lc or 'latency' in lc or 'response' in lc:
                elapsed_col = c
                break
    if elapsed_col not in df.columns:
        raise QueueInputError(f"Coluna de elapsed não encontrada. Colunas: {list(df.columns)}")
    elapsed_ms = pd.to_numeric(df[elapsed_col], errors='coerce').dropna()
    N = int(elapsed_ms.shape[0])
    avg_elapsed_ms = float(elapsed_ms.mean()) if N > 0 else float("nan")
    mu = float("nan")
    if avg_elapsed_ms and avg_elapsed_ms > 0:
        mu = 1.0 / (avg_elapsed_ms / 1000.0)
    duration_s = float("nan")
    if ts_col in df.columns:
        ts = pd.to_numeric(df[ts_col], errors='coerce')
        if ts.notnull().any():
            tmin, tmax = float(ts.min()), float(ts.max())
            if tmax > tmin:
                duration_s = (tmax - tmin) / 1000.0
    lam = float("nan")
    if N > 0 and duration_s and duration_s > 0:
        lam = N / duration_s
    return lam, mu, N, duration_s, avg_elapsed_ms
