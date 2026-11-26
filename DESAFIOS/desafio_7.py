#%%
# PASSO 1 -> carregar os dados
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

caminho = r'C:\Users\sherv\OneDrive\Desktop\ESTUDO\HARVE\Desafio_final\tabelas'

df_geo = pd.read_csv(caminho + r'\olist_geolocation_dataset.csv')
df_customers = pd.read_csv(caminho + r'\olist_customers_dataset.csv')
df_sellers = pd.read_csv(caminho + r'\olist_sellers_dataset.csv')
df_orders = pd.read_csv(caminho + r'\olist_orders_dataset.csv')
df_items = pd.read_csv(caminho + r'\olist_order_items_dataset.csv')
df_products = pd.read_csv(caminho + r'\olist_products_dataset.csv')

print('Geolocalização:', len(df_geo), 'linhas |', df_geo['geolocation_zip_code_prefix'].nunique(), 'CEPs distintos')
print('Clientes:      ', df_customers['customer_unique_id'].nunique(), 'clientes únicos')
print('Vendedores:    ', len(df_sellers))

#%%
# PASSO 2 -> tratar a tabela de geolocalização

# 1) manter só coordenadas dentro dos limites do Brasil
dentro_brasil = (df_geo['geolocation_lat'].between(-34, 5.5) &
                df_geo['geolocation_lng'].between(-74, -34))
print('Coordenadas fora do Brasil:', (~dentro_brasil).sum())
df_geo = df_geo[dentro_brasil]

# 2) 1 ponto por CEP (média das coordenadas)
df_geo_cep = df_geo.groupby('geolocation_zip_code_prefix', as_index=False)[
    ['geolocation_lat', 'geolocation_lng']].mean()

print('Linhas depois do agrupamento:', len(df_geo_cep))
df_geo_cep.head()

#%%
# PASSO 3 -> clientes e vendedores por estado
clientes_estado = df_customers.groupby('customer_state')['customer_unique_id'].nunique().sort_values(ascending=False)
vendedores_estado = df_sellers['seller_state'].value_counts()

pct_clientes = (clientes_estado / clientes_estado.sum() * 100).round(1)
pct_vendedores = (vendedores_estado / vendedores_estado.sum() * 100).round(1)

print('% de CLIENTES por estado (top 6):')
print(pct_clientes.head(6))
print('\n% de VENDEDORES por estado (top 6):')
print(pct_vendedores.head(6))

fig, ax = plt.subplots(1, 2, figsize=(14, 5))
pct_clientes.head(10).plot(kind='bar', ax=ax[0], color='steelblue')
ax[0].set_title('Clientes por estado (top 10)')
ax[0].set_ylabel('% dos clientes')
ax[0].set_xlabel('')
ax[0].tick_params(axis='x', rotation=0)

pct_vendedores.head(10).plot(kind='bar', ax=ax[1], color='darkorange')
ax[1].set_title('Vendedores por estado (top 10)')
ax[1].set_ylabel('% dos vendedores')
ax[1].set_xlabel('')
ax[1].tick_params(axis='x', rotation=0)

plt.tight_layout()
plt.show()

#%%
# PASSO 4 -> clientes e vendedores por cidade
print('Top 10 cidades - CLIENTES:')
print(df_customers.groupby('customer_city')['customer_unique_id'].nunique().sort_values(ascending=False).head(10))

print('\nTop 10 cidades - VENDEDORES:')
print(df_sellers['seller_city'].value_counts().head(10))

#%%
# PASSO 5 -> mapa de clientes e vendedores
mapa_clientes = df_customers.merge(df_geo_cep, left_on='customer_zip_code_prefix',
                                right_on='geolocation_zip_code_prefix', how='inner')
mapa_vendedores = df_sellers.merge(df_geo_cep, left_on='seller_zip_code_prefix',
                                right_on='geolocation_zip_code_prefix', how='inner')

fig, ax = plt.subplots(1, 2, figsize=(14, 7))

