# DESAFIO 1
# Qual é o tempo médio/mediano desde a aprovação do pedido até a sua entrega?
# Tabela usada: olist_orders_dataset.csv

#%%
import pandas as pd
import matplotlib.pyplot as plt

#%%
# PASSO 1 - Carregar e inspecionar os dados
df_dataset = pd.read_csv(r'C:\Users\sherv\OneDrive\Desktop\ESTUDO\HARVE\Desafio_final\tabelas\olist_orders_dataset.csv')

df_dataset.info()
print(df_dataset['order_status'].value_counts())

#%%
# PASSO 2 - Converter as colunas de data (str -> datetime)
df_dataset['order_approved_at'] = pd.to_datetime(df_dataset['order_approved_at'])
df_dataset['order_delivered_customer_date'] = pd.to_datetime(df_dataset['order_delivered_customer_date'])

df_dataset[['order_approved_at', 'order_delivered_customer_date']].info()

# Quantos valores vazios (NaT) existem em cada coluna
print(df_dataset[['order_approved_at', 'order_delivered_customer_date']].isna().sum())

#%%
# PASSO 3 - Filtrar: apenas pedidos ENTREGUES com as DUAS datas preenchidas
# (o status 'delivered' remove 6 pedidos cancelados que tinham data de entrega)
df_entregues = df_dataset[
    (df_dataset['order_status'] == 'delivered') &
    (df_dataset['order_approved_at'].notna()) &
    (df_dataset['order_delivered_customer_date'].notna())
].copy()

print('Total de pedidos:  ', len(df_dataset))
print('Pedidos entregues: ', len(df_entregues))
print('Pedidos removidos: ', len(df_dataset) - len(df_entregues))

#%%
# PASSO 4 - Calcular o tempo de entrega em dias (com fração)
df_entregues['tempo_entrega_dias'] = (
    df_entregues['order_delivered_customer_date'] - df_entregues['order_approved_at']
).dt.total_seconds() / 86400   # 86400 = segundos em 1 dia

df_entregues[['order_approved_at', 'order_delivered_customer_date', 'tempo_entrega_dias']].head(10)

#%%
# PASSO 5 - Qualidade dos dados: tempos negativos (entrega antes da aprovação)
df_negativos = df_entregues[df_entregues['tempo_entrega_dias'] < 0]
print('Pedidos com tempo negativo:', len(df_negativos))
print(df_negativos['tempo_entrega_dias'].describe())

# Remover os registros inconsistentes
df_entregues = df_entregues[df_entregues['tempo_entrega_dias'] >= 0]
print('Pedidos válidos para análise:', len(df_entregues))

#%%
# PASSO 6 - Agregação: média e mediana (resposta do desafio)
media = df_entregues['tempo_entrega_dias'].mean()
mediana = df_entregues['tempo_entrega_dias'].median()

print(f'Tempo MÉDIO de entrega:   {media:.2f} dias')
print(f'Tempo MEDIANO de entrega: {mediana:.2f} dias')

#%%
# PASSO 7 - Distribuição do tempo de entrega
print(df_entregues['tempo_entrega_dias'].describe())
print(df_entregues['tempo_entrega_dias'].quantile([0.90, 0.95, 0.99]))

print('Pedidos com mais de 30 dias:', (df_entregues['tempo_entrega_dias'] > 30).sum())
print('Pedidos com mais de 60 dias:', (df_entregues['tempo_entrega_dias'] > 60).sum())

#%%
# PASSO 8 - Histograma
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(df_entregues['tempo_entrega_dias'], bins=100, range=(0, 60), color='steelblue', edgecolor='white')
ax.axvline(media, color='red', linestyle='--', label=f'Média: {media:.1f} dias')
ax.axvline(mediana, color='green', linestyle='--', label=f'Mediana: {mediana:.1f} dias')
ax.set_title('Tempo entre aprovação e entrega do pedido (até 60 dias)')
ax.set_xlabel('Dias')
ax.set_ylabel('Quantidade de pedidos')
ax.legend()
plt.show()

#%%
# PASSO 9 -> CONCLUSÃO DO DESAFIO 1
# ---------------------------------------------------------------------
# 1) Tempo entre aprovação e entrega:
#    - MEDIANA: 9,86 dias  -> um pedido típico chega em ~10 dias
#    - MÉDIA:   12,14 dias -> puxada para cima pelos pedidos muito demorados
#    - 25% chegam em até 6,3 dias | 75% em até 15,1 dias | 95% em até 28,9 dias
#
# 2) Distribuição assimétrica à direita:
#    - 4.327 pedidos (4,5%) levaram mais de 30 dias; 298 mais de 60 dias
#    - máximo de 208 dias -> por isso a MEDIANA é a melhor resposta
#
# 3) Qualidade dos dados:
#    - 2.985 pedidos removidos (não entregues / sem data / 6 cancelados com entrega)
#    - 61 pedidos com tempo NEGATIVO (entrega antes da aprovação) -> removidos
#    - 96.395 pedidos válidos na análise
# =====================================================================
