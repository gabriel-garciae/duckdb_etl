import os
import gdown
import duckdb
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def conectar_banco():
    """Conecta ao banco de dados DuckDB; cria o banco se não existir"""
    return duckdb.connect(database='duckdb.db', read_only=False)

def inicializar_tabela(con):
    """Cria a tabela se ela não existir"""
    con.execute("""
                CREATE TABLE IF NOT EXISTS historico_arquivos(
                    nome_arquivo VARCHAR,
                    horario_processamento TIMESTAMP
                )
        """)
    
def registrar_arquivo(con, nome_arquivo):
    """Registra um novo arquivo no banco com o horário atual"""
    con.execute("""
                INSERT INTO historico_arquivos (nome_arquivo, horario_processamento)
                VALUES (?,?)
                """, (nome_arquivo, datetime.now()))
    
def arquivos_processados(con):
    """Retorna um set com os nomes de todos os arquivos já processados"""
    return set(row[0] for row in con.execute("SELECT nome_arquivo FROM historico_arquivos").fetchall())

def baixar_arquivos_do_google_drive(url_pasta, diretorio_local):
    os.makedirs(diretorio_local, exist_ok=True)
    gdown.download_folder(url_pasta, output=diretorio_local, quiet=False, use_cookies=False)

def listar_arquivos_csv(diretorio):
    arquivos_csv = []
    todos_os_arquivos = os.listdir(diretorio)
    for arquivo in todos_os_arquivos:
        if arquivo.endswith(".csv"):
            caminho_completo = os.path.join(diretorio, arquivo)
            arquivos_csv.append(caminho_completo)
    return arquivos_csv

# ler o arquivo csv no diretório com duckdb
def ler_csv(caminho_do_arquivo):
    dataframe_duckdb = duckdb.read_csv(caminho_do_arquivo)
    return dataframe_duckdb

# função para adiconar uma coluna no df
def adicionar_coluna(df):
    df_transformado = duckdb.sql("SELECT *, idade * 2 AS dobro_da_idade FROM df").df()
    return df_transformado

# função converter o duckdb em pandas e salvar o dataframe no postgreSQL
def salvar_no_postgres(df_duckdb, tabela):
    DATABASE_URL = os.getenv('DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    df_duckdb.to_sql(tabela, con=engine, if_exists='append', index=False)

if __name__ == "__main__":
    url_pasta = 'https://drive.google.com/drive/folders/1Vgb3SoyJQf19oCbv59yERoiQ_gI9IYqo?usp=drive_link'
    diretorio_local = './pasta_gdown'
    #baixar_arquivos_do_google_drive(url_pasta, diretorio_local)
    lista_de_arquivos = listar_arquivos_csv(diretorio_local)
    con = conectar_banco()
    inicializar_tabela(con)
    processados = arquivos_processados(con)

    for caminho_do_arquivo in lista_de_arquivos:
        nome_arquivo = os.path.basename(caminho_do_arquivo)
        if nome_arquivo not in processados:
            df = ler_csv(caminho_do_arquivo)
            df_tranformado = adicionar_coluna(df)
            salvar_no_postgres(df_tranformado, "idade_dobro")
            registrar_arquivo(con, nome_arquivo)
            print(f"Arquivo {nome_arquivo} processado e salvo")
        else:
            print(f"Arquivo {nome_arquivo} já foi processado anteriormente")


    ''' duck_db_df = ler_csv(lista_de_arquivos)
        pandas_df_transformado = adicionar_coluna(duck_db_df)
        salvar_no_postgres(pandas_df_transformado, "idade_dobro")'''
    