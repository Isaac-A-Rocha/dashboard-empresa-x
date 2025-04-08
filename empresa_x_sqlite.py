import sqlite3
import pandas as pd
import random
from datetime import datetime
from faker import Faker


fake = Faker('pt_BR')
random.seed(42)

# Conexão 
conn = sqlite3.connect('empresa_x.db')
cursor = conn.cursor()

# Reset 
cursor.execute("DROP TABLE IF EXISTS marcas")
cursor.execute("DROP TABLE IF EXISTS vendas_mensais")
cursor.execute("DROP TABLE IF EXISTS campanhas")

# tabelas
cursor.execute("""
CREATE TABLE marcas (
    id_marca INTEGER PRIMARY KEY,
    nome_marca TEXT
)
""")

cursor.execute("""
CREATE TABLE vendas_mensais (
    id_venda INTEGER PRIMARY KEY AUTOINCREMENT,
    id_marca INTEGER,
    ano INTEGER,
    mes INTEGER,
    faturamento REAL,
    qtd_vendas INTEGER,
    FOREIGN KEY(id_marca) REFERENCES marcas(id_marca)
)
""")

cursor.execute("""
CREATE TABLE campanhas (
    id_campanha INTEGER PRIMARY KEY AUTOINCREMENT,
    id_marca INTEGER,
    nome_campanha TEXT,
    data_inicio TEXT,
    data_fim TEXT,
    valor_investido REAL,
    FOREIGN KEY(id_marca) REFERENCES marcas(id_marca)
)
""")


marcas = ['Marca A', 'Marca B', 'Marca C', 'Marca D', 'Marca E']
for i, nome in enumerate(marcas, start=1):
    cursor.execute("INSERT INTO marcas (id_marca, nome_marca) VALUES (?, ?)", (i, nome))

# Inserção de dados de vendas de 2020 até o mês atual
ano_atual = datetime.now().year
mes_atual = datetime.now().month

for marca_id in range(1, 6):
    for ano in range(2020, ano_atual + 1):
        for mes in range(1, 13):
            if ano == ano_atual and mes > mes_atual:
                break
            qtd = random.randint(500, 1500)
            faturamento = round(qtd * random.uniform(90, 160), 2)
            cursor.execute("""
                INSERT INTO vendas_mensais (id_marca, ano, mes, faturamento, qtd_vendas)
                VALUES (?, ?, ?, ?, ?)""", (marca_id, ano, mes, faturamento, qtd))


temas = ["Promoção", "Desconto", "Liquidação", "Lançamento", "Ofertas", "Aniversário da Loja", "Black Friday", "Verão de Ofertas"]
for _ in range(15):  # 15 campanhas aleatórias
    marca_id = random.randint(1, 5)
    ano = random.randint(2021, ano_atual)
    mes = random.randint(1, 12)
    if ano == ano_atual and mes > mes_atual:
        continue
    dia = 1
    data_inicio = f"{ano}-{mes:02d}-{dia:02d}"
    data_fim = f"{ano}-{mes:02d}-{random.randint(15, 28)}"
    valor = round(random.uniform(5000, 30000), 2)
    nome = random.choice(temas) + " " + fake.word().capitalize()
    cursor.execute("""
        INSERT INTO campanhas (id_marca, nome_campanha, data_inicio, data_fim, valor_investido)
        VALUES (?, ?, ?, ?, ?)""", (marca_id, nome, data_inicio, data_fim, valor))

conn.commit()
conn.close()

print("📊 Banco de dados atualizado com sucesso: empresa_x.db")
