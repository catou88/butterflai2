"""Render the retained, conditional cycle-validation results; no fitting."""
from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/butterflai-ml-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
m=json.loads((HERE/'comparison_metrics.json').read_text());core=json.loads((HERE/'metrics.json').read_text())
rows=m['all_model_LOCO'];plt.rcParams.update({'figure.dpi':130,'axes.grid':True,'grid.alpha':.2,'font.size':9})
fig,axes=plt.subplots(1,2,figsize=(13,5.5))
labels=[r['model'] for r in rows];y=np.arange(len(rows));colors=['#27658c' if 'boost_' in r['model'] else '#555555' for r in rows]
axes[0].scatter([r['mean_NLL'] for r in rows],y,c=colors);axes[0].set_yticks(y,labels);axes[0].invert_yaxis();axes[0].set_xlabel('Mean conditional held-out NLL [nats / hemicycle-year]');axes[0].set_title('All nine models: lower is better')
close=[r for r in rows if r['mean_NLL']<0 and r['model']!='poisson_tree'];yy=np.arange(len(close))
axes[1].errorbar([r['mean_gain_vs_constant_belt'] for r in close],yy,xerr=[r['paired_SE_9_cycles'] for r in close],fmt='o',color='#27658c',capsize=3)
axes[1].axvline(0,color='black',lw=.8);axes[1].set_yticks(yy,[r['model'] for r in close]);axes[1].invert_yaxis();axes[1].set_xlabel('Paired likelihood gain [nats / hemicycle-year]');axes[1].set_title('Against constant-width belt: mean ± cycle-level SE')
fig.suptitle('Nine development-cycle folds; both hemispheres reserved together')
fig.text(.02,.01,'Source: retained comparison_metrics.json. Cycles 12–23 excluding sealed 16/20/22. Test-derived clocks and full-cycle area are supplied; not a future-cycle forecast.',fontsize=8)
fig.tight_layout(rect=[0,.045,1,.96]);fig.savefig(HERE/'comparison_scores.png');plt.close(fig)

fig,ax=plt.subplots(figsize=(6.5,5))
for name,color in [('boost_raw_15','#27658c'),('boost_drift_residual','#99753b')]:
 r=[r for r in m['rows'] if r['protocol']=='LOCO' and r['model']==name];ax.scatter([x['n'] for x in r],[x['expected_count'] for x in r],label=name,c=color,s=28,alpha=.75)
r=[r for key,d in core['fold_details'].items() if key.startswith('amplitude:') for r in d['rows']]
ax.scatter([x['n'] for x in r],[x['predicted (area record)'] for x in r],label='amplitude-width belt',marker='x',c='#555555',s=35)
ax.plot([400,1700],[400,1700],color='black',lw=.8);ax.set_xlabel('Observed groups in reserved wing');ax.set_ylabel('Predicted total groups');ax.set_title('Count prediction is a separate diagnostic');ax.legend(fontsize=8)
fig.text(.02,.01,'Conditional nine-fold results; area covariate from each reserved wing is supplied. Source: retained metrics.',fontsize=8)
fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(HERE/'comparison_counts.png');plt.close(fig)

S=np.linspace(-6,11,201);L=np.linspace(0,60,241);SE=np.r_[S[0],(S[1:]+S[:-1])/2,S[-1]];LE=np.r_[L[0],(L[1:]+L[:-1])/2,L[-1]]
h='19N';lat,s=map(np.asarray,core['heldout_events_on_constant_fold_clock'][h]);surfaces=[]
for name in ['boost_raw_15','boost_drift_residual']:
 p=ROOT/f'data/derived/week03_ml_comparison/LOCO_19_{name}.npz';surfaces.append((name,np.load(p)[h]))
d=core['fold_details']['amplitude:cycle19'];p=d['fit']['shared'];a=next(r['a (area record)'] for r in d['rows'] if r['hemicycle']==h)
x=S+6;peak=(p['k']-1)*p['theta'];g=np.zeros_like(x);live=x>0;g[live]=(x[live]/peak)**(p['k']-1)*np.exp(-(x[live]-peak)/p['theta'])
mu=p['mu_a']*np.exp(-S/p['mu_b']);w=p['width_params'][0]*(a/d['reference'])**p['width_params'][1]
B=a*g[None,:]*np.exp(-.5*((L[:,None]-mu)/w)**2);surfaces.append(('amplitude-width belt',p['c']*np.logaddexp(0,B-1)))
fig,axes=plt.subplots(1,3,figsize=(14,4.2),sharex=True,sharey=True);vmax=max(z.max() for _,z in surfaces)
for ax,(name,z) in zip(axes,surfaces):
 im=ax.pcolormesh(SE,LE,z,shading='flat',vmin=0,vmax=vmax,cmap='magma');ax.scatter(s,lat,s=2,c='white',alpha=.25,linewidths=0);ax.set_title(name);ax.set_xlabel('Shifted time s [years]');ax.set_ylim(0,50)
axes[0].set_ylabel('Absolute latitude [degrees]')
cax=fig.add_axes([.91,.18,.014,.62]);fig.colorbar(im,cax=cax,label='Expected groups / degree / year')
fig.suptitle('Cycle 19 north reserved from training: predicted intensities and observed appearances')
fig.text(.02,.01,'Source: retained fold surfaces. All three use the same reserved events and clock. Own-wing alignment and retrospective area supplied; no direct magnetic measurements.',fontsize=8)
fig.subplots_adjust(top=.83,bottom=.16,left=.06,right=.88,wspace=.12);fig.savefig(HERE/'comparison_intensities.png');plt.close(fig)
print('Rendered comparison_scores.png, comparison_counts.png, comparison_intensities.png')
