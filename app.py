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
        
        # Mostra as primeiras linhas (Raw)
        st.write("Prévia dos dados originais:")
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

        if 'data' in df.columns:
            try:
                #Data primeiro
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

            
            # Cálculos básicos
            df['faturamento'] = df['qtd'] * df['preco_venda']
            
            if 'custo_unitario' in df.columns:
                df['lucro'] = (df['preco_venda'] - df['custo_unitario']) * df['qtd']
                df['margem'] = ((df['preco_venda'] - df['custo_unitario']) / df['preco_venda']) * 100 
                st.write("✅ Custo detectado! Lucro calculado.")
            
            st.markdown("---")
            st.subheader(" Resultado Preliminar")
            
            # Métricas Rápidas
            c1, c2, c3 = st.columns(3)
            c1.metric("Faturamento Total", f"R$ {df['faturamento'].sum():,.2f}")
            c2.metric("Vendas Totais", int(df['qtd'].sum()))
            
            if 'lucro' in df.columns:
                c3.metric("Lucro Total", f"R$ {df['lucro'].sum():,.2f}")

            # --- PARTE 3: O SHOW VISUAL (GRÁFICOS + CADEADO) ---
            
            # A. BARRA LATERAL (CONTROLE)
            st.sidebar.header("Painel do Consultor")
            modo_pago = st.sidebar.checkbox("🔓 Desbloquear Nomes (Modo Pago)", value=False)
            
            # Cria uma cópia para não estragar os dados originais enquanto manipula
            df_display = df.copy()
            
            # Lógica do "Cadeado" (Esconde nomes se não pagar)
            if not modo_pago:
                st.warning("🔒 MODO DEMONSTRAÇÃO: Nomes dos produtos estão ocultos.")
                # Ordena primeiro para o "Produto #1" ser sempre o que mais vende
                df_display = df_display.sort_values('faturamento', ascending=False).reset_index(drop=True)
                # Troca o nome real por um código
                df_display['produto'] = [f"🔒 Produto Secreto #{i+1}" for i in range(len(df_display))]

            st.markdown("---")

            # B. GRÁFICOS LADO A LADO
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                st.subheader("Ranking de Receita")
                # Pega os 7 produtos que mais faturam
                top_fat = df_display.groupby('produto')['faturamento'].sum().nlargest(7).reset_index()
                fig1 = px.bar(top_fat, x='faturamento', y='produto', orientation='h', 
                              color_discrete_sequence=['#0083B8'], text_auto='.2s')
                st.plotly_chart(fig1, use_container_width=True)
            
            with col_g2:
                # Verifica se tem a coluna Categoria para fazer o gráfico de pizza
                if 'categoria' in df_display.columns:
                    st.subheader("Faturamento por Categoria")
                    fat_cat = df_display.groupby('categoria')['faturamento'].sum().reset_index()
                    fig2 = px.pie(fat_cat, values='faturamento', names='categoria', hole=0.4,
                                  color_discrete_sequence=px.colors.sequential.RdBu)
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Adicione uma coluna 'CATEGORIA' na planilha para ver o gráfico de pizza.")

            # C. ALERTA DE MARGEM 
            if 'margem' in df_display.columns:
                st.markdown("---")
                st.subheader("⚠️ Menores Margens (%)")
                st.caption("Estes produtos dão pouco lucro. Se estiver no modo gratuito, os nomes estarão ocultos.")
                
                # Pega os 5 piores produtos (mas que venderam)
                piores = df_display[df_display['faturamento'] > 0].nsmallest(5, 'margem')
                
                fig3 = px.bar(piores, x='margem', y='produto', orientation='h',
                              title="Top 5 Produtos com Menor Margem (%)",
                              text_auto='.1f', # Mostra o numero da % na barra
                              color='margem', color_continuous_scale='RdYlGn')
                st.plotly_chart(fig3, use_container_width=True)

            # D. TABELA FINAL FORMATADA
            st.markdown("### 🔎 Tabela final")
            
            # Define quais colunas mostrar
            cols_to_show = ['produto', 'qtd', 'preco_venda', 'faturamento']
            if 'data' in df_display.columns: cols_to_show.insert(0, 'data')
            if 'categoria' in df_display.columns: cols_to_show.insert(1, 'categoria')
            if 'lucro' in df_display.columns: cols_to_show.extend(['custo_unitario', 'lucro', 'margem'])
            
            # Formata os números (R$ e %)
            st.dataframe(
                df_display[cols_to_show].style.format({
                    'preco_venda': 'R$ {:.2f}',
                    'custo_unitario': 'R$ {:.2f}',
                    'faturamento': 'R$ {:.2f}',
                    'lucro': 'R$ {:.2f}',
                    'margem': '{:.1f}%' 
                }),
                use_container_width=True
            )

    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
    
else:
    # Mensagem de espera enquanto não tem arquivo
    st.info("Aguardando upload...")