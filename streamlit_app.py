import streamlit as st
import requests
import pandas as pd

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Blockchain Dashboard", layout="wide")

# -------------------- CUSTOM CSS --------------------
st.markdown("""
    <style>
    body {
        background-color: #ffffff;
        color: #000000;
        font-family: 'Arial', sans-serif;
    }
    .title {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 20px;
    }
    .node-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin: 10px;
        border: 2px solid #3498db;
        transition: 0.3s;
        cursor: pointer;
    }
    .node-card:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(52,152,219,0.5);
    }
    .node-title {
        font-size: 20px;
        font-weight: bold;
        color: #2980b9;
        margin-bottom: 10px;
    }
    .node-stat {
        font-size: 16px;
        margin: 5px 0;
        color: #34495e;
    }
    .mine-btn {
        background-color: #3498db;
        color: white;
        font-size: 14px;
        font-weight: bold;
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        text-decoration: none;
    }
    .mine-btn:hover {
        background-color: #2980b9;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- TITLE --------------------
st.markdown("<div class='title'>🔗 Blockchain Dashboard</div>", unsafe_allow_html=True)

# -------------------- SIDEBAR FOR ACTIONS --------------------
st.sidebar.title("⚡ Actions")

# Select a node for transactions
node_address = st.sidebar.selectbox("Select Node", [
    "http://127.0.0.1:5000",
    "http://127.0.0.1:5001",
    "http://127.0.0.1:5002",
    "http://127.0.0.1:5003"
])

# Add Transaction
st.sidebar.subheader("➕ Add Transaction")
sender = st.sidebar.text_input("Sender")
receiver = st.sidebar.text_input("Receiver")
amount = st.sidebar.number_input("Amount", min_value=0.01)

if st.sidebar.button("✅ Submit Transaction"):
    data = {"sender": sender.strip(), "receiver": receiver.strip(), "amount": amount}
    response = requests.post(f"{node_address}/add_transaction", json=data)
    if response.status_code == 201:
        st.sidebar.success(response.json()['message'])
    else:
        st.sidebar.error("Failed to add transaction")

# Mine Block
if st.sidebar.button("⛏️ Mine Block"):
    response = requests.get(f"{node_address}/mine_block")
    if response.status_code == 200:
        st.sidebar.success("Block mined successfully!")
    else:
        st.sidebar.error("Failed to mine block")

# Replace Chain (Consensus)
if st.sidebar.button("🔄 Replace Chain"):
    response = requests.get(f"{node_address}/replace_chain")
    if response.status_code == 200:
        st.sidebar.success(response.json()['message'])
    else:
        st.sidebar.error("Consensus failed")

# Connect Node
st.sidebar.subheader("🔗 Connect Node")
new_node = st.sidebar.text_input("Enter Node URL (e.g., http://127.0.0.1:5002)")
if st.sidebar.button("Connect Node"):
    data = {"nodes": [new_node]}
    response = requests.post(f"{node_address}/connect_node", json=data)
    if response.status_code == 201:
        st.sidebar.success("Node connected successfully!")
    else:
        st.sidebar.error("Failed to connect node")

# -------------------- NODE STATUS SECTION --------------------
st.markdown("### 📊 Node Status")

nodes = [
    {"name": "Node 5000", "url": "http://127.0.0.1:5000"},
    {"name": "Node 5001", "url": "http://127.0.0.1:5001"},
    {"name": "Node 5002", "url": "http://127.0.0.1:5002"},
    {"name": "Node 5003", "url": "http://127.0.0.1:5003"}
]

cols = st.columns(len(nodes))

for i, node in enumerate(nodes):
    try:
        response = requests.get(f"{node['url']}/get_chain")
        if response.status_code == 200:
            chain_data = response.json()
            blocks_count = chain_data['length']
            pending_tx = 0
        else:
            blocks_count = "N/A"
            pending_tx = "N/A"
    except:
        blocks_count = "Offline"
        pending_tx = "Offline"

    with cols[i]:
        if st.button(f"View {node['name']}"):
            st.subheader(f"Blockchain for {node['name']}")
            if response.status_code == 200:
                for block in chain_data['chain']:
                    with st.expander(f"📦 Block {block['index']}"):
                        st.write(f"**Timestamp:** {block['timestamp']}")
                        st.write(f"**Proof:** {block['proof']}")
                        st.write(f"**Previous Hash:** {block['previous_hash']}")
                        if block['transactions']:
                            st.write("**Transactions:**")
                            df = pd.DataFrame(block['transactions'])
                            st.table(df)
                        else:
                            st.write("No transactions in this block.")
            else:
                st.error("Could not fetch blockchain details.")

        st.markdown(f"""
            <div class="node-card">
                <div class="node-title">{node['name']}</div>
                <div class="node-stat">Blocks: <b>{blocks_count}</b></div>
                <div class="node-stat">Pending: <b>{pending_tx}</b></div>
                <a class="mine-btn" href="{node['url']}/mine_block" target="_blank">Mine</a>
            </div>
        """, unsafe_allow_html=True)
