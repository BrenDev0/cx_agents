import bcrypt
import hashlib

def deterministic_hash(value: str) -> str:
        bytes = value.lower().encode('utf-8')
        hashed_data = hashlib.sha256(bytes).hexdigest()
        return hashed_data


def hash_token(value: str) -> str:
        """Case-preserving hash for high-entropy random tokens (e.g. webhook
        secrets). Unlike deterministic_hash, does not lowercase the input --
        doing so would throw away entropy from a random token's mixed case."""
        return hashlib.sha256(value.encode('utf-8')).hexdigest()


def hash_password(str_to_hash: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(str_to_hash.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(
    unhashed_password: str, 
    hashed_password: str,
) -> bool:
    return bcrypt.checkpw(unhashed_password.encode('utf-8'), hashed_password.encode('utf-8'))

            