from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "123456"  # chave da sessão

def criar_tabela_financeiro():
    import sqlite3
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()

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


criar_tabela_financeiro()
# 🔹 CONEXÃO COM BANCO
def conectar():
    return sqlite3.connect("banco.db")


# 🔹 LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        # LOGIN SIMPLES (fixo)
        if usuario == "admin" and senha == "123":
            session["usuario"] = usuario
            return redirect("/home")
        else:
            return render_template("login.html", erro="Usuário ou senha inválidos")

    return render_template("login.html")


# 🔹 HOME (PROTEGIDA)
@app.route("/home")
def home():
    if "usuario" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    # total de produtos
    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0]

    # valor total estoque
    cursor.execute("SELECT SUM(preco * quantidade) FROM produtos")
    valor_estoque = cursor.fetchone()[0]

    if valor_estoque is None:
        valor_estoque = 0

    conn.close()

    return render_template(
        "home.html",
        total_produtos=total_produtos,
        valor_estoque=valor_estoque
    )


# 🔹 PRODUTOS
@app.route("/produtos")
def produtos():
    if "usuario" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM produtos")
    lista = cursor.fetchall()

    conn.close()

    return render_template("produtos.html", produtos=lista)


# 🔹 ADICIONAR PRODUTO
@app.route("/adicionar", methods=["GET", "POST"])
def adicionar():
    if "usuario" not in session:
        return redirect("/")

    if request.method == "POST":
        nome = request.form["nome"]
        preco = request.form["preco"]
        quantidade = request.form["quantidade"]

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)",
            (nome, preco, quantidade)
        )

        conn.commit()
        conn.close()

        return redirect("/produtos")

    return render_template("adicionar.html")


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


# 🔹 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# 🔹 RODAR
if __name__ == "__main__":
    app.run(debug=True)