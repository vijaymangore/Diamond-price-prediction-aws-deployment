# frontend/app.py
import streamlit as st
import requests
import os

st.set_page_config(page_title="Diamond Evaluation Interface", page_icon="💎", layout="centered")

# Read cross-container endpoints dynamically
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8080")
API_KEY = os.getenv("DIAMOND_API_KEY", "prod-secret-diamond-key-9988")

st.title("💎 Real-time Diamond Pricing Portal")
st.markdown("---")

st.subheader("1. Dimensional & Carat Adjustments")
carat = st.slider("Carat Weight", min_value=0.2, max_value=5.1, value=0.7, step=0.01)

c1, c2, c3 = st.columns(3)
with c1:
    cut = st.selectbox("Cut Quality", ["Ideal", "Premium", "Very Good", "Good", "Fair"])
with c2:
    color = st.selectbox("Color Grade", ["D", "E", "F", "G", "H", "I", "J"])
with c3:
    clarity = st.selectbox("Clarity Grade", ["IF", "VVS1", "VVS2", "VS1", "VS2", "SI1", "SI2", "I1"])

st.subheader("2. Physical Geometries (Structural Measurements)")
g1, g2, g3, g4, g5 = st.columns(5)
with g1:
    depth = st.number_input("Depth %", min_value=43.0, max_value=79.0, value=61.5)
with g2:
    table = st.number_input("Table %", min_value=43.0, max_value=95.0, value=55.0)
with g3:
    x = st.number_input("Length (x) mm", min_value=0.0, max_value=11.0, value=5.7)
with g4:
    y = st.number_input("Width (y) mm", min_value=0.0, max_value=59.0, value=5.7)
with g5:
    z = st.number_input("Depth (z) mm", min_value=0.0, max_value=32.0, value=3.5)

st.markdown("---")

if st.button("Evaluate Valuation Metrics", type="primary", use_container_width=True):
    payload = {
        "carat": carat, "cut": cut, "color": color, "clarity": clarity,
        "depth": depth, "table": table, "x": x, "y": y, "z": z
    }
    
    headers = {"X-API-Key":"Vijay@10",
               "Content-Type": "application/json"}
    
    try:
        response = requests.post(f"{BACKEND_URL}/predict", json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            valuation = data["valuation_usd"]
            st.balloons()
            st.success(f"### Predicted Market Price: ${valuation:,.2f} USD")
        else:
            st.error(f"Execution Error [{response.status_code}]: {response.json().get('detail')}")
            
    except Exception as network_error:
        st.error(f"Inability to establish data pathway to inference microservice network: {network_error}")