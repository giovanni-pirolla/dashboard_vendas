import streamlit as st
import requests
import pandas as pd
import time

@st.cache_data
def converte_csv(df):
    return df.to_csv(index= False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Download realizado com sucesso!', icon="✅")
    time.sleep(5)
    sucesso.empty()
    

st.title('DADOS BRUTOS 📈')

url = 'https://labdados.com/produtos'

response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

# Filtros
with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas que deseja visualizar', list(dados.columns), default = list(dados.columns))

st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do Produto'):
    produto = st.multiselect('Selecione o Nome do Produto: ', dados['Produto'].unique(), default= dados['Produto'].unique())
with st.sidebar.expander('Preço do Produto'):
    preco = st.slider('Selecione o preço: ', 0, 5000, (0, 5000))
with st.sidebar.expander('Data da Compra'):
    data_compra = st.date_input('Selecione o período da compra', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))
with st.sidebar.expander('Categoria do Produto'):
    categorias = st.multiselect('Selecione as categorias de produtos desejadas', dados['Categoria do Produto'].unique(), default = dados['Categoria do Produto'].unique())
with st.sidebar.expander('Frete'):
    frete = st.slider('Selecione o valor do frete: ', 0, 500, (0, 500))
with st.sidebar.expander('Vendedores'):
    vendedores = st.multiselect('Selecione os vendedores desejados: ', dados['Vendedor'].unique().tolist(), default = dados['Vendedor'].unique().tolist())
with st.sidebar.expander('Local da Compra'):
    locais = st.multiselect('Selecione os locais de compra desejados: ', dados['Local da compra'].unique(), default = dados['Local da compra'].unique())
with st.sidebar.expander('Avaliação do Produto'):
    avaliacao = st.slider('Selecione a avaliação do produto: ', 1, 5, (1, 5))
with st.sidebar.expander('Tipo de Pagamento'):
    tipo_pagamento = st.multiselect('Selecione os tipos de pagamento desejados: ', dados['Tipo de pagamento'].unique(), default = dados['Tipo de pagamento'].unique())
with st.sidebar.expander('Quantidade de Parcelas'):
    parcelas = st.slider('Selecione a quantidade de parcelas:', dados['Quantidade de parcelas'].min(), dados['Quantidade de parcelas'].max(), (dados['Quantidade de parcelas'].min(), dados['Quantidade de parcelas'].max()))

query = '''
Produto in @produto and\
@preco[0] <= Preço <= @preco[1] and\
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and\
`Categoria do Produto` in @categorias and\
@frete[0] <= Frete <= @frete[1] and\
`Local da compra` in @locais and\
@avaliacao[0] <= `Avaliação da compra` <= @avaliacao[1] and\
`Tipo de pagamento` in @tipo_pagamento and\
@parcelas[0] <= `Quantidade de parcelas` <= @parcelas[1]
'''

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]
dados_filtrados = dados_filtrados[dados_filtrados['Vendedor'].isin(vendedores)]

st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas.')

st.markdown('Escreva um nome para o arquivo')

coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')
    
with coluna2:
    botao_download = st.download_button('Fazer o Download da tabela em CSV', data = converte_csv(dados_filtrados), file_name = f'{nome_arquivo}.csv', mime = 'text/csv', on_click = mensagem_sucesso)
