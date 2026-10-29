#!/usr/bin/env python3
"""Local BriefBridge review UI; no model, messaging or account integrations."""
import json
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
from briefbridge import validate,render
ROOT=Path(__file__).parent
PAGE='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BriefBridge</title><style>body{background:#edf1f3;color:#182a36;font:17px/1.6 system-ui;margin:0}main{max-width:900px;margin:40px auto;padding:36px;background:white;border-radius:14px}h1{font:46px Georgia;margin:10px 0}h2{font:27px Georgia}textarea{width:100%;box-sizing:border-box;padding:15px;border:1px solid #bdcdd2;border-radius:6px;font:14px/1.5 monospace;min-height:170px}button{background:#276453;border:0;border-radius:6px;color:white;padding:13px 20px;font-size:16px;cursor:pointer;margin:10px 10px 10px 0}.notice{background:#fff4d8;padding:16px}small{color:#427063}#error{color:#b32222}@media(max-width:600px){main{margin:0;padding:24px 16px}h1{font-size:38px}}</style><main><small>PRIVATE WORKING PROTOTYPE / NO MESSAGES SENT</small><h1>BriefBridge</h1><p>Turn meeting notes into an evidence-linked action handoff. Keep uncertain owners and deadlines visible.</p><p class="notice">The Agent37 workflow proposes actions from notes. This local review step checks source quotes and exports a draft report. Text matching cannot prove semantic truth or a commitment.</p><button id="demo">Load synthetic example</button><form id="form"><h2>1. Source notes</h2><textarea id="notes" aria-label="Source notes" required></textarea><h2>2. Agent action proposal</h2><p>Paste the JSON proposal produced by the Agent37 workflow. Each action needs task, line, evidence, owner and due. Missing owner/due stays unresolved.</p><textarea id="proposal" aria-label="Action proposal JSON" required></textarea><button>Validate and review handoff</button><p id="error" role="alert"></p></form><p>Localhost only. No real meeting data is included. No email, calendar or messaging action occurs.</p></main><script>document.querySelector('#demo').onclick=async()=>{let r=await fetch('/sample');let x=await r.json();document.querySelector('#notes').value=x.notes;document.querySelector('#proposal').value=JSON.stringify(x.proposal,null,2)};document.querySelector('#form').onsubmit=async e=>{e.preventDefault();let error=document.querySelector('#error');try{let r=await fetch('/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({notes:document.querySelector('#notes').value,proposal:JSON.parse(document.querySelector('#proposal').value)})});let t=await r.text();if(!r.ok)throw Error(t);document.open();document.write(t);document.close()}catch(x){error.textContent=x.message}};</script></html>'''
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def send(self,body,status=200,kind='text/html; charset=utf-8'):
  b=body.encode();self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(b)));self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(b)
 def do_GET(self):
  if self.path=='/':self.send(PAGE)
  elif self.path=='/sample':self.send(json.dumps({'notes':(ROOT/'samples/notes.txt').read_text(),'proposal':json.loads((ROOT/'samples/proposal.json').read_text())}),kind='application/json')
  else:self.send('Not found',404,'text/plain')
 def do_POST(self):
  if self.path!='/review':return self.send('Not found',404,'text/plain')
  try:
   n=int(self.headers.get('Content-Length','0'))
   if not 0<n<=100000:raise ValueError('Request must be between 1 and 100,000 bytes.')
   x=json.loads(self.rfile.read(n));notes=x.get('notes')
   if not isinstance(notes,str):raise ValueError('Notes must be text.')
   self.send(render(validate(notes,x.get('proposal'))))
  except (ValueError,TypeError,AttributeError) as e:self.send(str(e),400,'text/plain')
if __name__=='__main__':
 print('BriefBridge: http://127.0.0.1:8766 (localhost only)')
 HTTPServer(('127.0.0.1',8766),Handler).serve_forever()
