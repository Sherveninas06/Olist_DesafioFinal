#%%
# PASSO 1 -> carregar os dados
import pandas as pd
import matplotlib.pyplot as plt

caminho = r'C:\Users\sherv\OneDrive\Desktop\ESTUDO\HARVE\Desafio_final\tabelas'

df_items = pd.read_csv(caminho + r'\olist_order_items_dataset.csv')
df_products = pd.read_csv(caminho + r'\olist_products_dataset.csv')

colunas_medidas = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']
print(df_products[colunas_medidas].describe())

#%%
# PASSO 2 -> juntar itens + produtos (merge)
df_frete = df_items[['order_id', 'product_id', 'price', 'freight_value']].merge(
    df_products[['product_id'] + colunas_medidas],
    on='product_id',
    how='left'
)

print('Linhas:', len(df_frete))
df_frete.head()

#%%
# PASSO 3 -> tratamento (nulos e peso zero)
print('Nulos por coluna:')
print(df_frete[colunas_medidas].isna().sum())
print('\nProdutos com peso = 0:', (df_frete['product_weight_g'] == 0).sum())

linhas_antes = len(df_frete)

df_frete = df_frete.dropna(subset=colunas_medidas)
df_frete = df_frete[df_frete['product_weight_g'] > 0]

print(f'\nLinhas antes:    {linhas_antes}')
print(f'Linhas depois:   {len(df_frete)}')
print(f'Linhas removidas: {linhas_antes - len(df_frete)}')

# frete = 0 -> provavelmente frete grátis (mantido, mas sinalizado)
print('\nItens com frete = 0 (frete grátis):', (df_frete['freight_value'] == 0).sum())

#%%
# PASSO 4 -> feature engineering (volume_cm3 e peso_kg)
df_frete['volume_cm3'] = (df_frete['product_length_cm'] *
                        df_frete['product_height_cm'] *
                        df_frete['product_width_cm'])

df_frete['peso_kg'] = df_frete['product_weight_g'] / 1000

print(df_frete[['freight_value', 'peso_kg', 'volume_cm3']].describe().round(2))

#%%
# PASSO 5 -> correlação
colunas_analise = ['freight_value', 'peso_kg', 'volume_cm3', 'price']

print('Correlação de Pearson:')
print(df_frete[colunas_analise].corr().round(3))

print('\nCorrelação de Spearman:')
print(df_frete[colunas_analise].rank().corr().round(3))

# mapa de calor da correlação de Pearson
correlacao = df_frete[colunas_analise].corr()

fig, ax = plt.subplots(figsize=(7, 6))
imagem = ax.imshow(correlacao, cmap='Blues', vmin=0, vmax=1)
ax.set_xticks(range(len(colunas_analise)))
ax.set_yticks(range(len(colunas_analise)))
ax.set_xticklabels(colunas_analise, rotation=45)
ax.set_yticklabels(colunas_analise)
for i in range(len(colunas_analise)):
    for j in range(len(colunas_analise)):
        ax.text(j, i, f'{correlacao.iloc[i, j]:.2f}', ha='center', va='center')
fig.colorbar(imagem)
ax.set_title('Correlação (Pearson)')
plt.tight_layout()
plt.show()

#%%
# PASSO 6 -> frete por faixa de peso
df_frete['faixa_peso'] = pd.cut(df_frete['peso_kg'],
                                bins=[0, 0.5, 1, 2, 5, 10, 50],
                                labels=['até 0,5kg', '0,5-1kg', '1-2kg', '2-5kg', '5-10kg', '10kg+'])

frete_por_peso = df_frete.groupby('faixa_peso', observed=True)['freight_value'].agg(['mean', 'median', 'count']).round(2)
frete_por_peso.columns = ['frete_medio', 'frete_mediano', 'qtd_itens']
print(frete_por_peso)

fig, ax = plt.subplots(figsize=(9, 5))
frete_por_peso['frete_medio'].plot(kind='bar', ax=ax, color='steelblue')
ax.set_title('Frete médio por faixa de peso')
ax.set_xlabel('')
ax.set_ylabel('Frete médio (R$)')
ax.tick_params(axis='x', rotation=0)
plt.tight_layout()
plt.show()

