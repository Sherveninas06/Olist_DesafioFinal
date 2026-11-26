# Desafio Final Harve: Análise de Dados Olist

Projeto final do módulo **"Projetos para Cientista de Dados"** da Harve. O objetivo é explorar os dados públicos da **Olist**, um marketplace brasileiro, para responder a 7 perguntas de negócio sobre vendas, entregas, satisfação, produtos, frete e geografia. O resultado é apresentado em um **dashboard interativo em HTML**, com storytelling.

> **Período analisado:** set/2016 a out/2018  
> **Volume:** 99.441 pedidos · 96.096 clientes · 3.095 vendedores · 32.951 produtos · 112.650 itens vendidos  
> **Ferramentas:** Python (pandas, numpy, matplotlib, scikit-learn) e HTML/CSS/JS puro no dashboard

---

## 🔗 Acessar o dashboard

### ▶ [Abrir o dashboard (arquivo local)](dashboard/dashboard_olist.html)

| Onde | Como acessar |
|---|---|
| **No seu computador** | Clique no link acima ou dê um duplo clique em `dashboard/dashboard_olist.html`. Ele abre no navegador, sem instalar nada. |
| **Online (GitHub Pages)** | `https://SEU-USUARIO.github.io/NOME-DO-REPO/`. Siga o passo a passo abaixo. |
| **Aba específica** | Acrescente o tema no fim do link: `#vendas`, `#logistica`, `#satisfacao`, `#produtos`, `#frete` ou `#geo`. |

> No GitHub, clicar direto no arquivo `.html` mostra só o código-fonte. Para ver o dashboard funcionando online, publique no **GitHub Pages** (de graça, cerca de 2 minutos).

### Publicar online com GitHub Pages

1. Suba esta pasta para um repositório **público** no GitHub. A pasta `tabelas/` tem cerca de 125 MB e o GitHub recusa arquivos acima de 100 MB, como o `olist_geolocation_dataset.csv`. Coloque `tabelas/` no `.gitignore`: o dashboard não precisa dos CSVs, porque os dados já estão dentro do HTML.
2. No repositório, vá em **Settings → Pages**.
3. Em **Source**, escolha **Deploy from a branch**. Em **Branch**, selecione `main` e a pasta `/ (root)` e clique em **Save**.
4. Espere 1 ou 2 minutos. O link aparece no topo da página do Pages: `https://SEU-USUARIO.github.io/NOME-DO-REPO/`.
5. Volte a este README e troque `SEU-USUARIO` e `NOME-DO-REPO` pelos valores reais em todos os links.

O `index.html` na raiz do projeto redireciona automaticamente para `dashboard/dashboard_olist.html`. Assim, o link principal do Pages já abre o dashboard.

**Links diretos depois de publicado:**

