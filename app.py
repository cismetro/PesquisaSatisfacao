from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Conexão com o banco de dados SQLite
def init_db():
    conn = sqlite3.connect('pesquisa.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS respostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setor TEXT,
            avaliacao TEXT,
            identificacao TEXT,
            nome TEXT,
            contato TEXT,
            opiniao TEXT,
            data_resposta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        setor = request.form['setor']
        avaliacao = request.form['avaliacao']
        identificacao = request.form['identificacao']
        nome = request.form.get('nome', '')
        contato = request.form.get('contato', '')
        opiniao = request.form.get('opiniao', '')

        # Inserindo dados no banco
        conn = sqlite3.connect('pesquisa.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO respostas (setor, avaliacao, identificacao, nome, contato, opiniao)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (setor, avaliacao, identificacao, nome, contato, opiniao))
        conn.commit()
        conn.close()

        return render_template('success.html')

    return render_template('formulario.html')

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5050, debug=False)