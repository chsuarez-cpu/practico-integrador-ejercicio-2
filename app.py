import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Inventario Monte Carlo", layout="wide")

# =========================
# DATOS
# =========================
demanda = [40, 50, 60, 70, 80, 90]
prob = [0.10, 0.20, 0.30, 0.25, 0.10, 0.05]
acum = np.cumsum(prob)

# =========================
# FUNCIONES
# =========================
def generar_demanda():
    r = np.random.rand()
    for i, a in enumerate(acum):
        if r <= a:
            return demanda[i]

def utilidad(Q, D, precio, costo, rescate, penal):
    if D <= Q:
        return (precio * D) + (rescate * (Q - D)) - (costo * Q)
    else:
        return (precio * Q) - (costo * Q) - penal * (D - Q)

def simular(Q, dias, precio, costo, rescate, penal):
    datos = []
    for _ in range(dias):
        D = generar_demanda()
        U = utilidad(Q, D, precio, costo, rescate, penal)
        datos.append((D, U))

    return pd.DataFrame(datos, columns=["Demanda", "Utilidad"])

# =========================
# INTERFAZ
# =========================
st.title("🛒 Inventario Monte Carlo")

precio = st.sidebar.number_input("Precio venta", value=33)
costo = st.sidebar.number_input("Costo compra", value=24)
rescate = st.sidebar.number_input("Valor rescate", value=18)
penal = st.sidebar.number_input("Costo faltante", value=6)
dias = st.sidebar.slider("Días a simular", 10, 200, 50)

politicas = [50, 60, 70, 80, 90]

# =========================
# SIMULACIÓN
# =========================
resultados = []

for Q in politicas:
    df = simular(Q, dias, precio, costo, rescate, penal)

    resultados.append({
        "Q": Q,
        "Utilidad Promedio": df["Utilidad"].mean(),
        "Prob Faltante": (df["Demanda"] > Q).mean(),
        "Prob Sobrante": (df["Demanda"] < Q).mean()
    })

df_res = pd.DataFrame(resultados)

st.subheader("📊 Resultados")
st.dataframe(df_res)

# =========================
# MEJOR POLÍTICA
# =========================
mejor = df_res.loc[df_res["Utilidad Promedio"].idxmax()]
st.success(f"Mejor política: Q = {int(mejor['Q'])}")

# =========================
# GRÁFICOS SIN matplotlib
# =========================
st.subheader("📈 Utilidad promedio")
st.bar_chart(df_res.set_index("Q")["Utilidad Promedio"])

st.subheader("📉 Probabilidad de faltantes")
st.bar_chart(df_res.set_index("Q")["Prob Faltante"])

# =========================
# DETALLE
# =========================
st.subheader("📊 Evolución diaria")

Q_sel = st.selectbox("Selecciona política", politicas)
df_det = simular(Q_sel, dias, precio, costo, rescate, penal)

st.line_chart(df_det["Utilidad"])

# =========================
# INTERPRETACIÓN
# =========================
st.subheader("🧠 Interpretación")

st.write("La mejor política equilibra faltantes y excedentes.")

if mejor["Prob Faltante"] > 0.4:
    st.warning("Alta probabilidad de faltantes")

if mejor["Prob Sobrante"] > 0.4:
    st.warning("Alta probabilidad de sobrantes")