from sqlalchemy import Column, Integer, String, Text, Enum, Date, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class Tarefa(Base):
    __tablename__ = "tarefas"

    id_tarefa = Column(Integer, primary_key=True, index=True)
    projeto_id = Column(Integer, ForeignKey("projetos.id_projeto", ondelete="CASCADE"), nullable=False)
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text)
    status = Column(Enum('a_fazer','em_execucao','concluida', name="status_enum"), default='a_fazer')
    prioridade = Column(Enum('baixa','media','alta', name="priority_enum"), default='media')
    responsavel_id = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="SET NULL"))
    data_criacao = Column(TIMESTAMP, server_default=func.now())
    prazo = Column(Date)
