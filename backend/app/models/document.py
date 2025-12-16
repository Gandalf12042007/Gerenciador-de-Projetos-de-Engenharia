from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class Documento(Base):
    __tablename__ = "documentos"

    id_documento = Column(Integer, primary_key=True, index=True)
    projeto_id = Column(Integer, ForeignKey("projetos.id_projeto", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    categoria = Column(Enum('planta','diario','rrt_art','medicao','relatorio_fotos','outro', name="categoria_doc"), default='outro')
    arquivo_url = Column(String(512), nullable=False)
    titulo = Column(String(255))
    versao = Column(Integer, default=1)
    criado_em = Column(TIMESTAMP, server_default=func.now())
