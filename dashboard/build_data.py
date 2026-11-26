"""Gera os dados agregados do dashboard Olist (mesma lógica dos scripts DESAFIOS/desafio_1..7.py)."""
import json, sys
import numpy as np
import pandas as pd

P = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/uploads/Desafio_final/tabelas'
rd = lambda n: pd.read_csv(f'{P}/{n}.csv')
orders = rd('olist_orders_dataset'); pays = rd('olist_order_payments_dataset')
items = rd('olist_order_items_dataset'); prods = rd('olist_products_dataset')
revs = rd('olist_order_reviews_dataset'); cust = rd('olist_customers_dataset')
sell = rd('olist_sellers_dataset'); geo = rd('olist_geolocation_dataset')
r2 = lambda x, n=2: None if pd.isna(x) else round(float(x), n)
D = {}

for c in ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_customer_date', 'order_estimated_delivery_date']:
    orders[c] = pd.to_datetime(orders[c])

# ---------------- DESAFIO 1: tempo aprovação -> entrega
e = orders[(orders.order_status == 'delivered') & orders.order_approved_at.notna() & orders.order_delivered_customer_date.notna()].copy()
e['dias'] = (e.order_delivered_customer_date - e.order_approved_at).dt.total_seconds() / 86400
neg = int((e.dias < 0).sum()); e = e[e.dias >= 0]
h, edges = np.histogram(e.dias.clip(upper=60), bins=60, range=(0, 60))
D['d1'] = dict(media=r2(e.dias.mean()), mediana=r2(e.dias.median()), p25=r2(e.dias.quantile(.25)), p75=r2(e.dias.quantile(.75)),
               p90=r2(e.dias.quantile(.9)), p95=r2(e.dias.quantile(.95)), maximo=r2(e.dias.max(), 0), validos=len(e), negativos=neg,
               removidos=int(len(orders) - len(e) - neg), mais30=int((e.dias > 30).sum()), mais60=int((e.dias > 60).sum()),
               hist=[int(x) for x in h])
# tempo mediano por ano-mes (entregues)
e['ym'] = e.order_purchase_timestamp.dt.to_period('M').astype(str)

# ---------------- DESAFIO 2: vendas por mês
orders['ym'] = orders.order_purchase_timestamp.dt.to_period('M').astype(str)
ppm = orders.groupby('ym').order_id.count()
pag_ped = pays.groupby('order_id', as_index=False).payment_value.sum()
op = orders.merge(pag_ped, on='order_id', how='left')
pgm = op.groupby('ym').payment_value.sum()
completos = ppm[ppm >= 100].index
D['d2'] = dict(meses=[dict(m=m, pedidos=int(ppm[m]), receita=r2(pgm.get(m, 0), 0), ticket=r2(pgm.get(m, 0) / ppm[m]),
                           completo=bool(m in completos), entrega_med=r2(e[e.ym == m].dias.median(), 1) if (e.ym == m).any() else None) for m in ppm.index])
nov = orders[orders.ym == '2017-11']
pd_dia = nov.groupby(nov.order_purchase_timestamp.dt.day).order_id.count()
D['d2']['nov2017'] = [dict(d=int(k), n=int(v)) for k, v in pd_dia.items()]
pico = int(pd_dia.idxmax()); D['d2']['pico'] = dict(dia=pico, n=int(pd_dia.max()), media_outros=r2(pd_dia.drop(pico).mean(), 0))
pt = pays.groupby('payment_type').agg(n=('order_id', 'count'), valor=('payment_value', 'sum'))
D['d2']['tipos'] = [dict(t=t, n=int(r.n), valor=r2(r.valor, 0)) for t, r in pt.sort_values('n', ascending=False).iterrows()]
cc = pays[pays.payment_type == 'credit_card']
D['d2']['parcelas'] = [dict(p=int(k), n=int(v)) for k, v in cc.payment_installments.clip(upper=10).value_counts().sort_index().items() if k > 0]
D['d2']['outliers'] = {}
for col, df in [('payment_value', pays), ('price', items), ('freight_value', items)]:
    q1, q3 = df[col].quantile([.25, .75]); iqr = q3 - q1; hi = q3 + 1.5 * iqr
    D['d2']['outliers'][col] = dict(q1=r2(q1), mediana=r2(df[col].median()), q3=r2(q3), lim=r2(hi), n=int((df[col] > hi).sum()),
                                    pct=r2((df[col] > hi).mean() * 100, 1), max=r2(df[col].max()))
