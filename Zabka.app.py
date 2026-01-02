import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="Zabka Licenses - Dashboard", layout="wide")

# Space Theme CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0d17;
        color: #e0e0e0;
    }
    .stButton>button {
        background-color: #4b0082;
        color: white;
        border: 1px solid #8a2be2;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #8a2be2;
        border: 1px solid #00d4ff;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #1a1c2c !important;
        color: #00d4ff !important;
    }
    h1, h2, h3 {
        color: #8a2be2;
        text-shadow: 1px 1px 5px #000;
        font-family: 'Courier New', Courier, monospace;
    }
    .stDataFrame {
        border: 1px solid #4b0082;
    }
    </style>
    """, unsafe_allow_html=True)

# Data Initialization
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {
            "ID": "ZF682", 
            "Store": "zabka-pl-ost-1", 
            "Name": "Ostróda Yachts", 
            "Address": "Ostróda, ul. Spokojna 1", 
            "Status": "Active", 
            "Comments": "Initial setup"
        }
    ])

st.title("🌌 Zabka Licenses Management")

# --- DISPLAY SECTION ---
st.subheader("🛰️ License Registry")
st.dataframe(st.session_state.data, use_container_width=True)

# --- PUBLIC SECTION: ADD COMMENT ---
st.divider()
st.subheader("💬 Public Feedback")
col1, col2 = st.columns([1, 2])

with col1:
    selected_id = st.selectbox("Select Station ID", st.session_state.data["ID"])
with col2:
    new_comment = st.text_input("Enter comment / note")

if st.button("Post Comment"):
    if new_comment:
        idx = st.session_state.data.index[st.session_state.data['ID'] == selected_id][0]
        old_comm = st.session_state.data.at[idx, "Comments"]
        st.session_state.data.at[idx, "Comments"] = f"{old_comm} | {new_comment}" if old_comm else new_comment
        st.success("Comment added successfully!")
        st.rerun()
    else:
        st.warning("Please enter a comment first.")

# --- ADMIN SECTION (Password Protected) ---
st.sidebar.title("🔐 Admin Access")
password = st.sidebar.text_input("Enter Credentials", type="password")

if password == "Aifi-2026":
    st.sidebar.success("Authorized Access")
    st.divider()
    st.header("🛠️ Administrative Tools")
    
    action = st.radio("Choose Action", ["Add New License", "Update Status", "Remove Entry"], horizontal=True)
    
    if action == "Add New License":
        with st.form("add_license"):
            c1, c2 = st.columns(2)
            with c1:
                n_id = st.text_input("Station ID")
                n_store = st.text_input("Store ID")
                n_name = st.text_input("Location Name")
            with c2:
                n_adr = st.text_input("Address")
                n_stat = st.selectbox("Current Status", ["Active", "Inactive", "Pending", "Maintenance"])
            
            if st.form_submit_button("Confirm Addition"):
                new_row = {"ID": n_id, "Store": n_store, "Name": n_name, "Address": n_adr, "Status": n_stat, "Comments": ""}
                st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
                st.rerun()

    elif action == "Update Status":
        u_id = st.selectbox("Select ID to update", st.session_state.data["ID"])
        u_stat = st.selectbox("New Status", ["Active", "Inactive", "Pending", "Maintenance"])
        if st.button("Apply Changes"):
            idx = st.session_state.data.index[st.session_state.data['ID'] == u_id][0]
            st.session_state.data.at[idx, "Status"] = u_stat
            st.rerun()

    elif action == "Remove Entry":
        r_id = st.selectbox("Select ID to remove", st.session_state.data["ID"])
        if st.button("Delete Permanently"):
            st.session_state.data = st.session_state.data[st.session_state.data["ID"] != r_id]
            st.rerun()
else:
    if password:
        st.sidebar.error("Access Denied: Incorrect Password")
