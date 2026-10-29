#!/usr/bin/env python3
"""BriefBridge: evidence-linked meeting action validation and handoff export."""
import argparse, json, html, hashlib, re
from pathlib import Path

def validate(notes, proposal):
    lines=notes.splitlines()
    if not notes.strip(): raise ValueError('Notes must not be empty.')
    if not isinstance(proposal,dict) or not isinstance(proposal.get('actions'),list): raise ValueError('Proposal needs an actions list.')
    if len(proposal['actions'])>100: raise ValueError('Maximum 100 actions.')
    actions=[];issues=[];seen=set()
    for i,a in enumerate(proposal['actions'],1):
        if not isinstance(a,dict): issues.append(f'Action {i}: not an object; rejected.');continue
        task=a.get('task'); evidence=a.get('evidence'); line=a.get('line')
        if not isinstance(task,str) or not task.strip() or len(task)>500: issues.append(f'Action {i}: missing or oversized task; rejected.');continue
        if type(line) is not int or line<1 or line>len(lines) or not isinstance(evidence,str) or not evidence.strip() or evidence not in lines[line-1]:
            issues.append(f'Action {i}: evidence does not match the cited source line; rejected.');continue
        key=(line,task.strip().casefold())
        if key in seen:issues.append(f'Action {i}: duplicate task and source line; rejected.');continue
        seen.add(key)
        row=dict(task=task.strip(),line=line,evidence=evidence,owner=None,due=None,review=[])
        for field in ['owner','due']:
            value=a.get(field)
            if value is None or value=='': row['review'].append(f'{field} unresolved');continue
            if not isinstance(value,str) or not value.strip() or value not in evidence:
                row['review'].append(f'{field} not supported verbatim by evidence; cleared');continue
            row[field]=value
        row['review'].append('Human check required: task meaning, commitment and context are not proven by a text match.')
        actions.append(row)
    return dict(project='BriefBridge',notes_sha256=hashlib.sha256(notes.encode()).hexdigest(),input_actions=len(proposal['actions']),accepted=len(actions),rejected=len(proposal['actions'])-len(actions),actions=actions,issues=issues,source_lines=lines,limitations=['Text matching checks provenance, not semantic truth.','Relative dates remain as written. No inferred calendar deadlines.','No messages sent, invitations created or commitments made.'])

def render(r):
    e=lambda x:html.escape(str(x),quote=True)
    cards=''.join('<article><span class="tag">SOURCE LINE '+str(a['line'])+'</span><h3>'+e(a['task'])+'</h3><div class="meta"><b>Owner</b> '+e(a['owner'] or 'Unresolved')+' <b>When</b> '+e(a['due'] or 'Unresolved')+'</div><blockquote>'+e(a['evidence'])+'</blockquote><details><summary>Review notes</summary><ul>'+''.join('<li>'+e(x)+'</li>' for x in a['review'])+'</ul></details></article>' for a in r['actions'])
    source=''.join('<div><b>'+str(i)+'</b> '+e(x)+'</div>' for i,x in enumerate(r['source_lines'],1))
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BriefBridge handoff</title><style>body{margin:0;background:#edf1f3;color:#182a36;font:16px/1.6 system-ui}main{max-width:1050px;margin:auto;padding:32px 24px}h1{font:44px/1.1 Georgia;margin:10px 0}h2{font:30px Georgia}h3{font-size:21px;margin:8px 0}.tag{font-size:12px;letter-spacing:1px;color:#427063}article{background:white;border:1px solid #d9e3e5;border-radius:12px;padding:24px;margin:20px 0}blockquote{margin:20px 0;background:#eff5f3;padding:18px;border-left:4px solid #427063}.stats{display:flex;gap:36px;margin:30px 0}.stats strong{display:block;font-size:35px;color:#427063}.notice{background:#fff4d8;padding:18px;border-radius:8px}.meta b{margin-right:6px}.meta b:not(:first-child){margin-left:20px}.source{background:white;padding:22px;overflow-wrap:anywhere}.source b{display:inline-block;min-width:30px;color:#427063}summary{cursor:pointer}li{margin-bottom:8px}@media(max-width:600px){main{padding:24px 16px}h1{font-size:36px}article{padding:18px}.stats{gap:24px}}</style><main><span class="tag">BRIEFBRIDGE / PRIVATE PROTOTYPE</span><h1>From notes to a checkable handoff.</h1><p class="notice">Draft actions for human review. Evidence links do not prove a commitment. Nothing has been sent or scheduled.</p><div class="stats"><div><strong>'''+str(r['accepted'])+'''</strong>Evidence-linked actions</div><div><strong>'''+str(r['rejected'])+'''</strong>Rejected proposals</div></div>'''+cards+'''<h2>Validation issues</h2><ul>'''+(''.join('<li>'+e(x)+'</li>' for x in r['issues']) or '<li>No structural rejections.</li>')+'''</ul><h2>Source notes</h2><div class="source">'''+source+'''</div><h2>Limits</h2><ul>'''+''.join('<li>'+e(x)+'</li>' for x in r['limitations'])+'''</ul></main></html>'''

def export(notes,proposal,out):
    r=validate(notes,proposal);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'handoff.json').write_text(json.dumps(r,indent=2))
    (out/'report.html').write_text(render(r))
    (out/'review.md').write_text('# BriefBridge review draft\n\n'+ '\n'.join(f"- {a['task']} | Owner: {a['owner'] or 'Unresolved'} | When: {a['due'] or 'Unresolved'} | Source line {a['line']}" for a in r['actions'])+'\n\nNo messages or calendar events created.\n')
    return r
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('notes',type=Path);p.add_argument('proposal',type=Path);p.add_argument('--out',default='output');a=p.parse_args();r=export(a.notes.read_text(),json.loads(a.proposal.read_text()),a.out);print(f"Saved handoff pack: {r['accepted']} evidence-linked actions, {r['rejected']} rejected. Human review required.")
