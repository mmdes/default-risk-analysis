import pandas as pd
import sys
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# Realiza a imputação hierárquica em uma coluna.
def _imputar_hierarquia(df, target_col, group_hierarchy, strategy='median'):
    
    imputed_col = df[target_col].copy()
    
    # Itera sobre a hierarquia de grupos
    for group in group_hierarchy:
        if strategy == 'mode':
            # Para moda, ordene os resultados antes de pegar o primeiro para garantir determinismo
            imputation_values = df.groupby(group)[target_col].transform(
                lambda x: sorted(x.mode())[0] if not x.mode().empty else np.nan
            )
        else:
            imputation_values = df.groupby(group)[target_col].transform(strategy)
        
        imputed_col = imputed_col.fillna(imputation_values)
        
    # Aplica o fallback global final de forma determinística
    if strategy == 'median':
        global_fallback = df[target_col].median()
    else: # mode
        # Ordena a moda global também
        global_fallback = sorted(df[target_col].mode())[0]
        
    imputed_col = imputed_col.fillna(global_fallback)
    
    return imputed_col

# Faz o pré processamento dos dados antes da imputação
def processar_dados(df, status, bar):

    if status:
        status.info("Iniciando tratamento dos dados...")

    if bar:
        bar.progress(0)

    # removend duplicadas da base de teste
    df = df.drop_duplicates(keep='last')

    # realizando as conversões das datas
    df['SAFRA_REF'] = pd.to_datetime(
    df['SAFRA_REF'], format='%Y-%m', errors='coerce'
    )

    df['DATA_EMISSAO_DOCUMENTO'] = pd.to_datetime(
        df['DATA_EMISSAO_DOCUMENTO'], format='%Y-%m-%d'
    )

    df['DATA_VENCIMENTO'] = pd.to_datetime(
        df['DATA_VENCIMENTO'], format='%Y-%m-%d'
    )

    df['PRAZO_PAGAMENTO_DIAS'] = (df['DATA_VENCIMENTO'] - df['DATA_EMISSAO_DOCUMENTO']).dt.days
    # tratando inconsistências nas datas (datas negativas)
    # Filtra apenas os prazos positivos
    prazos_validos = df[df['PRAZO_PAGAMENTO_DIAS'] >= 0]

    # Calcula a mediana dos prazos
    mediana_prazo = prazos_validos['PRAZO_PAGAMENTO_DIAS'].median()

    # Cria uma máscara para os prazos negativos
    mask_negativo = df['PRAZO_PAGAMENTO_DIAS'] < 0

    # Corrige a data de vencimento somando a mediana à data de emissão
    df.loc[mask_negativo, 'DATA_VENCIMENTO'] = (
        df.loc[mask_negativo, 'DATA_EMISSAO_DOCUMENTO'] + pd.to_timedelta(mediana_prazo, unit='D'))

    # recalculando prazo
    df['PRAZO_PAGAMENTO_DIAS'] = (
        df['DATA_VENCIMENTO'] - df['DATA_EMISSAO_DOCUMENTO']
    ).dt.days

    # exluindo coluna temporária
    df = df.drop(columns=['PRAZO_PAGAMENTO_DIAS'])

    # importando bases cadastral e info tratadas
    df_cadastral = pd.read_csv('./data/processed/cleaned_base_cadastral.csv')
    df_info = pd.read_csv('./data/processed/cleaned_base_info.csv')

    # tratando os tipos das datas inicialmente
    df_cadastral['DATA_CADASTRO'] = pd.to_datetime(df_cadastral['DATA_CADASTRO'])
    df_info['SAFRA_REF'] = pd.to_datetime(
    df_info['SAFRA_REF'], format='%Y-%m-%d', errors='coerce')


    # join para pegar dados da info e cadastral
    merged_teste_info = df.merge(
    df_info,
    how='left',
    on=['ID_CLIENTE', 'SAFRA_REF'],
    )

    merged_teste = merged_teste_info.merge(
        df_cadastral,
        how='left',
        on='ID_CLIENTE',
        validate='many_to_one'
    )

    # importando base dev tratada
    merged_dataset = pd.read_csv('./data/processed/merged_dataset.csv', sep=',')

    # copiando a base dev
    dev_temp = merged_dataset.copy()

    # criando coluna que identifica que é um registro da base dev
    dev_temp['EH_DEV'] = 1

    # concatenando bases 
    # copiando a nova base teste
    tst_temp = merged_teste.copy()

    # indica que não é a base dev
    tst_temp['EH_DEV'] = 0

    # colunas que nao tem na teste
    tst_temp['DIAS_ATRASO'] = 0
    tst_temp['TARGET_INADIMPLENCIA'] = 0 
    tst_temp['DIAS_ADIANTAMENTO'] = 0
    

    cc = pd.concat([dev_temp, tst_temp], ignore_index=True)

    cc = cc.sort_values(by=['ID_CLIENTE', 'DATA_EMISSAO_DOCUMENTO'])

    if status:
        status.info("Imputação dos dados que têm uma ordem natural com interpolação linear, backward fill e forward fill...")

    # realizando imputação de dados: interpolação linear, bfill e ffill
    cc['RENDA_MES_ANTERIOR'] = (
        cc
        .groupby('ID_CLIENTE')['RENDA_MES_ANTERIOR']
        .transform(lambda x: x.interpolate(method='linear').ffill().bfill())
    )

    cc['NO_FUNCIONARIOS'] = (
        cc
        .groupby('ID_CLIENTE')['NO_FUNCIONARIOS']
        .transform(lambda x: x.interpolate(method='linear').ffill().bfill().round().astype('Int64'))
    )

    if bar:
        bar.progress(20)

    # ajustando os tipos
    cc['SAFRA_REF'] = pd.to_datetime(
    cc['SAFRA_REF'], format='%Y-%m-%d', errors='coerce')
    cc['DATA_EMISSAO_DOCUMENTO'] = pd.to_datetime(cc['DATA_EMISSAO_DOCUMENTO'], format='%Y-%m-%d', errors='coerce')
    cc['DATA_VENCIMENTO'] = pd.to_datetime(cc['DATA_VENCIMENTO'], format='%Y-%m-%d', errors='coerce')
    cc['DATA_CADASTRO'] = pd.to_datetime(cc['DATA_CADASTRO'], format='%Y-%m-%d', errors='coerce')

    cc['CEP_2_DIG'] = cc['CEP_2_DIG'].astype(str).str.split('.').str[0]  # Remove ".0" se for float
    cc['CEP_2_DIG'] = cc['CEP_2_DIG'].astype('category')

    cc['SEGMENTO_INDUSTRIAL'] = cc['SEGMENTO_INDUSTRIAL'].astype('category')
    cc['DOMINIO_EMAIL'] = cc['DOMINIO_EMAIL'].astype('category')
    cc['PORTE'] = cc['PORTE'].astype('category')

    cc['FLAG_PF'] = cc['FLAG_PF'].astype('Int64') # Int64 tem suporte a nan, por isso 

    # definindo hierarquias para a imputação hierárquica (moda e mediana levando em conta o contexto)
    hierarquia = [
        ['FLAG_PF', 'PORTE', 'SEGMENTO_INDUSTRIAL', 'DOMINIO_EMAIL', 'CEP_2_DIG', 'TAXA'],
        ['PORTE', 'SEGMENTO_INDUSTRIAL', 'DOMINIO_EMAIL', 'CEP_2_DIG', 'TAXA'],
        ['FLAG_PF', 'SEGMENTO_INDUSTRIAL', 'DOMINIO_EMAIL', 'CEP_2_DIG', 'TAXA'],
        ['FLAG_PF', 'PORTE', 'DOMINIO_EMAIL', 'CEP_2_DIG', 'TAXA'],
        ['FLAG_PF', 'PORTE', 'SEGMENTO_INDUSTRIAL', 'CEP_2_DIG', 'TAXA'],
        ['FLAG_PF', 'PORTE', 'SEGMENTO_INDUSTRIAL', 'DOMINIO_EMAIL', 'TAXA'],
        ['FLAG_PF', 'PORTE', 'SEGMENTO_INDUSTRIAL', 'DOMINIO_EMAIL', 'CEP_2_DIG'],
        ['FLAG_PF', 'PORTE', 'SEGMENTO_INDUSTRIAL', 'DOMINIO_EMAIL'],
        ['FLAG_PF', 'PORTE', 'SEGMENTO_INDUSTRIAL', 'TAXA'],
        ['FLAG_PF', 'PORTE', 'DOMINIO_EMAIL', 'CEP_2_DIG'],
        ['FLAG_PF', 'SEGMENTO_INDUSTRIAL', 'DOMINIO_EMAIL', 'TAXA'],
        ['PORTE', 'SEGMENTO_INDUSTRIAL', 'DOMINIO_EMAIL', 'TAXA'],
        ['FLAG_PF', 'PORTE', 'SEGMENTO_INDUSTRIAL'],
        ['FLAG_PF', 'PORTE', 'TAXA'],
        ['FLAG_PF', 'SEGMENTO_INDUSTRIAL', 'TAXA'],
        ['PORTE', 'SEGMENTO_INDUSTRIAL', 'TAXA'],
        ['FLAG_PF', 'DOMINIO_EMAIL', 'CEP_2_DIG'],
        ['FLAG_PF', 'PORTE'],
        ['FLAG_PF', 'TAXA'],
        ['FLAG_PF', 'SEGMENTO_INDUSTRIAL'],
        ['PORTE', 'TAXA'],
        ['SEGMENTO_INDUSTRIAL', 'TAXA'],
        ['DOMINIO_EMAIL', 'CEP_2_DIG'],
        ['FLAG_PF'],
        ['PORTE'],
        ['SEGMENTO_INDUSTRIAL'],
        ['DOMINIO_EMAIL'],
        ['CEP_2_DIG'],
        ['TAXA']
    ]

    # imputando dados 
    colunas_para_imputar = ['FLAG_PF', 'PORTE', 'SEGMENTO_INDUSTRIAL', 
                        'VALOR_A_PAGAR', 'RENDA_MES_ANTERIOR', 
                        'NO_FUNCIONARIOS', 
                        'DOMINIO_EMAIL', 'CEP_2_DIG',
                        ] 
    estrategias = {
        'FLAG_PF': 'mode',
        'PORTE': 'mode',
        'SEGMENTO_INDUSTRIAL': 'mode',
        'VALOR_A_PAGAR': 'median',
        'RENDA_MES_ANTERIOR': 'median', 
        'NO_FUNCIONARIOS': 'median', # para escapar de possíveis outliers, estou pegando mediana e nao moda
        'DOMINIO_EMAIL':'mode',
        'CEP_2_DIG':'mode',
    }

    if status:
        status.info("Iniciando imputação hierárquica com contexto...")

    total_colunas = len(colunas_para_imputar)
    progresso_inicial = 20
    progresso_final = 80
    step = (progresso_final - progresso_inicial) / total_colunas
    progresso_atual = progresso_inicial
    
    # Aplica a imputação hierárquica (imputação com contexto) para cada coluna da lista
    for coluna in colunas_para_imputar:

        hierar = hierarquia.copy()

        hierar = [
            [col for col in grupo if col != coluna]
            for grupo in hierarquia
            if any(col != coluna for col in grupo)  # garante que restou algo no grupo
        ]

        # Converte para float temporariamente, se for int
        is_int = pd.api.types.is_integer_dtype(cc[coluna])

        if is_int:
            cc[coluna] = cc[coluna].astype(float)

        if status:
            status.info(f"Imputação hierárquica coluna: {coluna}, com estratégia: {estrategias.get(coluna)}")

        cc[coluna + '_INPUTED'] = _imputar_hierarquia(cc, coluna, hierar, strategy=estrategias.get(coluna))

        # Se originalmente era int, arredonda e converte de volta
        if is_int:
            cc[coluna] = cc[coluna + '_INPUTED'].round().astype('int64')
        else:
            cc[coluna] = cc[coluna + '_INPUTED']
        cc.drop(columns=[coluna + '_INPUTED'], inplace=True)

        progresso_atual += step
        if bar:
            bar.progress(int(progresso_atual))
      

    # criando as features pro dataset concateanado
    cc['TEMPO_CADASTRO_PARA_VENCIMENTO'] = (cc['DATA_VENCIMENTO'] - cc['DATA_CADASTRO']).dt.days

    cc['TEMPO_DE_CASA_MESES'] = cc['TEMPO_CADASTRO_PARA_VENCIMENTO'] // 30

    cc = cc.drop(columns='TEMPO_CADASTRO_PARA_VENCIMENTO')

    cc['PRAZO_PAGAMENTO_DIAS'] = (cc['DATA_VENCIMENTO'] - cc['DATA_EMISSAO_DOCUMENTO']).dt.days

    cc['MES_SAFRA'] = cc['SAFRA_REF'].dt.month

    cc = cc.sort_values(by=['ID_CLIENTE', 'DATA_EMISSAO_DOCUMENTO'])

    cc['INADIMPLENCIAS_ANTERIORES'] = (
        cc
        .groupby('ID_CLIENTE')['TARGET_INADIMPLENCIA']
        .shift(fill_value=0)  # desloca a inadimplência para não pegar a atual (evita data leakage)
        .groupby(cc['ID_CLIENTE'])
        .cumsum()
    )

    # colocando um limite para essa abordagem para não prejudicar o modelo como um todo 
    cc['INADIMPLENCIAS_ANTERIORES']=cc['INADIMPLENCIAS_ANTERIORES'].clip(upper=15)

    # criação de coluna temporarea para armazenar os adiantamentos 
    cc['HOUVE_ADIANTAMENTO'] = (cc['DIAS_ADIANTAMENTO'] >= 1).astype(int)

    cc['ADIANTAMENTOS_ANTERIORES'] = (
        cc
        .groupby('ID_CLIENTE')['HOUVE_ADIANTAMENTO']
        .shift(fill_value=0)  # desloca a inadimplência para não pegar a atual (evita data leakage)
        .groupby(cc['ID_CLIENTE'])
        .cumsum()
    )

    cc['ADIANTAMENTOS_ANTERIORES']=cc['ADIANTAMENTOS_ANTERIORES'].clip(upper=15)

    cc = cc.drop(columns='HOUVE_ADIANTAMENTO')

    # tratando tempo de cada com imputação herárquica (variável importante para a predição)
    colunas_para_imputar = ['TEMPO_DE_CASA_MESES'] 
    estrategias = {
        'TEMPO_DE_CASA_MESES': 'median',
    }

    total_colunas = len(colunas_para_imputar)
    progresso_inicial = 80
    progresso_final = 95
    step = (progresso_final - progresso_inicial) / total_colunas
    progresso_atual = progresso_inicial

    # Aplica a imputação hierárquica (imputação com contexto) para cada coluna da lista
    for coluna in colunas_para_imputar:

        hierar = hierarquia.copy()

        hierar = [
            [col for col in grupo if col != coluna]
            for grupo in hierarquia
            if any(col != coluna for col in grupo)  # garante que restou algo no grupo
        ]

        # Converte para float temporariamente, se for int
        is_int = pd.api.types.is_integer_dtype(cc[coluna])

        if is_int:
            cc[coluna] = cc[coluna].astype(float)
        
        if status:
            status.info(f"Imputação hierárquica coluna: {coluna}, com estratégia: {estrategias.get(coluna)}")

        cc[coluna + '_INPUTED'] = _imputar_hierarquia(cc, coluna, hierar, strategy=estrategias.get(coluna))

        # Se originalmente era int, arredonda e converte de volta
        if is_int:
            cc[coluna] = cc[coluna + '_INPUTED'].round().astype('int64')
        else:
            cc[coluna] = cc[coluna + '_INPUTED']
        cc.drop(columns=[coluna + '_INPUTED'], inplace=True)

        progresso_atual += step
        if bar:
            bar.progress(int(progresso_atual))


    # reconstrução do datasets com as features
    test_features_v1 = cc[cc['EH_DEV']==0]
    
    # removendo colunas desnecessárias
    test_features_v1 = test_features_v1.drop(columns=['EH_DEV', 'DATA_PAGAMENTO', 'DIAS_ATRASO', 'TARGET_INADIMPLENCIA', 'DIAS_ADIANTAMENTO'])


    if bar:
        bar.progress(100)

    return(test_features_v1) 
