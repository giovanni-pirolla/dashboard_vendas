import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

def formata_numero(valor, prefixo = 'R$ '):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

st.title('DASHBOARD DE VENDAS :shopping_cart:')

url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

# Filtros
## Filtro de região
st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Selecione a Região Desejada', regioes)
if regiao == 'Brasil':
    regiao = ''
    
## Filtro de Ano
todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True)

if todos_anos == True:
    ano = ''
else:
    ano = st.sidebar.slider('Selecione o Ano Desejado', 2020, 2023)

# Leitura dos Dados
query_string = {'regiao': regiao.lower(), 'ano': ano}
response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

# Filtro dos vendedores
filtro_vendedores = st.sidebar.multiselect('Selecione os Vendedores Desejados', dados['Vendedor'].unique().tolist())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]
    
# Tabelas de receita
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

## Tabelas de quantidade de vendas
vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].count().reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mês'] = vendas_mensal['Data da Compra'].dt.month_name()

vendas_estados = dados.groupby('Local da compra')[['Preço']].count()
vendas_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

vendas_categorias = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending=False)

## Tabelas de vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

# Gráficos de receita
fig_mapa_receita = px.scatter_geo(receita_estados, 
                                  lat= 'lat',
                                  lon= 'lon',
                                  scope= 'south america',
                                  size= 'Preço',
                                  template='seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data= {
                                      'lat' : False, 'lon' : False
                                  }, 
                                  title= 'Receita por Estado')

fig_receita_mensal = px.line(receita_mensal, 
                             x= 'Mês',
                             y = 'Preço',
                             markers= True,
                             range_y = [receita_mensal['Preço'].min(), receita_mensal['Preço'].max()],
                             color= 'Ano', 
                             line_dash= 'Ano',
                             title= 'Receita Mensal')
fig_receita_mensal.update_layout(xaxis_title='Mês', yaxis_title='Receita (R$)')

fig_receita_estado = px.bar(receita_estados.head(),
                            x = 'Local da compra', 
                            y = 'Preço', 
                            text_auto= True,
                            title = 'Top 5 estados por Receita')
fig_receita_estado.update_layout(yaxis_title = 'Receita')


fig_receita_categoria = px.bar(receita_categorias,
                                x = receita_categorias.index, 
                                y = 'Preço', 
                                text_auto= True,
                                title = 'Top 5 categorias por Receita')
fig_receita_categoria.update_layout(yaxis_title = 'Receita', xaxis_title = 'Categoria do Produto')

# Gráficos de quantidade de vendas
fig_mapa_vendas = px.scatter_geo(vendas_estados, 
                                 lat = 'lat',
                                 lon = 'lon',
                                 size= 'Preço',
                                 scope= 'south america',
                                 template='seaborn',
                                 hover_name= 'Local da compra',
                                 hover_data= {'lat' : False, 'lon' : False},
                                 title= 'Vendas por estado')

fig_vendas_estados = px.bar(vendas_estados.head(), 
                            x= 'Local da compra', 
                            y= 'Preço',
                            text_auto= True,
                            title = 'Top 5 estados por Vendas')
fig_receita_estado.update_layout(yaxis_title = 'Receita')

fig_vendas_mensais = px.line(vendas_mensal,
                             x= 'Mês',
                             y='Preço',
                             markers= True,
                             range_y = [0, vendas_mensal['Preço'].max()],
                             color='Ano',
                             line_dash='Ano',
                             title= 'Vendas por mês')

fig_vendas_categorias = px.bar(vendas_categorias, 
                            x= vendas_categorias.index, 
                            y= 'Preço',
                            text_auto= True,
                            title = 'Vendas por categoria de produto')
fig_receita_estado.update_layout(yaxis_title = 'Receita')
                            

# Visualização no streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])

with aba1:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita Gerada', formata_numero(dados['Preço'].sum()))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estado, use_container_width=True)
        
    with col2:    
        st.metric('Nº de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categoria, use_container_width=True)

with aba2:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita Gerada', formata_numero(dados['Preço'].sum()))
        st.plotly_chart(fig_mapa_vendas)
        st.plotly_chart(fig_vendas_estados)
        
    with col2:    
        st.metric('Nº de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensais)
        st.plotly_chart(fig_vendas_categorias)

with aba3:
    qtd_vendedores = st.number_input('Escolha a quantidade de vendedores a serem exibidos', min_value=1, max_value=10, value=5, step=1)
    fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum').head(qtd_vendedores), 
                                    x = 'sum',
                                    y = vendedores[['sum']].sort_values('sum').head(qtd_vendedores).index,
                                    text_auto= True, 
                                    title= f'Top {qtd_vendedores} Vendedores por Receita')
    fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count').head(qtd_vendedores), 
                                    x = 'count',
                                    y = vendedores[['count']].sort_values('count').head(qtd_vendedores).index,
                                    text_auto= True, 
                                    title= f'Top {qtd_vendedores} Vendedores por Vendas')
    
    fig_receita_vendedores.update_layout(xaxis_title='Receita', yaxis_title='Vendedor')
    fig_vendas_vendedores.update_layout(xaxis_title='Receita', yaxis_title='Vendedor')
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita Gerada', formata_numero(dados['Preço'].sum()))
        st.plotly_chart(fig_receita_vendedores, use_container_width=True)
        
    with col2:    
        st.metric('Nº de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_vendedores, use_container_width=True)
        
