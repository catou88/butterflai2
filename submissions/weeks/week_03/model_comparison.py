"""Fixed-configuration, cycle-grouped Poisson intensity benchmark for Homework 3.

Run from the repository root. Reads the completed notebook's frozen fold data,
reconstructs all event inputs from the raw catalog, and never imports another week.
The supplemental ML intensities are constant on the mandated mesh's Voronoi cells.
Their point-process event likelihood and exposure integral are therefore consistent.
"""
from __future__ import annotations
import os
os.environ.setdefault('OMP_NUM_THREADS','2')
os.environ.setdefault('MPLCONFIGDIR','/tmp/butterflai-ml-mpl')
import argparse, hashlib, json, platform, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import pandas as pd
import scipy
from scipy.optimize import minimize_scalar
from scipy.stats import kstest
import sklearn
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import PoissonRegressor
from threadpoolctl import threadpool_limits

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
RAW=ROOT/'data/composite_sunspot_groups_daily_measurements_10_23.csv'
CACHE=ROOT/'data/derived/week03_ml_comparison'
S=np.linspace(-6.,11.,201); L=np.linspace(0.,60.,241)
SE=np.r_[S[0],(S[1:]+S[:-1])/2,S[-1]]
LE=np.r_[L[0],(L[1:]+L[:-1])/2,L[-1]]
EXPOSURE=np.diff(LE)[:,None]*np.diff(SE)[None,:]
FLOOR=1e-10
SEED=42
CONFIGS={
 'uniform_area':dict(kind='uniform',features='area',alpha=0.0),
 'boost_time_only':dict(kind='boost',features='time',leaves=15,iterations=120),
 'poisson_tree':dict(kind='tree',features='raw',depth=6,leaves=64,min_leaf=1500),
 'boost_raw_15':dict(kind='boost',features='raw',leaves=15,iterations=120),
 'boost_raw_31':dict(kind='boost',features='raw',leaves=31,iterations=160),
 'boost_drift_residual':dict(kind='boost',features='residual',leaves=15,iterations=120),
}
COMMON_BOOST=dict(loss='poisson',learning_rate=.08,min_samples_leaf=1500,
                  l2_regularization=1.0,max_bins=255,early_stopping=False,random_state=SEED)

def clean(x):
 if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [clean(v) for v in x]
 if isinstance(x,np.ndarray):return clean(x.tolist())
 if isinstance(x,np.generic):return clean(x.item())
 if isinstance(x,float) and not np.isfinite(x):return None
 return x

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(clean(x),sort_keys=True).encode()).hexdigest()

def raw_inputs():
 d=pd.read_csv(RAW)
 stamp=pd.to_datetime(dict(year=d.year,month=d.month,day=d.day,
       hour=d.hour.fillna(12).astype(int),minute=d.minute.fillna(0).astype(int),second=d.second.fillna(0).astype(int)))
 frac=(stamp.dt.dayofyear-1+stamp.dt.hour/24+stamp.dt.minute/1440+stamp.dt.second/86400)
 d['t']=stamp.dt.year+frac/np.where(stamp.dt.is_leap_year,366.,365.)
 obs=d[d.uniqueID.notna()].sort_values('t',kind='stable')
 first=obs.drop_duplicates('uniqueID').set_index('uniqueID');groups=obs.groupby('uniqueID')
 e=first[['t','latitude']].copy();e['cycle']=groups.CYCLE.first();e['peak_area']=groups.correctedArea.max()
 e=e[e.cycle.between(12,23)&(e.peak_area>30)].copy();e['cycle']=e.cycle.astype(int)
 e['hemicycle']=e.cycle.astype(str)+np.where(e.latitude>=0,'N','S')
 dev=e[~e.cycle.isin([16,20,22])].copy()
 assert len(e)==22122 and len(dev)==16611
 events={h:(g.latitude.abs().to_numpy(),g.t.to_numpy()) for h,g in dev.groupby('hemicycle')}
 return events

def bins(lat,s):
 lat=np.asarray(lat);s=np.asarray(s)
 if np.any((lat<0)|(lat>60)|(s<-6)|(s>11)):raise ValueError('Events outside fixed observation domain')
 return np.clip(np.searchsorted(LE,lat,side='right')-1,0,len(L)-1),np.clip(np.searchsorted(SE,s,side='right')-1,0,len(S)-1)

def feature_grid(area,mu_b,kind):
 ss=np.broadcast_to(S[None,:],EXPOSURE.shape).ravel()
 ll=np.broadcast_to(L[:,None],EXPOSURE.shape).ravel()
 aa=np.full(len(ss),np.log(area))
 if kind=='raw':return np.column_stack([ss,ll,aa]).astype('float32')
 if kind=='residual':return np.column_stack([ss,ll-15*np.exp(-ss/mu_b),aa]).astype('float32')
 if kind=='time':return np.column_stack([ss,aa]).astype('float32')
 raise ValueError(kind)

