from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class Orcamento(Base):
    __tablename__ = "orcamentos"

    id_orcamento = Column(Integer, primary_key=True, index=True)
    projeto_id = Column(Integer, ForeignKey("projetos.id_projeto", ondelete="CASCADE"), nullable=False)
    descricao = Column(String(255))
    valor_previsto = Column(DECIMAL(12,2), default=0.00)
    valor_gasto = Column(DECIMAL(12,2), default=0.00)
    criado_em = Column(TIMESTAMP, server_default=func.now())
