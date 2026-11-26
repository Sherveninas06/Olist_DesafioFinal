

#%%
# PASSO 1 -  carregar dados 
import pandas as pd
import matplotlib.pyplot as plt

caminho = r'C:\Users\sherv\OneDrive\Desktop\ESTUDO\HARVE\Desafio_final\tabelas'

df_orders = pd.read_csv(caminho + r'\olist_orders_dataset.csv')
df_payments = pd.read_csv(caminho + r'\olist_order_payments_dataset.csv')

df_payments.info()
df_payments.head()


#%%
# PASSO 2 - criar coluna ano-mes
df_orders['order_purchase_timestamp'] = pd.to_datetime(df_orders['order_purchase_timestamp'])

# to_period('M') transforma 2017-11-24 15:30 em 2017-11
df_orders['ano_mes'] = df_orders['order_purchase_timestamp'].dt.to_period('M')

# conferir se a coluna foi criada
df_orders[['order_purchase_timestamp', 'ano_mes']].head()


#%%
# PASSO 3 - o mes com mais pedidos
pedidos_por_mes = df_orders.groupby('ano_mes')['order_id'].count()
print(pedidos_por_mes)

print(f'Mês com MAIS pedidos : {pedidos_por_mes.idxmax()} - {pedidos_por_mes.max()} pedidos.')
# -> idxmax devolve qual mes tem o maior valor, max devolve o valor


#%%
# PASSO 4 -> o mes com mais pagamento 

# 1º: somar os pagamentos de cada pedido (1 linha por pedido)
pagamento_por_pedido = df_payments.groupby('order_id', as_index=False)['payment_value'].sum()

# 2º: juntar com orders para obter o mês de cada pedido
df_pedidos_pag = df_orders.merge(pagamento_por_pedido, on='order_id', how='left')

# 3º: somar os pagamentos por mês
pagamentos_por_mes = df_pedidos_pag.groupby('ano_mes')['payment_value'].sum()
print(pagamentos_por_mes)

print(f'Mês com MAIORES pagamentos: {pagamentos_por_mes.idxmax()} - R$ {pagamentos_por_mes.max():,.2f}')

#%%
#PASSO 5 -> gráficos por mes 

fig, ax = plt.subplots(2, 1, figsize=(12, 8))

pedidos_por_mes.plot(kind='bar', ax=ax[0], color='steelblue')
ax[0].set_title('Quantidade de pedidos por mês')
ax[0].set_ylabel('Pedidos')

pagamentos_por_mes.plot(kind='bar', ax=ax[1], color='seagreen')
ax[1].set_title('Total de pagamentos por mês (R$)')
ax[1].set_ylabel('R$')

plt.tight_layout()
plt.show()


#%%
# PASSO 6 -> outliers ( metodo IQR) 
colunas_numericas = ['payment_sequential', 'payment_installments', 'payment_value']

for coluna in colunas_numericas:
    q1 = df_payments[coluna].quantile(0.25)
    q3 = df_payments[coluna].quantile(0.75)
    iqr = q3 - q1
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr

    outliers = df_payments[(df_payments[coluna] < limite_inferior) |
        (df_payments[coluna] > limite_superior)]

    print(f'--- {coluna} ---')
    print(f'Limites: {limite_inferior:.2f} até {limite_superior:.2f}')
    print(f'Outliers: {len(outliers)} ({len(outliers) / len(df_payments) * 100:.1f}%)')
    print(f'Máximo: {df_payments[coluna].max()}\n')

#%%
# PASSO 7 -> bloxplot 
fig, ax = plt.subplots(1, 3, figsize=(15, 5))

for i, coluna in enumerate(colunas_numericas):
    ax[i].boxplot(df_payments[coluna])
    ax[i].set_title(coluna)

plt.tight_layout()
plt.show()


#%%
# PASSO 8 -> valores estranhos ( qualidade dos dados )
print('Pagamentos com valor 0:', (df_payments['payment_value'] == 0).sum())
print('Pagamentos com 0 parcelas:', (df_payments['payment_installments'] == 0).sum())
print(df_payments['payment_type'].value_counts())


# %%
#PASSO 9 -> remover meses incompletos 

# meses com menos pedidos = base começou/terminou no meio do mês
meses_incompletos = pedidos_por_mes[pedidos_por_mes <100]
print(f"Meses removidos : {meses_incompletos}")

#manter só os meses completos
pedidos_mes_completo= pedidos_por_mes[pedidos_por_mes >= 100]
pagamentos_mes_completo = pagamentos_por_mes[pagamentos_por_mes.index.isin(pedidos_mes_completo.index)]