ax[0].scatter(mapa_clientes['geolocation_lng'], mapa_clientes['geolocation_lat'],
            s=1, alpha=0.2, color='steelblue')
ax[0].set_title(f'Clientes ({len(mapa_clientes)})')

ax[1].scatter(mapa_vendedores['geolocation_lng'], mapa_vendedores['geolocation_lat'],
            s=3, alpha=0.5, color='darkorange')
ax[1].set_title(f'Vendedores ({len(mapa_vendedores)})')

for eixo in ax:
    eixo.set_xlabel('Longitude')
    eixo.set_ylabel('Latitude')
    eixo.set_xlim(-75, -33)
    eixo.set_ylim(-35, 6)

plt.tight_layout()
plt.show()

#%%
# PASSO 6 -> montar a base do modelo
colunas_medidas = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']

df_modelo = df_items[['order_id', 'seller_id', 'price', 'freight_value', 'product_id']].merge(
    df_products[['product_id'] + colunas_medidas], on='product_id', how='left')

# tratamentos do Desafio 6
df_modelo = df_modelo.dropna(subset=colunas_medidas)
df_modelo = df_modelo[df_modelo['product_weight_g'] > 0]
df_modelo['volume_cm3'] = (df_modelo['product_length_cm'] *
                           df_modelo['product_height_cm'] *
                            df_modelo['product_width_cm'])
df_modelo['peso_kg'] = df_modelo['product_weight_g'] / 1000

# ligar pedido -> cliente -> CEP do cliente
df_modelo = df_modelo.merge(df_orders[['order_id', 'customer_id']], on='order_id', how='left')
df_modelo = df_modelo.merge(df_customers[['customer_id', 'customer_zip_code_prefix']], on='customer_id', how='left')

# ligar vendedor -> CEP do vendedor
df_modelo = df_modelo.merge(df_sellers[['seller_id', 'seller_zip_code_prefix']], on='seller_id', how='left')

print('Linhas:', len(df_modelo))
df_modelo.head()

#%%
# PASSO 7 -> feature engineering: distância cliente-vendedor

# coordenadas do cliente
df_modelo = df_modelo.merge(
    df_geo_cep.rename(columns={'geolocation_lat': 'lat_cliente', 'geolocation_lng': 'lng_cliente'}),
    left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix', how='left'
).drop(columns='geolocation_zip_code_prefix')

# coordenadas do vendedor
df_modelo = df_modelo.merge(
    df_geo_cep.rename(columns={'geolocation_lat': 'lat_vendedor', 'geolocation_lng': 'lng_vendedor'}),
    left_on='seller_zip_code_prefix', right_on='geolocation_zip_code_prefix', how='left'
).drop(columns='geolocation_zip_code_prefix')

# remover quem ficou sem coordenada (CEP não encontrado)
print('Sem coordenadas:', df_modelo[['lat_cliente', 'lat_vendedor']].isna().any(axis=1).sum())
df_modelo = df_modelo.dropna(subset=['lat_cliente', 'lat_vendedor'])

# fórmula de Haversine
def distancia_haversine(lat1, lng1, lat2, lng2):
    raio_terra_km = 6371
    lat1, lng1, lat2, lng2 = map(np.radians, [lat1, lng1, lat2, lng2])
    a = (np.sin((lat2 - lat1) / 2) ** 2 +
         np.cos(lat1) * np.cos(lat2) * np.sin((lng2 - lng1) / 2) ** 2)
    return 2 * raio_terra_km * np.arcsin(np.sqrt(a))

df_modelo['distancia_km'] = distancia_haversine(df_modelo['lat_cliente'], df_modelo['lng_cliente'],
                                                df_modelo['lat_vendedor'], df_modelo['lng_vendedor'])

print('Linhas finais:', len(df_modelo))
print(df_modelo['distancia_km'].describe().round(1))
print('\nCorrelação com o frete:')
print(df_modelo[['freight_value', 'peso_kg', 'volume_cm3', 'price', 'distancia_km']].corr()['freight_value'].round(3))

