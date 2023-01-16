# -*- coding: utf-8 -*- 

import unittest
import texture as txt

class CliParseTest(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		# Make sure we're not overwriting TestCase's init
		super(CliParseTest, self).__init__(*args, **kwargs)

		# Some sample command line arguments. Individual methods can be tested with other combinations
		# Keys with defaults and helpstrings
		self.keys = { \
				'que':		['q default',	'q', 	'True or false', True], \
				'doublew':	['w default',	'w', 	'Value of pi'], \
				'ee':		['e default', 	'e'], \
				'ar':		[None,	'r', 	True], \
				}
		self.keys_clean = { \
				'que':		['q default',	'q', 	True,	'True or false'], \
				'doublew':	['w default',	'w', 	False, 	'Value of pi'], \
				'ee':		['e default', 	'e',	False,	''], \
				'ar':		[None,	'r', 	True,	''], \
				}
		self.argv = ['script_name', '-que', 'True', '--doublew', '3.14', '-ee', '42', '---ar', 'Qwerty']
		# The above should be parsed to the following
		self.cfg_raw = {'que': 'True', 'doublew': '3.14', 'ee':'42', 'ar':'Qwerty'}
		# which should be cleaned up to the following
		self.cfg_clean = {'que': True, 'doublew': 3.14, 'ee':42, 'ar':'Qwerty'}
	
	def test_parse(self):
		cfg = txt.config.cliparse.CliParse(argv=self.argv) \
				.parse()

		self.assertDictEqual(cfg, self.cfg_clean)

	def test_clean_keys(self):
		cfg = txt.config.cliparse.CliParse()
		clean_keys = cfg.clean_keys(self.keys)
		self.assertDictEqual(clean_keys, self.keys_clean)

	def test_load_defaults(self):
		cfg = txt.config.cliparse.CliParse()
		defaults = cfg.load_defaults(self.keys)
		self.assertDictEqual(defaults, {'ee': 'e default', 'que': 'q default', 'doublew': 'w default'})

	def test_parse_config(self):
		cfg = txt.config.cliparse.CliParse()
		config = cfg.parse_config('data/test_config.ini')
		self.assertDictEqual(config, {'que': 'Q Config', 'doublew': '3.14'})
		
	def test_parse_argv(self):
		cfg = txt.config.cliparse.CliParse()
		args = cfg.parse_argv(self.argv, self.keys_clean)
		self.assertDictEqual(args,self.cfg_raw)

	def test_get_summary(self):
		cfg = txt.config.cliparse.CliParse()
		summary = cfg.get_summary(self.cfg_clean)
		self.assertRegex(summary, "que: True\n")
		self.assertRegex(summary, "ar: Qwerty\n")
		self.assertRegex(summary, "ee: 42\n")
		self.assertRegex(summary, "doublew: 3.14\n")

	def test_clean_config(self):
		cfg = txt.config.cliparse.CliParse()
		self.assertEqual(cfg.clean_config(self.cfg_raw), self.cfg_clean)

if __name__ == '__main__':
	unittest.main()
