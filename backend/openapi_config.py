"""
Configuração de OpenAPI/Swagger para a API
Desenvolvido por: Vicente de Souza
"""

from fastapi.openapi.utils import get_openapi
from typing import Dict, Any


def custom_openapi(app) -> Dict[str, Any]:
    """
    Personaliza esquema OpenAPI com documentação detalhada
    
    Adiciona:
    - Descrições de endpoints
    - Exemplos de request/response
    - Documentação de autenticação
    - Tags de operação
    - Status codes esperados
    """
    
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Gerenciador de Projetos de Engenharia Civil",
        version="2.0.0",
        description="""
        API completa para gerenciamento de projetos de engenharia civil.
        
        ## Recursos Principais:
        
        ### 🔐 Autenticação
        - Registro de usuários com validação de senha forte
        - Login com JWT tokens
        - Autenticação de dois fatores (2FA) via email
        - Validação de tokens
        
        ### 📋 Gerenciamento de Projetos
        - Criar, ler, atualizar e deletar projetos
        - Controlar status, orçamento e cronograma
        - Atribuir equipes a projetos
        
        ### ✅ Tarefas
        - Gerenciar tarefas do projeto
        - Definir prioridades e prazos
        - Rastrear progresso
        
        ### 👥 Equipes
        - Adicionar/remover membros da equipe
        - Definir papéis (admin, manager, técnico, visitante)
        - Controlar permissões
        
        ### 📄 Documentos
        - Upload de documentos com validação de segurança
        - Versionamento de arquivos
        - Suporte para múltiplos tipos de arquivo
        
        ### 🛠️ Materiais e Recursos
        - Registrar materiais necessários
        - Controlar quantidade e custos
        
        ### 💰 Orçamentos
        - Criar e aprovar orçamentos
        - Rastrear gastos vs. orçado
        
        ### 💬 Chat
        - Comunicação em tempo real com equipe
        - Histórico de mensagens
        
        ### 📊 Métricas
        - Relatórios de progresso
        - Timeline do projeto
        - Indicadores de desempenho
        
        ## Segurança
        
        - **Rate Limiting**: 5 logins/min, 100 req/min padrão
        - **2FA Email**: Código OTP com 15 min expiry
        - **Validação de Uploads**: Detecta arquivos disfarçados
        - **HTTPS/TLS**: Recomendado para produção
        - **CORS**: Configurado conforme necessário
        - **JWT**: Tokens com expiração
        
        ## Status HTTP
        
        | Código | Significado |
        |--------|-------------|
        | 200 | OK - Requisição bem-sucedida |
        | 201 | Created - Recurso criado |
        | 204 | No Content - Recurso deletado |
        | 400 | Bad Request - Dados inválidos |
        | 401 | Unauthorized - Autenticação necessária |
        | 403 | Forbidden - Permissão negada |
        | 404 | Not Found - Recurso não encontrado |
        | 429 | Too Many Requests - Rate limit atingido |
        | 500 | Internal Server Error - Erro do servidor |
        
        """,
        routes=app.routes,
        tags=[
            {
                "name": "Autenticação",
                "description": "Endpoints de registro, login e validação",
                "externalDocs": {
                    "description": "Mais informações",
                    "url": "https://github.com/Gandalf12042007/Gerenciador-de-Projetos-de-Engenharia"
                }
            },
            {
                "name": "Projetos",
                "description": "CRUD de projetos de engenharia",
            },
            {
                "name": "Tarefas",
                "description": "Gerenciamento de tarefas",
            },
            {
                "name": "Equipes",
                "description": "Gerenciamento de equipe e permissões",
            },
            {
                "name": "Documentos",
                "description": "Upload, download e versionamento de documentos",
            },
            {
                "name": "Materiais",
                "description": "Registro de materiais necessários",
            },
            {
                "name": "Orçamentos",
                "description": "Gerenciamento de orçamento do projeto",
            },
            {
                "name": "Chat",
                "description": "Comunicação em tempo real",
            },
            {
                "name": "Métricas",
                "description": "Relatórios e indicadores",
            },
        ],
        servers=[
            {
                "url": "http://localhost:8000",
                "description": "Servidor local de desenvolvimento"
            },
            {
                "url": "https://api.seu-dominio.com",
                "description": "Servidor de produção"
            }
        ]
    )
    
    # Adicionar informações de segurança
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Token JWT obtido após login"
        }
    }
    
    # Adicionar exemplos aos componentes
    openapi_schema["components"]["schemas"]["Usuario"] = {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "example": 1},
            "nome": {"type": "string", "example": "Vicente de Souza"},
            "email": {"type": "string", "example": "vicente@exemplo.com"},
            "cargo": {"type": "string", "example": "Engenheiro Civil"},
            "ativo": {"type": "boolean", "example": True},
            "data_criacao": {"type": "string", "format": "date-time"}
        }
    }
    
    openapi_schema["components"]["schemas"]["Projeto"] = {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "example": 1},
            "nome": {"type": "string", "example": "Residencial Vista Verde"},
            "descricao": {"type": "string", "example": "Construção residencial de 20 unidades"},
            "cliente": {"type": "string", "example": "Construtora XYZ"},
            "status": {
                "type": "string",
                "enum": ["planejamento", "em_andamento", "pausado", "concluido"],
                "example": "em_andamento"
            },
            "progresso": {"type": "integer", "minimum": 0, "maximum": 100, "example": 45},
            "orcamento": {"type": "number", "example": 500000.00},
            "data_inicio": {"type": "string", "format": "date"},
            "data_fim": {"type": "string", "format": "date"}
        }
    }
    
    openapi_schema["components"]["schemas"]["Tarefa"] = {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "example": 1},
            "titulo": {"type": "string", "example": "Fundação"},
            "descricao": {"type": "string", "example": "Escavar e preparar fundação"},
            "prioridade": {
                "type": "string",
                "enum": ["baixa", "media", "alta", "critica"],
                "example": "alta"
            },
            "status": {
                "type": "string",
                "enum": ["aberta", "em_andamento", "bloqueada", "concluida"],
                "example": "em_andamento"
            },
            "data_vencimento": {"type": "string", "format": "date"},
            "progresso": {"type": "integer", "minimum": 0, "maximum": 100, "example": 75}
        }
    }
    
    # Atualizar security global (se necessário)
    openapi_schema["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Função para adicionar exemplos a endpoints específicos
def adicionar_exemplos_endpoints(app):
    """
    Adiciona exemplos de request/response aos endpoints
    para melhor documentação no Swagger
    """
    
    # Exemplos de Request
    exemplos_request = {
        "auth/register": {
            "summary": "Registrar novo usuário",
            "examples": {
                "sucesso": {
                    "summary": "Exemplo de sucesso",
                    "value": {
                        "nome": "Vicente de Souza",
                        "email": "vicente@example.com",
                        "senha": "SenhaForte123!",
                        "telefone": "11999999999",
                        "cargo": "Engenheiro Civil"
                    }
                },
                "minimo": {
                    "summary": "Campos mínimos",
                    "value": {
                        "nome": "Vicente",
                        "email": "vicente@example.com",
                        "senha": "SenhaForte123!"
                    }
                }
            }
        },
        "auth/login": {
            "summary": "Fazer login",
            "examples": {
                "credenciais": {
                    "value": {
                        "email": "vicente@example.com",
                        "senha": "SenhaForte123!"
                    }
                }
            }
        },
        "projetos": {
            "summary": "Criar novo projeto",
            "examples": {
                "completo": {
                    "value": {
                        "nome": "Residencial Vista Verde",
                        "descricao": "Construção de 20 unidades residenciais",
                        "cliente": "Construtora ABC",
                        "status": "planejamento",
                        "orcamento": 500000.00,
                        "data_inicio": "2025-01-15",
                        "data_fim": "2026-12-31",
                        "localizacao": "São Paulo, SP"
                    }
                }
            }
        }
    }
    
    # Exemplos de Response
    exemplos_response = {
        "sucesso_201": {
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Recurso criado com sucesso",
                        "id": 1
                    }
                }
            }
        },
        "sucesso_200": {
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {}
                    }
                }
            }
        },
        "erro_400": {
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "detail": "Dados inválidos: email já existe"
                    }
                }
            }
        },
        "erro_401": {
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "detail": "Não autenticado. Forneça token JWT válido."
                    }
                }
            }
        },
        "erro_429": {
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "detail": "Muitas requisições. Tente novamente em 60 segundos.",
                        "retry_after": 60
                    }
                }
            }
        }
    }
    
    return exemplos_request, exemplos_response


# Tags de operação para organizar endpoints
OPERACAO_TAGS = {
    "autenticacao": {
        "name": "Autenticação",
        "description": "Endpoints de autenticação e autorização"
    },
    "projetos": {
        "name": "Projetos",
        "description": "CRUD e gerenciamento de projetos"
    },
    "tarefas": {
        "name": "Tarefas",
        "description": "Gerenciamento de tarefas e atividades"
    },
    "equipes": {
        "name": "Equipes",
        "description": "Gerenciamento de equipe e permissões"
    },
    "documentos": {
        "name": "Documentos",
        "description": "Upload, download e versionamento de documentos"
    },
    "materiais": {
        "name": "Materiais",
        "description": "Registro e controle de materiais"
    },
    "orcamentos": {
        "name": "Orçamentos",
        "description": "Gerenciamento de orçamento do projeto"
    },
    "chat": {
        "name": "Chat",
        "description": "Comunicação em tempo real da equipe"
    },
    "metricas": {
        "name": "Métricas",
        "description": "Relatórios, métricas e indicadores"
    }
}
