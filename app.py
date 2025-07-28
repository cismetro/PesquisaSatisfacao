from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configurações - carregar do .env
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
SECRET_KEY = os.getenv('SECRET_KEY')

# Verificar se as variáveis foram definidas
if not ADMIN_PASSWORD:
    raise ValueError("❌ ADMIN_PASSWORD não foi definida no arquivo .env")
if not SECRET_KEY:
    raise ValueError("❌ SECRET_KEY não foi definida no arquivo .env")

print("✅ Configurações carregadas do arquivo .env")

app.secret_key = SECRET_KEY

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
            data_resposta TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('pesquisa.db')
    conn.row_factory = sqlite3.Row
    return conn

def check_column_exists(conn, table_name, column_name):
    """Verifica se uma coluna existe na tabela"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    return column_name in columns

@app.route('/', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        setor = request.form['setor']
        avaliacao = request.form['avaliacao']
        identificacao = request.form['identificacao']
        nome = request.form.get('nome', '')
        contato = request.form.get('contato', '')
        opiniao = request.form.get('opiniao', '')
        
        # Data atual formatada
        data_resposta = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Inserindo dados no banco
        conn = sqlite3.connect('pesquisa.db')
        cursor = conn.cursor()
        
        # Verificar se a coluna data_resposta existe
        cursor.execute("PRAGMA table_info(respostas)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'data_resposta' in columns:
            cursor.execute('''
                INSERT INTO respostas (setor, avaliacao, identificacao, nome, contato, opiniao, data_resposta)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (setor, avaliacao, identificacao, nome, contato, opiniao, data_resposta))
        else:
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
        
        # Verificar se a coluna data_resposta existe
        has_data_resposta = check_column_exists(conn, 'respostas', 'data_resposta')
        
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
        
        # Última resposta
        if has_data_resposta:
            ultima_resposta = conn.execute('''
                SELECT data_resposta 
                FROM respostas 
                WHERE data_resposta IS NOT NULL
                ORDER BY id DESC 
                LIMIT 1
            ''').fetchone()
            ultima_info = ultima_resposta['data_resposta'] if ultima_resposta else 'N/A'
        else:
            ultima_resposta = conn.execute('''
                SELECT id
                FROM respostas 
                ORDER BY id DESC 
                LIMIT 1
            ''').fetchone()
            ultima_info = f"ID: {ultima_resposta['id']}" if ultima_resposta else 'N/A'
        
        # Filtros
        setor_filtro = request.args.get('setor', '')
        avaliacao_filtro = request.args.get('avaliacao', '')
        
        # Query base - usar data_resposta se existir, senão usar id
        if has_data_resposta:
            base_query = 'SELECT id, setor, avaliacao, identificacao, nome, contato, opiniao, data_resposta FROM respostas WHERE 1=1'
        else:
            base_query = 'SELECT id, setor, avaliacao, identificacao, nome, contato, opiniao, "Registro #" || id as data_resposta FROM respostas WHERE 1=1'
        
        params = []
        
        if setor_filtro:
            base_query += ' AND setor = ?'
            params.append(setor_filtro)
        
        if avaliacao_filtro:
            base_query += ' AND avaliacao = ?'
            params.append(avaliacao_filtro)
        
        base_query += ' ORDER BY id DESC'
        
        respostas = conn.execute(base_query, params).fetchall()
        
        # Setores únicos para o filtro
        setores_unicos = conn.execute('SELECT DISTINCT setor FROM respostas ORDER BY setor').fetchall()
        
        conn.close()
        
        estatisticas = {
            'total_respostas': total_respostas,
            'avaliacao_media': media,
            'setor_mais_avaliado': setor_mais_avaliado['setor'].replace('_', ' ') if setor_mais_avaliado else 'N/A',
            'ultima_resposta': ultima_info
        }
        
        return render_template('admin_dashboard.html', 
                             estatisticas=estatisticas,
                             respostas=respostas,
                             setores_unicos=setores_unicos,
                             setor_filtro=setor_filtro,
                             avaliacao_filtro=avaliacao_filtro,
                             has_data_resposta=has_data_resposta)
    
    except Exception as e:
        return f"<h1>Erro Debug:</h1><p>{str(e)}</p><a href='/admin/login'>Voltar</a>"

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