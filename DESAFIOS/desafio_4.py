#%%
# PASSO 1 -> carregar os dados
import pandas as pd
import matplotlib.pyplot as plt

caminho = r'C:\Users\sherv\OneDrive\Desktop\ESTUDO\HARVE\Desafio_final\tabelas'

df_orders = pd.read_csv(caminho + r'\olist_orders_dataset.csv')
df_reviews = pd.read_csv(caminho + r'\olist_order_reviews_dataset.csv')

print('Pedidos:   ', len(df_orders))
print('Avaliações:', len(df_reviews))

#%%
# PASSO 2 -> converter datas e filtrar pedidos entregues
df_orders['order_delivered_customer_date'] = pd.to_datetime(df_orders['order_delivered_customer_date'])
df_orders['order_estimated_delivery_date'] = pd.to_datetime(df_orders['order_estimated_delivery_date'])

df_entregues = df_orders[
    (df_orders['order_status'] == 'delivered') &
    (df_orders['order_delivered_customer_date'].notna()) &
    (df_orders['order_estimated_delivery_date'].notna())
].copy()

print('Pedidos entregues:', len(df_entregues))

#%%
# PASSO 3 -> feature engineering

# 1) duas datas -> um número: diferença em dias (só a data, sem hora)
df_entregues['dias_diferenca'] = (
    df_entregues['order_delivered_customer_date'].dt.normalize() -
    df_entregues['order_estimated_delivery_date'].dt.normalize()
).dt.days
# negativo = chegou ANTES do prazo | 0 = no dia | positivo = dias de ATRASO

# 2) número -> categoria
def classificar_entrega(dias):
    if dias < 0:
        return 'Adiantado'
    elif dias == 0:
        return 'No prazo'
    else:
        return 'Atrasado'

df_entregues['status_entrega'] = df_entregues['dias_diferenca'].apply(classificar_entrega)

# 3) flag 0/1 (1 = atrasado)
df_entregues['entrega_atrasada'] = (df_entregues['dias_diferenca'] > 0).astype(int)

print(df_entregues['status_entrega'].value_counts())
print((df_entregues['status_entrega'].value_counts(normalize=True) * 100).round(1))
print(df_entregues['dias_diferenca'].describe())

df_entregues[['order_delivered_customer_date', 'order_estimated_delivery_date',
            'dias_diferenca', 'status_entrega', 'entrega_atrasada']].head(10)


#%%
# PASSO 4 -> remover avaliações duplicadas
df_reviews['review_answer_timestamp'] = pd.to_datetime(df_reviews['review_answer_timestamp'])

# ordenar da mais antiga para a mais recente e manter a última de cada pedido
df_reviews_unicas = (df_reviews
                    .sort_values('review_answer_timestamp')
                    .drop_duplicates(subset='order_id', keep='last'))

print('Avaliações antes: ', len(df_reviews))
print('Avaliações depois:', len(df_reviews_unicas))

#%%
# PASSO 5 -> juntar pedidos + avaliações (merge)
df_analise = df_entregues.merge(
    df_reviews_unicas[['order_id', 'review_score']],
    on='order_id',
    how='inner'
)

print('Pedidos com avaliação:', len(df_analise))
df_analise[['order_id', 'dias_diferenca', 'status_entrega', 'review_score']].head()

#%%
# PASSO 6 -> nota média por status de entrega
ordem = ['Adiantado', 'No prazo', 'Atrasado']

nota_por_status = df_analise.groupby('status_entrega')['review_score'].agg(['mean', 'median', 'count'])
nota_por_status = nota_por_status.reindex(ordem).round(2)
nota_por_status.columns = ['nota_media', 'nota_mediana', 'qtd_pedidos']
print(nota_por_status)

# % de insatisfeitos (nota 1 ou 2) em cada grupo
df_analise['insatisfeito'] = df_analise['review_score'] <= 2
print('\n% de insatisfeitos (nota 1-2):')
print((df_analise.groupby('status_entrega')['insatisfeito'].mean() * 100).reindex(ordem).round(1))