D['kpi'] = dict(pedidos=int(len(orders)), receita=r2(pays.payment_value.sum(), 0), clientes=int(cust.customer_unique_id.nunique()),
                vendedores=int(len(sell)), produtos=int(len(prods)), itens=int(len(items)),
                ticket=r2(pag_ped.payment_value.mean()), inicio=str(orders.order_purchase_timestamp.min().date()),
                fim=str(orders.order_purchase_timestamp.max().date()))

# ---------------- DESAFIO 3: satisfação
rv = revs.copy()
for c in ['review_comment_title', 'review_comment_message']:
    rv[c] = rv[c].str.strip().replace('', pd.NA)
rv['tem_com'] = rv.review_comment_message.notna(); rv['tem_tit'] = rv.review_comment_title.notna()
rv['tam'] = rv.review_comment_message.str.len()
notas = []
for s in range(1, 6):
    g = rv[rv.review_score == s]
    notas.append(dict(nota=s, n=int(len(g)), pct=r2(len(g) / len(rv) * 100, 1), pct_com=r2(g.tem_com.mean() * 100, 1),
                      tam=r2(g.tam.median(), 0)))
sat = lambda x: 'Insatisfeito' if x <= 2 else ('Neutro' if x == 3 else 'Satisfeito')
rv['sat'] = rv.review_score.apply(sat)
D['d3'] = dict(media=r2(rv.review_score.mean()), mediana=int(rv.review_score.median()), total=int(len(rv)), notas=notas,
               pct_com=r2(rv.tem_com.mean() * 100, 1), pct_tit=r2(rv.tem_tit.mean() * 100, 1),
               grupos={k: dict(pct=r2((rv.sat == k).mean() * 100, 1), pct_com=r2(rv[rv.sat == k].tem_com.mean() * 100, 1))
                       for k in ['Satisfeito', 'Neutro', 'Insatisfeito']},
               dup_review=int(revs.review_id.duplicated().sum()), dup_order=int(revs.order_id.duplicated().sum()))

# ---------------- DESAFIO 4: prazo x nota
e4 = orders[(orders.order_status == 'delivered') & orders.order_delivered_customer_date.notna() & orders.order_estimated_delivery_date.notna()].copy()
e4['dd'] = (e4.order_delivered_customer_date.dt.normalize() - e4.order_estimated_delivery_date.dt.normalize()).dt.days
e4['st'] = np.where(e4.dd < 0, 'Adiantado', np.where(e4.dd == 0, 'No prazo', 'Atrasado'))
revs['review_answer_timestamp'] = pd.to_datetime(revs.review_answer_timestamp)
ru = revs.sort_values('review_answer_timestamp').drop_duplicates('order_id', keep='last')
a = e4.merge(ru[['order_id', 'review_score']], on='order_id')
st = []
for k in ['Adiantado', 'No prazo', 'Atrasado']:
    g = a[a.st == k]
    st.append(dict(s=k, n=int((e4.st == k).sum()), pct=r2((e4.st == k).mean() * 100, 1), nota=r2(g.review_score.mean()),
                   insat=r2((g.review_score <= 2).mean() * 100, 1),
                   dist=[r2((g.review_score == s).mean() * 100, 1) for s in range(1, 6)]))
