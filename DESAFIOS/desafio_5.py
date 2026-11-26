#%%
# PASSO 1 -> carregar os dados
import pandas as pd
import matplotlib.pyplot as plt

caminho = r'C:\Users\sherv\OneDrive\Desktop\ESTUDO\HARVE\Desafio_final\tabelas'

df_items = pd.read_csv(caminho + r'\olist_order_items_dataset.csv')
df_products = pd.read_csv(caminho + r'\olist_products_dataset.csv')

print('Itens vendidos:', len(df_items))
print('Produtos:      ', len(df_products))
df_products.info()

#%%
# PASSO 2 -> tratar categorias nulas
print(df_products.isna().sum())

df_products['product_category_name'] = df_products['product_category_name'].fillna('sem_categoria')

print('\nCategorias distintas:', df_products['product_category_name'].nunique())

#%%
# PASSO 3 -> juntar itens + produtos (merge)
df_vendas = df_items.merge(
    df_products[['product_id', 'product_category_name', 'product_photos_qty']],
    on='product_id',
    how='left'
)

print('Linhas antes do merge: ', len(df_items))
print('Linhas depois do merge:', len(df_vendas))
df_vendas.head()

#%%
# PASSO 4 -> categorias MAIS vendidas
vendas_categoria = df_vendas.groupby('product_category_name').agg(
    qtd_vendida=('order_id', 'count'),
    preco_medio=('price', 'mean'),
    receita=('price', 'sum')
).sort_values('qtd_vendida', ascending=False)

print('TOP 10 categorias mais vendidas:')
print(vendas_categoria.head(10).round(2))

fig, ax = plt.subplots(figsize=(10, 6))
vendas_categoria.head(10)['qtd_vendida'].sort_values().plot(kind='barh', ax=ax, color='seagreen')
ax.set_title('Top 10 categorias mais vendidas (itens)')
ax.set_xlabel('Itens vendidos')
ax.set_ylabel('')
plt.tight_layout()
plt.show()

#%%
# PASSO 5 -> categorias MENOS vendidas
print('10 categorias MENOS vendidas:')
print(vendas_categoria.tail(10).round(2))

fig, ax = plt.subplots(figsize=(10, 6))
vendas_categoria.tail(10)['qtd_vendida'].sort_values().plot(kind='barh', ax=ax, color='#d73027')
ax.set_title('10 categorias menos vendidas (itens)')
ax.set_xlabel('Itens vendidos')
ax.set_ylabel('')
plt.tight_layout()
plt.show()

# concentração: quanto as top 10 representam do total
pct_top10 = vendas_categoria.head(10)['qtd_vendida'].sum() / vendas_categoria['qtd_vendida'].sum() * 100
print(f'\nAs 10 categorias mais vendidas representam {pct_top10:.1f}% dos itens vendidos')

#%%
# PASSO 6 -> relação entre vendas e preço

# 1) dispersão: cada ponto = 1 categoria
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(vendas_categoria['preco_medio'], vendas_categoria['qtd_vendida'], alpha=0.6, color='steelblue')
for categoria in vendas_categoria.head(5).index:
    ax.annotate(categoria,
                (vendas_categoria.loc[categoria, 'preco_medio'], vendas_categoria.loc[categoria, 'qtd_vendida']),
                fontsize=8)
ax.set_title('Quantidade vendida x preço médio (por categoria)')
ax.set_xlabel('Preço médio (R$)')
ax.set_ylabel('Itens vendidos')
plt.tight_layout()
plt.show()

# 2) correlação
pearson = vendas_categoria['qtd_vendida'].corr(vendas_categoria['preco_medio'])
spearman = vendas_categoria['qtd_vendida'].rank().corr(vendas_categoria['preco_medio'].rank())
print(f'Correlação de Pearson:  {pearson:.3f}')
print(f'Correlação de Spearman: {spearman:.3f}')

# 3) faixas de preço dos itens vendidos
df_vendas['faixa_preco'] = pd.cut(df_vendas['price'],
                                bins=[0, 50, 100, 200, 500, 7000],
                                labels=['até 50', '50-100', '100-200', '200-500', '500+'])

pct_faixa = (df_vendas['faixa_preco'].value_counts(normalize=True).sort_index() * 100).round(1)
print('\n% dos itens vendidos por faixa de preço (R$):')
print(pct_faixa)

