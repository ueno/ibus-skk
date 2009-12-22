# -*- coding: utf-8 -*-

import unittest
import os, os.path
import skk

class TestSKK(unittest.TestCase):
    def setUp(self):
        # Make sure to start with new empty usrdict.
        usrdict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    ".skk-ibus-jisyo")
        try:
            os.unlink(usrdict_path)
        except:
            pass

        sysdict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "SKK-JISYO.S")
        if not os.path.exists(sysdict_path):
            raise RuntimeError('SKK-JISYO.S not found; do "wget http://openlab.ring.gr.jp/skk/skk/dic/SKK-JISYO.S"')

        self.__skk = skk.Context(usrdict=skk.UsrDict(usrdict_path),
                                 sysdict=skk.SysDict(sysdict_path))

    def testromkana(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        # ka -> か
        self.assertEqual(self.__skk.press_key(u'k'), u'')
        self.assertEqual(self.__skk.preedit, u'k')
        self.assertEqual(self.__skk.press_key(u'a'), u'か')
        self.assertEqual(self.__skk.preedit, u'')
        # myo -> みょ
        self.assertEqual(self.__skk.press_key(u'm'), u'')
        self.assertEqual(self.__skk.preedit, u'm')
        self.assertEqual(self.__skk.press_key(u'y'), u'')
        self.assertEqual(self.__skk.preedit, u'my')
        self.assertEqual(self.__skk.press_key(u'o'), u'みょ')
        self.assertEqual(self.__skk.preedit, u'')
        # toggle submode to katakana
        self.assertEqual(self.__skk.press_key(u'q'), u'')
        # ka -> カ
        self.assertEqual(self.__skk.press_key(u'k'), u'')
        self.assertEqual(self.__skk.preedit, u'k')
        self.assertEqual(self.__skk.press_key(u'a'), u'カ')
        self.assertEqual(self.__skk.preedit, u'')
        # nX -> ンX
        self.__skk.press_key(u'n')
        self.assertEqual(self.__skk.press_key(u'.'), u'ン。')

    def testhiraganakatakana(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+a')
        self.__skk.press_key(u'i')
        self.assertEqual(self.__skk.press_key(u'q'), u'アイ')
        self.assertEqual(self.__skk.preedit, u'')
        self.__skk.press_key(u'shift+a')
        self.__skk.press_key(u'i')
        self.assertEqual(self.__skk.press_key(u'q'), u'あい')
        self.assertEqual(self.__skk.preedit, u'')
        
    def testokurinasi(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+a')
        self.assertEqual(self.__skk.preedit, u'▽あ')
        self.__skk.press_key(u'i')
        self.assertEqual(self.__skk.preedit, u'▽あい')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'▼愛')
        self.__skk.press_key(u' ')
        self.assertEqual(self.__skk.preedit, u'▼哀')

    def testokuriari(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'n')
        self.__skk.press_key(u'g')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'shift+e')
        self.assertEqual(self.__skk.preedit, u'▼考え')
        self.assertEqual(self.__skk.press_key(u'r'), u'考え')
        self.assertEqual(self.__skk.preedit, u'r')
        self.assertEqual(self.__skk.press_key(u'u'), u'る')

        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+h')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'shift+z')
        self.assertEqual(self.__skk.preedit, u'▽は*z')
        self.__skk.press_key(u'u')
        self.assertEqual(self.__skk.preedit, u'▼恥ず')

        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+t')
        self.__skk.press_key(u'u')
        self.__skk.press_key(u'k')
        self.__skk.press_key(u'a')
        self.__skk.press_key(u'shift+t')
        self.__skk.press_key(u't')
        self.assertEqual(self.__skk.preedit, u'▽つか*っt')

    def testcompletion(self):
        self.__skk.reset()
        self.__skk.activate_input_mode(skk.INPUT_MODE_HIRAGANA)
        self.__skk.press_key(u'shift+a')
        self.assertEqual(self.__skk.preedit, u'▽あ')
        self.__skk.press_key(u'\t')
        self.assertEqual(self.__skk.preedit, u'▽あ')
        self.__skk.press_key(u'\t')
        self.assertEqual(self.__skk.preedit, u'▽あい')
        self.__skk.press_key(u'\t')
        self.assertEqual(self.__skk.preedit, u'▽あいさつ')
        self.__skk.press_key(u' ')
        self.__skk.kakutei()
        self.__skk.press_key(u'shift+a')
        self.assertEqual(self.__skk.preedit, u'▽あ')
        self.__skk.press_key(u'\t')
        self.assertEqual(self.__skk.preedit, u'▽あいさつ')
        
if __name__ == '__main__':
    unittest.main()
