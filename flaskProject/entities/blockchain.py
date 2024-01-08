import datetime
import hashlib
import json

import psycopg2
from psycopg2.extras import RealDictCursor

from entities.block import Block

DB_NAME = "saxajbgf"
DB_USER = "saxajbgf"
DB_PASSWORD = "JoSURjRw3DW9WJKez527UjiLaORDc0tt"
DB_HOST = "balarama.db.elephantsql.com"
DB_PORT = "5432"


class Blockchain:
    def __init__(self):
        # Establish a connection to the PostgreSQL database
        self.conn = psycopg2.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

        # Create a cursor
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

        # Create the blocks table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                id SERIAL PRIMARY KEY,
                index INTEGER,
                timestamp TIMESTAMP,
                proof INTEGER,
                previous_hash VARCHAR(255),
                transactions JSONB
            )
        ''')
        self.conn.commit()

        # Load the blockchain from the database
        self.load_blocks_from_db()

        if len(self.chain) == 0:
            self.create_block(proof=1, previous_hash='0', transactions=[])

    def load_blocks_from_db(self):
        # Load existing blocks from the database
        self.cursor.execute("SELECT * FROM blocks ORDER BY index")
        rows = self.cursor.fetchall()

        # Convert each row to a Block object and add it to the chain
        self.chain = [Block(**row) for row in rows]

    def create_block(self, proof, previous_hash, transactions):
        block = Block(index=len(self.chain) + 1,
                      timestamp=str(datetime.datetime.now()),
                      proof=proof,
                      previous_hash=previous_hash,
                      transactions=transactions)
        self.save_block_to_db(block)
        self.chain.append(block)
        return block

    def save_block_to_db(self, block):
        # Save the block to the database
        self.cursor.execute('''
            INSERT INTO blocks (index, timestamp, proof, previous_hash, transactions)
            VALUES (%s, %s, %s, %s, %s)
        ''', (block.index, block.timestamp, block.proof, block.previous_hash, json.dumps(block.transactions)))

        self.conn.commit()

    def print_previous_block(self):
        if len(self.chain) > 0:
            return self.chain[-1]
        return None

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False

        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:5] == '00000':
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def chain_valid(self):
        block_index = 1
        while block_index < len(self.chain):
            current_block = self.chain[block_index]
            previous_block = self.chain[block_index - 1]
            if not current_block.is_valid(previous_block):
                return False
            block_index += 1
        return True

    def __del__(self):
        # Close the database connection when the object is deleted
        self.cursor.close()
        self.conn.close()