#%%
# PASSO 7 -> frete por faixa de volume
df_frete['faixa_volume'] = pd.qcut(df_frete['volume_cm3'], q=5,
                            labels=['muito pequeno', 'pequeno', 'médio', 'grande', 'muito grande'])

frete_por_volume = df_frete.groupby('faixa_volume', observed=True)['freight_value'].agg(['mean', 'median', 'count']).round(2)
frete_por_volume.columns = ['frete_medio', 'frete_mediano', 'qtd_itens']
print(frete_por_volume)

fig, ax = plt.subplots(figsize=(9, 5))
frete_por_volume['frete_medio'].plot(kind='bar', ax=ax, color='seagreen')
ax.set_title('Frete médio por faixa de volume')
ax.set_xlabel('')
ax.set_ylabel('Frete médio (R$)')
ax.tick_params(axis='x', rotation=0)
plt.tight_layout()
plt.show()

#%%
# PASSO 8 -> gráficos de dispersão
amostra = df_frete.sample(5000, random_state=42)

fig, ax = plt.subplots(1, 2, figsize=(14, 5))

ax[0].scatter(amostra['peso_kg'], amostra['freight_value'], alpha=0.3, s=10, color='steelblue')
ax[0].set_title('Frete x Peso')
ax[0].set_xlabel('Peso (kg)')
ax[0].set_ylabel('Frete (R$)')

ax[1].scatter(amostra['volume_cm3'], amostra['freight_value'], alpha=0.3, s=10, color='seagreen')
ax[1].set_title('Frete x Volume')
ax[1].set_xlabel('Volume (cm³)')
ax[1].set_ylabel('Frete (R$)')

plt.tight_layout()
plt.show()

#%%
# PASSO 9 -> separar treino e teste

# variáveis que o modelo vai usar (X) e o que queremos prever (y)
colunas_modelo = ['peso_kg', 'volume_cm3', 'price', 'freight_value']
df_modelo = df_frete[colunas_modelo].copy()

# 80% treino (sorteio fixo com random_state)
df_treino = df_modelo.sample(frac=0.8, random_state=42)

# 20% teste = tudo que NÃO foi para o treino
df_teste = df_modelo.drop(df_treino.index)

print(f'Total:  {len(df_modelo)}')
print(f'Treino: {len(df_treino)} ({len(df_treino) / len(df_modelo) * 100:.0f}%)')
print(f'Teste:  {len(df_teste)} ({len(df_teste) / len(df_modelo) * 100:.0f}%)')

# conferir se os dois grupos são parecidos
print(f'\nFrete médio no treino: R$ {df_treino["freight_value"].mean():.2f}')
print(f'Frete médio no teste:  R$ {df_teste["freight_value"].mean():.2f}')

#%%
# PASSO 10 -> CONCLUSÃO DO DESAFIO 6
# ---------------------------------------------------------------------
# 1) SIM: peso e volume impactam no frete
#    - Correlação frete x peso:   0,61 (moderada/forte)
#    - Correlação frete x volume: 0,59 (moderada)
#    - Correlação frete x preço:  0,41 (mais fraca)
#    -> o PESO é a variável que mais explica o frete
#
# 2) Frete médio por peso:
#    - até 0,5kg: R$ 15,23  ->  10kg+: R$ 54,62 (3,6x mais caro)
#    - até ~2kg o frete sobe pouco; a partir de 5kg dispara
#
# 3) Frete médio por volume:
#    - muito pequeno: R$ 15,02  ->  muito grande: R$ 31,21 (2x mais caro)
#    - salto maior só no grupo "muito grande"
#
# 4) Peso e volume são muito correlacionados entre si (0,80)
#    -> carregam informação parecida (atenção no modelo do Desafio 7)
#
# 5) Frete não depende só do produto: a distância (cliente x vendedor) também
#    influencia, o que explica a dispersão nos gráficos
#
# 6) Tratamentos: 26 linhas removidas (nulos e peso 0); 383 fretes = 0 mantidos
#    Treino: 90.099 linhas (80%) | Teste: 22.525 linhas (20%)
# =====================================================================