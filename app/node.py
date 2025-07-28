from flask import Flask, jsonify, request
import requests
from app.blockchain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    return jsonify({'message': 'Block mined successfully!', 'block': block}), 200

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json_data = request.get_json()
    if not all(k in json_data for k in ('sender', 'receiver', 'amount')):
        return 'Missing fields', 400
    index = blockchain.add_transaction(json_data['sender'], json_data['receiver'], json_data['amount'])
    return jsonify({'message': f'Transaction will be added to Block {index}'}), 201

@app.route('/connect_node', methods=['POST'])
def connect_node():
    json_data = request.get_json()
    nodes = json_data.get('nodes')
    if nodes is None:
        return 'No nodes provided', 400
    for node in nodes:
        blockchain.add_node(node)
    return jsonify({'message': 'Nodes connected successfully!', 'total_nodes': list(blockchain.nodes)}), 201

@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    network = blockchain.nodes
    longest_chain = None
    max_length = len(blockchain.chain)
    for node in network:
        response = requests.get(f'http://{node}/get_chain')
        if response.status_code == 200:
            length = response.json()['length']
            chain = response.json()['chain']
            if length > max_length and blockchain.is_chain_valid(chain):
                max_length = length
                longest_chain = chain
    if longest_chain:
        blockchain.chain = longest_chain
        return jsonify({'message': 'Chain replaced', 'new_chain': blockchain.chain}), 200
    return jsonify({'message': 'Current chain is the longest', 'chain': blockchain.chain}), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    return jsonify({'chain': blockchain.chain, 'length': len(blockchain.chain)}), 200

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int)
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port)
