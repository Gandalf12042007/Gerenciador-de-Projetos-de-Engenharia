from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class EquipeProjeto(Base):
    __tablename__ = "equipe_projeto"

    id_equipe = Column(Integer, primary_key=True, index=True)
    projeto_id = Column(Integer, ForeignKey("projetos.id_projeto", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    funcao = Column(String(100))

    pode_criar_tarefas = Column(Boolean, default=False)
    pode_excluir_tarefas = Column(Boolean, default=False)
    pode_editar_documentos = Column(Boolean, default=False)
    pode_acessar_orcamento = Column(Boolean, default=False)
    pode_admin_equipe = Column(Boolean, default=False)

    criado_em = Column(TIMESTAMP, server_default=func.now())
