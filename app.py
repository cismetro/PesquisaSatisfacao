from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui_mude_para_producao'

# Senha do administrador
ADMIN_PASSWORD = 'dG4rTALaq8'

# Conexão com o banco de dados SQLite
def init_db():
    conn = sqlite3.connect('pesquisa.db')
    cursor = conn.cursor()
    
    # Criar tabela se não existir
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
    
    # Verificar se a coluna data_resposta existe, se não, adicionar
    try:
        cursor.execute("PRAGMA table_info(respostas)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'data_resposta' not in columns:
            cursor.execute('ALTER TABLE respostas ADD COLUMN data_resposta TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            # Atualizar registros existentes com data atual
            cursor.execute('UPDATE respostas SET data_resposta = CURRENT_TIMESTAMP WHERE data_resposta IS NULL')
            print("Coluna data_resposta adicionada e registros atualizados.")
    except Exception as e:
        print(f"Erro na migração: {e}")
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('pesquisa.db')
    conn.row_factory = sqlite3.Row
    return conn

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

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Senha incorreta!', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        conn = get_db_connection()
        
        # Estatísticas gerais
        total_respostas = conn.execute('SELECT COUNT(*) as count FROM respostas').fetchone()['count']
        
        # Avaliação média
        avaliacoes_map = {'pessimo': 1, 'ruim': 2, 'regular': 3, 'bom': 4, 'otimo': 5}
        avaliacoes = conn.execute('SELECT avaliacao FROM respostas').fetchall()
        if avaliacoes:
            soma = sum(avaliacoes_map.get(av['avaliacao'], 0) for av in avaliacoes)
            media = round(soma / len(avaliacoes), 1)
        else:
            media = 0
        
        # Setor mais avaliado
        setor_mais_avaliado = conn.execute('''
            SELECT setor, COUNT(*) as count 
            FROM respostas 
            GROUP BY setor 
            ORDER BY count DESC 
            LIMIT 1
        ''').fetchone()
        
        # Última resposta - verificar se a coluna existe
        try:
            ultima_resposta = conn.execute('''
                SELECT data_resposta 
                FROM respostas 
                ORDER BY id DESC 
                LIMIT 1
            ''').fetchone()
        except sqlite3.OperationalError:
            # Se a coluna não existir, usar o ID como referência
            ultima_resposta = conn.execute('''
                SELECT 'ID: ' || id as data_resposta
                FROM respostas 
                ORDER BY id DESC 
                LIMIT 1
            ''').fetchone()
        
        # Filtros
        setor_filtro = request.args.get('setor', '')
        avaliacao_filtro = request.args.get('avaliacao', '')
        
        # Query base - verificar se data_resposta existe
        try:
            # Tentar usar data_resposta
            query = 'SELECT *, data_resposta FROM respostas WHERE 1=1'
        except:
            # Se não existir, usar apenas os campos básicos
            query = 'SELECT *, id as data_resposta FROM respostas WHERE 1=1'
        
        params = []
        
        if setor_filtro:
            query += ' AND setor = ?'
            params.append(setor_filtro)
        
        if avaliacao_filtro:
            query += ' AND avaliacao = ?'
            params.append(avaliacao_filtro)
        
        query += ' ORDER BY id DESC'
        
        respostas = conn.execute(query, params).fetchall()
        
        # Setores únicos para o filtro
        setores_unicos = conn.execute('SELECT DISTINCT setor FROM respostas ORDER BY setor').fetchall()
        
        conn.close()
        
        estatisticas = {
            'total_respostas': total_respostas,
            'avaliacao_media': media,
            'setor_mais_avaliado': setor_mais_avaliado['setor'].replace('_', ' ') if setor_mais_avaliado else 'N/A',
            'ultima_resposta': ultima_resposta['data_resposta'] if ultima_resposta else 'N/A'
        }
        
        return render_template('admin_dashboard.html', 
                             estatisticas=estatisticas,
                             respostas=respostas,
                             setores_unicos=setores_unicos,
                             setor_filtro=setor_filtro,
                             avaliacao_filtro=avaliacao_filtro)
    
    except Exception as e:
        return f"<h1>Erro:</h1><p>{str(e)}</p><a href='/admin/login'>Voltar</a>"

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('formulario'))

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5050, debug=False)