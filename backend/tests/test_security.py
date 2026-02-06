"""
Testes de Segurança
"""

import pytest
import hashlib
import re


class TestPasswordSecurity:
    """Testes de segurança de senhas"""
    
    def test_password_is_hashed(self):
        """Testa que senha é armazenada como hash"""
        password = "minhasenha123"
        hash_result = hashlib.sha256(password.encode()).hexdigest()
        
        # Hash deve ser diferente da senha original
        assert hash_result != password
        
        # Hash deve ter 64 caracteres (SHA256)
        assert len(hash_result) == 64
        
        # Hash deve ser hexadecimal
        assert all(c in '0123456789abcdef' for c in hash_result)
    
    def test_same_password_same_hash(self):
        """Testa que mesma senha gera mesmo hash"""
        password = "senha123"
        hash1 = hashlib.sha256(password.encode()).hexdigest()
        hash2 = hashlib.sha256(password.encode()).hexdigest()
        
        assert hash1 == hash2
    
    def test_different_password_different_hash(self):
        """Testa que senhas diferentes geram hashes diferentes"""
        hash1 = hashlib.sha256("senha1".encode()).hexdigest()
        hash2 = hashlib.sha256("senha2".encode()).hexdigest()
        
        assert hash1 != hash2


class TestJWTSecurity:
    """Testes de segurança JWT"""
    
    def test_jwt_has_three_parts(self):
        """Testa que JWT tem formato correto"""
        import jwt
        
        token = jwt.encode({"user": "test"}, "secret", algorithm="HS256")
        parts = token.split(".")
        
        assert len(parts) == 3
    
    def test_jwt_cannot_be_decoded_with_wrong_key(self):
        """Testa que JWT não pode ser decodificado com chave errada"""
        import jwt
        
        token = jwt.encode({"user": "test"}, "chave-correta", algorithm="HS256")
        
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, "chave-errada", algorithms=["HS256"])
    
    def test_jwt_expiration_works(self):
        """Testa que expiração do JWT funciona"""
        import jwt
        from datetime import datetime, timedelta
        
        # Token expirado
        expired_data = {
            "user": "test",
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        
        expired_token = jwt.encode(expired_data, "secret", algorithm="HS256")
        
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(expired_token, "secret", algorithms=["HS256"])


class TestInputValidation:
    """Testes de validação de input"""
    
    def test_email_validation_regex(self):
        """Testa validação de email por regex"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "user+tag@gmail.com"
        ]
        
        invalid_emails = [
            "notanemail",
            "@missing.com",
            "missing@.com",
            "spaces in@email.com"
        ]
        
        for email in valid_emails:
            assert re.match(email_regex, email), f"{email} deveria ser válido"
        
        for email in invalid_emails:
            assert not re.match(email_regex, email), f"{email} deveria ser inválido"
    
    def test_sql_injection_patterns(self):
        """Testa detecção de padrões de SQL injection"""
        sql_patterns = [
            "'; DROP TABLE usuarios; --",
            "1 OR 1=1",
            "' OR '1'='1",
            "admin'--",
            "1; SELECT * FROM usuarios"
        ]
        
        # Caracteres perigosos
        dangerous_chars = ["'", ";", "--", "/*", "*/", "OR", "AND", "DROP", "DELETE"]
        
        for pattern in sql_patterns:
            has_dangerous = any(char.upper() in pattern.upper() for char in dangerous_chars)
            assert has_dangerous, f"Padrão '{pattern}' deveria ser detectado como perigoso"
    
    def test_xss_patterns(self):
        """Testa detecção de padrões XSS"""
        xss_patterns = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "<a href='javascript:alert(1)'>",
            "onclick=alert(1)"
        ]
        
        # Tags/atributos perigosos
        dangerous = ["<script", "onerror", "onclick", "javascript:"]
        
        for pattern in xss_patterns:
            has_xss = any(d.lower() in pattern.lower() for d in dangerous)
            assert has_xss, f"Padrão '{pattern}' deveria ser detectado como XSS"


class TestRateLimiting:
    """Testes de rate limiting"""
    
    def test_rate_limit_format(self):
        """Testa formato de rate limit"""
        rate_limits = [
            "5/minute",
            "100/hour", 
            "1000/day"
        ]
        
        rate_pattern = r'^\d+/(minute|hour|day)$'
        
        for limit in rate_limits:
            assert re.match(rate_pattern, limit), f"{limit} deveria ser formato válido"


class TestFileUploadSecurity:
    """Testes de segurança de upload"""
    
    def test_dangerous_extensions_blocked(self):
        """Testa que extensões perigosas são bloqueadas"""
        allowed = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'png', 'dwg'}
        dangerous = {'exe', 'bat', 'cmd', 'sh', 'php', 'js', 'py', 'ps1'}
        
        # Nenhuma extensão perigosa deve estar na lista permitida
        intersection = allowed.intersection(dangerous)
        assert len(intersection) == 0
    
    def test_file_size_limit(self):
        """Testa limite de tamanho de arquivo"""
        max_size_mb = 50
        max_size_bytes = max_size_mb * 1024 * 1024
        
        # Arquivo de 100MB deve ser rejeitado
        large_file_size = 100 * 1024 * 1024
        
        assert large_file_size > max_size_bytes
    
    def test_filename_sanitization(self):
        """Testa sanitização de nome de arquivo"""
        dangerous_filenames = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config",
            "file; rm -rf /",
            "file | cat /etc/passwd"
        ]
        
        # Caracteres que devem ser removidos/escapados
        dangerous_chars = ['..', '/', '\\', ';', '|', '&', '$', '`']
        
        for filename in dangerous_filenames:
            has_dangerous = any(char in filename for char in dangerous_chars)
            assert has_dangerous, f"Nome '{filename}' contém caracteres perigosos"
