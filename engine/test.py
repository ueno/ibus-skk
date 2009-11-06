# -*- coding: utf-8 -*-

import unittest
import skk

class TestSKK(unittest.TestCase):
    def setUp(self):
        self.__skk = skk.Context()

    def testromkana(self):
        self.__skk.reset()
        # ka -> か
        self.assertEqual(self.__skk.append(u'k'), u'')
        self.assertEqual(self.__skk.preedit(), u'k')
        self.assertEqual(self.__skk.append(u'a'), u'か')
        self.assertEqual(self.__skk.preedit(), u'')
        # myo -> みょ
        self.assertEqual(self.__skk.append(u'm'), u'')
        self.assertEqual(self.__skk.preedit(), u'm')
        self.assertEqual(self.__skk.append(u'y'), u'')
        self.assertEqual(self.__skk.preedit(), u'my')
        self.assertEqual(self.__skk.append(u'o'), u'みょ')
        self.assertEqual(self.__skk.preedit(), u'')
        # toggle submode to katakana
        self.assertEqual(self.__skk.append(u'q'), u'')
        # ka -> カ
        self.assertEqual(self.__skk.append(u'k'), u'')
        self.assertEqual(self.__skk.preedit(), u'k')
        self.assertEqual(self.__skk.append(u'a'), u'カ')
        self.assertEqual(self.__skk.preedit(), u'')

    def testokurinasi(self):
        self.__skk.reset()
        self.__skk.append(u'shift+a')
        self.assertEqual(self.__skk.preedit(), u'▽あ')
        self.__skk.append(u'i')
        self.assertEqual(self.__skk.preedit(), u'▽あい')
        self.__skk.append(u' ')
        self.assertEqual(self.__skk.preedit(), u'▼愛')
        self.__skk.append(u' ')
        self.assertEqual(self.__skk.preedit(), u'▼相')

    def testokuriari(self):
        self.__skk.reset()
        self.__skk.append(u'shift+k')
        self.__skk.append(u'a')
        self.__skk.append(u'n')
        self.__skk.append(u'g')
        self.__skk.append(u'a')
        self.__skk.append(u'shift+e')
        self.assertEqual(self.__skk.preedit(), u'▼考え')
        self.assertEqual(self.__skk.append(u'r'), u'考え')
        self.assertEqual(self.__skk.preedit(), u'r')
        self.assertEqual(self.__skk.append(u'u'), u'る')

        self.__skk.reset()
        self.__skk.append(u'shift+a')
        self.__skk.append(u'i')
        self.__skk.append(u'shift+s')
        self.assertEqual(self.__skk.preedit(), u'▽あい*s')
        self.__skk.append(u'u')
        self.assertEqual(self.__skk.preedit(), u'▼愛す')

        self.__skk.reset()
        self.__skk.append(u'shift+t')
        self.__skk.append(u'u')
        self.__skk.append(u'k')
        self.__skk.append(u'a')
        self.__skk.append(u'shift+t')
        self.__skk.append(u't')
        self.assertEqual(self.__skk.preedit(), u'▽つか*っt')

if __name__ == '__main__':
    unittest.main()
