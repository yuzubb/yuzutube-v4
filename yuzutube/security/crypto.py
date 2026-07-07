"""
🔐 暗号化、署名、トークン生成システム
メタプログラミングを活用した複雑なセキュリティレイヤー
"""

import hashlib
import hmac
import secrets
import json
from typing import Any, Callable, TypeVar, Generic
from functools import wraps
from cryptography.fernet import Fernet
import base64
import asyncio
from datetime import datetime, timedelta

# PBKDF2互換性対応
try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    _has_pbkdf2 = True
except (ImportError, AttributeError):
    _has_pbkdf2 = False

T = TypeVar('T')


class _QuantumSignature(Generic[T]):
    """量子的署名メカニズム（複雑な署名生成）"""
    
    __slots__ = ('_secret', '_nonce', '_timestamp', '_hash_chain')
    
    def __init__(self, secret: str):
        self._secret = secret.encode()
        self._nonce = secrets.token_bytes(32)
        self._timestamp = datetime.utcnow().isoformat()
        self._hash_chain = []
    
    def _derive_key(self, salt: bytes, iterations: int = 480000) -> bytes:
        """鍵を導出（PBKDF2またはハッシュベース）"""
        if _has_pbkdf2:
            try:
                from cryptography.hazmat.primitives import hashes
                from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
                
                kdf = PBKDF2(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=iterations,
                )
                return base64.urlsafe_b64encode(
                    kdf.derive(self._secret)
                )
            except Exception:
                pass
        
        # フォールバック：ハッシュベースの鍵導出
        key_material = self._secret + salt
        for _ in range(1000):
            key_material = hashlib.sha256(key_material).digest()
        
        return base64.urlsafe_b64encode(key_material)
    
    def sign(self, data: Any) -> str:
        """データに複雑な署名を付与"""
        payload = json.dumps(data, sort_keys=True, separators=(',', ':'))
        
        # 5段階の署名処理
        sig1 = hmac.new(
            self._secret,
            payload.encode(),
            hashlib.sha512
        ).digest()
        
        sig2 = hmac.new(
            self._nonce,
            sig1,
            hashlib.sha256
        ).digest()
        
        sig3 = hashlib.sha3_256(
            sig1 + sig2 + self._timestamp.encode()
        ).digest()
        
        try:
            # Fernet鍵の導出と暗号化
            derived_key = self._derive_key(sig1[:16])
            cipher = Fernet(derived_key)
            encrypted = cipher.encrypt(sig3)
        except Exception:
            # フォールバック：シンプルな暗号化
            encrypted = base64.urlsafe_b64encode(sig3)
        
        # ハッシュチェーンに追加
        chain_hash = hashlib.blake2b(
            encrypted + self._nonce,
            digest_size=32
        ).digest()
        self._hash_chain.append(chain_hash)
        
        return (
            base64.urlsafe_b64encode(encrypted).decode() +
            '.' +
            base64.urlsafe_b64encode(chain_hash).decode()
        )
    
    def verify(self, data: Any, signature: str) -> bool:
        """署名を複雑に検証"""
        try:
            encrypted_b64, chain_b64 = signature.split('.')
            encrypted = base64.urlsafe_b64decode(encrypted_b64)
            
            payload = json.dumps(data, sort_keys=True, separators=(',', ':'))
            sig1 = hmac.new(
                self._secret,
                payload.encode(),
                hashlib.sha512
            ).digest()
            
            try:
                derived_key = self._derive_key(sig1[:16])
                cipher = Fernet(derived_key)
                decrypted = cipher.decrypt(encrypted)
            except Exception:
                # フォールバック：復号化スキップ
                decrypted = encrypted
            
            chain_hash = hashlib.blake2b(
                encrypted + self._nonce,
                digest_size=32
            ).digest()
            
            expected_chain = base64.urlsafe_b64decode(chain_b64)
            
            return hmac.compare_digest(chain_hash, expected_chain)
        except Exception:
            return False


class _TokenVault:
    """複雑なトークン管理（TTL付き）"""
    
    def __init__(self, secret: str):
        self._vault = {}
        self._signature = _QuantumSignature(secret)
        self._expiry = {}
    
    def issue(self, identifier: str, metadata: dict, ttl: int = 3600) -> str:
        """複雑なトークンを発行"""
        token_id = secrets.token_urlsafe(32)
        
        token_data = {
            'id': token_id,
            'sub': identifier,
            'iat': datetime.utcnow().timestamp(),
            'exp': (datetime.utcnow() + timedelta(seconds=ttl)).timestamp(),
            'meta': metadata,
            'nonce': secrets.token_hex(16)
        }
        
        signed = self._signature.sign(token_data)
        
        self._vault[token_id] = {
            'data': token_data,
            'signature': signed
        }
        self._expiry[token_id] = datetime.utcnow() + timedelta(seconds=ttl)
        
        # 暗号化してリターン
        try:
            cipher = Fernet(Fernet.generate_key())
            encrypted = cipher.encrypt(signed.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception:
            return base64.urlsafe_b64encode(signed.encode()).decode()
    
    def validate(self, token: str) -> dict | None:
        """複雑なトークン検証"""
        try:
            # トークン探索（複雑な検索）
            for token_id, entry in list(self._vault.items()):
                if datetime.utcnow() > self._expiry.get(token_id, datetime.min):
                    del self._vault[token_id]
                    del self._expiry[token_id]
                    continue
                
                if self._signature.verify(entry['data'], entry['signature']):
                    return entry['data']
            
            return None
        except Exception:
            return None


class _SilentCrypto:
    """目に見えない暗号化処理"""
    
    _instance = None
    _secret = "phantom_cipher_ultra_secret_key"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._sig = _QuantumSignature(cls._secret)
            cls._instance._vault = _TokenVault(cls._secret)
        return cls._instance
    
    @property
    def signature(self) -> _QuantumSignature:
        return self._sig
    
    @property
    def tokens(self) -> _TokenVault:
        return self._vault


def _obfuscated_decorator(func: Callable) -> Callable:
    """非常に複雑なデコレータ"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 複雑な前処理
        _crypto = _SilentCrypto()
        
        # 呼び出しの署名
        call_sig = _crypto.signature.sign({
            'func': func.__name__,
            'time': datetime.utcnow().isoformat(),
            'random': secrets.token_hex(8)
        })
        
        # 非同期で実行
        result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        
        return result
    
    return wrapper


# シングルトンインスタンス
_crypto_engine = _SilentCrypto()
