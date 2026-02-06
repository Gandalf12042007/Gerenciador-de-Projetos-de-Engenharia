"""
Serviço de Email com SendGrid
Autor: Vicente de Souza
"""

import os
import logging
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent

logger = logging.getLogger(__name__)


class EmailService:
    """Serviço para envio de emails via SendGrid"""
    
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY", "")
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@gerenciador-projetos.com")
        self.from_name = os.getenv("SENDGRID_FROM_NAME", "Gerenciador de Projetos")
        self.app_url = os.getenv("APP_URL", "http://localhost:3000")
        
        if self.api_key:
            self.client = SendGridAPIClient(self.api_key)
        else:
            self.client = None
            logger.warning("SENDGRID_API_KEY não configurada. Emails não serão enviados.")
    
    def is_configured(self) -> bool:
        """Verifica se o serviço está configurado"""
        return bool(self.api_key and self.client)
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None
    ) -> dict:
        """
        Envia um email
        
        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            html_content: Conteúdo HTML do email
            plain_content: Conteúdo texto simples (opcional)
            
        Returns:
            dict com status do envio
        """
        if not self.is_configured():
            logger.error("SendGrid não configurado")
            return {
                "success": False,
                "error": "Serviço de email não configurado. Configure SENDGRID_API_KEY."
            }
        
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            if plain_content:
                message.add_content(Content("text/plain", plain_content))
            
            response = self.client.send(message)
            
            logger.info(f"Email enviado para {to_email} - Status: {response.status_code}")
            
            return {
                "success": True,
                "status_code": response.status_code,
                "message": "Email enviado com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Erro ao enviar email para {to_email}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_invite_code(
        self,
        to_email: str,
        codigo: str,
        projeto_nome: str,
        papel: str,
        convidado_por: str,
        expira_em: str
    ) -> dict:
        """
        Envia um código de convite por email
        
        Args:
            to_email: Email do destinatário
            codigo: Código de convite (6 caracteres)
            projeto_nome: Nome do projeto
            papel: Papel no projeto (gerente, engenheiro, etc)
            convidado_por: Nome de quem convidou
            expira_em: Data de expiração formatada
            
        Returns:
            dict com status do envio
        """
        subject = f"🎉 Convite para o projeto: {projeto_nome}"
        
        # Mapear papéis para português
        papeis_pt = {
            'gerente': 'Gerente',
            'engenheiro': 'Engenheiro',
            'tecnico': 'Técnico',
            'colaborador': 'Colaborador',
            'cliente': 'Cliente'
        }
        papel_display = papeis_pt.get(papel, papel.capitalize())
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 30px;
        }}
        .code-box {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            font-size: 36px;
            font-weight: bold;
            letter-spacing: 8px;
            text-align: center;
            padding: 25px;
            border-radius: 12px;
            margin: 25px 0;
            font-family: 'Courier New', monospace;
        }}
        .info-box {{
            background-color: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }}
        .info-row {{
            display: flex;
            margin: 8px 0;
        }}
        .info-label {{
            font-weight: bold;
            color: #667eea;
            width: 120px;
        }}
        .btn {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            padding: 15px 40px;
            border-radius: 30px;
            font-weight: bold;
            margin: 20px 0;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }}
        .warning {{
            color: #856404;
            background-color: #fff3cd;
            padding: 12px;
            border-radius: 8px;
            margin-top: 20px;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Gerenciador de Projetos</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">Você foi convidado para participar de um projeto!</p>
        </div>
        
        <div class="content">
            <p>Olá! 👋</p>
            
            <p><strong>{convidado_por}</strong> convidou você para participar do projeto com o seguinte código de acesso:</p>
            
            <div class="code-box">
                {codigo}
            </div>
            
            <div class="info-box">
                <div class="info-row">
                    <span class="info-label">📁 Projeto:</span>
                    <span>{projeto_nome}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">👤 Seu papel:</span>
                    <span>{papel_display}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">⏰ Válido até:</span>
                    <span>{expira_em}</span>
                </div>
            </div>
            
            <p style="text-align: center;">
                <a href="{self.app_url}/entrar-projeto.html" class="btn">
                    🚀 Acessar Sistema
                </a>
            </p>
            
            <div class="warning">
                ⚠️ <strong>Importante:</strong> Este código é pessoal e intransferível. 
                Não compartilhe com outras pessoas. O código expira em {expira_em}.
            </div>
        </div>
        
        <div class="footer">
            <p>Este email foi enviado pelo Gerenciador de Projetos de Engenharia</p>
            <p>Se você não solicitou este convite, ignore este email.</p>
        </div>
    </div>
</body>
</html>
"""
        
        plain_content = f"""
Você foi convidado para o projeto: {projeto_nome}

Código de Acesso: {codigo}

Detalhes:
- Projeto: {projeto_nome}
- Seu papel: {papel_display}
- Convidado por: {convidado_por}
- Válido até: {expira_em}

Para usar o código, acesse: {self.app_url}/entrar-projeto.html

Este código é pessoal e intransferível.
"""
        
        return self.send_email(to_email, subject, html_content, plain_content)


# Instância global do serviço
email_service = EmailService()
