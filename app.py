import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from datetime import datetime
import plotly.io as pio
from datetime import datetime

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
            
            st.subheader("Resultado")
            
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

            fig3 = None  # usado no relatório HTML caso margem exista

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
                st.subheader("Faturamento por Categoria")
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

            # --- EXPORTAR RELATÓRIO HTML (somente visualização) ---
            def _fmt_brl(val: float) -> str:
                return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            def _fmt_pct(val: float) -> str:
                return f"{val:.1f}%"

            df_html = df_agrupado[cols_to_show].copy()
            if 'faturamento' in df_html.columns:
                df_html['faturamento'] = df_html['faturamento'].map(_fmt_brl)
            if 'lucro' in df_html.columns:
                df_html['lucro'] = df_html['lucro'].map(_fmt_brl)
            if 'margem' in df_html.columns:
                df_html['margem'] = df_html['margem'].map(_fmt_pct)
            df_html_table = df_html.to_html(index=False, escape=False)

            fig1_export = go.Figure(fig1) if fig1 is not None else None
            fig2_export = go.Figure(fig2) if fig2 is not None else None
            fig3_export = go.Figure(fig3) if fig3 is not None else None

            for _fig in [fig1_export, fig2_export, fig3_export]:
                if _fig is not None:
                    _fig.update_layout(
                        plot_bgcolor='#0f172a',
                        paper_bgcolor='#0f172a',
                        font_color='#e5e7eb'
                    )

            fig1_html = pio.to_html(fig1_export, include_plotlyjs='cdn', full_html=False) if fig1_export is not None else ""
            fig2_html = pio.to_html(fig2_export, include_plotlyjs=False, full_html=False) if fig2_export is not None else ""
            fig3_html = pio.to_html(fig3_export, include_plotlyjs=False, full_html=False) if fig3_export is not None else "<p><em>Margem não disponível.</em></p>"

            agora = datetime.now().strftime("%d/%m/%Y %H:%M")
            total_fat = _fmt_brl(df['faturamento'].sum())
            total_qtd = int(df['qtd'].sum())
            total_lucro = _fmt_brl(df['lucro'].sum()) if 'lucro' in df.columns else "N/A"

            html_report = f"""
<!DOCTYPE html>
<html lang=\"pt-BR\">
<head>
    <meta charset=\"UTF-8\" />
    <title>Relatório OAKLYZER</title>
    <style>
        :root {{
            --bg: #0f172a;
            --panel: #111827;
            --text: #e5e7eb;
            --muted: #cbd5e1;
            --accent: #f63366;
            --accent-2: #38bdf8;
            --border: #1f2937;
            --pill: #1d4ed8;
        }}
        body {{ margin: 0; padding: 24px; font-family: 'Segoe UI', Arial, sans-serif; background: var(--bg); color: var(--text); }}
        h1, h2, h3 {{ color: var(--text); margin-bottom: 10px; }}
        .pill {{ display: inline-block; padding: 6px 12px; border-radius: 999px; background: var(--pill); color: #fff; font-weight: 600; margin-bottom: 12px; }}
        .panel {{ background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px; box-shadow: 0 6px 18px rgba(0,0,0,0.25); margin-bottom: 18px; }}
        .metrics {{ display: flex; gap: 12px; flex-wrap: wrap; }}
        .card {{ flex: 1 1 180px; background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.18); }}
        .card strong {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; color: var(--text); }}
        th, td {{ border: 1px solid var(--border); padding: 10px; text-align: left; }}
        th {{ background: #1f2937; color: var(--muted); }}
        tr:nth-child(even) td {{ background: #0b1220; }}
        footer {{ margin-top: 24px; font-size: 12px; color: var(--muted); }}
    </style>
</head>
<body>
    <h1>Relatório OAKLYZER</h1>
    <div class=\"pill\">Gerado em {agora}</div>

    <div class=\"panel\">
        <h2>Métricas Rápidas</h2>
        <div class=\"metrics\">
            <div class=\"card\"><strong>Faturamento Total</strong><br><span>{total_fat}</span></div>
            <div class=\"card\"><strong>Vendas Totais</strong><br><span>{total_qtd}</span></div>
            <div class=\"card\"><strong>Lucro Total</strong><br><span>{total_lucro}</span></div>
        </div>
    </div>

    <div class=\"panel\">
        <h2>🏆 Ranking de Receita</h2>
        {fig1_html}
    </div>

    <div class=\"panel\">
        <h2>Faturamento por Categoria</h2>
        {fig2_html}
    </div>

    <div class=\"panel\">
        <h2>⚠️ Menores Margens (%)</h2>
        {fig3_html}
    </div>

    <div class=\"panel\">
        <h2>🔎 Resumo por Produto</h2>
        {df_html_table}
    </div>

    <div class=\"panel\">
        <h2>🚀 Vamos escalar juntos</h2>
        <p>Para acesso completo e decisões rápidas, fale direto comigo (Cauã) no WhatsApp <a href=\"https://wa.me/5512997042612\" style=\"color: var(--accent-2); font-weight: 700; text-decoration: none;\">+55 12 99704-2612</a>. Fechamos negócio rápido e você recebe tudo pronto.</p>
        <p>Oferecemos consultoria baseada nesses dados; se quiser avançar, me chama e alinhamos o próximo passo.</p>
    </div>

    <footer>Relatório estático para visualização e interação</footer>
</body>
</html>
"""
            st.download_button(
                label="⬇️ Exportar relatório HTML (somente visualização)",
                data=html_report,
                file_name="relatorio_oaklyzer.html",
                mime="text/html"
            )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
    
else:
    # Mensagem de espera enquanto não tem arquivo
    st.info("Aguardando upload...")