print(f'\nMês com MAIS pedidos: {pedidos_mes_completo.idxmax()} - {pedidos_mes_completo.max()} pedidos')
print(f'Média de pedidos por mês: {pedidos_mes_completo.mean():.0f}')
print(f'\nMês com MAIORES pagamentos: {pagamentos_mes_completo.idxmax()} - R$ {pagamentos_mes_completo.max():,.2f}')
print(f'Média de pagamentos por mês: R$ {pagamentos_mes_completo.mean():,.2f}')

# gráficos atualizados (linha = mostra melhor a tendência ao longo do tempo)
fig, ax = plt.subplots(2, 1, figsize=(12, 8))

pedidos_mes_completo.plot(kind='line', marker='o', ax=ax[0], color='steelblue')
ax[0].set_title('Pedidos por mês (somente meses completos)')
ax[0].set_ylabel('Pedidos')

pagamentos_mes_completo.plot(kind='line', marker='o', ax=ax[1], color='seagreen')
ax[1].set_title('Pagamentos por mês em R$ (somente meses completos)')
ax[1].set_ylabel('R$')

plt.tight_layout()
plt.show()


#%%
# PASSO 10 -> outliers em price e freight_value (tabela de itens)
df_items = pd.read_csv(caminho + r'\olist_order_items_dataset.csv')

colunas_itens = ['price', 'freight_value']

for coluna in colunas_itens:
    q1 = df_items[coluna].quantile(0.25)
    q3 = df_items[coluna].quantile(0.75)
    iqr = q3 - q1
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr

    outliers = df_items[(df_items[coluna] < limite_inferior) |
                        (df_items[coluna] > limite_superior)]

    print(f'--- {coluna} ---')
    print(f'Limites: {limite_inferior:.2f} até {limite_superior:.2f}')
    print(f'Outliers: {len(outliers)} ({len(outliers) / len(df_items) * 100:.1f}%)')
    print(f'Máximo: {df_items[coluna].max()}')
    print(f'Valores iguais a 0: {(df_items[coluna] == 0).sum()}\n')

# boxplots
fig, ax = plt.subplots(1, 2, figsize=(12, 5))

for i, coluna in enumerate(colunas_itens):
    ax[i].boxplot(df_items[coluna])
    ax[i].set_title(coluna)

plt.tight_layout()
plt.show()

#%%
# PASSO 11 -> pico de novembro/2017 (Black Friday)

# filtrar só os pedidos de novembro de 2017
df_nov_2017 = df_orders[df_orders['ano_mes'] == '2017-11']

# contar pedidos por dia do mês
pedidos_por_dia = df_nov_2017.groupby(df_nov_2017['order_purchase_timestamp'].dt.day)['order_id'].count()

dia_pico = pedidos_por_dia.idxmax()
media_outros_dias = pedidos_por_dia.drop(dia_pico).mean()

print(f'Dia com mais pedidos: {dia_pico}/11/2017 - {pedidos_por_dia.max()} pedidos')
print(f'Média dos outros dias do mês: {media_outros_dias:.0f} pedidos')
print(f'O pico foi {pedidos_por_dia.max() / media_outros_dias:.1f}x maior que um dia comum')

# gráfico por dia
fig, ax = plt.subplots(figsize=(12, 5))
pedidos_por_dia.plot(kind='bar', ax=ax, color='steelblue')
ax.set_title('Pedidos por dia - Novembro/2017')
ax.set_xlabel('Dia')
ax.set_ylabel('Pedidos')
plt.tight_layout()
plt.show()


#%%
# CONCLUSÃO DO DESAFIO 2
# ---------------------------------------------------------------------
# 1) Mês com MAIS pedidos: novembro/2017
# 2) Mês com MAIORES pagamentos: novembro/2017
#    -> O pico é explicado pela Black Friday (24/11/2017)
#
# 3) Outliers:
#    - payment_value, price e freight_value têm distribuição assimétrica:
#      a maioria dos valores é baixa e poucos valores são muito altos
#    - Os outliers parecem compras reais de alto valor, NÃO erros
#      -> decisão: manter na análise, apenas sinalizar
#
# 4) Qualidade dos dados:
#    - Meses incompletos (2016-09, 2016-12, 2018-09, 2018-10) foram removidos da comparação
#    - Pagamentos com valor 0 e com 0 parcelas são poucos e devem ser investigados
# =====================================================================