fig, ax = plt.subplots(figsize=(8, 5))
nota_por_status['nota_media'].plot(kind='bar', ax=ax, color=['#1a9850', '#fee08b', '#d73027'])
ax.set_title('Nota média por status de entrega')
ax.set_xlabel('')
ax.set_ylabel('Nota média')
ax.set_ylim(0, 5)
ax.tick_params(axis='x', rotation=0)
for i, valor in enumerate(nota_por_status['nota_media']):
    ax.text(i, valor, f'{valor:.2f}', ha='center', va='bottom')
plt.tight_layout()
plt.show()


#%%
# PASSO 7 -> distribuição das notas por status de entrega
distribuicao = pd.crosstab(df_analise['status_entrega'],
                    df_analise['review_score'],
                    normalize='index') * 100
distribuicao = distribuicao.reindex(ordem).round(1)
print(distribuicao)

fig, ax = plt.subplots(figsize=(10, 5))
distribuicao.plot(kind='barh', stacked=True, ax=ax,
    color=['#d73027', '#fc8d59', '#fee08b', '#91cf60', '#1a9850'])
ax.set_title('Distribuição das notas por status de entrega (%)')
ax.set_xlabel('%')
ax.set_ylabel('')
ax.legend(title='Nota', bbox_to_anchor=(1.01, 1), loc='upper left')
plt.tight_layout()
plt.show()

#%%
# PASSO 8 -> nota por faixa de dias (antes/depois do prazo)
limites = [-200, -15, -8, -1, 0, 3, 7, 14, 30, 300]
nomes = ['15+ dias antes', '8-14 antes', '1-7 antes', 'no dia',
        '1-3 atraso', '4-7 atraso', '8-14 atraso', '15-30 atraso', '30+ atraso']

df_analise['faixa_entrega'] = pd.cut(df_analise['dias_diferenca'], bins=limites, labels=nomes)

nota_por_faixa = df_analise.groupby('faixa_entrega', observed=True)['review_score'].agg(['mean', 'count']).round(2)
nota_por_faixa.columns = ['nota_media', 'qtd_pedidos']
print(nota_por_faixa)

fig, ax = plt.subplots(figsize=(12, 5))
nota_por_faixa['nota_media'].plot(kind='line', marker='o', ax=ax, color='steelblue')
ax.axvline(3, color='red', linestyle='--', label='Prazo estimado')
ax.set_title('Nota média conforme a entrega (antes x depois do prazo)')
ax.set_xticks(range(len(nota_por_faixa)))
ax.set_xticklabels(nota_por_faixa.index, rotation=45)
ax.set_ylabel('Nota média')
ax.set_ylim(1, 5)
ax.legend()
plt.tight_layout()
plt.show()

#%%
# PASSO 9 -> correlação
correlacao = df_analise['dias_diferenca'].corr(df_analise['review_score'])
print(f'Correlação entre dias_diferenca e review_score: {correlacao:.3f}')

#%%
# PASSO 10 -> CONCLUSÃO DO DESAFIO 4
# ---------------------------------------------------------------------
# 1) Pontualidade:
#    - 91,9% dos pedidos chegam ANTES do prazo; 1,3% no dia; 6,8% atrasados
#    - Em média, a entrega chega ~12 dias antes do prazo estimado
#      -> a Olist superestima o prazo (é "conservadora")
#
# 2) Satisfação x entrega -> SIM, existe um padrão forte:
#    - Adiantado: nota média 4,28 | 9,5% insatisfeitos
#    - No prazo:  nota média 4,01 | 13,0% insatisfeitos
#    - Atrasado:  nota média 2,26 | 62,9% insatisfeitos
#    - Entre os atrasados, 54,2% deram NOTA 1
#
# 3) Efeito do tamanho do atraso:
#    - Antes do prazo, a nota fica estável (~4,2 a 4,3)
#    - Com 1-3 dias de atraso, cai para 3,28; com 8+ dias, fica abaixo de 1,7
#    -> a nota despenca logo nos primeiros dias de atraso
#
# 4) Correlação: -0,27 (negativa) -> quanto maior o atraso, menor a nota
#
# 5) Feature engineering:
#    - 2 datas -> 1 coluna numérica (dias_diferenca)
#    - dias_diferenca -> categoria (status_entrega) e flag 0/1 (entrega_atrasada)
#    - faixas de dias (faixa_entrega) com pd.cut
#    - avaliações duplicadas removidas (mantida a mais recente por pedido)
# =====================================================================