- [Visão geral](https://SEU-USUARIO.github.io/NOME-DO-REPO/dashboard/dashboard_olist.html#overview)
- [Vendas](https://SEU-USUARIO.github.io/NOME-DO-REPO/dashboard/dashboard_olist.html#vendas)
- [Logística](https://SEU-USUARIO.github.io/NOME-DO-REPO/dashboard/dashboard_olist.html#logistica)
- [Satisfação](https://SEU-USUARIO.github.io/NOME-DO-REPO/dashboard/dashboard_olist.html#satisfacao)
- [Produtos](https://SEU-USUARIO.github.io/NOME-DO-REPO/dashboard/dashboard_olist.html#produtos)
- [Frete & Modelo](https://SEU-USUARIO.github.io/NOME-DO-REPO/dashboard/dashboard_olist.html#frete)
- [Geografia](https://SEU-USUARIO.github.io/NOME-DO-REPO/dashboard/dashboard_olist.html#geo)

> **Opção sem configurar nada:** depois de subir no GitHub, o link `https://htmlpreview.github.io/?https://github.com/SEU-USUARIO/NOME-DO-REPO/blob/main/dashboard/dashboard_olist.html` mostra o HTML direto. Use como alternativa; o GitHub Pages é mais estável.

---

## Estrutura da pasta

```
Desafio_final/
├── README.md                      ← este arquivo
├── index.html                     ← redireciona para o dashboard (para o GitHub Pages)
├── .gitignore                     ← ignora tabelas/ e .venv/ (arquivos grandes demais para o GitHub)
├── .txt                           ← anotações das dicas dos desafios 1 e 2
├── apresentacao_PCD_Padrão.pdf    ← slides do módulo (enunciado dos desafios)
├── tabelas/                       ← 9 CSVs do dataset Olist (fora do Git; baixe no Kaggle)
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_customers_dataset.csv
│   ├── olist_sellers_dataset.csv
│   ├── olist_geolocation_dataset.csv
│   └── product_category_name_translation.csv
├── DESAFIOS/                      ← um script por desafio, com a conclusão no final
│   ├── desafio_1.py … desafio_7.py
└── dashboard/
    ├── dashboard_olist.html       ← O DASHBOARD (abra no navegador)
    ├── build_data.py              ← gera os números agregados a partir das tabelas
    └── template.html              ← layout e gráficos do dashboard (sem os dados)
```

---

## Como usar o dashboard

O arquivo funciona em qualquer navegador moderno (Chrome, Edge, Firefox), sem servidor. Os dados já estão dentro do HTML; veja a seção [Acessar o dashboard](#-acessar-o-dashboard).

- **Abas no topo:** cada aba é um tema. O endereço muda (`#vendas`, `#geo` etc.), então dá para mandar o link de uma aba específica.
- **Chips verdes:** são filtros (métrica, período, ranking, camada do mapa).
- **Passar o mouse** sobre qualquer gráfico mostra os valores exatos.
- **Botão `TABELA`** em vários cards troca o gráfico pela tabela de dados.
- Os achados na **Visão geral** levam direto ao tema correspondente.

### Como regenerar os números

Se você alterar alguma análise ou as tabelas:

```bash
pip install pandas numpy scikit-learn
cd dashboard
python build_data.py ../tabelas      # gera data.json (~35 s, inclui o treino do modelo)
```

Depois, insira o `data.json` no lugar do marcador `/*__DATA__*/` do `template.html` para gerar o `dashboard_olist.html`. O trecho abaixo faz isso:

```python
t = open('template.html', encoding='utf-8').read()
d = open('data.json', encoding='utf-8').read()
open('dashboard_olist.html', 'w', encoding='utf-8').write(t.replace('/*__DATA__*/', d))
```

O `build_data.py` usa **exatamente a mesma lógica** dos scripts da pasta `DESAFIOS/`: os mesmos filtros, tratamentos, faixas e o mesmo `random_state=42`. Por isso os números do dashboard batem com as conclusões de cada desafio.

---

## Os temas do dashboard

O dashboard é organizado **por tema**, e cada tema responde a um ou mais desafios.

| Aba | Desafios | Pergunta |
|---|---|---|
| Visão geral | todos | Resumo, indicadores principais e storytelling |
| Vendas | D2 | Qual mês teve mais pedidos e mais pagamentos? Há outliers? |
| Logística | D1, D4 | Quanto tempo leva a entrega? Atrasar afeta a nota? |
| Satisfação | D3 | Os clientes estão satisfeitos? Estão comentando? |
| Produtos | D5 | O que mais e menos vende? Preço e fotos importam? |
| Frete & Modelo | D6, D7 | Peso e volume afetam o frete? Dá para prever o frete? |
| Geografia | D7 | Onde estão os clientes e os vendedores? |

---

### 🏠 Visão geral
- **99.441 pedidos**, **R$ 16,01 milhões** pagos e **ticket médio de R$ 160,99** (valor médio pago por pedido).
- **Entrega mediana:** 9,9 dias. **Nota média:** 4,07 de 5.
- O gráfico de pedidos por mês mostra crescimento forte em 2017 e estabilidade em 2018, na faixa de 6 a 7 mil pedidos por mês.
- "Saúde da operação" traz um indicador de cada tema em forma de barra.

### 💳 Vendas (Desafio 2)
**Pergunta:** qual mês teve a maior quantidade de pedidos e o maior valor de pagamentos?

**Como foi feito:** `order_purchase_timestamp` virou um período mensal (`to_period('M')`). Os pedidos foram contados por mês na `olist_orders`. Os pagamentos foram somados por pedido na `olist_order_payments` e depois agrupados pelo mês da compra. Os meses com menos de 100 pedidos (2016-09, 2016-12, 2018-09 e 2018-10) foram removidos porque estão incompletos.

**Resultados**
- **Novembro/2017** foi o mês com mais pedidos (**7.544**) e com mais pagamentos (**R$ 1,19 milhão**). A média é de 4.734 pedidos por mês.
- O motivo é a **Black Friday**: **1.176 pedidos em 24/11/2017**, 5,3 vezes um dia comum (cerca de 220 pedidos).
- **Formas de pagamento:** cartão de crédito com 76,8 mil transações (R$ 12,5 milhões), boleto com 19,8 mil, voucher com 5,8 mil e débito com 1,5 mil.
- **Outliers (método IQR):**

| Variável | Mediana | Limite superior | % outliers | Máximo |
|---|---|---|---|---|
| Pagamento | R$ 100,00 | R$ 344,41 | 7,7% | R$ 13.664 |
| Preço do item | R$ 74,99 | R$ 277,40 | 7,5% | R$ 6.735 |
| Frete | R$ 16,26 | R$ 33,25 | 10,3% | R$ 410 |

As distribuições são assimétricas: a maioria dos valores é baixa e poucos são muito altos. Os outliers são **compras reais de alto valor**, não erros, e por isso foram **mantidos** e apenas sinalizados.

### 🚚 Logística (Desafios 1 e 4)
**Perguntas:** qual é o tempo médio e mediano da aprovação até a entrega? Existe relação entre a satisfação e a entrega antes ou depois do prazo?

**Como foi feito**
- As datas foram convertidas com `pd.to_datetime`.
- Ficaram só os pedidos `delivered` com as duas datas preenchidas.
- O tempo foi calculado como `entrega − aprovação`, em dias.
- 61 pedidos com tempo negativo (entrega antes da aprovação) foram removidos.
- No D4 foi criada a variável `dias_diferenca = entrega real − prazo estimado`. Ela gerou a categoria `status_entrega` (Adiantado, No prazo ou Atrasado), a flag `entrega_atrasada` (0 ou 1) e faixas de dias com `pd.cut`.
- As avaliações duplicadas foram removidas, mantendo a mais recente de cada pedido, e o resultado foi unido aos pedidos (`merge`).

**Resultados (D1)**
- **Mediana: 9,86 dias.** É a melhor resposta, porque a distribuição tem cauda longa.
- **Média: 12,14 dias.** Fica mais alta por causa dos casos extremos (o máximo é 209 dias).
- 25% dos pedidos chegam em até 6,3 dias, 75% em até 15,1 dias e 95% em até 28,9 dias.
- 4.327 pedidos (4,5%) levaram mais de 30 dias. A base final tem 96.395 pedidos válidos.

**Resultados (D4)**
- **91,9% dos pedidos chegam antes do prazo**, 1,3% no dia e **6,8% atrasados**. Em média, a entrega chega **11,9 dias antes** do prometido: a Olist é conservadora no prazo.

| Status | Nota média | % insatisfeitos (nota 1–2) |
|---|---|---|
| Adiantado | 4,28 | 9,5% |
| No prazo | 4,01 | 13,0% |
| **Atrasado** | **2,26** | **62,9%** |

- Entre os atrasados, **54% deram nota 1**.
- A nota despenca logo nos primeiros dias de atraso:
  - antes do prazo, fica estável entre 4,2 e 4,3;
  - com 1 a 3 dias de atraso, cai para **3,28**;
  - com 4 a 7 dias, para **2,09**;
  - com 8 a 14 dias, para **1,67**.
- **Correlação entre dias de atraso e nota: −0,27.** Quanto maior o atraso, menor a nota.
- Na evolução mensal, os meses com mais atrasos (nov/2017 e fev–mar/2018) também têm notas mais baixas.

### ⭐ Satisfação (Desafio 3)
**Pergunta:** os clientes estão satisfeitos? Estão comentando?

**Como foi feito**
- Os textos vazios ou só com espaços foram tratados como nulos.
- Título e comentário nulos significam que **o cliente não escreveu**, não que houve erro. Por isso viraram as colunas `tem_comentario` e `tem_titulo`, e o texto foi preenchido com "sem comentario".
- As notas foram agrupadas em: 1–2 = insatisfeito, 3 = neutro, 4–5 = satisfeito.

**Resultados**
- **Nota média: 4,07.** Mediana: 5.
- **76,6% satisfeitos**, 8,3% neutros e **15,1% insatisfeitos**.
- **Padrão em "U":** 57,4% dão nota 5 e 11,9% dão nota 1, com poucas notas 2 e 3.
- Só **41,7%** das avaliações têm comentário e só 11,7% têm título.
- **Os insatisfeitos falam mais:** 75,6% deles comentam, contra 34,8% dos satisfeitos. Na nota 1, os textos têm cerca de 91 caracteres, contra cerca de 42 na nota 5 (o dobro).
- Ponto de atenção: há 827 `review_id` e 559 `order_id` repetidos, que foram tratados antes dos merges.

### 📦 Produtos (Desafio 5)
**Perguntas:** quais categorias vendem mais e menos? Há relação com o preço? A quantidade de fotos impacta as vendas?

**Como foi feito:** a `olist_order_items` (uma linha por item vendido) foi unida à `olist_products` pelo `product_id`. As categorias nulas viraram "sem_categoria". Também foram criadas faixas de preço e de fotos, além de dummies (top 10 categorias + "outras" e faixas de preço).

**Resultados**
- **Categorias que mais vendem:** cama_mesa_banho (11.115 itens), beleza_saude (9.670), esporte_lazer (8.641), moveis_decoracao (8.334) e informatica_acessorios (7.827). **As top 10 concentram 63,6% dos itens.**
- **Categorias que menos vendem:** seguros_e_servicos (2), fashion_roupa_infanto_juvenil (8), pc_gamer (9), la_cuisine e cds_dvds_musicais (14 cada).
- **Preço × vendas:** a correlação por categoria é de **−0,11** (Pearson) e **0,10** (Spearman). Ou seja, o preço sozinho **não explica** o que vende. Mesmo assim, **64% dos itens custam até R$ 100** e só cerca de 3% passam de R$ 500.
- **Fotos × vendas:** a correlação é de **0,004**. A média fica entre 3,3 e 3,7 vendas por produto, seja qual for o número de fotos, então as fotos **não têm impacto relevante**. A maioria dos produtos tem só 1 foto.

### 🚛 Frete & Modelo (Desafios 6 e 7)
**Perguntas:** o volume e o peso impactam o frete? Dá para criar um modelo de regressão que preveja o frete?

**Como foi feito**
- Foram criadas as variáveis `volume_cm3 = comprimento × altura × largura` e `peso_kg = peso_g / 1000`.
- 26 linhas com medidas nulas ou peso 0 foram removidas. Os 383 fretes iguais a zero (frete grátis) foram mantidos.
- No D7, foi criada a variável **`distancia_km`**: a distância entre o CEP do cliente e o do vendedor, calculada com a **fórmula de Haversine**.

**Resultados (D6)**

| Correlação com o frete | Pearson |
|---|---|
| Peso | **0,61** |
| Volume | **0,59** |
| Preço | 0,41 |

- O frete sobe pouco até cerca de 2 kg e dispara a partir de 5 kg. Itens com **mais de 10 kg pagam R$ 54,62** de frete médio, contra **R$ 15,23** dos itens com até 0,5 kg (3,6 vezes mais).
- Por volume, o frete vai de R$ 15,02 nos produtos muito pequenos a R$ 31,21 nos muito grandes.
- **Por distância:** até 100 km o frete médio é de R$ 11,76, e acima de 2.000 km é de R$ 35,90.
- Peso e volume são muito correlacionados entre si (**0,80**), ou seja, carregam informação parecida.

**Resultados (D7: modelo para prever `freight_value`)**

Variáveis usadas: `peso_kg`, `volume_cm3`, `price` e `distancia_km`. Divisão em 80% treino (89.655 linhas) e 20% teste (22.414 linhas), com `random_state=42`.

O **MAE** é o erro médio em reais. O **RMSE** também mede o erro, mas pesa mais os erros grandes. O **R²** mostra quanto da variação do frete o modelo explica (de 0 a 1).

| Modelo | MAE | RMSE | R² (teste) |
|---|---|---|---|
| Baseline (sempre a média) | R$ 8,60 | R$ 15,39 | 0,000 |
| Linear sem distância | R$ 6,77 | R$ 11,58 | 0,434 |
| Regressão Linear | R$ 5,33 | R$ 9,93 | 0,584 |
| **Random Forest** ✅ | **R$ 4,06** | **R$ 8,16** | **0,719** |

- **Modelo escolhido: Random Forest**, com o menor erro e o maior R². Ele erra cerca de **53% menos** que o baseline.
- **Overfitting** (quando o modelo se ajusta demais aos dados de treino):
  - Linear: R² de 0,588 no treino e 0,584 no teste, então não há overfitting.
  - Random Forest: R² de 0,840 no treino e 0,719 no teste, um overfitting leve. Mesmo assim, ele continua bem melhor que a regressão linear no teste.
- **Validação cruzada** (`cross_val_score`, 5 divisões): linear com R² de **0,587 ± 0,007** e Random Forest com **0,714 ± 0,014**. Os resultados são estáveis.
- **Importância das variáveis (RF):** volume 41%, distância 30%, peso 19% e preço 11%. Como peso e volume andam juntos, o modelo usa o volume para representar os dois.
- **Incluir a distância** levou a regressão linear de R² 0,43 para 0,58.

### 🗺️ Geografia (Desafio 7)
**Pergunta:** onde está a maior concentração de clientes e vendedores?

**Como foi feito**
- Na `olist_geolocation`, ficaram só as coordenadas dentro do Brasil, e foi calculada a média de latitude e longitude por prefixo de CEP.
- Clientes e vendedores foram ligados aos seus CEPs para montar o mapa.
- Os clientes foram contados por `customer_unique_id` único.

**Resultados**
- **SP concentra 41,9% dos clientes e 59,7% dos vendedores.** Seis em cada dez vendedores estão em São Paulo.
- **SP, RJ e MG juntos somam 66,5% dos clientes.**
- Cidades com mais clientes: São Paulo (~15 mil), Rio de Janeiro (~6,6 mil) e Belo Horizonte (~2,7 mil).
- Cidades com mais vendedores: São Paulo (694), Curitiba (127) e Rio de Janeiro (96).
- O mapa mostra o mercado concentrado no litoral Sul e Sudeste. A **distância mediana** entre cliente e vendedor é de **432 km**.
- **Impacto regional** (por estado do cliente):

| Indicador | SP | Pior estado |
|---|---|---|
| Frete médio por item | R$ 15,15 | RR: R$ 42,98 |
| Entrega mediana | 6,9 dias | AM: 25,8 dias |
| % de pedidos atrasados | 4,5% | AL: 21,4% |
| Nota média | 4,23 (a melhor) | MA: 3,81 |

---

## 📖 Storytelling: a mensagem principal

> A Olist vende muito, principalmente **produtos baratos** e **no Sudeste**, com pico na **Black Friday**, e **3 em cada 4 clientes estão satisfeitos**.
>
> O ponto fraco é a **logística**. Quanto mais longe de São Paulo, **mais caro o frete e maior a espera**. Quando o pedido **atrasa**, a nota cai de 4,3 para 2,3 e o cliente insatisfeito **escreve para reclamar**.
>
> **Preço e fotos não mudam o que vende. Entrega no prazo muda a satisfação.** Por isso, a melhor alavanca para a experiência do cliente é **reduzir atrasos e aproximar vendedores das regiões fora do Sudeste**. O modelo de frete (Random Forest, erro médio de R$ 4) pode apoiar essa decisão, estimando custos por região.

---

## 🎨 Design do dashboard

O dashboard segue o design system **Sonic.Link**, fornecido para o projeto:
- **Fundo:** preto (`#000`) com o **campo prismático** animado (o shader do `prism-background.js` reescrito em WebGL puro), um brilho índigo, uma grade de pontos e linhas estruturais.
- **Cards:** vidro escuro (`#18181B` com 90% de opacidade e desfoque) e borda com gradiente fino.
- **Cores:** índigo `#6366F1` como cor principal, lime `#bef264` nos filtros selecionados e emerald `#34d399` para status positivo.
- **Tipografia:** **Inter** nos textos e **JetBrains Mono** nos rótulos em caixa alta.
- **Componentes do DS:** barra de navegação em pílula, chips de filtro, medidores, badges de status e tabelas.

**Cores dos gráficos:** foram validadas para o fundo escuro, com contraste suficiente e separação para daltonismo:
- séries: índigo `#818cf8`, verde `#78a91a` e fúcsia `#d65ce8`;
- notas de 1 a 5: escala divergente, de fúcsia (nota ruim) a cinza e índigo (nota boa).

**Acessibilidade e desempenho**
- O botão "Tabela" mostra os dados de cada gráfico em lista.
- O dashboard se adapta à tela do celular.
- A animação respeita a opção de reduzir movimento do sistema e pausa quando a aba do navegador fica em segundo plano.

Os gráficos são desenhados em **SVG com JavaScript puro**, sem bibliotecas externas. A única dependência online são as fontes do Google Fonts; sem internet, o navegador usa uma fonte do sistema.

---

## Fonte dos dados

[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle). São dados reais e anonimizados de pedidos feitos entre 2016 e 2018.
