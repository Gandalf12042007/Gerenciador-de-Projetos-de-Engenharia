from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class ComentarioTarefa(Base):
    __tablename__ = "comentarios_tarefa"

    id_comentario = Column(Integer, primary_key=True, index=True)
    tarefa_id = Column(Integer, ForeignKey("tarefas.id_tarefa", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    comentario = Column(Text, nullable=False)
    criado_em = Column(TIMESTAMP, server_default=func.now())
