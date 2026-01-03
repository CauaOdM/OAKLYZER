import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="OAKLYZER", layout="wide")

st.title("🫐 OAKLYZER")
st.write("Faça o upload da sua planilha preenchida para começar a análise.")

uploaded_file = st.file_uploader("Carregar Planilha (.xlsx ou .csv)", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Lê o arquivo
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("Arquivo carregado com sucesso!")
        
        # Mostra as primeiras linhas 
        with st.expander("Ver dados originais (Prévia)"):
            st.dataframe(df.head())

        # --- PADRONIZAÇÃO DAS COLUNAS ---
        colunas_novas = []
        for col in df.columns:
            c = str(col).lower().strip()
            c = c.replace(" ", "_").replace("-", "_")
            c = c.replace("ç", "c").replace("ã", "a").replace("á", "a")
            c = c.replace("é", "e").replace("ó", "o").replace("í", "i")
            c = c.replace("ú", "u")
            colunas_novas.append(c)

        df.columns = colunas_novas

        # Tratamento de Data
        if 'data' in df.columns:
            try:
                # Força ser data
                df['data'] = pd.to_datetime(df['data'], errors='coerce')
                # Transforma em texto DIA/MÊS/ANO 
                df['data'] = df['data'].dt.strftime('%d/%m/%Y')
            except:
                pass 

        # Verificação das colunas vitais
        colunas_vitais = ['produto', 'qtd', 'preco_venda']
        if not all(col in df.columns for col in colunas_vitais):
            st.error(f"❌ Erro nas colunas. O sistema detectou: {df.columns.tolist()}")
            st.warning("A planilha precisa ter: PRODUTO, QTD, PREÇO_VENDA")
            st.stop()
        
        else: 
            st.success("✅ Colunas validadas!")

            # --- CÁLCULOS ---
            df['faturamento'] = df['qtd'] * df['preco_venda']
            
            if 'custo_unitario' in df.columns:
                df['lucro'] = (df['preco_venda'] - df['custo_unitario']) * df['qtd']
                
                df['margem'] = ((df['preco_venda'] - df['custo_unitario']) / df['preco_venda']) * 100 
                st.write("✅ Custo detectado! Lucro calculado.")
            
            
            if 'categoria' not in df.columns:
                df['categoria'] = 'Geral'

            st.markdown("---")
            
            
            # --- AGRUPAMENTO POR PRODUTO ---
            agregacoes = {
                'qtd': 'sum',
                'faturamento': 'sum',
                'preco_venda': 'mean' # Preço médio
            }
            if 'categoria' in df.columns: agregacoes['categoria'] = 'first'
            if 'lucro' in df.columns: agregacoes['lucro'] = 'sum'
            if 'custo_unitario' in df.columns: agregacoes['custo_unitario'] = 'mean'
            
            # Cria a tabela resumida
            df_agrupado = df.groupby('produto').agg(agregacoes).reset_index()

            # Recalcula a margem correta baseada nos totais (Média Ponderada)
            if 'lucro' in df_agrupado.columns:
                df_agrupado['margem'] = (df_agrupado['lucro'] / df_agrupado['faturamento']) * 100

            # --- VISUALIZAÇÃO ---
            
            st.subheader("📊 Resultado Consolidado")
            
            # Métricas Rápidas 
            c1, c2, c3 = st.columns(3)
            c1.metric("Faturamento Total", f"R$ {df['faturamento'].sum():,.2f}")
            c2.metric("Vendas Totais", int(df['qtd'].sum()))
            
            if 'lucro' in df.columns:
                c3.metric("Lucro Total", f"R$ {df['lucro'].sum():,.2f}")

            # --- BARRA LATERAL (CONTROLE) ---
            st.sidebar.header("Painel do Consultor")
            modo_pago = st.sidebar.checkbox("🔓 Desbloquear Nomes (Modo Pago)", value=False)
            
            
            if not modo_pago:
                st.warning("🔒 MODO DEMONSTRAÇÃO: Nomes dos produtos estão ocultos.")
                # Ordena por faturamento
                df_agrupado = df_agrupado.sort_values('faturamento', ascending=False).reset_index(drop=True)
                # Mascara os nomes
                df_agrupado['produto'] = [f"🔒 Produto Secreto #{i+1}" for i in range(len(df_agrupado))]
            else:
                # Se pagou, apenas ordena
                df_agrupado = df_agrupado.sort_values('faturamento', ascending=False).reset_index(drop=True)

            st.markdown("---")

            # --- GRÁFICOS (USANDO DADOS AGRUPADOS) ---
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                st.subheader("🏆 Ranking de Receita")
                # Pega os 7 maiores
                top_fat = df_agrupado.head(7)
                fig1 = px.bar(top_fat, x='faturamento', y='produto', orientation='h', 
                              color_discrete_sequence=['#0083B8'], text_auto='.2s')
                # Inverte eixo Y para o maior ficar em cima
                fig1.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig1, use_container_width=True)
            
            with col_g2:
                # Gráfico de pizza (Agrupando por categoria)
                st.subheader("🍕 Faturamento por Categoria")
                # Agrupa a original ou a agrupada por categoria para ter o total da fatia
                fat_cat = df.groupby('categoria')['faturamento'].sum().reset_index()
                fig2 = px.pie(fat_cat, values='faturamento', names='categoria', hole=0.4,
                                color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig2, use_container_width=True)

            # --- ALERTA DE MARGEM ---
            if 'margem' in df_agrupado.columns:
                st.markdown("---")
                st.subheader("⚠️ Menores Margens (%)")
                st.caption("Estes produtos dão pouco lucro no total acumulado.")
                
                # Pega os 5 piores (que venderam)
                piores = df_agrupado[df_agrupado['faturamento'] > 0].nsmallest(5, 'margem')
                
                fig3 = px.bar(piores, x='margem', y='produto', orientation='h',
                              title="Top 5 Produtos com Menor Margem (%)",
                              text_auto='.1f', # Mostra o numero da % na barra
                              color='margem', color_continuous_scale='RdYlGn')
                st.plotly_chart(fig3, use_container_width=True)

            # --- TABELA FINAL (RESUMO) ---
            st.markdown("### 🔎 Resumo por Produto")
            
            # Define quais colunas mostrar na tabela final
            cols_to_show = ['produto', 'qtd', 'faturamento']
            if 'categoria' in df_agrupado.columns: cols_to_show.insert(1, 'categoria')
            if 'margem' in df_agrupado.columns: cols_to_show.extend(['lucro', 'margem'])
            
            # Formata os números (R$ e %)
            st.dataframe(
                df_agrupado[cols_to_show].style.format({
                    'faturamento': 'R$ {:.2f}',
                    'lucro': 'R$ {:.2f}',
                    'margem': '{:.1f}%' 
                }),
                use_container_width=True
            )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
    
else:
    # Mensagem de espera enquanto não tem arquivo
    st.info("Aguardando upload...")