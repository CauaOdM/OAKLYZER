git clone https://github.com/CauaOdM/OAKLYZER.git
# 🫐 OAKLYZER – Seu copiloto de decisão

> **Transforma planilhas de vendas em ações claras para qualquer negócio com produtos e custos unitários.** 🚀

[![GitHub](https://img.shields.io/badge/GitHub-CauaOdM-blue?style=flat-square&logo=github)](https://github.com/CauaOdM)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-yellow?style=flat-square&logo=python)](https://www.python.org/)

---

## 🎯 Por que usar

O **OAKLYZER** ajuda gestores a sair do “achismo” e decidir rápido: padroniza dados, calcula faturamento, lucro, ROI e ponto de equilíbrio, cria gráficos interativos e exporta um relatório HTML bonito para compartilhar. Serve para açaiterias, pizzarias, dark kitchens, bares ou qualquer operação que venda itens com custo unitário.

---

## ✨ Entregas principais

- **Métricas rápidas**: faturamento total, vendas e lucro (quando há custo).
- **Ranking TOP 7**: produtos que puxam o caixa, já ordenados.
- **Faturamento por categoria**: pizza interativa para ver o mix.
- **Curva ABC/Pareto**: classifica A/B/C, mostra % acumulado e linhas de corte 80/95.
- **Menores margens**: alerta visual dos 5 piores itens.
- **Evolução temporal**: linhas para faturamento e quantidade por data.
- **ROI e ponto de equilíbrio**: ROI médio, melhor ROI e tabela com status (acima/abaixo do break-even).
- **Máscara de nomes**: modo demonstração esconde produtos; modo pago revela.
- **Exportar HTML dark**: relatório estático com métricas, gráficos, resumo por produto e guia “entenda seus números”.

---

## 🛠️ Como rodar

Requisitos: Python 3.8+ e `streamlit`, `pandas`, `plotly`, `openpyxl` (já listados em `requirements.txt`).

```bash
git clone https://github.com/CauaOdM/OAKLYZER.git
cd OAKLYZER
pip install -r requirements.txt
streamlit run app.py
```

Após processar os dados, use o botão **“Exportar relatório HTML (somente visualização)”** para baixar o relatório estático.

---

## 🧾 Estrutura da planilha

**Obrigatórias**
- `PRODUTO` – nome do item.
- `QTD` – quantidade vendida.
- `PREÇO_VENDA` – preço unitário.

**Opcionais (recomendadas)**
- `CUSTO_UNITÁRIO` – ativa lucro, margem, ROI e ponto de equilíbrio.
- `CATEGORIA` – agrupa no gráfico de pizza.
- `DATA` – habilita evolução temporal (formata para DD/MM/AAAA).

**Exemplo mínimo**

| PRODUTO | CATEGORIA | QTD | PREÇO_VENDA | CUSTO_UNITÁRIO | DATA |
|---------|-----------|-----|-------------|----------------|------|
| Açaí Tradicional | Açaí | 15 | 28.90 | 12.00 | 15/01/2025 |
| Combo Smash | Lanches | 22 | 34.00 | 15.50 | 16/01/2025 |
| Suco Natural | Bebidas | 12 | 12.50 | 4.00 | 16/01/2025 |

---

## 🔍 O que você vê na prática

- Painel de métricas e ranking já filtrado pelo modo (demo ou pago).
- Pareto com classificação ABC e linhas de referência.
- Tabela de break-even com status e diferença de unidades necessárias.
- Séries diárias para faturamento e quantidade (quando há data).
- Resumo por produto com faturamento, categoria, margem, ROI e ponto de equilíbrio.

---

## 🧠 Como calculamos

- **Faturamento** = QTD × PREÇO_VENDA
- **Lucro** = (PREÇO_VENDA − CUSTO_UNITÁRIO) × QTD
- **Margem %** = LUCRO / FATURAMENTO × 100
- **ROI %** = LUCRO / CUSTO_TOTAL × 100
- **Ponto de equilíbrio** = CUSTO_TOTAL / (PREÇO_VENDA − CUSTO_UNITÁRIO)
- **Curva ABC**: A (até 80%), B (até 95%), C (restante) por faturamento acumulado.

---

## 📁 Estrutura do projeto

```
OAKLYZER/
├── app.py              # Aplicação principal (Streamlit)
├── requirements.txt    # Dependências
├── README.md           # Este arquivo
└── LICENSE             # MIT License
```

---

## 🚀 Próximos passos

- Histórico persistente e dashboard contínuo.
- Previsão de tendência (ML) e alertas.
- Exportação em PDF e integração com banco de dados.
- Autenticação/usuários e app mobile.

---

## 👨‍💻 Autor

**Cauã Sarraf** ([@CauaOdM](https://github.com/CauaOdM))

---

## 📜 Licença

Este projeto está sob a licença **MIT**. Veja [LICENSE](LICENSE) para detalhes.

---

## 💬 Feedback

Ideias ou bugs? Abra uma issue ou fale comigo. Vamos evoluir juntos. ⚡

