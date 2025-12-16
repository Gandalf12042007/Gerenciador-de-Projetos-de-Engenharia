from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class Material(Base):
    __tablename__ = "materiais"

    id_material = Column(Integer, primary_key=True, index=True)
    projeto_id = Column(Integer, ForeignKey("projetos.id_projeto", ondelete="CASCADE"), nullable=False)
    nome = Column(String(200), nullable=False)
    unidade = Column(String(50))
    quantidade_prevista = Column(DECIMAL(12,2), default=0)
    quantidade_consumida = Column(DECIMAL(12,2), default=0)
    criado_em = Column(TIMESTAMP, server_default=func.now())
