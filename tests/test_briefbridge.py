import unittest,sys,json,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from briefbridge import validate,render,export
class Tests(unittest.TestCase):
 def base(self,**kw):
  a={'task':'Draft copy','line':1,'evidence':'Mira: draft copy by Friday','owner':'Mira','due':'Friday'};a.update(kw);return validate('Mira: draft copy by Friday',{'actions':[a]})
 def test_valid(self):self.assertEqual(self.base()['accepted'],1)
 def test_owner(self):self.assertIsNone(self.base(owner='Omar')['actions'][0]['owner'])
 def test_due(self):self.assertIsNone(self.base(due='2026-10-30')['actions'][0]['due'])
 def test_relative(self):self.assertEqual(self.base()['actions'][0]['due'],'Friday')
 def test_evidence(self):self.assertEqual(self.base(evidence='invented')['rejected'],1)
 def test_line(self):self.assertEqual(self.base(line=2)['rejected'],1)
 def test_bool_line(self):self.assertEqual(self.base(line=True)['rejected'],1)
 def test_empty_task(self):self.assertEqual(self.base(task='')['rejected'],1)
 def test_duplicate(self):
  a={'task':'x','line':1,'evidence':'x'};self.assertEqual(validate('x',{'actions':[a,a]})['rejected'],1)
 def test_empty_notes(self):
  with self.assertRaises(ValueError):validate('',{'actions':[]})
 def test_escape(self):self.assertNotIn('<script>',render(validate('<script>',{'actions':[{'task':'<script>','line':1,'evidence':'<script>'}]})))
 def test_demo(self):
  p=Path(__file__).resolve().parents[1]/'samples';r=validate((p/'notes.txt').read_text(),json.loads((p/'proposal.json').read_text()));self.assertEqual((r['accepted'],r['rejected']),(4,1))
 def test_export(self):
  with tempfile.TemporaryDirectory() as d:
   export('x',{'actions':[]},d);self.assertTrue((Path(d)/'report.html').exists())
if __name__=='__main__':unittest.main()
