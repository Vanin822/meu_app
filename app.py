from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "123"


def conectar():
    return sqlite3.connect("banco.db")


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        preco REAL,
        quantidade INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto TEXT,
        quantidade INTEGER,
        valor REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financeiro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        descricao TEXT,
        valor REAL
    )
    """)

    conn.commit()
    conn.close()


criar_tabelas()


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["usuario"] == "admin" and request.form["senha"] == "123":
            session["usuario"] = "admin"
            return redirect("/home")
        return render_template("login.html", erro="Login inválido")

    return render_template("login.html")


@app.route("/home")
def home():
    if "usuario" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(preco * quantidade) FROM produtos")
    valor_estoque = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(valor) FROM financeiro WHERE tipo='entrada'")
    entrada = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(valor) FROM financeiro WHERE tipo='saida'")
    saida = cursor.fetchone()[0] or 0

    saldo = entrada - saida

    conn.close()

    return render_template("home.html",
                           total_produtos=total_produtos,
                           valor_estoque=valor_estoque,
                           saldo=saldo)


@app.route("/produtos", methods=["GET", "POST"])
def produtos():
    if "usuario" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        nome = request.form["nome"]
        preco = float(request.form["preco"])
        quantidade = int(request.form["quantidade"])

        cursor.execute("INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)",
                       (nome, preco, quantidade))
        conn.commit()

    cursor.execute("SELECT * FROM produtos")
    lista = cursor.fetchall()

    conn.close()
    return render_template("produtos.html", produtos=lista)


@app.route("/vendas", methods=["GET", "POST"])
def vendas():
    if "usuario" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        produto_id = request.form["produto_id"]
        quantidade = int(request.form["quantidade"])

        cursor.execute("SELECT nome, preco, quantidade FROM produtos WHERE id=?", (produto_id,))
        p = cursor.fetchone()

        if p:
            nome, preco, estoque = p

            if quantidade <= estoque:
                total = preco * quantidade

                cursor.execute("UPDATE produtos SET quantidade=? WHERE id=?",
                               (estoque - quantidade, produto_id))

                cursor.execute("INSERT INTO vendas (produto, quantidade, valor) VALUES (?, ?, ?)",
                               (nome, quantidade, total))

                cursor.execute("INSERT INTO financeiro (tipo, descricao, valor) VALUES (?, ?, ?)",
                               ("entrada", f"Venda de {nome}", total))

                conn.commit()

    cursor.execute("SELECT * FROM vendas")
    vendas_lista = cursor.fetchall()

    cursor.execute("SELECT id, nome FROM produtos")
    produtos = cursor.fetchall()

    conn.close()

    return render_template("vendas.html",
                           vendas=vendas_lista,
                           produtos=produtos)


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

        cursor.execute("INSERT INTO financeiro (tipo, descricao, valor) VALUES (?, ?, ?)",
                       (tipo, descricao, valor))
        conn.commit()

    cursor.execute("SELECT * FROM financeiro")
    dados = cursor.fetchall()

    entrada = sum([i[3] for i in dados if i[1] == "entrada"])
    saida = sum([i[3] for i in dados if i[1] == "saida"])
    saldo = entrada - saida

    conn.close()

    return render_template("financeiro.html",
                           dados=dados,
                           saldo=saldo)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)