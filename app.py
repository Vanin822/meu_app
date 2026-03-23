import os
import sqlite3
from flask import Flask, render_template, request, redirect, session

# 🔵 CAMINHO DO PROJETO
base_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = "chave_super_secreta"


# 🔵 CONEXÃO PADRÃO (SEMPRE USA ESSE)
def conectar():
    caminho = os.path.join(base_dir, "banco.db")
    return sqlite3.connect(caminho)


# 🔵 CRIAR BANCO (SEM ERRO)
def criar_banco():
    con = conectar()
    cur = con.cursor()

    # PRODUTOS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        preco REAL,
        quantidade INTEGER
    )
    """)

    # VENDAS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        quantidade INTEGER,
        valor_total REAL,
        data TEXT
    )
    """)

    # COLABORADORES
    cur.execute("""
    CREATE TABLE IF NOT EXISTS colaboradores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        cargo TEXT,
        email TEXT
    )
    """)

    con.commit()
    con.close()


# 🔥 CRIA O BANCO AO INICIAR
criar_banco()


# 🔵 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if usuario == "admin" and senha == "123":
            session["logado"] = True
            return redirect("/home")

    return render_template("login.html")


# 🔵 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# 🔵 INICIO
@app.route("/")
def inicio():
    return redirect("/login")


# 🔵 HOME
@app.route("/home")
def home():
    if "logado" not in session:
        return redirect("/login")

    con = conectar()
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cur.fetchone()[0]

    cur.execute("SELECT SUM(preco * quantidade) FROM produtos")
    valor_estoque = cur.fetchone()[0] or 0

    con.close()

    return "<h1>TESTE APP PY</h1>"
                           total_produtos=total_produtos,
                           valor_estoque=valor_estoque)


# 🔵 PRODUTOS
@app.route("/produtos", methods=["GET", "POST"])
def produtos():
    if "logado" not in session:
        return redirect("/login")

    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        nome = request.form.get("nome")
        preco_compra = float(request.form.get("preco_compra"))
        porcentagem = float(request.form.get("porcentagem"))
        quantidade = int(request.form.get("quantidade"))

        preco = preco_compra + (preco_compra * porcentagem / 100)

        cur.execute(
            "INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)",
            (nome, preco, quantidade)
        )

        con.commit()
        return redirect("/produtos")

    cur.execute("SELECT * FROM produtos")
    produtos = cur.fetchall()

    con.close()

    return render_template("produtos.html", produtos=produtos)


# 🔵 EXCLUIR PRODUTO
@app.route("/excluir/<int:id>")
def excluir(id):
    con = conectar()
    cur = con.cursor()

    cur.execute("DELETE FROM produtos WHERE id=?", (id,))
    con.commit()
    con.close()

    return redirect("/produtos")


# 🔵 EDITAR PRODUTO
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        nome = request.form.get("nome")
        preco = request.form.get("preco")
        quantidade = request.form.get("quantidade")

        cur.execute(
            "UPDATE produtos SET nome=?, preco=?, quantidade=? WHERE id=?",
            (nome, preco, quantidade, id)
        )

        con.commit()
        return redirect("/produtos")

    cur.execute("SELECT * FROM produtos WHERE id=?", (id,))
    produto = cur.fetchone()

    con.close()

    return render_template("estoque.html", produto=produto)


# 🔵 COLABORADORES
@app.route("/colaborador", methods=["GET", "POST"])
def colaborador():
    if "logado" not in session:
        return redirect("/login")

    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        nome = request.form.get("nome")
        cargo = request.form.get("cargo")
        email = request.form.get("email")

        cur.execute(
            "INSERT INTO colaboradores (nome, cargo, email) VALUES (?, ?, ?)",
            (nome, cargo, email)
        )

        con.commit()
        return redirect("/colaborador")

    cur.execute("SELECT * FROM colaboradores")
    colaboradores = cur.fetchall()

    con.close()

    return render_template("colaborador.html", colaboradores=colaboradores)


# 🔵 EXCLUIR COLABORADOR
@app.route("/excluir_colaborador/<int:id>")
def excluir_colaborador(id):
    con = conectar()
    cur = con.cursor()

    cur.execute("DELETE FROM colaboradores WHERE id=?", (id,))
    con.commit()
    con.close()

    return redirect("/colaborador")


# 🔵 VENDAS
@app.route("/vendas", methods=["GET", "POST"])
def vendas():
    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        produto_id = int(request.form.get("produto"))
        quantidade = int(request.form.get("quantidade"))

        cur.execute("SELECT preco, quantidade FROM produtos WHERE id=?", (produto_id,))
        produto = cur.fetchone()

        preco = produto[0]
        estoque = produto[1]

        if quantidade <= estoque:
            total = preco * quantidade

            cur.execute(
                "INSERT INTO vendas (produto_id, quantidade, valor_total, data) VALUES (?, ?, ?, datetime('now'))",
                (produto_id, quantidade, total)
            )

            cur.execute(
                "UPDATE produtos SET quantidade = quantidade - ? WHERE id=?",
                (quantidade, produto_id)
            )

            con.commit()

    cur.execute("SELECT id, nome FROM produtos")
    produtos = cur.fetchall()

    con.close()

    return render_template("vendas.html", produtos=produtos)


# 🔵 FINANCEIRO
@app.route("/financeiro")
def financeiro():
    con = conectar()
    cur = con.cursor()

    cur.execute("SELECT SUM(valor_total) FROM vendas")
    total_vendas = cur.fetchone()[0] or 0

    con.close()

    return render_template("financeiro.html", total_vendas=total_vendas)
@app.route("/estoque")
def estoque():
    if "logado" not in session:
        return redirect("/login")

    con = conectar()
    cur = con.cursor()

    cur.execute("SELECT * FROM produtos")
    produtos = cur.fetchall()

    con.close()

    return render_template("estoque.html", produtos=produtos)


if __name__ == "__main__":
    app.run()