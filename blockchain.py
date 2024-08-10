import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, request, jsonify

class Blockchain:
    difficulty_target = "0000"
    
    def hash_block(self, block):
        """
        Create a SHA-256 hash of a block.
        """
        block_encoded = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_encoded).hexdigest()
    
    def __init__(self):
        """
        Initialize the blockchain with the genesis block.
        """
        self.chain = []
        self.current_transactions = []
        
        # Create the genesis block
        genesis_block = {
            'index': 0,
            'timestamp': time(),
            'transactions': [],
            'nonce': 100,  # Set a nonce value for the genesis block
            'hash_of_previous_block': '0'
        }
        genesis_block['hash'] = self.hash_block(genesis_block)
        self.chain.append(genesis_block)
    
    def proof_of_work(self, index, hash_of_previous_block, transactions):
        """
        Find a nonce that satisfies the difficulty target.
        """
        nonce = 0
        while not self.valid_proof(index, hash_of_previous_block, transactions, nonce):
            nonce += 1
        return nonce
    
    def valid_proof(self, index, hash_of_previous_block, transactions, nonce):
        """
        Validate the proof of work.
        """
        content = f'{index}{hash_of_previous_block}{json.dumps(transactions, sort_keys=True)}{nonce}'.encode()
        content_hash = hashlib.sha256(content).hexdigest()
        return content_hash[:len(self.difficulty_target)] == self.difficulty_target
    
    def append_block(self, nonce, hash_of_previous_block):
        """
        Append a new block to the blockchain.
        """
        block = {
            'index': len(self.chain),
            'timestamp': time(),
            'transactions': self.current_transactions,
            'nonce': nonce,
            'hash_of_previous_block': hash_of_previous_block
        }
        block['hash'] = self.hash_block(block)
        self.current_transactions = []
        self.chain.append(block)
        return block
    
    def add_transaction(self, sender, recipient, amount):
        """
        Add a transaction to the list of transactions.
        """
        self.current_transactions.append({
            'amount': amount,
            'recipient': recipient,
            'sender': sender
        })
        return self.last_block['index'] + 1
    
    @property
    def last_block(self):
        """
        Return the last block in the chain.
        """
        return self.chain[-1]

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    """
    Mine a new block and return it.
    """
    last_block = blockchain.last_block
    last_hash = last_block['hash']
    index = last_block['index'] + 1
    
    # Find the nonce that satisfies the proof of work
    nonce = blockchain.proof_of_work(index, last_hash, blockchain.current_transactions)
    
    # Append the block to the blockchain
    block = blockchain.append_block(nonce, last_hash)
    
    response = {
        'message': 'New Block Forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'nonce': block['nonce'],
        'hash': block['hash']
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """
    Create a new transaction.
    """
    values = request.get_json()
    
    # Check that the required fields are in the POST data
    required_fields = ['sender', 'recipient', 'amount']
    if not all(field in values for field in required_fields):
        return 'Missing values', 400
    
    # Create a new transaction
    index = blockchain.add_transaction(values['sender'], values['recipient'], values['amount'])
    
    response = {
        'message': f'Transaction will be added to Block {index}'
    }
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    """
    Return the full blockchain.
    """
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    """
    Resolve conflicts between nodes.
    """
    # This function is a placeholder for a consensus algorithm.
    response = {
        'message': 'Consensus resolution is not yet implemented.'
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
