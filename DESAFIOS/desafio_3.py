#%%
# PASSO 1 -> carregar e inspecionar os dados
import pandas as pd
import matplotlib.pyplot as plt

caminho = r'C:\Users\sherv\OneDrive\Desktop\ESTUDO\HARVE\Desafio_final\tabelas'

df_reviews= pd.read_csv(caminho + r'\olist_order_reviews_dataset.csv')

df_reviews.info()
df_reviews.head()

# %%
# PASSO 2 -> valores nulos e duplicados
nulos = df_reviews.isna().sum()
percentual_nulos = (df_reviews.isna().mean()* 100).round(1)

tabela_nulos = pd.DataFrame({'nulos': nulos, '%nulos': percentual_nulos})
print(tabela_nulos)

print('\nreview_id repetidos:', df_reviews['review_id'].duplicated().sum())
print('order_id repetidos: ', df_reviews['order_id'].duplicated().sum())

#%%
# PASSO 3 -> tratamento dos nulos

# 1º: textos só com espaços também são considerados vazios
for coluna in ['review_comment_title', 'review_comment_message']:
    df_reviews[coluna] = df_reviews[coluna].str.strip().replace('', pd.NA)

# 2º: colunas indicadoras (True = cliente escreveu)
df_reviews['tem_comentario'] = df_reviews['review_comment_message'].notna()
df_reviews['tem_titulo'] = df_reviews['review_comment_title'].notna()

# 3º: preencher os textos vazios
df_reviews['review_comment_message'] = df_reviews['review_comment_message'].fillna('sem comentario')
df_reviews['review_comment_title'] = df_reviews['review_comment_title'].fillna('sem titulo')

# conferir: não deve sobrar nenhum nulo
print(df_reviews.isna().sum())

#%%
# PASSO 4 -> distribuição das notas
contagem_notas = df_reviews['review_score'].value_counts().sort_index()
percentual_notas = (df_reviews['review_score'].value_counts(normalize=True).sort_index() * 100).round(1)

print(pd.DataFrame({'quantidade': contagem_notas, '%': percentual_notas}))
print(f'\nNota média:   {df_reviews["review_score"].mean():.2f}')
print(f'Nota mediana: {df_reviews["review_score"].median():.0f}')

fig, ax = plt.subplots(figsize=(8, 5))
contagem_notas.plot(kind='bar', ax=ax, color=['#d73027', '#fc8d59', '#fee08b', '#91cf60', '#1a9850'])
ax.set_title('Distribuição das notas de avaliação')
ax.set_xlabel('Nota')
ax.set_ylabel('Quantidade de avaliações')
ax.tick_params(axis='x', rotation=0)

# mostrar o % em cima de cada barra
for i, valor in enumerate(contagem_notas):
    ax.text(i, valor, f'{percentual_notas.iloc[i]}%', ha='center', va='bottom')

plt.tight_layout()
plt.show()

#%%
# PASSO 5 -> classificação da satisfação
def classificar_satisfacao(nota):
    if nota <= 2:
        return 'Insatisfeito'
    elif nota == 3:
        return 'Neutro'
    else:
        return 'Satisfeito'

df_reviews['satisfacao'] = df_reviews['review_score'].apply(classificar_satisfacao)

print((df_reviews['satisfacao'].value_counts(normalize=True) * 100).round(1))

fig, ax = plt.subplots(figsize=(6, 6))
df_reviews['satisfacao'].value_counts().plot(
    kind='pie', ax=ax, autopct='%1.1f%%',
    colors=['#1a9850', '#d73027', '#fee08b'])
ax.set_title('Satisfação dos clientes')
ax.set_ylabel('')
plt.show()

#%%
# PASSO 6 -> os clientes estão comentando?
pct_comentario = df_reviews['tem_comentario'].mean() * 100
pct_titulo = df_reviews['tem_titulo'].mean() * 100

print(f'Avaliações COM comentário: {pct_comentario:.1f}%')
print(f'Avaliações SEM comentário: {100 - pct_comentario:.1f}%')
print(f'Avaliações COM título:     {pct_titulo:.1f}%')

#%%
# PASSO 7 -> comentários por nota
comentario_por_nota = pd.crosstab(df_reviews['review_score'],
                                df_reviews['tem_comentario'],
                                normalize='index') * 100
comentario_por_nota.columns = ['Sem comentário', 'Com comentário']
print(comentario_por_nota.round(1))

print('\n% com comentário por grupo de satisfação:')
print((df_reviews.groupby('satisfacao')['tem_comentario'].mean() * 100).round(1))

fig, ax = plt.subplots(figsize=(8, 5))
comentario_por_nota.plot(kind='bar', stacked=True, ax=ax, color=['lightgray', 'steelblue'])
ax.set_title('Percentual de avaliações com comentário por nota')
ax.set_xlabel('Nota')
ax.set_ylabel('%')
ax.tick_params(axis='x', rotation=0)
ax.legend(loc='upper right')
plt.tight_layout()
plt.show()

#%%
# PASSO 8 -> tamanho dos comentários
df_com_comentario = df_reviews[df_reviews['tem_comentario']].copy()
df_com_comentario['tamanho_comentario'] = df_com_comentario['review_comment_message'].str.len()

tamanho_por_nota = df_com_comentario.groupby('review_score')['tamanho_comentario'].median()
print('Tamanho mediano do comentário (caracteres) por nota:')
print(tamanho_por_nota)

fig, ax = plt.subplots(figsize=(8, 5))
tamanho_por_nota.plot(kind='bar', ax=ax, color='steelblue')
ax.set_title('Tamanho mediano dos comentários por nota')
ax.set_xlabel('Nota')
ax.set_ylabel('Caracteres')
ax.tick_params(axis='x', rotation=0)
plt.tight_layout()
plt.show()

#%%
# CONCLUSÃO DO DESAFIO 3
# ---------------------------------------------------------------------
# 1) Notas:
#    - Nota média 4,07 e mediana 5 -> clientes, em geral, satisfeitos
#    - 57,4% deram nota 5; 11,9% deram nota 1
#    - Satisfeitos (4-5): 76,6% | Neutros (3): 8,3% | Insatisfeitos (1-2): 15,1%
#    - Distribuição em "U": concentração nos extremos (5 e 1), pouca nota 2 e 3
#
# 2) Comentários:
#    - Apenas 41,7% das avaliações têm comentário; 11,7% têm título
#    - A maioria dos clientes só dá a nota, sem escrever
#
# 3) Quem comenta mais:
#    - Insatisfeitos comentam MUITO mais: 75,6% contra 34,8% dos satisfeitos
#    - Nota 1: 77% comentam, com textos ~2x maiores que os de nota 5
#    -> O cliente insatisfeito usa o comentário para reclamar/explicar o problema
#
# 4) Tratamento de nulos:
#    - Nulos em título/comentário = cliente não escreveu (não é erro)
#    - Criadas colunas tem_comentario / tem_titulo e textos preenchidos
#    - review_id e order_id com repetições (827 / 559): registrar como ponto
#      de atenção para os merges dos próximos desafios
#
#================MENSAGEM PARA O STORYTELLING================
#"Três em cada quatro clientes da Olist estão satisfeitos, e a nota mais comum é 5.
#  Mas os 15% insatisfeitos são os que mais falam: 3 em cada 4 deixam comentário, 
# com textos duas vezes maiores. Os comentários são, portanto, uma fonte rica para 
# entender os problemas. E o padrão em 'U' das notas mostra que, quando algo dá 
# errado, o cliente vai direto para a nota 1."
# =====================================================================