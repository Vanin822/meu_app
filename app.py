from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# =========================
# DASHBOARD
# =========================
@app.route("/")
def dashboard():
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(preco * quantidade) FROM produtos")
    valor_estoque = cursor.fetchone()[0] or 0

    conexao.close()

    return render_template(
        "inicio.html",
        total_produtos=total_produtos,
        valor_estoque=valor_estoque
    )

# =========================
# LISTAR PRODUTOS
# =========================
@app.route("/produtos")
def produtos():
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()

    conexao.close()

    return render_template("produtos.html", produtos=produtos)

# =========================
# ADICIONAR PRODUTO
# =========================
@app.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        nome = request.form.get("nome")
        preco = request.form.get("preco")
        quantidade = request.form.get("quantidade")

        conexao = sqlite3.connect("banco.db")
        cursor = conexao.cursor()

        cursor.execute(
            "INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)",
            (nome, preco, quantidade)
        )

        conexao.commit()
        conexao.close()

        return redirect("/produtos")

    return render_template("novo.html")

# =========================
# EXCLUIR PRODUTO
# =========================
@app.route("/excluir/<int:id>")
def excluir(id):
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("DELETE FROM produtos WHERE id = ?", (id,))

    conexao.commit()
    conexao.close()

    return redirect("/produtos")

# =========================
# EDITAR PRODUTO
# =========================
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    if request.method == "POST":
        nome = request.form.get("nome")
        preco = request.form.get("preco")
        quantidade = request.form.get("quantidade")

        cursor.execute(
            "UPDATE produtos SET nome=?, preco=?, quantidade=? WHERE id=?",
            (nome, preco, quantidade, id)
        )

        conexao.commit()
        conexao.close()

        return redirect("/produtos")

    cursor.execute("SELECT * FROM produtos WHERE id=?", (id,))
    produto = cursor.fetchone()

    conexao.close()

    return render_template("editar.html", produto=produto)


# =========================
# RODAR O SERVIDOR
# =========================
if __name__ == "__main__":
    app.run(debug=True)