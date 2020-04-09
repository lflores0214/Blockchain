# Paste your version of blockchain.py from the client_mining_p
# folder here

import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request
from flask_cors import CORS


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        if len(self.chain) > 0:
            block_string = json.dumps(self.last_block, sort_keys=True)
            guess = f"{block_string}{proof}".encode()
            current_hash = hashlib.sha256(guess).hexdigest()
        else:
            current_hash = ""
        block = {
            'index': len(self.chain)+1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            "hash": current_hash,

        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Append the chain to the block
        self.chain.append(block)
        # Return the new block
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient.strip(),
            'amount': amount
        })
        return self.last_block['index'] + 1

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It converts the Python string into a byte string.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # TODO: Create the block_string
        string_object = json.dumps(block, sort_keys=True)
        block_string = string_object.encode()
        # TODO: Hash this string using sha256
        raw_hash = hashlib.sha256(block_string)
        hex_hash = raw_hash.hexdigest()
        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # TODO: Return the hashed block string in hexadecimal format
        return hex_hash

    @property
    def last_block(self):
        return self.chain[-1]

    # def proof_of_work(self):
    # #     """
    # #     Simple Proof of Work Algorithm
    # #     Stringify the block and look for a proof.
    # #     Loop through possibilities, checking each one against `valid_proof`
    # #     in an effort to find a number that is a valid proof
    # #     :return: A valid proof for the provided block
    # #     """
    # #     # TODO
    #     block_string = json.dumps(self.last_block, sort_keys=True)
    #     proof = 0
    #     while self.valid_proof(block_string, proof) is False:
    #         proof += 1
    #     return proof

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        guess = f"{block_string}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:6] == "000000"

        # return True or False


# Instantiate our Node
app = Flask(__name__)
CORS(app)
# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

# * Modify the `mine` endpoint to instead receive and validate or reject a new proof sent by a client.
# * It should accept a POST
@app.route('/mine', methods=['POST'])
def mine():
    # * Use `data = request.get_json()` to pull the data out of the POST
    data = request.get_json()
    # * Check that 'proof', and 'id' are present
    # * if either 'proof' or 'id' is not present
    if data['proof'] is None or data['id'] is None:
        # * return a 400 error using `jsonify(response)` with a 'message'
        return jsonify({
            'message:': "You need to submit both 'proof' and 'id' with your request"
        }), 400

    # * if they are present
    # * get the block string
    block_string = json.dumps(blockchain.last_block, sort_keys=True)
    # * validate the 'proof' sent
    valid_proof = blockchain.valid_proof(block_string, data['proof'])
    # * if proof is valid
    if valid_proof:
        # * forge a new block using the previous hash
        blockchain.new_transaction(sender="0", recipient=data["id"], amount=1)
        last_block = blockchain.last_block
        previous_hash = blockchain.hash(last_block)
        new_block = blockchain.new_block(data['proof'], previous_hash)

        # * send a 'success' response
        response = {
            'message': 'New block forged',
            'index': new_block['index'],
            'timestamp': new_block['timestamp'],
            'transaction': new_block['transactions'],
            'proof': new_block['proof'],
            'previous_hash': new_block['previous_hash']
        }
        return jsonify(response), 200
    # * else if proof is not valid
    else:
        # * send a 'failure' message
        return jsonify({
            'message': "Invalid proof"
        }), 400


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'length': len(blockchain.chain),
        'chain': blockchain.chain
    }
    return jsonify(response), 200


@app.route('/last_block', methods=['GET'])
def last_block():
    lastBlock = blockchain.chain[-1]
    response = {
        'last_block': lastBlock
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'missing values', 400

    index = blockchain.new_transaction(values['sender'],
                                       values['recipient'],
                                       values['amount'])

    response = {
        'message': f"Transaction will be added to block {index}"
    }
    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
