from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# criar banco de dados
def criar_banco():
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        preco TEXT,
        quantidade INTEGER
    )
    """)

    conexao.commit()
    conexao.close()

criar_banco()

# pagina inicial


@app.route("/")
def inicio():

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(preco * quantidade) FROM produtos")
    valor_estoque = cursor.fetchone()[0]

    if valor_estoque == None:
        valor_estoque = 0

    conexao.close()

    return render_template(
        "inicio.html",
        total_produtos=total_produtos,
        valor_estoque=valor_estoque
    )   

# pagina produtos
@app.route("/produtos", methods=["GET","POST"])
def produtos():

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    busca = request.args.get("busca")

    if request.method == "POST":

        nome = request.form.get("nome")
        preco = request.form.get("preco")
        quantidade = request.form.get("quantidade")

        cursor.execute(
            "INSERT INTO produtos (nome, preco, quantidade) VALUES (?,?,?)",
            (nome, preco, quantidade)
        )

        conexao.commit()

    if busca:
        cursor.execute("SELECT * FROM produtos WHERE nome LIKE ?", ('%' + busca + '%',))
    else:
        cursor.execute("SELECT * FROM produtos")

    produtos = cursor.fetchall()

    conexao.close()

    return render_template("produtos.html", produtos=produtos)

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    if request.method == "POST":

        nome = request.form.get("nome")
        preco = request.form.get("preco")
        quantidade = request.form.get("quantidade")

        cursor.execute(
            "INSERT INTO produtos (nome, preco, quantidade) VALUES (?,?,?)",
            (nome, preco, quantidade)
        )

        conexao.commit()

    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()

    conexao.close()

    return render_template("produtos.html", produtos=produtos)

# excluir produto
@app.route("/excluir/<int:id>")
def excluir(id):

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("DELETE FROM produtos WHERE id = ?", (id,))

    conexao.commit()
    conexao.close()

    return redirect("/produtos")

@app.route("/editar/<int:id>", methods=["GET","POST"])
def editar(id):

produtos = cursor.fetchall()

conexao.close()

return render_template("produtos.html", produtos=produtos)
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

app.run(debug=True)