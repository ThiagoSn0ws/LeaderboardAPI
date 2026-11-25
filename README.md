# Game Leaderboard API

API REST feita com **FastAPI** para gerenciar ranking de pontuação de jogadores em jogos. Cada jogador se cadastra, faz login (autenticação JWT) e envia pontuações; a API calcula o ranking pela melhor pontuação de cada um.

Projeto pensado como peça de portfólio para vaga de estágio em backend: cobre CRUD, banco de dados relacional, autenticação e testes automatizados — os pontos que mais aparecem em entrevista técnica.

## O que a API faz

- Cadastro e login de jogadores, com senha protegida por hash (bcrypt) e sessão via token JWT.
- Envio de pontuação por jogo (rota protegida — só quem está logado pode enviar).
- Ranking (`/leaderboard`) com a melhor pontuação de cada jogador, filtrável por jogo.
- Histórico de pontuações de um jogador específico.
- Documentação interativa gerada automaticamente pelo FastAPI.

## Stack

- **FastAPI** — framework web
- **SQLAlchemy** — ORM (mapeia classes Python para tabelas do banco)
- **SQLite** — banco de dados (um arquivo só, zero configuração)
- **python-jose** — geração e validação de token JWT
- **bcrypt** — hash de senha
- **pytest** — testes automatizados

## Estrutura do projeto

```
game-leaderboard-api/
├── app/
│   ├── main.py              # cria o app e registra as rotas
│   ├── database.py          # configuração da conexão com o banco
│   ├── models.py            # tabelas (Player, Score)
│   ├── schemas.py           # formato dos dados de entrada/saída da API
│   ├── auth.py               # hash de senha, JWT, dependency de autenticação
│   └── routers/
│       ├── players.py        # registro de jogador, /players/me
│       ├── auth_router.py    # login
│       ├── scores.py         # enviar/listar pontuações
│       └── leaderboard.py    # ranking
├── tests/
│   └── test_api.py           # testes automatizados
├── requirements.txt
└── pytest.ini
```

## Como rodar localmente

```bash
# 1. crie e ative um ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate   # no Windows: venv\Scripts\activate

# 2. instale as dependências
pip install -r requirements.txt

# 3. suba o servidor
uvicorn app.main:app --reload
```

Com o servidor rodando, abra **http://127.0.0.1:8000/docs** — o FastAPI gera uma interface (Swagger UI) onde dá pra testar cada rota clicando, sem precisar de Postman.

## Rodando os testes

```bash
pytest -v
```

Os testes usam um banco SQLite em memória separado do banco real (`leaderboard.db`), então rodar `pytest` nunca mexe nos seus dados.

## Endpoints

| Método | Rota | Autenticação | O que faz |
|---|---|---|---|
| POST | `/players/register` | não | Cria um novo jogador |
| POST | `/auth/login` | não | Retorna um token JWT |
| GET | `/players/me` | sim | Dados do jogador logado |
| POST | `/scores` | sim | Envia uma pontuação |
| GET | `/players/{username}/scores` | não | Histórico de pontuações de um jogador |
| GET | `/leaderboard?game_name=...` | não | Ranking pela melhor pontuação |

### Exemplo de fluxo (via curl)

```bash
# registrar
curl -X POST localhost:8000/players/register \
  -H "Content-Type: application/json" \
  -d '{"username": "thiago", "password": "senha123"}'

# login (retorna o token)
curl -X POST localhost:8000/auth/login \
  -d "username=thiago&password=senha123"

# enviar pontuação (troque SEU_TOKEN pelo access_token recebido no login)
curl -X POST localhost:8000/scores \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"game_name": "tetris", "points": 800}'

# ver o ranking
curl "localhost:8000/leaderboard?game_name=tetris"
```


