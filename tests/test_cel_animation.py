import importlib.util,json,tempfile,unittest
from pathlib import Path
from PIL import Image
spec=importlib.util.spec_from_file_location('cel_animation',Path(__file__).parents[1]/'studio/cel_animation.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class CelTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)
  Image.new('RGBA',(8,8),(230,210,170,255)).save(self.p/'bg.png')
  Image.new('RGBA',(2,2),(255,0,0,255)).save(self.p/'a.png')
  Image.new('RGBA',(2,2),(0,0,255,255)).save(self.p/'b.png')
  self.data={'schema':1,'size':[8,8],'fps':24,'frames':6,'cels':{'bg':'bg.png','a':'a.png','b':'b.png'},'layers':[{'id':'background','exposures':[{'start':0,'stop':6,'cel':'bg'}]},{'id':'drawing','position':[2,3],'exposures':[{'start':0,'stop':2,'cel':'a'},{'start':2,'stop':4,'cel':'b'}]}]}
 def tearDown(self):self.tmp.cleanup()
 def scene(self):
  p=self.p/'sheet.json';p.write_text(json.dumps(self.data));return m.CelScene(p)
 def test_holds_actual_layer_pixels_and_blank_exposures(self):
  s=self.scene();self.assertEqual(s.frame(0).tobytes(),s.frame(1).tobytes());self.assertEqual(s.frame(2).getpixel((2,3)),(0,0,255,255));self.assertEqual(s.frame(4).getpixel((2,3)),(230,210,170,255));self.assertEqual(s.frame(0).getpixel((0,0)),(230,210,170,255))
 def test_overlap_rejected(self):
  self.data['layers'][1]['exposures'][1]['start']=1
  with self.assertRaisesRegex(AssertionError,'Overlapping'):self.scene()
 def test_missing_drawing_rejected(self):
  self.data['layers'][1]['exposures'][0]['cel']='missing'
  with self.assertRaisesRegex(AssertionError,'Unknown'):self.scene()
 def test_counts_distinct_cels_not_output_frames(self):
  s=self.scene();r=s.report();self.assertEqual(r['uniqueCelsUsed'],3);self.assertEqual(r['frames'],6);self.assertEqual(r['seconds'],.25)
 def test_out_of_range_rejected(self):
  self.data['layers'][1]['exposures'][1]['stop']=7
  with self.assertRaisesRegex(AssertionError,'outside'):self.scene()
if __name__=='__main__':unittest.main()
