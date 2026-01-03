# 🫐 OAKLYZER - Seu Analista de Dados Alimentício

> **Transformando dados brutos em insights poderosos para sua açaiteria (ou qualquer negócio alimentício)** 🚀

[![GitHub](https://img.shields.io/badge/GitHub-CauaOdM-blue?style=flat-square&logo=github)](https://github.com/CauaOdM)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-yellow?style=flat-square&logo=python)](https://www.python.org/)

---

## 🎯 O que é OAKLYZER?

Bem-vindo ao **OAKLYZER** — a ferramenta que todo gestor alimentício deveria ter! 🫐

Cansado de planilhas confusas e números que não fazem sentido? O OAKLYZER é aqui para **padronizar**, **analisar** e **revelar** os segredos do seu negócio. Quer seja uma açaiteria, pizzaria, hamburgueria ou qualquer estabelecimento alimentício, esta aplicação transforma dados brutos em **insights acionáveis** que aumentam faturamento, margem de lucro e ticket médio.

### 💡 Como Funciona?

O fluxo é bem simples:

1. **Você envia** → Gestor envia planilha com dados brutos (CSV ou XLSX)
2. **Nós padronizamos** → OAKLYZER standardiza nomes, datas e formatos automaticamente
3. **Analisamos** → Cálculos inteligentes de faturamento, lucro e margem
4. **Você age** → Visualizações incríveis e alertas que dizem exatamente o que fazer

---

## ✨ Funcionalidades Principais

### 📊 Análise Consolidada
- **Faturamento Total** - Veja quanto você faturou rapidinho
- **Vendas Totais** - Quantidade total de produtos vendidos
- **Lucro Total** - O que sobrou depois dos custos (se informado)

### 🏆 Ranking Dinâmico
- Identifique os **TOP 7 produtos por faturamento**
- Veja quais estão levando o dinheiro em casa
- Dados organizados do maior para o menor

### 🍕 Análise por Categoria
- Gráfico em pizza mostra a distribuição de receita
- Saiba qual categoria é sua queridinha 💚
- Identifique oportunidades de crescimento

### ⚠️ Alerta Inteligente de Margens
- Mostra os **5 produtos com MENOR margem de lucro**
- Diz exatamente o que está prejudicando seu lucro
- Visualização em cores: verde (bom) → vermelho (cuidado!)

### 📋 Tabela Resumida
- Dados organizados e formatados em BRL
- Percentuais de margem claros
- Pronto para usar em reuniões com sócios

### 🔒 Modo Demonstração vs. Modo Pago
- **Modo Demonstração** → Nomes dos produtos ocultos (para privacidade)
- **Modo Pago** → Nomes visíveis (desbloqueável via checkbox)

---

## 🛠️ Como Usar

### Requisitos
- Python 3.8+
- Bibliotecas: `streamlit`, `pandas`, `plotly`, `openpyxl`

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/CauaOdM/OAKLYZER.git
cd OAKLYZER

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Inicie a aplicação
streamlit run app.py
```

### Sua Planilha Precisa Ter

**Colunas Obrigatórias:**
- `PRODUTO` - Nome do produto (ex: "Açaí Tradicional")
- `QTD` - Quantidade vendida (ex: 15)
- `PREÇO_VENDA` - Preço unitário (ex: 28.90)

**Colunas Opcionais (Recomendadas):**
- `CUSTO_UNITÁRIO` - Custo do produto (ativa cálculo de lucro)
- `CATEGORIA` - Tipo do produto (ex: "Açaí", "Suco", "Açaí Premium")
- `DATA` - Data da venda (será formatada automaticamente)

**Exemplo de Estrutura:**

| PRODUTO | CATEGORIA | QTD | PREÇO_VENDA | CUSTO_UNITÁRIO | DATA |
|---------|-----------|-----|-------------|----------------|------|
| Açaí Tradicional | Açaí | 15 | 28.90 | 12.00 | 15/01/2025 |
| Açaí Premium | Açaí | 8 | 35.90 | 16.00 | 15/01/2025 |
| Suco Natural | Bebidas | 12 | 12.50 | 4.00 | 15/01/2025 |

---

## 📈 O Que Você Vai Descobrir

✅ **Qual produto traz mais dinheiro?**
Ranking claro de faturamento

✅ **Qual categoria é a estrela?**
Gráfico de pizza mostrando proporções

✅ **Quais produtos estão te prejuízando?**
Alerta de margens baixas em destaque

✅ **Como estou indo no geral?**
Métricas rápidas: faturamento, vendas e lucro

✅ **Posso confiar nos dados?**
Validação automática de colunas e formatação

---

## 🧠 Lógica por Trás

### Padronização Automática de Dados
```
"Açaí  Açucarado" → "acai_acucarado"
"PREÇO VENDA" → "preco_venda"
"Data" → "data" (formatada em DD/MM/YYYY)
```

### Cálculos Inteligentes
- **Faturamento** = QTD × PREÇO_VENDA
- **Lucro** = (PREÇO_VENDA - CUSTO) × QTD
- **Margem** = (LUCRO / FATURAMENTO) × 100

### Agrupamento por Produto
Mesmo que você venda o mesmo produto em múltiplos dias, o OAKLYZER **consolida automaticamente**:
- Soma as quantidades
- Soma o faturamento
- Calcula a margem ponderada corretamente

---

## 🎨 Interface

A aplicação roda em **Streamlit** — bonita, rápida e intuitiva:

- ✅ Upload drag-and-drop
- ✅ Processamento em tempo real
- ✅ Gráficos interativos (Plotly)
- ✅ Modo escuro/claro automático
- ✅ Responsiva (mobile-friendly)

---

## 📁 Estrutura do Projeto

```
OAKLYZER/
├── app.py              # Aplicação principal (Streamlit)
├── requirements.txt    # Dependências
├── README.md          # Este arquivo
└── LICENSE            # MIT License
```

---

## 🚀 Próximas Melhorias

- 📊 Dashboard com histórico de dados
- 📈 Previsões de tendências (ML)
- 💾 Integração com banco de dados
- 📧 Geração de relatórios em PDF
- 🔐 Sistema de usuários e autenticação
- 📱 Aplicativo mobile

---

## 👨‍💻 Autor

**Cauã Sarraf** ([@CauaOdM](https://github.com/CauaOdM))

---

## 📜 Licença

Este projeto está sob a licença **MIT**. Veja [LICENSE](LICENSE) para mais detalhes.

---

## 💬 Sugestões e Feedback

Tem alguma ideia para melhorar? Encontrou um bug? **Abre uma issue ou entra em contato!**

Não está em GitHub? Você ainda está no tempo certo para se conectar: [@CauaOdM](https://github.com/CauaOdM) 🎯

---

## ⚡ Comece Agora!

```bash
streamlit run app.py
```

Carregue sua primeira planilha e veja a magia acontecer! 🫐✨

