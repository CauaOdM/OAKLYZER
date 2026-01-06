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
- **Ticket Médio**: faturamento total ÷ quantidade vendida.
- **Ranking TOP 7**: produtos que puxam o caixa, já ordenados.
- **Faturamento por categoria**: pizza interativa para ver o mix.
- **Curva ABC/Pareto**: classifica A/B/C, mostra % acumulado e linhas de corte 80/95.
- **Ponto de Equilíbrio Geral**: calcula quantas unidades precisa vender para cobrir custos fixos.
  - ⭐ **Smart Period Detection**: detecta automaticamente se dados são de período < 30 dias
  - ⭐ **Custo Proporcional**: oferece ajustar o custo fixo proporcionalmente ao período
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
- **Ponto de Equilíbrio Geral** = CUSTO_FIXO / MARGEM_CONTRIB_MÉDIA_PONDERADA
- **Curva ABC**: A (até 80%), B (até 95%), C (restante) por faturamento acumulado.

### ⭐ Smart Period Detection (Novo!)

Se sua planilha tem dados de um período **menor que 30 dias**, o OAKLYZER detecta automaticamente e oferece:

1. **Aviso inteligente** na sidebar mostrando quantos dias de dados você tem
2. **Checkbox de ajuste proporcional**: calcula o custo fixo para o período exato
   - Exemplo: dados de 14 dias + custo fixo R$ 3.000/mês → ajusta para R$ 1.400
3. **Exibição clara** do período e qual valor foi usado no PE

Isso garante que o **Ponto de Equilíbrio não fique distorcido** quando você não tem dados de um mês completo!

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

