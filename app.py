import streamlit as st
import pandas as pd

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
    
        # --- SUA LÓGICA DE LIMPEZA (Mantida igualzinha) ---
        colunas_novas = []
        for col in df.columns:
            c = str(col).lower().strip()
            c = c.replace(" ", "_").replace("-", "_")
            c = c.replace("ç", "c").replace("ã", "a").replace("á", "a")
            c = c.replace("é", "e").replace("ó", "o").replace("í", "i")
            c = c.replace("ú", "u")
            colunas_novas.append(c)

        df.columns = colunas_novas

        # Verificação das colunas vitais
        colunas_vitais = ['produto', 'qtd', 'preco_venda']
        if not all(col in df.columns for col in colunas_vitais):
            st.error(f"❌ Erro nas colunas. O sistema detectou: {df.columns.tolist()}")
            st.warning("A planilha precisa ter: PRODUTO, QTD, PREÇO_VENDA")
            st.stop()
        
        else: 
            # Se chegou aqui, as colunas bateram!
            st.success("✅ Colunas validadas!")
            
            # --- CÁLCULOS EXTRAS (Aproveitando sua planilha rica) ---
            df['faturamento'] = df['qtd'] * df['preco_venda']
            
            if 'custo_unitario' in df.columns:
                df['lucro'] = (df['preco_venda'] - df['custo_unitario']) * df['qtd']
                df['margem'] = ((df['preco_venda'] - df['custo_unitario']) / df['preco_venda']) * 100
                st.write("✅ Custo detectado! Lucro calculado.")
            
            st.markdown("---")
            st.subheader("📊 Resultado Preliminar")
            
            # Métricas Rápidas
            c1, c2, c3 = st.columns(3)
            c1.metric("Faturamento Total", f"R$ {df['faturamento'].sum():,.2f}")
            c2.metric("Vendas Totais", int(df['qtd'].sum()))
            
            if 'lucro' in df.columns:
                c3.metric("Lucro Total", f"R$ {df['lucro'].sum():,.2f}")

            st.dataframe(df.head())

    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
    
else:
    # Mensagem de espera enquanto não tem arquivo
    st.info("Aguardando upload...")