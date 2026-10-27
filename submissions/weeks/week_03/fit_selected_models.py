"""Refit the two statistically unresolved boosting finalists on all development wings.

Artifacts are regenerated under ignored data/derived; this produces no new test score.
Both models require a standardized clock and full-cycle area, so are conditional tools.
"""
from pathlib import Path
import json,time
import joblib
import numpy as np
from threadpoolctl import threadpool_limits
import model_comparison as b


def main():
 core=json.loads((b.HERE/'metrics.json').read_text());comparison=json.loads((b.HERE/'comparison_metrics.json').read_text())
 if comparison['manifest']['script_sha256']!=b.sha(b.HERE/'model_comparison.py'):
  raise RuntimeError('Comparison source changed: regenerate benchmark before selecting a model')
 raw=b.raw_inputs();labels=sorted(raw);areas={r['index']:r['A'] for r in core['pooled_count_records']}
 origins={r['index']:r['t0_fitted'] for r in core['origins']};mu_b=core['alignment']['mu_b']
 weights=np.tile(b.EXPOSURE.ravel(),len(labels));counts=[]
 for h in labels:
  lat,t=raw[h];il,it=b.bins(lat,t-origins[h]);z=np.zeros(b.EXPOSURE.shape);np.add.at(z,(il,it),1);counts.append(z.ravel())
 target=np.concatenate(counts)/weights;result=[]
 with threadpool_limits(limits=2):
  for name in ['boost_raw_15','boost_drift_residual']:
   cfg=b.CONFIGS[name];X=np.concatenate([b.feature_grid(areas[h],mu_b,cfg['features']) for h in labels])
   model=b.HistGradientBoostingRegressor(max_leaf_nodes=cfg['leaves'],max_iter=cfg['iterations'],**b.COMMON_BOOST)
   begin=time.perf_counter();model.fit(X,target,sample_weight=weights);elapsed=time.perf_counter()-begin
   output=b.CACHE/f'final_{name}.joblib'
   artifact=dict(model=model,features=cfg['features'],training_mu_b=mu_b,time_nodes=b.S,latitude_nodes=b.L,
       time_edges=b.SE,latitude_edges=b.LE,intensity_floor=b.FLOOR,
       scope='Conditional intensity; standardized clock and retrospective cycle area required')
   joblib.dump(artifact,output)
   result.append(dict(model=name,artifact=str(output.relative_to(b.ROOT)),artifact_sha256=b.sha(output),
       fit_seconds=elapsed,train_events=16611,train_cycles=core['development_cycles'],
       features=cfg['features'],heldout_score_added=False))
 manifest=dict(status='COMPLETE',models=result,core_metrics_sha256=b.sha(b.HERE/'metrics.json'),
  comparison_metrics_sha256=b.sha(b.HERE/'comparison_metrics.json'),source_sha256=b.sha(__file__),
  choice='Raw15 is LOCO point winner; residual is within paired SE and wins secondary3fold. Retain both as finalists.',
  scope='Full-development refits only; no new validation claim, sealed cycles excluded, no magnetic-strength measurement.')
 (b.HERE/'selected_models.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(manifest,indent=2))

if __name__=='__main__':main()
