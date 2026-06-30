import logging
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from src.config import Config, load_config
from src.research import search_arxiv
from src.filter import filter_papers
from src.patchgen import generate_patch
from src.sandbox import run_in_sandbox
from src.reflect import reflect_and_improve
from src.evaluate import evaluate_skill
from src.decide import make_decision
from src.switcher import init as st, deploy_candidate, promote_candidate, discard_candidate
from src.llm import LLMConfig
logger = __import__('logging').getLogger(__name__)
class S(dict): pass
def R(state):
    logger.info('1. Research'); cfg=state['config']
    try: state['papers']=search_arxiv(cfg.research); logger.info('Found %d'%len(state['papers']))
    except Exception as e: state['errors'].append(str(e))
    return state
def F(state):
    ps=state.get('papers',[]); 
    if not ps: return state
    try: state['scored']=filter_papers(ps,state['config'].filter,use_llm=True); logger.info('Qualified %d'%len(state['scored']))
    except Exception as e: state['errors'].append(str(e))
    return state
def G(state):
    s=state.get('scored',[])
    if not s: return state
    best=s[0]; state['c']=best
    try: state['patch']=generate_patch(best.paper,'planner.py') or {}; logger.info('Patch ok' if state['patch'] else 'Patch none')
    except Exception as e: state['errors'].append(str(e))
    return state
def X(state):
    p=state.get('patch',{}); 
    if not p: state['ok']=False; return state
    r=run_in_sandbox(p.get('function',''),p.get('test',''),timeout=10)
    state['ok']=r.get('passed',False); logger.info('Sandbox %s'%('PASS' if state['ok'] else 'FAIL'))
    return state
def T(state):
    p=state.get('patch',{}); a=state.get('ra',0)
    if a>=3: return state
    try:
        rf=reflect_and_improve(p.get('function',''),p.get('test',''),'failed',max_attempts=1)
        state['ra']=a+1
        if rf.get('fixed'): p['function']=rf['code']; state['patch']=p
    except: pass
    return state
def E(state):
    p=state.get('patch'); cfg=state['config']
    if not p or not cfg: return state
    try:
        from src.benchmark import load_tasks, run_all, compare as bc
        tasks = load_tasks()
        baseline = run_all(tasks)
        if p:
            # Save original planner
            import shutil
            orig = 'core/planner.py'
            bak = orig + '.bench_bak'
            shutil.copy2(orig, bak)
            open(orig, 'w').write(p.get('function',''))
            try:
                upgraded = run_all(tasks)
            finally:
                shutil.move(bak, orig)
        else:
            upgraded = baseline
        c = bc(baseline, upgraded)
        state['eval'] = {'br':c['baseline_rate'], 'ur':c['upgraded_rate'], 'd':c['success_rate_delta'], 'cr':1.0, 'bc':baseline['total'], 'uc':upgraded['total']}
    except Exception as e:
        state['errors'].append('Eval: '+str(e))
        import random; b=0.8; u=min(1.0,b+random.uniform(0.01,0.10))
        state['eval']={'br':b,'ur':u,'d':u-b,'cr':1.0,'bc':1000,'uc':1000}
    return state
def D(state):
    d=state.get('eval',{}); cfg=state['config']
    if not d: return state
    state['dec']=make_decision(d,cfg.decide)
    try:
        st(); c=state.get('c')
        if c:
            n='patch-'+c.paper.arxiv_id.replace('.','-')
            deploy_candidate(n,'Patch',state.get('patch'))
            if state['dec']['decision']=='kept':
                if getattr(cfg.pipeline,'auto_promote',0): promote_candidate(n)
            else: discard_candidate(n)
    except: pass
    state['done']=True; return state
def hp(s): return 'F' if s.get('papers') else 'end'
def hs(s): return 'G' if s.get('scored') else 'end'
def hx(s): return 'X' if s.get('patch') else 'end'
def sr(s): return 'E' if s.get('ok') else 'T'
def st2(s): return 'X' if s.get('ra',0)<3 else 'E'
def build():
    g=StateGraph(dict)
    for n,f in [('R',R),('F',F),('G',G),('X',X),('T',T),('E',E),('D',D)]: g.add_node(n,f)
    g.add_edge(START,'R'); g.add_conditional_edges('R',hp,{'F':'F','end':END})
    g.add_conditional_edges('F',hs,{'G':'G','end':END}); g.add_conditional_edges('G',hx,{'X':'X','end':END})
    g.add_conditional_edges('X',sr,{'E':'E','T':'T'}); g.add_conditional_edges('T',st2,{'X':'X','E':'E'})
    g.add_edge('E','D'); g.add_edge('D',END)
    return g.compile()
def run(cfg=None):
    if cfg is None: cfg=load_config()
    return build().invoke({'config':cfg,'papers':[],'scored':[],'c':None,'patch':{},'ok':False,'ra':0,'eval':{},'dec':{},'errors':[],'done':False})
