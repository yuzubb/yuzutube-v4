"""セキュリティパッケージ"""

try:
    from .crypto import _crypto_engine, _QuantumSignature, _TokenVault, _obfuscated_decorator
except ImportError as e:
    import warnings
    warnings.warn(f"Crypto import error (Vercel compatible): {e}")
    # フォールバック用のダミー実装
    class _DummyCrypto:
        def __init__(self):
            self.tokens = type('obj', (object,), {
                'issue': lambda *args, **kwargs: "dummy_token"
            })()
            self.signature = type('obj', (object,), {
                'sign': lambda *args: "dummy_signature"
            })()
    
    _crypto_engine = _DummyCrypto()
    _QuantumSignature = type('_QuantumSignature', (), {})
    _TokenVault = type('_TokenVault', (), {})
    _obfuscated_decorator = lambda f: f

__all__ = [
    '_crypto_engine',
    '_QuantumSignature',
    '_TokenVault',
    '_obfuscated_decorator'
]
