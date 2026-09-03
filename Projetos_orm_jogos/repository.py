from sqlalchemy import select

from database import Session
from models import Jogo

def listar_jogos():
    with Session() as session:
        consulta = select(Jogo).order_by(Jogo.id.desc())
        return list(session.scalars(consulta))
    
def buscar_jogo(jogo_id):
    with Session() as session:
        return session.get(Jogo, jogo_id)

def criar_jogo(nome, genero, nota, imagem_url=""):
    with Session() as session:
        jogo = Jogo(nome = nome,
                    genero = genero,
                    nota = nota,
                    imagem_url = imagem_url)
        session.add(jogo)
        session.commit()

def atualizar_jogo(jogo_id,nome, genero, nota, imagem_url=""):
    with Session() as session:
        jogo = buscar_jogo(jogo_id)
        if jogo is None: #Se o jogo não for encontrado (não existe.)
            return False

        jogo.nome = nome
        jogo.genero = genero
        jogo.nota = nota
        jogo.imagem_url = imagem_url
        session.commit()
        return True

def excluir_jogo(jogo_id):
    with Session() as session:
        jogo = buscar_jogo(jogo_id)
        if jogo is None:
            return False

        session.delete(jogo)

