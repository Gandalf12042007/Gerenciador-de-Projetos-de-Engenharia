from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class ChatMensagem(Base):
    __tablename__ = "chat_mensagens"

    id_mensagem = Column(Integer, primary_key=True, index=True)
    projeto_id = Column(Integer, ForeignKey("projetos.id_projeto", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    mensagem = Column(Text, nullable=False)
    criado_em = Column(TIMESTAMP, server_default=func.now())
