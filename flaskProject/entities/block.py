import datetime
import hashlib
import json

class Block:
    def __init__(self, **kwargs):
        self.index = kwargs.get('index')
        self.timestamp = kwargs.get('timestamp')
        self.proof = kwargs.get('proof')
        self.previous_hash = kwargs.get('previous_hash')
        self.transactions = kwargs.get('transactions', [])
    def hash(self):
        encoded_block = json.dumps(self.__dict__, sort_keys=True, default=str).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_valid(self, previous_block):
        if self.previous_hash != previous_block.hash():
            return False

        hash_operation = hashlib.sha256(
            str(self.proof**2 - previous_block.proof**2).encode()).hexdigest()

        return hash_operation[:5] == '00000'