lim = [-200, -15, -8, -1, 0, 3, 7, 14, 30, 300]
nomes = ['15+ antes', '8–14 antes', '1–7 antes', 'No dia', '1–3 atraso', '4–7 atraso', '8–14 atraso', '15–30 atraso', '30+ atraso']
a['fx'] = pd.cut(a.dd, bins=lim, labels=nomes)
fx = a.groupby('fx', observed=True).review_score.agg(['mean', 'count'])
a['ym'] = a.order_purchase_timestamp.dt.to_period('M').astype(str)
atr_m = e4.assign(ym=e4.order_purchase_timestamp.dt.to_period('M').astype(str)).groupby('ym').apply(lambda g: (g.dd > 0).mean() * 100, include_groups=False)
nota_m = a.groupby('ym').review_score.mean()
D['d4'] = dict(status=st, faixas=[dict(f=str(k), nota=r2(r['mean']), n=int(r['count'])) for k, r in fx.iterrows()],
               corr=r2(a.dd.corr(a.review_score), 3), antecipacao_media=r2(-e4.dd.mean(), 1), antecipacao_mediana=r2(-e4.dd.median(), 0),
               mensal=[dict(m=m, atraso=r2(atr_m.get(m), 1), nota=r2(nota_m.get(m), 2)) for m in ppm.index if m in completos])

# ---------------- DESAFIO 5: categorias
tr = rd('product_category_name_translation')
prods['product_category_name'] = prods.product_category_name.fillna('sem_categoria')
v = items.merge(prods[['product_id', 'product_category_name', 'product_photos_qty']], on='product_id', how='left')
vc = v.groupby('product_category_name').agg(q=('order_id', 'count'), pm=('price', 'mean'), rec=('price', 'sum'),
                                            frete=('freight_value', 'mean')).sort_values('q', ascending=False)
D['d5'] = dict(categorias=[dict(c=k, q=int(r.q), pm=r2(r.pm), rec=r2(r.rec, 0), frete=r2(r.frete)) for k, r in vc.iterrows()],
               n_cat=int(len(vc)), pct_top10=r2(vc.head(10).q.sum() / vc.q.sum() * 100, 1),
               pearson=r2(vc.q.corr(vc.pm), 3), spearman=r2(vc.q.rank().corr(vc.pm.rank()), 3))
v['fp'] = pd.cut(v.price, bins=[0, 50, 100, 200, 500, 7000], labels=['Até R$ 50', 'R$ 50–100', 'R$ 100–200', 'R$ 200–500', 'R$ 500+'])
D['d5']['faixas_preco'] = [dict(f=str(k), pct=r2(x * 100, 1)) for k, x in v.fp.value_counts(normalize=True).sort_index().items()]
vp = v.groupby('product_id').agg(q=('order_id', 'count'), f=('product_photos_qty', 'first')).dropna()
vp['ff'] = pd.cut(vp.f, bins=[0, 1, 2, 4, 20], labels=['1 foto', '2 fotos', '3–4 fotos', '5+ fotos'])
fo = vp.groupby('ff', observed=True).q.agg(['mean', 'median', 'count'])
D['d5']['fotos'] = [dict(f=str(k), media=r2(r['mean']), n=int(r['count'])) for k, r in fo.iterrows()]
D['d5']['fotos_corr'] = dict(pearson=r2(vp.f.corr(vp.q), 3), spearman=r2(vp.f.rank().corr(vp.q.rank()), 3), mediana=r2(vp.f.median(), 0))

# ---------------- DESAFIO 6: frete
med = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']
f = items[['order_id', 'seller_id', 'product_id', 'price', 'freight_value']].merge(prods[['product_id'] + med], on='product_id', how='left')
n0 = len(f); f = f.dropna(subset=med); f = f[f.product_weight_g > 0]
f['volume_cm3'] = f.product_length_cm * f.product_height_cm * f.product_width_cm; f['peso_kg'] = f.product_weight_g / 1000
cols = ['freight_value', 'peso_kg', 'volume_cm3', 'price']
corr = f[cols].corr()
f['fpeso'] = pd.cut(f.peso_kg, bins=[0, .5, 1, 2, 5, 10, 50], labels=['até 0,5 kg', '0,5–1 kg', '1–2 kg', '2–5 kg', '5–10 kg', '10 kg+'])
f['fvol'] = pd.qcut(f.volume_cm3, q=5, labels=['Muito pequeno', 'Pequeno', 'Médio', 'Grande', 'Muito grande'])
gp = f.groupby('fpeso', observed=True).freight_value.agg(['mean', 'median', 'count'])
gv = f.groupby('fvol', observed=True).freight_value.agg(['mean', 'median', 'count'])
D['d6'] = dict(removidas=int(n0 - len(f)), frete_zero=int((f.freight_value == 0).sum()), linhas=int(len(f)),
               corr=dict(cols=['Frete', 'Peso', 'Volume', 'Preço'], m=[[r2(x, 2) for x in row] for row in corr.values]),
               spear=r2(f[cols].rank().corr().loc['freight_value', 'peso_kg'], 3),
               peso=[dict(f=str(k), media=r2(r['mean']), mediana=r2(r['median']), n=int(r['count'])) for k, r in gp.iterrows()],
               volume=[dict(f=str(k), media=r2(r['mean']), mediana=r2(r['median']), n=int(r['count'])) for k, r in gv.iterrows()],
               frete_medio=r2(f.freight_value.mean()))