def fit_clock(raw,labels,starts):
 # Equivalent profiled least squares: for fixed b each wing's positive exponential
 # coefficient has a closed-form OLS solution. Optimize the shared timescale only.
 def state(logb,origins=False):
  b=np.exp(logb);value=0.;result={}
  for h in labels:
   lat,t=raw[h];z=np.exp(-(t-starts[h])/b);coef=float(z@lat/(z@z))
   value+=float(np.sum((coef*z-lat)**2));result[h]=starts[h]+b*np.log(coef/15.)
  return result if origins else value
 out=minimize_scalar(lambda q:state(q),bounds=(np.log(2.),np.log(30.)),method='bounded',options={'xatol':1e-11})
 if not out.success:raise RuntimeError('Clock optimization failed')
 return float(np.exp(out.x)),state(out.x,True)

def align_held(raw,h,start,b):
 lat,t=raw[h];z=np.exp(-(t-start)/b);coef=float(z@lat/(z@z));return float(start+b*np.log(coef/15.))

def data_for_fold(raw,m,held_cycles,protocol):
 cycles=m['development_cycles'];train=sorted(h for h in raw if int(h[:-1]) not in held_cycles)
 held=sorted(h for h in raw if int(h[:-1]) in held_cycles)
 areas={r['index']:r['A'] for r in m['pooled_count_records']}
 starts={r['index']:r['t0_crossing'] for r in m['origins']}
 if protocol=='LOCO':
  det=m['fold_details'][f'constant:cycle{held_cycles[0]}'];b=float(det['alignment']['mu_b']);origins=det['origins']
  assert set(train)==set(det['training_labels']) and set(held)==set(det['held_labels'])
 else:
  b,origins=fit_clock(raw,train,starts)
  origins.update({h:align_held(raw,h,starts[h],b) for h in held})
 all_events={h:(raw[h][0],raw[h][1]-origins[h]) for h in train+held}
 for h,pair in all_events.items():bins(*pair)
 if protocol=='LOCO':
  for h in held:
   stored=m['heldout_events_on_constant_fold_clock'][h]
   current=np.column_stack(all_events[h]);reference=np.column_stack(stored)
   ix=np.lexsort((current[:,0],current[:,1]));iy=np.lexsort((reference[:,0],reference[:,1]))
   assert np.allclose(current[ix],reference[iy],rtol=0,atol=1e-12), 'Physical event cohort differs'
   # Equal timestamps may order different groups differently; preserve the core order after set verification.
   all_events[h]=(np.asarray(stored[0]),np.asarray(stored[1]))
 return train,held,areas,b,origins,all_events

def score_surface(surface,lat,s,seed):
 surface=np.maximum(np.asarray(surface,float),FLOOR)
 il,ist=bins(lat,s);expected=float(np.sum(surface*EXPOSURE))
 ll=float(np.log(surface[il,ist]).sum()-expected)
 # Exact compensator of the declared piecewise-constant time marginal.
 rate=np.sum(surface*np.diff(LE)[:,None],axis=0);cumulative=np.r_[0.,np.cumsum(rate*np.diff(SE))]
 jitter=np.sort(np.asarray(s)+np.random.default_rng(seed).uniform(0,1/365.25,len(s)))
 if jitter[-1]>11:raise ValueError('Jitter crosses observation boundary')
 idx=np.clip(np.searchsorted(SE,jitter,side='right')-1,0,len(S)-1)
 z=cumulative[idx]+rate[idx]*(jitter-SE[idx]);gaps=np.diff(np.r_[0.,z])
 ks=float(kstest(gaps,'expon').statistic)
 weights=np.sum(surface*np.diff(SE)[None,:],axis=1)*np.diff(LE)
 cell_mean=(LE[:-1]+LE[1:])/2
 cell_second=(LE[:-1]**2+LE[:-1]*LE[1:]+LE[1:]**2)/3
 centroid=float(weights@cell_mean/weights.sum())
 spread=float(np.sqrt(max(0.,float(weights@cell_second/weights.sum())-centroid**2)))
 return dict(n=len(lat),nll_per_year=-ll/17,expected_count=expected,
  count_error_pct=100*(expected-len(lat))/len(lat),KS_descriptive=ks,
  latitude_centroid=centroid,observed_centroid=float(np.mean(lat)),
  latitude_spread=spread,observed_spread=float(np.std(lat,ddof=1)),zero_floor_cells=int((surface<=FLOOR).sum()))

