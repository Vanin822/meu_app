from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "123456"


# 🔹 CONEXÃO
def conectar():
    return sqlite3.connect("banco.db")


# 🔹 CRIAR TODAS AS TABELAS
def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    # PRODUTOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        preco REAL,
        quantidade INTEGER
    )
    """)

    # FINANCEIRO
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financeiro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        descricao TEXT,
        valor REAL
    )
    """)

    # VENDAS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto TEXT,
        quantidade INTEGER,
        valor REAL
    )
    """)

    conn.commit()
    conn.close()


criar_tabelas()


# 🔹 LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if usuario == "admin" and senha == "123":
            session["usuario"] = usuario
            return redirect("/home")
        else:
            return render_template("login.html", erro="Login inválido")

    return render_template("login.html")


# 🔹 HOME (DASHBOARD)
@app.route("/home")
def home():
    if "usuario" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    # Produtos
    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(preco * quantidade) FROM produtos")
    valor_estoque = cursor.fetchone()[0] or 0

    # Financeiro
    cursor.execute("SELECT SUM(valor) FROM financeiro WHERE tipo='entrada'")
    entrada = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(valor) FROM financeiro WHERE tipo='saida'")
    saida = cursor.fetchone()[0] or 0

    saldo = entrada - saida

    conn.close()

    return render_template(
        "home.html",
        total_produtos=total_produtos,
        valor_estoque=valor_estoque,
        saldo=saldo
    )


# 🔹 PRODUTOS
@app.route("/produtos", methods=["GET", "POST"])
def produtos():
    if "usuario" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    # CADASTRAR
    if request.method == "POST":
        nome = request.form["nome"]
        preco = float(request.form["preco"])
        quantidade = int(request.form["quantidade"])

        cursor.execute(
            "INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)",
            (nome, preco, quantidade)
        )
        conn.commit()

    # LISTAR
    cursor.execute("SELECT * FROM produtos")
    lista = cursor.fetchall()

    conn.close()

    return render_template("produtos.html", produtos=lista)


# 🔹 EXCLUIR PRODUTO
@app.route("/excluir/<int:id>")
def excluir(id):
    if "usuario" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM produtos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect("/produtos")


# 🔹 VENDAS
@app.route("/vendas", methods=["GET", "POST"])
def vendas():
    if "usuario" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    # REGISTRAR VENDA
    if request.method == "POST":
        produto = request.form["produto"]
        quantidade = int(request.form["quantidade"])
        valor = float(request.form["valor"])

        cursor.execute(
            "INSERT INTO vendas (produto, quantidade, valor) VALUES (?, ?, ?)",
            (produto, quantidade, valor)
        )

        # ENTRADA NO FINANCEIRO
        cursor.execute(
            "INSERT INTO financeiro (tipo, descricao, valor) VALUES (?, ?, ?)",
            ("entrada", f"Venda de {produto}", valor)
        )

        conn.commit()

    cursor.execute("SELECT * FROM vendas")
    lista = cursor.fetchall()

    conn.close()

    return render_template("vendas.html", vendas=lista)


# 🔹 FINANCEIRO
@app.route("/financeiro", methods=["GET", "POST"])
def financeiro():
    if "usuario" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        tipo = request.form["tipo"]
        descricao = request.form["descricao"]
        valor = float(request.form["valor"])

        cursor.execute(
            "INSERT INTO financeiro (tipo, descricao, valor) VALUES (?, ?, ?)",
            (tipo, descricao, valor)
        )
        conn.commit()

    cursor.execute("SELECT * FROM financeiro")
    lista = cursor.fetchall()

    entrada = sum([i[3] for i in lista if i[1] == "entrada"])
    saida = sum([i[3] for i in lista if i[1] == "saida"])
    saldo = entrada - saida

    conn.close()

    return render_template("financeiro.html",
                           dados=lista,
                           saldo=saldo)


# 🔹 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)