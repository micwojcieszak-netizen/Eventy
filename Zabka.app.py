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
        border-radius: 5px;
    }
    h1, h2, h3 {
        color: #8a2be2;
        text-shadow: 1px 1px 5px #000;
        font-family: 'Courier New', Courier, monospace;
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
        },
        {
            "ID": "ZF999", 
            "Store": "zabka-pl-war-2", 
            "Name": "Warsaw Hub", 
            "Address": "Warszawa, ul. Prosta 1", 
            "Status": "Maintenance", 
            "Comments": ""
        }
    ])

st.title("🌌 Zabka Licenses Management")

# --- HIGHLIGHT LOGIC ---
def highlight_status(val):
    if val == "Active":
        return 'background-color: #004d00; color: #00ff00; font-weight: bold;'
    return ''

# Apply styling to the dataframe
styled_df = st.session_state.data.style.applymap(highlight_status, subset=['Status'])

# --- DISPLAY SECTION ---
st.subheader("🛰️ License Registry")
st.dataframe(styled_df, use_container_width=True, hide_index=True)

# --- PUBLIC SECTION: ADD COMMENT ---
st.divider()
st.subheader("💬 Public Feedback")
col_sel, col_txt = st.columns([1, 2])

with col_sel:
    selected_id = st.selectbox("Select Station ID", st.session_state.data["ID"])
with col_txt:
    new_comment = st.text_input("Enter comment / note")

if st.button("Post Comment"):
    if new_comment:
        idx = st.session_state.data.index[st.session_state.data['ID'] == selected_id][0]
        old_comm = st.session_state.data.at[idx, "Comments"]
        st.session_state.data.at[idx, "Comments"] = f"{old_comm} | {new_comment}" if old_comm else new_comment
        st.success("Comment added!")
        st.rerun()

# --- ADMIN SECTION ---
st.sidebar.title("🔐 Admin Access")
password = st.sidebar.text_input("Enter Credentials", type="password")

if password == "Aifi-2026":
    st.sidebar.success("Authorized")
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
        if st.confirm(f"Are you sure you want to delete {r_id}?") if hasattr(st, "confirm") else st.button("Confirm Delete"):
            st.session_state.data = st.session_state.data[st.session_state.data["ID"] != r_id]
            st.rerun()
else:
    if password:
        st.sidebar.error("Incorrect Password")
