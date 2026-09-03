from flask import Flask, abort, redirect, render_template, request, url_for

import repository
from database import criar_banco


app = Flask(__name__)


@app.get("/")
def index():
    jogos = repository.listar_jogos()
    return render_template("index.html", jogos=jogos)


@app.post("/cadastrar")
def cadastrar():
    repository.criar_jogo(
        nome=request.form["nome"],
        genero=request.form["genero"],
        nota=float(request.form["nota"]),
        imagem_url=request.form.get("imagem_url", ""),
    )
    return redirect(url_for("index"))


@app.route("/editar/<int:jogo_id>", methods=["GET", "POST"])
def editar(jogo_id):
    jogo = repository.buscar_jogo(jogo_id)
    if jogo is None:
        abort(404)

    if request.method == "POST":
        repository.atualizar_jogo(
            jogo_id=jogo_id,
            nome=request.form["nome"],
            genero=request.form["genero"],
            nota=float(request.form["nota"]),
            imagem_url=request.form.get("imagem_url", ""),
        )
        return redirect(url_for("index"))

    return render_template("editar.html", jogo=jogo)


@app.post("/excluir/<int:jogo_id>")
def excluir(jogo_id):
    if not repository.excluir_jogo(jogo_id):
        abort(404)
    return redirect(url_for("index"))


if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)