#%%
# PASSO 8 -> separar treino e teste
from sklearn.model_selection import train_test_split

variaveis = ['peso_kg', 'volume_cm3', 'price', 'distancia_km']

X = df_modelo[variaveis]
y = df_modelo['freight_value']

X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=0.2, random_state=42)

print(f'Treino: {len(X_treino)} linhas')
print(f'Teste:  {len(X_teste)} linhas')

#%%
# PASSO 9 -> modelo 1: regressão linear
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

modelo_linear = LinearRegression()
modelo_linear.fit(X_treino, y_treino)          # treinar

previsao_linear = modelo_linear.predict(X_teste)  # prever no teste

mae_linear = mean_absolute_error(y_teste, previsao_linear)
rmse_linear = np.sqrt(mean_squared_error(y_teste, previsao_linear))
r2_linear = r2_score(y_teste, previsao_linear)

print('REGRESSÃO LINEAR')
print(f'MAE:  R$ {mae_linear:.2f}')
print(f'RMSE: R$ {rmse_linear:.2f}')
print(f'R²:   {r2_linear:.3f}')

# coeficientes: quanto o frete muda para cada +1 unidade da variável
coeficientes = pd.Series(modelo_linear.coef_, index=variaveis)
print(f'\nIntercepto: R$ {modelo_linear.intercept_:.2f}')
print(coeficientes.round(5))

#%%
# PASSO 10 -> modelo 2: random forest
from sklearn.ensemble import RandomForestRegressor

modelo_rf = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
modelo_rf.fit(X_treino, y_treino)

previsao_rf = modelo_rf.predict(X_teste)

mae_rf = mean_absolute_error(y_teste, previsao_rf)
rmse_rf = np.sqrt(mean_squared_error(y_teste, previsao_rf))
r2_rf = r2_score(y_teste, previsao_rf)

print('RANDOM FOREST')
print(f'MAE:  R$ {mae_rf:.2f}')
print(f'RMSE: R$ {rmse_rf:.2f}')
print(f'R²:   {r2_rf:.3f}')

# importância de cada variável
importancia = pd.Series(modelo_rf.feature_importances_, index=variaveis).sort_values()
fig, ax = plt.subplots(figsize=(8, 4))
importancia.plot(kind='barh', ax=ax, color='seagreen')
ax.set_title('Importância das variáveis - Random Forest')
plt.tight_layout()
plt.show()

#%%
# PASSO 11 -> testes de validação
from sklearn.model_selection import cross_val_score

# 1) BASELINE: "chutar" sempre o frete médio do treino
previsao_baseline = np.full(len(y_teste), y_treino.mean())
mae_baseline = mean_absolute_error(y_teste, previsao_baseline)

comparacao = pd.DataFrame({
    'MAE (R$)': [mae_baseline, mae_linear, mae_rf],
    'RMSE (R$)': [np.sqrt(mean_squared_error(y_teste, previsao_baseline)), rmse_linear, rmse_rf],
    'R²': [r2_score(y_teste, previsao_baseline), r2_linear, r2_rf]
}, index=['Baseline (média)', 'Regressão Linear', 'Random Forest']).round(3)
print('1) COMPARAÇÃO DOS MODELOS (dados de TESTE):')
print(comparacao)

# 2) OVERFITTING: R² no treino x R² no teste
print('\n2) OVERFITTING (R² treino x teste):')
print(f'Linear:        treino {modelo_linear.score(X_treino, y_treino):.3f} | teste {r2_linear:.3f}')
print(f'Random Forest: treino {modelo_rf.score(X_treino, y_treino):.3f} | teste {r2_rf:.3f}')

