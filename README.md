# PesquisaSatisfacao
Um formulário em Python desenvolvido para coletar feedback e avaliar o nível de satisfação de usuários ou clientes. O projeto tem como objetivo simplificar a análise de opiniões, auxiliando na identificação de pontos fortes e oportunidades de melhoria.


-----------INFORMAÇÕES NESCESSÁRIA PARA OUTROS DESENVOLVEDORES

# Pesquisa de Satisfação

## Configuração

1. Clone o projeto
2. Crie um ambiente virtual: `python -m venv venv`
3. Ative: `venv\Scripts\activate` (Windows) ou `source venv/bin/activate` (Linux/Mac)
4. Instale dependências: `pip install -r requirements.txt`
5. Copie `.env.example` para `.env` e configure suas variáveis
6. Execute: `python app.py`

## Variáveis de Ambiente (.env)

- `ADMIN_PASSWORD`: Senha do administrador
- `SECRET_KEY`: Chave secreta do Flask