fig, ax = plt.subplots(figsize=(8, 5))
pct_faixa.plot(kind='bar', ax=ax, color='steelblue')
ax.set_title('Itens vendidos por faixa de preço')
ax.set_xlabel('Faixa de preço (R$)')
ax.set_ylabel('% dos itens')
ax.tick_params(axis='x', rotation=0)
plt.tight_layout()
plt.show()

#%%
# PASSO 7 -> fotos x vendas
vendas_produto = df_vendas.groupby('product_id').agg(
    qtd_vendida=('order_id', 'count'),
    qtd_fotos=('product_photos_qty', 'first')
).dropna()   # remove os produtos sem informação de fotos

print(vendas_produto['qtd_fotos'].describe())

vendas_produto['faixa_fotos'] = pd.cut(vendas_produto['qtd_fotos'],
                                    bins=[0, 1, 2, 4, 20],
                                    labels=['1 foto', '2 fotos', '3-4 fotos', '5+ fotos'])

vendas_por_fotos = vendas_produto.groupby('faixa_fotos', observed=True)['qtd_vendida'].agg(['mean', 'median', 'count']).round(2)
vendas_por_fotos.columns = ['media_vendas', 'mediana_vendas', 'qtd_produtos']
print(vendas_por_fotos)

pearson_fotos = vendas_produto['qtd_fotos'].corr(vendas_produto['qtd_vendida'])
spearman_fotos = vendas_produto['qtd_fotos'].rank().corr(vendas_produto['qtd_vendida'].rank())
print(f'\nCorrelação fotos x vendas (Pearson):  {pearson_fotos:.3f}')
print(f'Correlação fotos x vendas (Spearman): {spearman_fotos:.3f}')

fig, ax = plt.subplots(figsize=(8, 5))
vendas_por_fotos['media_vendas'].plot(kind='bar', ax=ax, color='steelblue')
ax.set_title('Média de vendas por produto conforme o nº de fotos')
ax.set_xlabel('')
ax.set_ylabel('Vendas médias por produto')
ax.tick_params(axis='x', rotation=0)
plt.tight_layout()
plt.show()

#%%
# PASSO 8 -> variáveis dummies

# reduzir: top 10 categorias + 'outras'
top10 = vendas_categoria.head(10).index
df_vendas['categoria_top'] = df_vendas['product_category_name'].where(
    df_vendas['product_category_name'].isin(top10), 'outras')

print(df_vendas['categoria_top'].value_counts())

# criar as dummies (0/1)
dummies_categoria = pd.get_dummies(df_vendas['categoria_top'], prefix='cat', dtype=int)
dummies_preco = pd.get_dummies(df_vendas['faixa_preco'], prefix='preco', dtype=int)

df_vendas_dummies = pd.concat([df_vendas, dummies_categoria, dummies_preco], axis=1)

print('\nColunas antes:', df_vendas.shape[1])
print('Colunas depois:', df_vendas_dummies.shape[1])
df_vendas_dummies[['product_category_name', 'categoria_top'] + list(dummies_categoria.columns[:3])].head()

#%%
# PASSO 9 -> CONCLUSÃO DO DESAFIO 5
# ---------------------------------------------------------------------
# 1) Categorias MAIS vendidas (itens):
#    cama_mesa_banho (11.115), beleza_saude (9.670), esporte_lazer (8.641),
#    moveis_decoracao (8.334), informatica_acessorios (7.827)
#    -> as top 10 concentram ~64% dos itens vendidos
#
#    Categorias MENOS vendidas:
#    seguros_e_servicos (2), fashion_roupa_infanto_juvenil (8), pc_gamer (9),
#    la_cuisine e cds_dvds_musicais (14)
#
# 2) Vendas x preço:
#    - Correlação por categoria praticamente nula (Pearson -0,11 / Spearman 0,10)
#      -> o preço médio, sozinho, NÃO explica quais categorias vendem mais
#    - Mas os itens vendidos são, em sua maioria, baratos:
#      ~64% custam até R$ 100 e só ~3% passam de R$ 500
#    - relogios_presentes vende muito mesmo com preço médio alto (~R$ 200)
#      -> maior receita por item entre as top 10
#
# 3) Fotos x vendas:
#    - Correlação ~0 (Pearson 0,004 / Spearman 0,015)
#    - A média de vendas por produto é parecida em todas as faixas (~3,3 a 3,7)
#    -> a quantidade de fotos NÃO tem impacto relevante nas vendas
#    - A maioria dos produtos tem só 1 foto (mediana = 1)
#
# 4) Dummies:
#    - Categoria reduzida para top 10 + 'outras' -> 11 colunas 0/1
#    - Faixa de preço -> 5 colunas 0/1
# =====================================================================