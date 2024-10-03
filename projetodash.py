import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, AgGridTheme
import plotly.express as px

# Configuração do tema
st.set_page_config(page_title="Dashboard de Anúncios", layout="wide")

# Cabeçalho com logo
st.image("logo.png", width=200)  # Verifique o caminho da imagem
st.title("Dashboard de Anúncios - Meta Ads")

# Campos para inserir Token e ID da conta
token = st.text_input("Insira seu Token de Acesso:")
account_id = st.text_input("Insira o ID da Conta:")

# Função para criar uma tabela interativa
def create_interactive_table(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)  # Adicionar paginação
    gb.configure_side_bar()  # Barra lateral para filtros
    gb.configure_default_column(editable=False)  # Colunas não editáveis
    grid_options = gb.build()
    AgGrid(df, gridOptions=grid_options, height=300, theme=AgGridTheme.STREAMLIT)  # Usando tema válido

# Botão para confirmar as credenciais
if st.button("Conectar à Conta"):
    if token and account_id:
        st.success(f"Conectado à conta {account_id}")

        # Fazer requisição para a API
        response = requests.get(f"http://fastapi:8000/get_ad_data?token={token}&account_id={account_id}")

        if response.status_code == 200:
            ad_data = response.json()

            if isinstance(ad_data, dict) and "data" in ad_data:
                st.subheader("Dados das Campanhas de Anúncios")

                # Lista para armazenar dados dos anúncios
                ads_list = []

                # Iterar sobre os anúncios e extrair os dados de insights
                for ad in ad_data["data"]:
                    insights = ad.get('insights', {}).get('data', [])
                    if insights:
                        for insight in insights:
                            ads_list.append({
                                "Nome do Anúncio": ad['name'],
                                "Cliques": insight.get('clicks', 0),
                                "Impressões": insight.get('impressions', 0),
                                "Valor Gasto (R$)": insight.get('spend', 0),
                                "CTR (%)": insight.get('ctr', 0),
                                "CPC (R$)": insight.get('cpc', 0),
                                "Conversões": insight.get('conversions', 0)
                            })

                # Verificar se existem dados de anúncios
                if ads_list:
                    # Criar DataFrame com os dados dos anúncios
                    df = pd.DataFrame(ads_list)

                    # Exibir o DataFrame em uma tabela interativa
                    st.subheader("Tabela de Desempenho dos Anúncios")
                    create_interactive_table(df)

                    # Exibir gráfico de cliques por campanha
                    fig = px.bar(df, x='Nome do Anúncio', y='Cliques', title='Cliques por Campanha')
                    st.plotly_chart(fig)

                else:
                    st.write("Nenhum dado de insights disponível para os anúncios.")
            else:
                st.error("Nenhum dado encontrado para esta conta.")
        else:
            st.error("Erro ao buscar dados da conta.")
    else:
        st.warning("Por favor, insira o Token e o ID da conta.")

from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/get_ad_data")
def get_ad_data(token: str = Query(...), account_id: str = Query(...)):
    # Definindo a URL corretamente
    url = f"https://graph.facebook.com/v14.0/act_{account_id}/ads"
    
    params = {
        "access_token": token,
        "fields": "id, name, insights{clicks,impressions,spend,ctr,cpc,conversions}"
    }
    
    print(f"Requesting data for account_id: {account_id} with token: {token}")

    # Fazendo a requisição HTTP para a API do Facebook
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        # Retorna os dados dos anúncios se a requisição foi bem-sucedida
        print("Data received successfully:", response.json())
        return response.json()
    
    else:
        # Em caso de erro, imprime o status e a mensagem de erro
        print(f"Erro: {response.status_code}, {response.text}")
        return {"error": "Erro ao buscar dados. Verifique o token e ID."}
