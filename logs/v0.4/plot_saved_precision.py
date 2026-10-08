from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
R=Path.cwd();rows=json.loads((R/'experiments/v0.4/analysis/principal_precision_all25.json').read_text(encoding='utf8'))['results'];ids=sorted({x['engine'] for x in rows});x=np.arange(len(ids))
fig,ax=plt.subplots(figsize=(11,4.8),layout='constrained');fig.set_layout_engine('constrained',rect=(0,.055,1,.945))
for j,(p,label,color) in enumerate([(0.05,'5% quantile','#285b98'),(0.5,'Median','#3b8767'),(0.95,'95% quantile','#b07024')]):
 values=[max(b['approximate_upper_quantile_rul_mcse'] for b in next(q for q in rows if q['engine']==eid and q['probability']==p)['batch_size_results']) for eid in ids]
 ax.bar(x+(j-1)*.25,values,.24,label=label,color=color)
ax.axhline(.5,color='#ac3842',linestyle='--',linewidth=1.6,label='Frozen 0.5-cycle criterion')
ax.set_xticks(x,ids);ax.set_ylim(0,.56);ax.set_ylabel('Approximate upper Monte Carlo SE (cycles)');ax.set_xlabel('Original training calibration engine ID');ax.set_title('All 25 development engines pass the numerical precision criterion',loc='left',fontsize=13,pad=12)
ax.grid(axis='y',alpha=.16);ax.set_axisbelow(True);ax.spines[['top','right']].set_visible(False);ax.legend(loc='upper left',ncols=2,frameon=False,fontsize=9)
idx=ids.index(86);ax.annotate('Maximum: 0.221',xy=(idx+.25,.2205130205556579),xytext=(idx-6,.31),arrowprops={'arrowstyle':'->','color':'#555'},fontsize=10)
fig.text(.012,.006,'Each bar takes the larger guard at batch size 250/500. Approximate diagnostic, not an absolute-error bound. Official endpoints untested.',fontsize=8,color='#555')
p=R/'figures/v0.4';p.mkdir(exist_ok=True);fig.savefig(p/'predictive_precision_all25.png',dpi=210);fig.savefig(p/'predictive_precision_all25.pdf');plt.close(fig)
doc=R/'docs/v0.4/02_numerical_precision_remediation.md';s=doc.read_text(encoding='utf8');s+='\n## Numerical guard across all calibration engines\n\n![Approximate upper Monte Carlo standard error for all75 quantiles; all below the frozen0.5cycle criterion.](../../figures/v0.4/predictive_precision_all25.png)\n\nThe plotted value is the larger approximate upper MCSE at batch250/500 for each quantile. This figure uses the saved precision arrays, adds no sampling and certifies no future endpoint. [Vector PDF](../../figures/v0.4/predictive_precision_all25.pdf).\n';
if '## Numerical guard across all calibration engines' not in doc.read_text(encoding='utf8'):doc.write_text(s,encoding='utf8')
print('Figure created from retained data; no new scientific sampling.')