def run_fold(raw,m,held_cycles,protocol,manifest):
 train,held,areas,b,origins,events=data_for_fold(raw,m,held_cycles,protocol)
 fold=','.join(map(str,held_cycles));rows=[];paths=[]
 counts=[]
 for h in train:
  il,it=bins(*events[h]);c=np.zeros(EXPOSURE.shape);np.add.at(c,(il,it),1)
  assert c.sum()==len(events[h][0]);counts.append(c.ravel())
 targets=np.concatenate(counts)/np.tile(EXPOSURE.ravel(),len(train))
 weights=np.tile(EXPOSURE.ravel(),len(train))
 matrices={}
 for name,cfg in CONFIGS.items():
  checkpoint=CACHE/f'{protocol}_{fold}_{name}.json';npz=checkpoint.with_suffix('.npz')
  signature=digest(dict(manifest=manifest,protocol=protocol,held=held_cycles,model=name))
  if checkpoint.exists() and npz.exists():
   try:
    cached=json.loads(checkpoint.read_text())
    if cached.get('signature')==signature:
     rows.extend(cached['rows']);paths.append(str(npz.relative_to(ROOT)));print(protocol,fold,name,'cache',flush=True);continue
   except (OSError,ValueError,KeyError):pass
  begin=time.perf_counter();kind=cfg['features']
  if cfg['kind']=='uniform':
   model=PoissonRegressor(alpha=cfg['alpha'],max_iter=500,tol=1e-10)
   xx=np.log([areas[h] for h in train])[:,None];yy=np.array([len(events[h][0])/1020 for h in train])
   model.fit(xx,yy,sample_weight=np.full(len(train),1020.))
  else:
   if kind not in matrices:matrices[kind]=np.concatenate([feature_grid(areas[h],b,kind) for h in train])
   if cfg['kind']=='tree':
    model=DecisionTreeRegressor(criterion='poisson',max_depth=cfg['depth'],max_leaf_nodes=cfg['leaves'],
         min_samples_leaf=cfg['min_leaf'],random_state=SEED)
   else:model=HistGradientBoostingRegressor(max_leaf_nodes=cfg['leaves'],max_iter=cfg['iterations'],**COMMON_BOOST)
   model.fit(matrices[kind],targets,sample_weight=weights)
  fit_seconds=time.perf_counter()-begin;surfaces={};current=[]
  for h in held:
   if kind=='area':surface=np.full(EXPOSURE.shape,float(model.predict([[np.log(areas[h])]])[0]))
   else:surface=model.predict(feature_grid(areas[h],b,kind)).reshape(EXPOSURE.shape)
   result=score_surface(surface,*events[h],SEED+5000+int(h[:-1])*2+(h[-1]=='S'))
   result.update(model=name,protocol=protocol,fold=fold,hemicycle=h,cycle=int(h[:-1]),
       training_cycles=sorted(set(int(x[:-1]) for x in train)),train_events=sum(len(events[x][0]) for x in train),
       origin=origins[h],training_mu_b=b,area=areas[h],fit_seconds=fit_seconds,
       feature_names=kind,iterations=int(getattr(model,'n_iter_',0)))
   if hasattr(model,'feature_importances_'):result['tree_impurity_importance']=model.feature_importances_.tolist()
   if cfg['kind']=='uniform':result['area_coefficient']=float(model.coef_[0])
   surfaces[h]=np.maximum(surface,FLOOR).astype('float64');current.append(result)
  np.savez_compressed(npz,**surfaces)
  temp=checkpoint.with_suffix('.json.tmp');temp.write_text(json.dumps(clean(dict(signature=signature,rows=current)),indent=2));temp.replace(checkpoint)
  rows.extend(current);paths.append(str(npz.relative_to(ROOT)));print(protocol,fold,name,'fit',round(fit_seconds,2),'seconds',flush=True)
 return rows,paths