smp = f.sample(1500, random_state=42)
D['d6']['amostra'] = [[r2(a_, 2), r2(b_, 2)] for a_, b_ in zip(smp.peso_kg, smp.freight_value)]

# ---------------- DESAFIO 7: geografia + modelo
geo = geo[geo.geolocation_lat.between(-34, 5.5) & geo.geolocation_lng.between(-74, -34)]
gc = geo.groupby('geolocation_zip_code_prefix', as_index=False)[['geolocation_lat', 'geolocation_lng']].mean()
ce = cust.groupby('customer_state').customer_unique_id.nunique()
se = sell.seller_state.value_counts()
# pedidos/frete médio/atraso/nota por estado do cliente
oc = orders.merge(cust[['customer_id', 'customer_state']], on='customer_id')
frete_uf = items.merge(oc[['order_id', 'customer_state']], on='order_id').groupby('customer_state').freight_value.mean()
e4c = e4.merge(cust[['customer_id', 'customer_state']], on='customer_id')
atr_uf = e4c.groupby('customer_state').dd.apply(lambda s: (s > 0).mean() * 100)
ent_uf = e.merge(cust[['customer_id', 'customer_state']], on='customer_id').groupby('customer_state').dias.median()
nota_uf = a.merge(cust[['customer_id', 'customer_state']], on='customer_id').groupby('customer_state').review_score.mean()
ufs = sorted(set(ce.index) | set(se.index))
D['d7'] = dict(estados=[dict(uf=u, cli=int(ce.get(u, 0)), pcli=r2(ce.get(u, 0) / ce.sum() * 100, 1), vend=int(se.get(u, 0)),
                             pvend=r2(se.get(u, 0) / se.sum() * 100, 1), frete=r2(frete_uf.get(u)), atraso=r2(atr_uf.get(u), 1),
                             entrega=r2(ent_uf.get(u), 1), nota=r2(nota_uf.get(u))) for u in ufs])
