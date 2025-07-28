# migration_fix.py - NOVA VERSÃO CORRIGIDA
import sqlite3
from datetime import datetime

def fix_database():
    conn = sqlite3.connect('pesquisa.db')
    cursor = conn.cursor()
    
    try:
        # Verificar estrutura atual
        cursor.execute("PRAGMA table_info(respostas)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Colunas existentes: {columns}")
        
        if 'data_resposta' not in columns:
            print("Adicionando coluna data_resposta...")
            
            # No SQLite, precisamos adicionar coluna sem DEFAULT CURRENT_TIMESTAMP
            cursor.execute('ALTER TABLE respostas ADD COLUMN data_resposta TEXT')
            
            # Depois atualizar todos os registros existentes com a data atual
            data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('UPDATE respostas SET data_resposta = ? WHERE data_resposta IS NULL', (data_atual,))
            
            print("Coluna adicionada e registros atualizados!")
        else:
            print("Coluna data_resposta já existe!")
            
        # Verificar quantos registros existem
        cursor.execute("SELECT COUNT(*) FROM respostas")
        count = cursor.fetchone()[0]
        print(f"Total de registros: {count}")
        
        # Mostrar alguns dados para verificação
        if count > 0:
            cursor.execute("SELECT id, setor, avaliacao, data_resposta FROM respostas LIMIT 3")
            sample_data = cursor.fetchall()
            print("Exemplo de dados:")
            for row in sample_data:
                print(f"  ID: {row[0]}, Setor: {row[1]}, Avaliação: {row[2]}, Data: {row[3]}")
        
        conn.commit()
        print("Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"Erro na migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    fix_database()