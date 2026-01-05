import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
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
        df['data_original'] = None
        if 'data' in df.columns:
            try:
                # Força ser data
                df['data_original'] = pd.to_datetime(df['data'], errors='coerce')
                # Transforma em texto DIA/MÊS/ANO 
                df['data'] = df['data_original'].dt.strftime('%d/%m/%Y')
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
            
            # --- ANÁLISE ABC (CURVA DE PARETO) ---
            # Ordena por faturamento decrescente
            df_abc = df_agrupado.sort_values('faturamento', ascending=False).reset_index(drop=True)
            
            # Calcula percentual de cada produto
            df_abc['percentual_faturamento'] = (df_abc['faturamento'] / df_abc['faturamento'].sum()) * 100
            
            # Calcula percentual acumulado
            df_abc['percentual_acumulado'] = df_abc['percentual_faturamento'].cumsum()
            
            # Classifica em A, B ou C
            df_abc['classificacao_abc'] = df_abc['percentual_acumulado'].apply(
                lambda x: 'A' if x <= 80 else ('B' if x <= 95 else 'C')
            )
            
            # Adiciona a classificação de volta ao df_agrupado
            df_agrupado = df_agrupado.merge(
                df_abc[['produto', 'classificacao_abc']], 
                on='produto', 
                how='left'
            )

            # --- CÁLCULO DE PONTO DE EQUILÍBRIO E ROI ---
            if 'custo_unitario' in df_agrupado.columns:
                # Calcula custo total de cada produto
                df_agrupado['custo_total'] = df_agrupado['custo_unitario'] * df_agrupado['qtd']
                
                # ROI = (Lucro / Investimento) * 100
                # Onde Investimento = Custo Total
                df_agrupado['roi'] = ((df_agrupado['lucro'] / df_agrupado['custo_total']) * 100).round(1)
                
                # Ponto de Equilíbrio = Custo Total / Margem de Contribuição Unitária
                # Margem de Contribuição Unitária = Preço - Custo Unitário
                df_agrupado['margem_contrib_unit'] = df_agrupado['preco_venda'] - df_agrupado['custo_unitario']
                
                # Evita divisão por zero
                df_agrupado['ponto_equilibrio'] = df_agrupado.apply(
                    lambda row: row['custo_total'] / row['margem_contrib_unit'] if row['margem_contrib_unit'] > 0 else 0,
                    axis=1
                ).round(0).astype(int)
            

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

            # --- INDICADORES DE DESEMPENHO (após aplicar máscara de nomes) ---
            if 'roi' in df_agrupado.columns:
                st.markdown("---")
                st.subheader("💎 Indicadores de Desempenho Financeiro")

                col_i1, col_i2 = st.columns(2)

                with col_i1:
                    # ROI Médio Ponderado
                    roi_medio = (df_agrupado['lucro'].sum() / df_agrupado['custo_total'].sum() * 100).round(1)
                    st.metric(
                        "ROI Médio do Negócio",
                        f"{roi_medio}%",
                        help="Retorno sobre Investimento: quanto cada R$ 1 investido retorna de lucro"
                    )
                    st.caption("📊 Quanto maior, melhor o retorno do capital investido")

                with col_i2:
                    # Melhor ROI
                    melhor_roi = df_agrupado.nlargest(1, 'roi').iloc[0]
                    st.metric(
                        "Melhor ROI Individual",
                        f"{melhor_roi['roi']}%",
                        help=f"Produto: {melhor_roi['produto']}"
                    )
                    st.caption(f"🏆 {melhor_roi['produto']}")

                # --- TABELA DE PONTO DE EQUILÍBRIO ---
                st.markdown("---")
                st.subheader("⚖️ Análise de Ponto de Equilíbrio")
                st.caption("Quantas unidades você precisa vender para não ter prejuízo em cada produto")

                # Seleciona produtos com melhor e pior situação
                df_equilibrio = df_agrupado[['produto', 'qtd', 'ponto_equilibrio', 'roi']].copy()
                df_equilibrio['status'] = df_equilibrio.apply(
                    lambda row: '✅ Acima' if row['qtd'] >= row['ponto_equilibrio'] else '⚠️ Abaixo',
                    axis=1
                )
                df_equilibrio['diferenca'] = df_equilibrio['qtd'] - df_equilibrio['ponto_equilibrio']

                # Ordena por diferença (os mais críticos primeiro)
                df_equilibrio = df_equilibrio.sort_values('diferenca').reset_index(drop=True)

                # Mostra apenas os 10 mais relevantes (5 piores + 5 melhores)
                piores = df_equilibrio.head(5)
                melhores = df_equilibrio.tail(5)
                df_display = pd.concat([piores, melhores]).drop_duplicates()

                st.dataframe(
                    df_display.style.format({
                        'qtd': '{:.0f}',
                        'ponto_equilibrio': '{:.0f}',
                        'roi': '{:.1f}%',
                        'diferenca': '{:+.0f}'
                    }),
                    use_container_width=True
                )

                # Alertas inteligentes
                produtos_criticos = df_equilibrio[df_equilibrio['status'] == '⚠️ Abaixo']
                if len(produtos_criticos) > 0:
                    st.warning(f"⚠️ **Atenção:** {len(produtos_criticos)} produto(s) estão vendendo abaixo do ponto de equilíbrio!")
                    with st.expander("Ver produtos críticos"):
                        st.dataframe(produtos_criticos[['produto', 'qtd', 'ponto_equilibrio']])
                else:
                    st.success("✅ Todos os produtos estão vendendo acima do ponto de equilíbrio!")

            st.markdown("---")

            fig3 = None  # usado no relatório HTML caso margem exista

            # --- ANALISE TEMPORAL ---
            if df['data_original'].notna().any():
                st.markdown("---")
                st.subheader("Evolução Temporal de Vendas")

                df_temporal = df.groupby('data_original').agg({
                    'faturamento': 'sum',
                    'qtd': 'sum'
                }).reset_index().sort_values('data_original')

                df_temporal = df_temporal[df_temporal['data_original'].notna()]

                if len(df_temporal) > 0:
                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        fig_temporal_fat = px.line(df_temporal, x='data_original', y='faturamento',
                                        title='Faturamento Diário',
                                        markers=True,
                                        color_discrete_sequence=['#38bdf8'])
                        fig_temporal_fat.update_layout(xaxis_title='Data', yaxis_title='Faturamento (R$)')
                        st.plotly_chart(fig_temporal_fat, use_container_width=True)
                    
                    with col_t2:
                        fig_temporal_qtd = px.line(df_temporal, x='data_original', y='qtd',
                                       title='Quantidade Vendida Diariamente',
                                       markers=True,
                                       color_discrete_sequence=['#f63366'])
                        fig_temporal_qtd.update_layout(xaxis_title='Data', yaxis_title='Quantidade')
                        st.plotly_chart(fig_temporal_qtd, use_container_width=True)


            # --- GRÁFICO DE PARETO ---
            st.markdown("---")
            st.subheader("📊 Análise ABC - Curva de Pareto")
            st.caption("Identifica os produtos vitais (A), importantes (B) e triviais (C)")
            
            # Cria gráfico combinado (barras + linha)
            fig_pareto = go.Figure()
            
            # Adiciona barras de faturamento
            fig_pareto.add_trace(go.Bar(
                x=df_abc['produto'].head(15),  # Top 15 para não poluir
                y=df_abc['faturamento'].head(15),
                name='Faturamento',
                marker_color='#0083B8',
                yaxis='y'
            ))
            
            # Adiciona linha de percentual acumulado
            fig_pareto.add_trace(go.Scatter(
                x=df_abc['produto'].head(15),
                y=df_abc['percentual_acumulado'].head(15),
                name='% Acumulado',
                mode='lines+markers',
                marker=dict(color='#f63366', size=8),
                line=dict(color='#f63366', width=3),
                yaxis='y2'
            ))
            
            # Adiciona linhas de referência (80% e 95%)
            fig_pareto.add_hline(y=80, line_dash="dash", line_color="green", 
                                annotation_text="80% (Classe A)", yref='y2')
            fig_pareto.add_hline(y=95, line_dash="dash", line_color="orange", 
                                annotation_text="95% (Classe B)", yref='y2')
            
            # Configura layout com dois eixos Y
            fig_pareto.update_layout(
                xaxis=dict(title='Produto'),
                yaxis=dict(title='Faturamento (R$)', side='left'),
                yaxis2=dict(title='% Acumulado', side='right', overlaying='y', range=[0, 100]),
                legend=dict(x=0.7, y=1.1, orientation='h'),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_pareto, use_container_width=True)
            
            # Mostra resumo da classificação
            col_abc1, col_abc2, col_abc3 = st.columns(3)
            
            qtd_a = len(df_abc[df_abc['classificacao_abc'] == 'A'])
            qtd_b = len(df_abc[df_abc['classificacao_abc'] == 'B'])
            qtd_c = len(df_abc[df_abc['classificacao_abc'] == 'C'])
            
            with col_abc1:
                st.metric("🟢 Classe A (Vitais)", f"{qtd_a} produtos", 
                         help="Representam ~80% do faturamento")
            with col_abc2:
                st.metric("🟡 Classe B (Importantes)", f"{qtd_b} produtos",
                         help="Representam ~15% do faturamento")
            with col_abc3:
                st.metric("🔴 Classe C (Triviais)", f"{qtd_c} produtos",
                         help="Representam ~5% do faturamento")
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
            if 'classificacao_abc' in df_agrupado.columns: cols_to_show.append('classificacao_abc')
            if 'margem' in df_agrupado.columns: cols_to_show.extend(['lucro', 'margem'])
            if 'roi' in df_agrupado.columns: cols_to_show.extend(['roi', 'ponto_equilibrio'])
            
            # Formata os números (R$ e %)
            formatacao = {
                'faturamento': 'R$ {:.2f}',
                'lucro': 'R$ {:.2f}',
                'margem': '{:.1f}%'
            }
            if 'roi' in df_agrupado.columns:
                formatacao['roi'] = '{:.1f}%'
                formatacao['ponto_equilibrio'] = '{:.0f} un'

            st.dataframe(
                df_agrupado[cols_to_show].style.format(formatacao),
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
            if 'roi' in df_html.columns:
                df_html['roi'] = df_html['roi'].map(_fmt_pct)
            if 'ponto_equilibrio' in df_html.columns:
                df_html['ponto_equilibrio'] = df_html['ponto_equilibrio'].map(lambda v: f"{int(v)} un")
            df_html_table = df_html.to_html(index=False, escape=False)

            # Dados adicionais para o HTML (ROI e ponto de equilíbrio)
            roi_medio_html = None
            melhor_roi_val = None
            melhor_roi_prod = None
            df_equilibrio_html = "<p><em>ROI/Ponto de equilíbrio não disponível.</em></p>"
            if 'roi' in df_agrupado.columns and 'ponto_equilibrio' in df_agrupado.columns and df_agrupado['custo_total'].sum() > 0:
                roi_medio_html = (df_agrupado['lucro'].sum() / df_agrupado['custo_total'].sum() * 100)
                melhor_row = df_agrupado.nlargest(1, 'roi').iloc[0]
                melhor_roi_val = melhor_row['roi']
                melhor_roi_prod = melhor_row['produto']

                df_eq = df_agrupado[['produto', 'qtd', 'ponto_equilibrio', 'roi']].copy()
                df_eq['status'] = df_eq.apply(lambda row: 'Acima' if row['qtd'] >= row['ponto_equilibrio'] else 'Abaixo', axis=1)
                df_eq['diferenca'] = df_eq['qtd'] - df_eq['ponto_equilibrio']
                df_eq = df_eq.sort_values('diferenca')
                df_eq['qtd'] = df_eq['qtd'].map('{:.0f}'.format)
                df_eq['ponto_equilibrio'] = df_eq['ponto_equilibrio'].map(lambda v: f"{int(v)} un")
                df_eq['roi'] = df_eq['roi'].map('{:.1f}%'.format)
                df_eq['diferenca'] = df_eq['diferenca'].map('{:+.0f}'.format)
                df_equilibrio_html = df_eq.head(10).to_html(index=False, escape=False)

            roi_medio_display = f"{roi_medio_html:.1f}%" if roi_medio_html is not None else "N/A"
            melhor_roi_display = f"{melhor_roi_val:.1f}%" if melhor_roi_val is not None else "N/A"
            melhor_roi_prod_display = melhor_roi_prod if melhor_roi_prod is not None else "—"

            # Exporta todos os gráficos
            fig1_export = go.Figure(fig1) if fig1 is not None else None
            fig2_export = go.Figure(fig2) if fig2 is not None else None
            fig3_export = go.Figure(fig3) if fig3 is not None else None
            fig_pareto_export = go.Figure(fig_pareto) if 'fig_pareto' in locals() and fig_pareto is not None else None
            fig_temporal_fat_export = go.Figure(fig_temporal_fat) if 'fig_temporal_fat' in locals() and fig_temporal_fat is not None else None
            fig_temporal_qtd_export = go.Figure(fig_temporal_qtd) if 'fig_temporal_qtd' in locals() and fig_temporal_qtd is not None else None

            # Ajuste de altura/margem e alinhamento do eixo Y para rankings
            for _fig in [fig1_export, fig3_export]:
                if _fig is not None and _fig.data and hasattr(_fig.data[0], 'y'):
                    y_vals = list(_fig.data[0].y) if _fig.data[0].y is not None else []
                    n_bars = len(y_vals) if y_vals else 5
                    _fig.update_layout(
                        height=140 + 40 * n_bars,
                        yaxis=dict(
                            automargin=True,
                            tickfont=dict(size=11),
                            ticklabelposition="outside",
                            ticks="outside",
                            categoryorder="array",
                            categoryarray=y_vals,
                            title=dict(text="Produtos", font=dict(size=12, color='#cbd5e1'), standoff=24)
                        ),
                        margin=dict(l=190, r=40, t=60, b=40)
                    )

            # Ajuste específico para gráfico de piores margens (fig3_export)
            if fig3_export is not None and fig3_export.data and hasattr(fig3_export.data[0], 'y'):
                y_vals = list(fig3_export.data[0].y) if fig3_export.data[0].y is not None else []
                n_bars = len(y_vals) if y_vals else 5
                fig3_export.update_layout(
                    height=140 + 42 * n_bars,
                    yaxis=dict(
                        automargin=True,
                        tickfont=dict(size=12),
                        ticklabelposition="outside",
                        ticks="outside",
                        categoryorder="array",
                        categoryarray=y_vals,
                        title=dict(text="Produtos", font=dict(size=12, color='#cbd5e1'), standoff=26)
                    ),
                    margin=dict(l=205, r=40, t=60, b=40)
                )

            for _fig in [fig1_export, fig2_export, fig3_export, fig_pareto_export, fig_temporal_fat_export, fig_temporal_qtd_export]:
                if _fig is not None:
                    _fig.update_layout(
                        plot_bgcolor='#0f172a',
                        paper_bgcolor='#0f172a',
                        font_color='#e5e7eb'
                    )

            fig1_html = pio.to_html(fig1_export, include_plotlyjs='cdn', full_html=False) if fig1_export is not None else ""
            fig2_html = pio.to_html(fig2_export, include_plotlyjs=False, full_html=False) if fig2_export is not None else ""
            fig3_html = pio.to_html(fig3_export, include_plotlyjs=False, full_html=False) if fig3_export is not None else "<p><em>Margem não disponível.</em></p>"
            fig_pareto_html = pio.to_html(fig_pareto_export, include_plotlyjs=False, full_html=False) if fig_pareto_export is not None else "<p><em>Pareto não disponível.</em></p>"
            fig_temporal_fat_html = pio.to_html(fig_temporal_fat_export, include_plotlyjs=False, full_html=False) if fig_temporal_fat_export is not None else "<p><em>Série de faturamento não disponível.</em></p>"
            fig_temporal_qtd_html = pio.to_html(fig_temporal_qtd_export, include_plotlyjs=False, full_html=False) if fig_temporal_qtd_export is not None else "<p><em>Série de quantidade não disponível.</em></p>"

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

    <div class="panel">
        <div class="section-title"><h2>💎 Indicadores Financeiros</h2><div class="badge">ROI &amp; Equilíbrio</div></div>
        <div class="metrics">
            <div class="card"><strong>ROI Médio</strong><br><span>{roi_medio_display}</span></div>
            <div class="card"><strong>Melhor ROI</strong><br><span>{melhor_roi_display}</span><br><small style="color: var(--muted);">{melhor_roi_prod_display}</small></div>
        </div>
        <h3 style="margin-top:14px;">⚖️ Ponto de Equilíbrio</h3>
        {df_equilibrio_html}
    </div>

    <div class=\"panel\">
        <h2>🏆 Ranking de Receita</h2>
        {fig1_html}
    </div>

    <div class=\"panel\">
        <h2>Faturamento por Categoria</h2>
        {fig2_html}
    </div>

    <div class="panel">
        <h2>📊 Curva de Pareto (ABC)</h2>
        {fig_pareto_html}
    </div>

    <div class="panel">
        <h2>📈 Evolução Temporal</h2>
        <div class="two-col">
            {fig_temporal_fat_html}
            {fig_temporal_qtd_html}
        </div>
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
        <p>Para acesso completo, fale direto comigo <a href=\"https://wa.me/5512997042612?text=Tenho%20interesse%20em%20fechar%20com%20voc%C3%AA!\" style=\"color: var(--accent-2); font-weight: 700; text-decoration: none;\">Cauã</a>. Fechamos negócio rápido e você recebe tudo pronto.</p>
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