# 3) VALIDAÇÃO CRUZADA (5 divisões) - só no treino
cv_linear = cross_val_score(LinearRegression(), X_treino, y_treino, cv=5, scoring='r2')
print('\n3) VALIDAÇÃO CRUZADA - Regressão Linear (R² em 5 divisões):')
print(cv_linear.round(3), f'-> média {cv_linear.mean():.3f} ± {cv_linear.std():.3f}')

cv_rf = cross_val_score(RandomForestRegressor(n_estimators=50, max_depth=12, random_state=42, n_jobs=-1),
                        X_treino, y_treino, cv=5, scoring='r2')
print('VALIDAÇÃO CRUZADA - Random Forest (R² em 5 divisões):')
print(cv_rf.round(3), f'-> média {cv_rf.mean():.3f} ± {cv_rf.std():.3f}')

# 4) GRÁFICOS: real x previsto e resíduos (melhor modelo)
residuos = y_teste - previsao_rf

fig, ax = plt.subplots(1, 2, figsize=(14, 5))

ax[0].scatter(y_teste, previsao_rf, alpha=0.2, s=5, color='steelblue')
ax[0].plot([0, 150], [0, 150], color='red', linestyle='--', label='Previsão perfeita')
ax[0].set_xlim(0, 150)
ax[0].set_ylim(0, 150)
ax[0].set_title('Random Forest: frete real x previsto')
ax[0].set_xlabel('Frete real (R$)')
ax[0].set_ylabel('Frete previsto (R$)')
ax[0].legend()

ax[1].hist(residuos, bins=100, range=(-50, 50), color='steelblue', edgecolor='white')
ax[1].axvline(0, color='red', linestyle='--')
ax[1].set_title('Distribuição dos erros (resíduos)')
ax[1].set_xlabel('Erro = real - previsto (R$)')
ax[1].set_ylabel('Quantidade')

plt.tight_layout()
plt.show()

#%%
# PASSO 12 -> CONCLUSÃO DO DESAFIO 7
# ---------------------------------------------------------------------
# PARTE A - GEOGRAFIA
# 1) Clientes concentrados no Sudeste:
#    SP 41,9% | RJ 12,9% | MG 11,7% -> 66,5% dos clientes em 3 estados
#    Cidades: São Paulo (~15 mil), Rio de Janeiro (~6,9 mil), Belo Horizonte
#
# 2) Vendedores AINDA MAIS concentrados:
#    SP 59,7% | PR 11,3% | MG 7,9% | SC 6,1%
#    -> 6 em cada 10 vendedores estão em SP
#
# 3) O mapa mostra concentração no litoral Sul/Sudeste e poucos pontos
#    no Norte/Centro-Oeste -> clientes distantes pagam frete maior
#
# PARTE B - MODELO DE REGRESSÃO (prever o frete)
# 4) Nova feature: distancia_km (Haversine) -> distância mediana ~430 km
#
# 5) Resultados no TESTE (89.655 linhas de treino | 22.414 de teste):
#    - Baseline (média):  MAE R$ 8,60 | RMSE R$ 15,39 | R² 0,00
#    - Regressão Linear:  MAE R$ 5,33 | RMSE R$  9,93 | R² 0,58
#    - Random Forest:     MAE R$ 4,06 | RMSE R$  8,16 | R² 0,72
#
# 6) Validação:
#    - Ambos os modelos superam o baseline (Random Forest erra ~53% menos)
#    - Linear: R² treino 0,59 x teste 0,58 -> sem overfitting
#    - Random Forest: R² treino 0,84 x teste 0,72 -> leve overfitting,
#      mas o desempenho no teste continua bem acima da regressão linear
#    - Validação cruzada (5 divisões) estável:
#      Linear 0,588 ± 0,008 | Random Forest 0,714 ± 0,014
#
# 7) Sem a distância, a regressão linear tinha R² de apenas 0,43 (MAE R$ 6,77)
#    -> incluir a distância melhorou bastante o modelo (R² 0,43 -> 0,58)
#
# MODELO ESCOLHIDO: Random Forest (menor MAE e maior R² no teste)
# =====================================================================