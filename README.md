# default-risk-analysis
Este projeto foi desenvolvido como parte de um case técnico da Datarisk, com o objetivo de prever a inadimplência em cobranças mensais com base em dados cadastrais, histórico de pagamentos e perfil dos clientes. Conforme o enunciado do case, a proposta do desafio simula um cenário real dentro da empresa, incentivando a construção de soluções que possam ser aplicadas na prática. Pensando nisso, foi criada uma interface interativa com Streamlit, que facilita a visualização dos dados, métricas e previsões de forma simples e acessível. A seguir, estão as informações sobre a estrutura do projeto e como executar os notebooks e a aplicação.

# Entendendo os diretórios

## `dashboard`

* **.streamlit**: Contém configurações específicas para execução do Streamlit (ex: layout, tema, etc).
* **assets**: Armazena recursos estáticos da aplicação.

  * **logo.png** e **mini-logo.png**: Logotipos usados na interface do Streamlit.
* **pages**: Contém os códigos Python das páginas da aplicação Streamlit.
* **app.py**: Arquivo principal que inicializa e gerencia a aplicação interativa em Streamlit.

## `data`

* **processed**: Contém os dados já tratados, prontos para uso nos modelos e na aplicação.

  * **dataset\_features\_v1.csv**: Dataset final com todas as features preparadas.
  * **merged\_dataset.csv / merged\_test.csv**: Bases unificadas com variáveis derivadas e estruturadas.
  * **submissao\_case.csv**: Resultado final da previsão sobre a base de teste com as probabilidades de inadimplência.
  * **test\_features\_v1.csv**: Base de teste com as mesmas features da base de treino.
  * **resultados\_grid\_search\_v6.pkl**: Resultados do tuning de hiperparâmetros com GridSearchCV.
  * **final\_random\_forest\_structure.pkl**: Estrutura do modelo Random Forest salva em disco.
  * **cleaned\_base\_cadastral.csv / cleaned\_base\_info.csv**: Bases intermediárias tratadas.
* **raw**: Contém os dados brutos originais fornecidos no início do projeto.

  * **base\_cadastral.csv**
  * **base\_info.csv**
  * **base\_pagamentos\_desenvolvimento.csv**
  * **base\_pagamentos\_teste.csv**

### `notebooks`

* **exploratory\_analysis.ipynb**: Notebook com a análise exploratória inicial e tratamento dos dados.
* **feature\_engineering.ipynb**: Notebook responsável pela construção das features finais
* **modeling.ipynb**: Pipeline de treinamento e avaliação dos modelos de machine learning (Random Forest, XGBoost, LightGBM e Logistic Regression).
* **predict\_test\_data.ipynb**: Script de inferência na base de teste e geração do arquivo final de submissão.

## `src`

Contém os scripts principais utilizados para pré-processamento e previsão pelo dashboard interativo:

* **model_utils.py**: Define funções relacionadas ao carregamento do modelo e à execução das previsões.
* **preprocessing.py**: Contém as funções responsáveis pelo tratamento dos dados, também para a aplicação Streamlit.

## Arquivos adicionais

* **.gitignore**: Arquivo de configuração para ignorar arquivos temporários e pesados no repositório.
* **requirements.txt**: Lista de bibliotecas necessárias para rodar a aplicação.

---

# Como rodar?

Siga os seguintes passos para executar a aplicação localment. **Lembre-se de rodar todos os comandos na raiz do projeto e esteja utilizando um ambiente com Python 3.10**:

1. **Instalação das dependências:**

   Certifique-se de estar usando **Python 3.10** no seu ambiente. Para instalar as dependências:


   ```bash
   pip install -r requirements.txt
   ```

2. **Organização dos dados:**

   Certifique-se de que os dados brutos estejam no diretório **/data/raw**. Utilize os notebooks para gerar os arquivos processados em **/data/processed**.

3. **Execução dos notebooks (é necessário executá-los nesta ordem):**

    1. Execute o notebook **/notebooks/exploratory\_analysis.ipynb** para a exploração e tratamento inicial dos dados e gerar os arquivos das bases processadas em **/data/processed**.
   2. Execute o notebook **/notebooks/feature\_engineering.ipynb** para gerar as features.
   3. Em seguida, execute o notebook **/notebooks/modeling.ipynb** para treinar os modelos e salvar as métricas e resultados.
   4. Por fim, rode o notebook **/notebooks/predict\_test\_data.ipynb** para gerar as previsões sobre os dados de teste.

4. **Executar a aplicação Streamlit (dashboard interativo):**

   Certifique-se de estar na **raiz do projeto** e de que **todos os notebooks responsáveis pela geração dos dados processados já foram executados** antes de iniciar a aplicação Streamlit. Para iniciar a aplicação, execute o seguinte comando:

   ```bash
   streamlit run ./dashboard/app.py
   ```