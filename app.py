from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "123"


# CONEXÃO
def conectar():
    return sqlite3.connect("banco.db")


# CRIAR TABELAS
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


# LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if usuario == "admin" and senha == "123":
            session["usuario"] = usuario
            return redirect("/home")

        return render_template("login.html", erro="Login inválido")

    return render_template("login.html")


# HOME
@app.route("/home")
def home():
    if "usuario" not in session:
        return redirect("/")

    try:
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

    except Exception as e:
        print("ERRO NO HOME:", e)
        total_produtos = 0
        valor_estoque = 0
        saldo = 0

    return render_template(
        "home.html",
        total_produtos=total_produtos,
        valor_estoque=valor_estoque,
        saldo=saldo
    )

    return render_template(
        "home.html",
        total_produtos=total_produtos,
        valor_estoque=valor_estoque,
        saldo=saldo
    )


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)