D['d7']['cid_cli'] = [dict(c=k, n=int(x)) for k, x in cust.groupby('customer_city').customer_unique_id.nunique().sort_values(ascending=False).head(10).items()]
D['d7']['cid_vend'] = [dict(c=k, n=int(x)) for k, x in sell.seller_city.value_counts().head(10).items()]
mc = cust.drop_duplicates('customer_unique_id').merge(gc, left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix')
ms = sell.merge(gc, left_on='seller_zip_code_prefix', right_on='geolocation_zip_code_prefix')
mcs = mc.sample(6000, random_state=1)
D['d7']['pts_cli'] = [[r2(x, 2), r2(y, 2)] for x, y in zip(mcs.geolocation_lng, mcs.geolocation_lat)]
D['d7']['pts_vend'] = [[r2(x, 2), r2(y, 2)] for x, y in zip(ms.geolocation_lng, ms.geolocation_lat)]

m = f.merge(orders[['order_id', 'customer_id']], on='order_id').merge(cust[['customer_id', 'customer_zip_code_prefix']], on='customer_id') \
     .merge(sell[['seller_id', 'seller_zip_code_prefix']], on='seller_id')
m = m.merge(gc.rename(columns={'geolocation_lat': 'lc', 'geolocation_lng': 'gcl'}), left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix').drop(columns='geolocation_zip_code_prefix')
m = m.merge(gc.rename(columns={'geolocation_lat': 'lv', 'geolocation_lng': 'gv'}), left_on='seller_zip_code_prefix', right_on='geolocation_zip_code_prefix').drop(columns='geolocation_zip_code_prefix')
def hav(a1, o1, a2, o2):
    a1, o1, a2, o2 = map(np.radians, [a1, o1, a2, o2])
    x = np.sin((a2 - a1) / 2) ** 2 + np.cos(a1) * np.cos(a2) * np.sin((o2 - o1) / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(x))
m['distancia_km'] = hav(m.lc, m.gcl, m.lv, m.gv)
m['fdist'] = pd.cut(m.distancia_km, bins=[-1, 100, 300, 600, 1000, 2000, 5000], labels=['até 100 km', '100–300', '300–600', '600–1000', '1000–2000', '2000+ km'])
gd = m.groupby('fdist', observed=True).freight_value.agg(['mean', 'count'])

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error as MAE, mean_squared_error as MSE, r2_score as R2
var = ['peso_kg', 'volume_cm3', 'price', 'distancia_km']
X, y = m[var], m.freight_value
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, random_state=42)
lin = LinearRegression().fit(Xtr, ytr); pl = lin.predict(Xte)
rf = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1).fit(Xtr, ytr); pr = rf.predict(Xte)
pb = np.full(len(yte), ytr.mean())
lin0 = LinearRegression().fit(Xtr[var[:3]], ytr); p0 = lin0.predict(Xte[var[:3]])
met = lambda p: dict(mae=r2(MAE(yte, p)), rmse=r2(np.sqrt(MSE(yte, p))), r2=r2(R2(yte, p), 3))
cvl = cross_val_score(LinearRegression(), Xtr, ytr, cv=5, scoring='r2')
cvr = cross_val_score(RandomForestRegressor(n_estimators=50, max_depth=12, random_state=42, n_jobs=-1), Xtr, ytr, cv=5, scoring='r2')
rs = np.random.RandomState(7).choice(len(yte), 1200, replace=False)
D['d7']['modelo'] = dict(
    treino=int(len(Xtr)), teste=int(len(Xte)), dist_mediana=r2(m.distancia_km.median(), 0),
    corr_dist=r2(m.freight_value.corr(m.distancia_km), 3),
    modelos=[dict(n='Baseline (média)', **met(pb)), dict(n='Linear sem distância', **met(p0)), dict(n='Regressão Linear', **met(pl)), dict(n='Random Forest', **met(pr))],
    overfit=dict(lin_tr=r2(lin.score(Xtr, ytr), 3), lin_te=r2(R2(yte, pl), 3), rf_tr=r2(rf.score(Xtr, ytr), 3), rf_te=r2(R2(yte, pr), 3)),
    cv=dict(lin=[r2(x, 3) for x in cvl], rf=[r2(x, 3) for x in cvr]),
    importancia=[dict(v=k, i=r2(x, 3)) for k, x in sorted(zip(var, rf.feature_importances_), key=lambda t: -t[1])],
    coef=dict(intercepto=r2(lin.intercept_), **{k: r2(c, 5) for k, c in zip(var, lin.coef_)}),
    real_prev=[[r2(yte.iloc[i], 1), r2(pr[i], 1)] for i in rs],
    resid=[int(x) for x in np.histogram((yte - pr).clip(-40, 40), bins=40, range=(-40, 40))[0]],
    frete_dist=[dict(f=str(k), media=r2(r['mean']), n=int(r['count'])) for k, r in gd.iterrows()])

json.dump(D, open('data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('ok', len(json.dumps(D)))
print(json.dumps({k: D[k] for k in ['kpi']}, ensure_ascii=False))
print(D['d1']['media'], D['d1']['mediana'], D['d3']['media'], [s['nota'] for s in D['d4']['status']], D['d7']['modelo']['modelos'])
