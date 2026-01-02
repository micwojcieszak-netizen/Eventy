import streamlit as st
import pandas as pd

# --- Dane startowe ---
try:
    df = pd.read_csv("stores.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=["Zabka MPK", "Tech ID", "Store name", "Adres", "Status"])

st.title("Zabka Licence Register")

# --- Statystyki ---
active_count = (df["Status"] == "Active").sum()
inactive_count = (df["Status"] == "Inactive").sum()
st.write(f"Active stores: {active_count} | Inactive stores: {inactive_count}")

# --- Wyświetl tabelę ---
st.dataframe(df)

# --- Dodawanie nowego wpisu ---
st.subheader("Add new store")
with st.form("add_store_form"):
    zabkaMPK = st.text_input("Zabka MPK")
    techID = st.text_input("Tech ID")
    storeName = st.text_input("Store name")
    adres = st.text_input("Adres")
    status = st.selectbox("Status", ["Active", "Inactive"])
    submitted = st.form_submit_button("Add store")
    if submitted:
        new_row = {
            "Zabka MPK": zabkaMPK,
            "Tech ID": techID,
            "Store name": storeName,
            "Adres": adres,
            "Status": status
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv("stores.csv", index=False)
        st.success("Store added!")
        st.experimental_rerun()
