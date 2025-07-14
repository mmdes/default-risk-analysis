import sys
import os
import pickle
import pandas as pd
import importlib
#import streamlit as st

sys.dont_write_bytecode = True
# Adiciona o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join('.')))

# módulos próprios
import src.preprocessing
importlib.reload(src.preprocessing)
from src.preprocessing import processar_dados

def predict(df_teste, status, bar):

    test_features_v1 = processar_dados(df_teste, status, bar)

    # Eliminar colunas irrelevantes para predição
    cols_drop = [
        'ID_CLIENTE', 'DATA_EMISSAO_DOCUMENTO', 
        'DATA_VENCIMENTO', 'DATA_CADASTRO', 'SAFRA_REF',
    ]

    df = test_features_v1.drop(columns=cols_drop)

    # Aplicando One-Hot Encoding em variáveis categóricas de baixa cardinalidade
    df = pd.get_dummies(df, columns=['SEGMENTO_INDUSTRIAL', 'PORTE', 'DOMINIO_EMAIL'], drop_first=True)

    # Aplicando Frequency Encoding para variável com alta cardinalidade 
    freq_map = df['CEP_2_DIG'].value_counts(normalize=True)
    df['CEP_2_DIG'] = df['CEP_2_DIG'].map(freq_map)

    # Importante não adionar a variável target, resultaria em data leackage e consequentemente overfitting
    X_new = df

    # Carregando o modelo treinado
    with open('./data/processed/final_random_forest_structure.pkl', 'rb') as f:
        modelo = pickle.load(f)

    # Prevendo as probabilidades
    y_proba = modelo.predict_proba(X_new)

    if status:
        status.info("Processamento concluído com sucesso!")

    # Construindo tabela de submissão 
    submissao_case = test_features_v1[['ID_CLIENTE', 'SAFRA_REF']].copy()

    # Convertendo data para o formato original para safra usado na base 
    submissao_case['SAFRA_REF'] = pd.to_datetime(submissao_case['SAFRA_REF']).dt.to_period('M').astype(str)

    submissao_case['PROBABILIDADE_INADIMPLENCIA'] = y_proba[:, 1]

    return submissao_case