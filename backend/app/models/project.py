from sqlalchemy import Column, Integer, String, Date, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class Projeto(Base):
    __tablename__ = "projetos"

    id_projeto = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    cidade = Column(String(120))
    estado = Column(String(80))
    data_inicio = Column(Date)
    data_previsao_fim = Column(Date)
    progresso = Column(DECIMAL(5,2), default=0.0)
    engenheiro_responsavel = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    criado_por = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    criado_em = Column(TIMESTAMP, server_default=func.now())
