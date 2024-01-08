from flask import Flask, request, jsonify

from entities.blockchain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()


@app.route('/add_block', methods=['POST'])
def add_block():
    data = request.get_json()
    if 'sender' not in data or 'recipient' not in data or 'amount' not in data:
        response = {'message': 'Invalid transaction data'}
        return jsonify(response), 400

    sender = data['sender']
    recipient = data['recipient']
    amount = data['amount']

    new_transaction = {
        'sender': sender,
        'recipient': recipient,
        'amount': amount
    }

    previous_block = blockchain.chain[-1]
    if not previous_block.proof:
        response = {'message': 'Mine a block first to establish proof of work'}
        return jsonify(response), 400

    previous_hash = previous_block.hash()

    previous_proof = previous_block.proof
    proof = blockchain.proof_of_work(previous_proof)
    new_block = blockchain.create_block(proof, previous_hash, [new_transaction])

    if new_block:
        response = {
            'message': 'Transaction added and a block is MINED',
            'index': new_block.index,
            'timestamp': new_block.timestamp,
            'proof': new_block.proof,
            'previous_hash': new_block.previous_hash,
            'hash': new_block.hash(),
            'transactions': new_block.transactions
        }
        return jsonify(response), 201
    else:
        response = {'message': 'Error adding transaction'}
        return jsonify(response), 500


@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.chain[-1]
    previous_proof = previous_block.proof
    proof = blockchain.proof_of_work(previous_proof)
    previous_block = blockchain.print_previous_block()
    previous_hash = previous_block.hash()

    transactions = []
    new_block = blockchain.create_block(proof, previous_hash, transactions)

    response = {
        'message': 'Congratulations, you just mined a block!',
        'index': new_block.index,
        'timestamp': new_block.timestamp,
        'proof': new_block.proof,
        'previous_hash': new_block.previous_hash,
        'transactions': new_block.transactions
    }

    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def display_chain():
    response = {'chain': [block.__dict__ for block in blockchain.chain],
                'length': len(blockchain.chain)}
    return jsonify(response), 200


@app.route('/valid', methods=['GET'])
def valid():
    if blockchain.chain_valid():
        response = {'message': 'The Blockchain is valid.'}
    else:
        response = {'message': 'The Blockchain is not valid.'}
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)