def summarize(frame,baseline=None):
 result=[]
 for name,g in frame.groupby('model'):
  row=dict(model=name,mean_NLL=float(g.nll_per_year.mean()),median_NLL=float(g.nll_per_year.median()),
     between_wing_SD=float(g.nll_per_year.std(ddof=1)),count_MAPE=float(g.count_error_pct.abs().mean()),
     count_RMSE=float(np.sqrt(np.mean((g.expected_count-g.n)**2))),median_KS=float(g.KS_descriptive.median()),
     centroid_RMSE_deg=float(np.sqrt(np.mean((g.latitude_centroid-g.observed_centroid)**2))))
  if baseline is not None:
   diff=g.set_index('hemicycle').nll_per_year-baseline
   cycle=diff.groupby([int(h[:-1]) for h in diff.index]).mean()
   row.update(mean_gain_vs_constant_belt=float(-diff.mean()),median_gain_vs_constant_belt=float(-diff.median()),
     paired_SE_9_cycles=float(cycle.std(ddof=1)/np.sqrt(len(cycle))),better_wings=int((diff<0).sum()),better_cycles=int((cycle<0).sum()))
  result.append(row)
 return sorted(result,key=lambda r:r['mean_NLL'])

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=2);args=parser.parse_args()
 CACHE.mkdir(parents=True,exist_ok=True);m=json.loads((HERE/'metrics.json').read_text());raw=raw_inputs()
 manifest=dict(version=1,created_UTC=pd.Timestamp.now(tz='UTC').isoformat(),script_sha256=sha(__file__),
   core_metrics_sha256=sha(HERE/'metrics.json'),catalog_sha256=sha(RAW),configs=CONFIGS,common_boost=COMMON_BOOST,
   sklearn=sklearn.__version__,numpy=np.__version__,scipy=scipy.__version__,python=platform.python_version(),
   mesh=[201,241],window=[-6,11],latitude=[0,60],intensity_floor=FLOOR,
   selection='Fixed settings frozen before supplemental ML scores; exploratory model comparison, no tuning on test folds',
   intensity='Piecewise constant on fixed mesh Voronoi cells; event assignment and integral exact for that intensity')
 # Timestamp is deliberately excluded from checkpoint identity.
 stable={k:v for k,v in manifest.items() if k!='created_UTC'}
 (HERE/'comparison_config.json').write_text(json.dumps(clean(manifest),indent=2)+'\n')
 start=time.perf_counter();rows=[];surfaces=[]
 jobs=[('LOCO',[c]) for c in m['development_cycles']]
 jobs += [('3fold',[12,15,19]),('3fold',[13,17,21]),('3fold',[14,18,23])]
 with threadpool_limits(limits=2):
  with ThreadPoolExecutor(max_workers=args.workers) as pool:
   futures=[pool.submit(run_fold,raw,m,held,protocol,stable) for protocol,held in jobs]
   for future in as_completed(futures):
    records,paths=future.result();rows.extend(records);surfaces.extend(paths)
 frame=pd.DataFrame(rows).sort_values(['protocol','model','cycle','hemicycle'])
 assert len(frame)==6*18*2 and not frame.cycle.isin([16,20,22]).any()
 assert all(r.cycle not in r.training_cycles for r in frame.itertuples())
 baseline=pd.Series({r['hemicycle']:r['nll/yr (area record)'] for r in m['loco']})
 tables={p:summarize(frame[frame.protocol==p],baseline if p=='LOCO' else None) for p in ['LOCO','3fold']}
 belt=[]
 for kind,name in [('constant','constant w'),('amplitude','w(a_hc)'),('latitude','w = w0 + w1 mu')]:
  records=[]
  for key,detail in m['fold_details'].items():
   if key.startswith(kind+':'):
    for r in detail['rows']:
     records.append(dict(model=name,hemicycle=r['hemicycle'],cycle=r['cycle'],n=r['n'],
      nll_per_year=r['nll/yr (area record)'],expected_count=r['predicted (area record)'],
      count_error_pct=100*(r['predicted (area record)']-r['n'])/r['n'],
      KS_descriptive=r['KS time (area record)'],latitude_centroid=np.nan,observed_centroid=np.nan))
  belt.extend(summarize(pd.DataFrame(records),baseline))
 all_loco=sorted(tables['LOCO']+belt,key=lambda r:r['mean_NLL'])
 result=dict(manifest=manifest,elapsed_seconds=time.perf_counter()-start,protocols=tables,
    all_model_LOCO=all_loco,rows=frame.to_dict(orient='records'),surfaces=sorted(set(surfaces)),
    best_mean_model=all_loco[0]['model'],scope='Development-set model comparison. Conditional held-out clocks and retrospective area; sealed cycles untouched. Best among tested settings, not a certified global winner.',
    secondary_protocol='Three prespecified grouped splits train on six cycles/test three; not directly comparable to eight-cycle-training LOCO. No belt models refit under secondary splits.')
 (HERE/'comparison_metrics.json').write_text(json.dumps(clean(result),indent=2,allow_nan=False)+'\n')
 frame.to_csv(HERE/'comparison_scores.csv',index=False)
 print(json.dumps(clean(dict(all_model_LOCO=all_loco,secondary=tables['3fold'],elapsed_seconds=result['elapsed_seconds'])),indent=2))

if __name__=='__main__':main()
