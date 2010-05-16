# vim:set et sts=4 sw=4:
# -*- coding: utf-8 -*-
#
# ibus-skk - The SKK engine for IBus
#
# Copyright (C) 2009-2010 Daiki Ueno <ueno@unixuser.org>
#   changed: 2010-04-13 tagomoris <tagomoris@intellilink.co.jp>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

from __future__ import with_statement
import itertools
import os.path
import socket
import re
import unicodedata
from kzik import KZIK_RULE
import struct

# Converted from skk-rom-kana-base-rule in skk-vars.el.
ROM_KANA_RULE = {
    u'a': (None, (u'ア', u'あ')),
    u'bb': (u'b', (u'ッ', u'っ')),
    u'ba': (None, (u'バ', u'ば')),
    u'be': (None, (u'ベ', u'べ')),
    u'bi': (None, (u'ビ', u'び')),
    u'bo': (None, (u'ボ', u'ぼ')),
    u'bu': (None, (u'ブ', u'ぶ')),
    u'bya': (None, (u'ビャ', u'びゃ')),
    u'bye': (None, (u'ビェ', u'びぇ')),
    u'byi': (None, (u'ビィ', u'びぃ')),
    u'byo': (None, (u'ビョ', u'びょ')),
    u'byu': (None, (u'ビュ', u'びゅ')),
    u'cc': (u'c', (u'ッ', u'っ')),
    u'cha': (None, (u'チャ', u'ちゃ')),
    u'che': (None, (u'チェ', u'ちぇ')),
    u'chi': (None, (u'チ', u'ち')),
    u'cho': (None, (u'チョ', u'ちょ')),
    u'chu': (None, (u'チュ', u'ちゅ')),
    u'cya': (None, (u'チャ', u'ちゃ')),
    u'cye': (None, (u'チェ', u'ちぇ')),
    u'cyi': (None, (u'チィ', u'ちぃ')),
    u'cyo': (None, (u'チョ', u'ちょ')),
    u'cyu': (None, (u'チュ', u'ちゅ')),
    u'dd': (u'd', (u'ッ', u'っ')),
    u'da': (None, (u'ダ', u'だ')),
    u'de': (None, (u'デ', u'で')),
    u'dha': (None, (u'デャ', u'でゃ')),
    u'dhe': (None, (u'デェ', u'でぇ')),
    u'dhi': (None, (u'ディ', u'でぃ')),
    u'dho': (None, (u'デョ', u'でょ')),
    u'dhu': (None, (u'デュ', u'でゅ')),
    u'di': (None, (u'ヂ', u'ぢ')),
    u'do': (None, (u'ド', u'ど')),
    u'du': (None, (u'ヅ', u'づ')),
    u'dya': (None, (u'ヂャ', u'ぢゃ')),
    u'dye': (None, (u'ヂェ', u'ぢぇ')),
    u'dyi': (None, (u'ヂィ', u'ぢぃ')),
    u'dyo': (None, (u'ヂョ', u'ぢょ')),
    u'dyu': (None, (u'ヂュ', u'ぢゅ')),
    u'e': (None, (u'エ', u'え')),
    u'ff': (u'f', (u'ッ', u'っ')),
    u'fa': (None, (u'ファ', u'ふぁ')),
    u'fe': (None, (u'フェ', u'ふぇ')),
    u'fi': (None, (u'フィ', u'ふぃ')),
    u'fo': (None, (u'フォ', u'ふぉ')),
    u'fu': (None, (u'フ', u'ふ')),
    u'fya': (None, (u'フャ', u'ふゃ')),
    u'fye': (None, (u'フェ', u'ふぇ')),
    u'fyi': (None, (u'フィ', u'ふぃ')),
    u'fyo': (None, (u'フョ', u'ふょ')),
    u'fyu': (None, (u'フュ', u'ふゅ')),
    u'gg': (u'g', (u'ッ', u'っ')),
    u'ga': (None, (u'ガ', u'が')),
    u'ge': (None, (u'ゲ', u'げ')),
    u'gi': (None, (u'ギ', u'ぎ')),
    u'go': (None, (u'ゴ', u'ご')),
    u'gu': (None, (u'グ', u'ぐ')),
    u'gya': (None, (u'ギャ', u'ぎゃ')),
    u'gye': (None, (u'ギェ', u'ぎぇ')),
    u'gyi': (None, (u'ギィ', u'ぎぃ')),
    u'gyo': (None, (u'ギョ', u'ぎょ')),
    u'gyu': (None, (u'ギュ', u'ぎゅ')),
    # u'h': (u'', (u'オ', u'お')),
    u'ha': (None, (u'ハ', u'は')),
    u'he': (None, (u'ヘ', u'へ')),
    u'hi': (None, (u'ヒ', u'ひ')),
    u'ho': (None, (u'ホ', u'ほ')),
    u'hu': (None, (u'フ', u'ふ')),
    u'hya': (None, (u'ヒャ', u'ひゃ')),
    u'hye': (None, (u'ヒェ', u'ひぇ')),
    u'hyi': (None, (u'ヒィ', u'ひぃ')),
    u'hyo': (None, (u'ヒョ', u'ひょ')),
    u'hyu': (None, (u'ヒュ', u'ひゅ')),
    u'i': (None, (u'イ', u'い')),
    u'jj': (u'j', (u'ッ', u'っ')),
    u'ja': (None, (u'ジャ', u'じゃ')),
    u'je': (None, (u'ジェ', u'じぇ')),
    u'ji': (None, (u'ジ', u'じ')),
    u'jo': (None, (u'ジョ', u'じょ')),
    u'ju': (None, (u'ジュ', u'じゅ')),
    u'jya': (None, (u'ジャ', u'じゃ')),
    u'jye': (None, (u'ジェ', u'じぇ')),
    u'jyi': (None, (u'ジィ', u'じぃ')),
    u'jyo': (None, (u'ジョ', u'じょ')),
    u'jyu': (None, (u'ジュ', u'じゅ')),
    u'kk': (u'k', (u'ッ', u'っ')),
    u'ka': (None, (u'カ', u'か')),
    u'ke': (None, (u'ケ', u'け')),
    u'ki': (None, (u'キ', u'き')),
    u'ko': (None, (u'コ', u'こ')),
    u'ku': (None, (u'ク', u'く')),
    u'kya': (None, (u'キャ', u'きゃ')),
    u'kye': (None, (u'キェ', u'きぇ')),
    u'kyi': (None, (u'キィ', u'きぃ')),
    u'kyo': (None, (u'キョ', u'きょ')),
    u'kyu': (None, (u'キュ', u'きゅ')),
    u'ma': (None, (u'マ', u'ま')),
    u'me': (None, (u'メ', u'め')),
    u'mi': (None, (u'ミ', u'み')),
    u'mo': (None, (u'モ', u'も')),
    u'mu': (None, (u'ム', u'む')),
    u'mya': (None, (u'ミャ', u'みゃ')),
    u'mye': (None, (u'ミェ', u'みぇ')),
    u'myi': (None, (u'ミィ', u'みぃ')),
    u'myo': (None, (u'ミョ', u'みょ')),
    u'myu': (None, (u'ミュ', u'みゅ')),
    # u'n': (None, (u'ン', u'ん')),
    u'n\'': (None, (u'ン', u'ん')),
    u'na': (None, (u'ナ', u'な')),
    u'ne': (None, (u'ネ', u'ね')),
    u'ni': (None, (u'ニ', u'に')),
    u'nn': (None, (u'ン', u'ん')),
    u'no': (None, (u'ノ', u'の')),
    u'nu': (None, (u'ヌ', u'ぬ')),
    u'nya': (None, (u'ニャ', u'にゃ')),
    u'nye': (None, (u'ニェ', u'にぇ')),
    u'nyi': (None, (u'ニィ', u'にぃ')),
    u'nyo': (None, (u'ニョ', u'にょ')),
    u'nyu': (None, (u'ニュ', u'にゅ')),
    u'o': (None, (u'オ', u'お')),
    u'pp': (u'p', (u'ッ', u'っ')),
    u'pa': (None, (u'パ', u'ぱ')),
    u'pe': (None, (u'ペ', u'ぺ')),
    u'pi': (None, (u'ピ', u'ぴ')),
    u'po': (None, (u'ポ', u'ぽ')),
    u'pu': (None, (u'プ', u'ぷ')),
    u'pya': (None, (u'ピャ', u'ぴゃ')),
    u'pye': (None, (u'ピェ', u'ぴぇ')),
    u'pyi': (None, (u'ピィ', u'ぴぃ')),
    u'pyo': (None, (u'ピョ', u'ぴょ')),
    u'pyu': (None, (u'ピュ', u'ぴゅ')),
    u'rr': (u'r', (u'ッ', u'っ')),
    u'ra': (None, (u'ラ', u'ら')),
    u're': (None, (u'レ', u'れ')),
    u'ri': (None, (u'リ', u'り')),
    u'ro': (None, (u'ロ', u'ろ')),
    u'ru': (None, (u'ル', u'る')),
    u'rya': (None, (u'リャ', u'りゃ')),
    u'rye': (None, (u'リェ', u'りぇ')),
    u'ryi': (None, (u'リィ', u'りぃ')),
    u'ryo': (None, (u'リョ', u'りょ')),
    u'ryu': (None, (u'リュ', u'りゅ')),
    u'ss': (u's', (u'ッ', u'っ')),
    u'sa': (None, (u'サ', u'さ')),
    u'se': (None, (u'セ', u'せ')),
    u'sha': (None, (u'シャ', u'しゃ')),
    u'she': (None, (u'シェ', u'しぇ')),
    u'shi': (None, (u'シ', u'し')),
    u'sho': (None, (u'ショ', u'しょ')),
    u'shu': (None, (u'シュ', u'しゅ')),
    u'si': (None, (u'シ', u'し')),
    u'so': (None, (u'ソ', u'そ')),
    u'su': (None, (u'ス', u'す')),
    u'sya': (None, (u'シャ', u'しゃ')),
    u'sye': (None, (u'シェ', u'しぇ')),
    u'syi': (None, (u'シィ', u'しぃ')),
    u'syo': (None, (u'ショ', u'しょ')),
    u'syu': (None, (u'シュ', u'しゅ')),
    u'tt': (u't', (u'ッ', u'っ')),
    u'ta': (None, (u'タ', u'た')),
    u'te': (None, (u'テ', u'て')),
    u'tha': (None, (u'テァ', u'てぁ')),
    u'the': (None, (u'テェ', u'てぇ')),
    u'thi': (None, (u'ティ', u'てぃ')),
    u'tho': (None, (u'テョ', u'てょ')),
    u'thu': (None, (u'テュ', u'てゅ')),
    u'ti': (None, (u'チ', u'ち')),
    u'to': (None, (u'ト', u'と')),
    u'tsu': (None, (u'ツ', u'つ')),
    u'tu': (None, (u'ツ', u'つ')),
    u'tya': (None, (u'チャ', u'ちゃ')),
    u'tye': (None, (u'チェ', u'ちぇ')),
    u'tyi': (None, (u'チィ', u'ちぃ')),
    u'tyo': (None, (u'チョ', u'ちょ')),
    u'tyu': (None, (u'チュ', u'ちゅ')),
    u'u': (None, (u'ウ', u'う')),
    u'vv': (u'v', (u'ッ', u'っ')),
    u'va': (None, (u'ヴァ', u'う゛ぁ')),
    u've': (None, (u'ヴェ', u'う゛ぇ')),
    u'vi': (None, (u'ヴィ', u'う゛ぃ')),
    u'vo': (None, (u'ヴォ', u'う゛ぉ')),
    u'vu': (None, (u'ヴ', u'う゛')),
    u'ww': (u'w', (u'ッ', u'っ')),
    u'wa': (None, (u'ワ', u'わ')),
    u'we': (None, (u'ウェ', u'うぇ')),
    u'wi': (None, (u'ウィ', u'うぃ')),
    u'wo': (None, (u'ヲ', u'を')),
    u'wu': (None, (u'ウ', u'う')),
    u'xx': (u'x', (u'ッ', u'っ')),
    u'xa': (None, (u'ァ', u'ぁ')),
    u'xe': (None, (u'ェ', u'ぇ')),
    u'xi': (None, (u'ィ', u'ぃ')),
    u'xka': (None, (u'ヵ', u'か')),
    u'xke': (None, (u'ヶ', u'け')),
    u'xo': (None, (u'ォ', u'ぉ')),
    u'xtsu': (None, (u'ッ', u'っ')),
    u'xtu': (None, (u'ッ', u'っ')),
    u'xu': (None, (u'ゥ', u'ぅ')),
    u'xwa': (None, (u'ヮ', u'ゎ')),
    u'xwe': (None, (u'ヱ', u'ゑ')),
    u'xwi': (None, (u'ヰ', u'ゐ')),
    u'xya': (None, (u'ャ', u'ゃ')),
    u'xyo': (None, (u'ョ', u'ょ')),
    u'xyu': (None, (u'ュ', u'ゅ')),
    u'yy': (u'y', (u'ッ', u'っ')),
    u'ya': (None, (u'ヤ', u'や')),
    u'ye': (None, (u'イェ', u'いぇ')),
    u'yo': (None, (u'ヨ', u'よ')),
    u'yu': (None, (u'ユ', u'ゆ')),
    u'zz': (u'z', (u'ッ', u'っ')),
    u'z,': (None, u'‥'),
    u'z-': (None, u'〜'),
    u'z.': (None, u'…'),
    u'z/': (None, u'・'),
    u'z[': (None, u'『'),
    u'z]': (None, u'』'),
    u'za': (None, (u'ザ', u'ざ')),
    u'ze': (None, (u'ゼ', u'ぜ')),
    u'zh': (None, u'←'),
    u'zi': (None, (u'ジ', u'じ')),
    u'zj': (None, u'↓'),
    u'zk': (None, u'↑'),
    u'zl': (None, u'→'),
    u'zo': (None, (u'ゾ', u'ぞ')),
    u'zu': (None, (u'ズ', u'ず')),
    u'zya': (None, (u'ジャ', u'じゃ')),
    u'zye': (None, (u'ジェ', u'じぇ')),
    u'zyi': (None, (u'ジィ', u'じぃ')),
    u'zyo': (None, (u'ジョ', u'じょ')),
    u'zyu': (None, (u'ジュ', u'じゅ')),
    u'-': (None, u'ー'),
    u':': (None, u'：'),
    u';': (None, u'；'),
    u'?': (None, u'？'),
    u'[': (None, u'「'),
    u']': (None, u'」'),
    # ("l" nil skk-latin-mode)
    # ("q" nil skk-toggle-kana)
    # ("L" nil skk-jisx0208-latin-mode)
    # ("Q" nil skk-set-henkan-point-subr)
    # ("X" nil skk-purge-from-jisyo)
    # ("/" nil skk-abbrev-mode)
    # ("$" nil skk-display-code-for-char-at-point)
    # ("@" nil skk-today)
    # ("\\" nil skk-input-by-code-or-menu)
    # (skk-kakutei-key nil skk-kakutei)
    }

# skk-jisx0208-latin-vector
WIDE_LATIN_TABLE = (None, None, None, None, None, None, None, None, 
                    None, None, None, None, None, None, None, None, 
                    None, None, None, None, None, None, None, None, 
                    None, None, None, None, None, None, None, None, 
                    u'　', u'！', u'”', u'＃', u'＄', u'％', u'＆', u'’', 
                    u'（', u'）', u'＊', u'＋', u'，', u'−', u'．', u'／', 
                    u'０', u'１', u'２', u'３', u'４', u'５', u'６', u'７', 
                    u'８', u'９', u'：', u'；', u'＜', u'＝', u'＞', u'？', 
                    u'＠', u'Ａ', u'Ｂ', u'Ｃ', u'Ｄ', u'Ｅ', u'Ｆ', u'Ｇ', 
                    u'Ｈ', u'Ｉ', u'Ｊ', u'Ｋ', u'Ｌ', u'Ｍ', u'Ｎ', u'Ｏ', 
                    u'Ｐ', u'Ｑ', u'Ｒ', u'Ｓ', u'Ｔ', u'Ｕ', u'Ｖ', u'Ｗ', 
                    u'Ｘ', u'Ｙ', u'Ｚ', u'［', u'＼', u'］', u'＾', u'＿', 
                    u'‘', u'ａ', u'ｂ', u'ｃ', u'ｄ', u'ｅ', u'ｆ', u'ｇ', 
                    u'ｈ', u'ｉ', u'ｊ', u'ｋ', u'ｌ', u'ｍ', u'ｎ', u'ｏ', 
                    u'ｐ', u'ｑ', u'ｒ', u'ｓ', u'ｔ', u'ｕ', u'ｖ', u'ｗ', 
                    u'ｘ', u'ｙ', u'ｚ', u'｛', u'｜', u'｝', u'〜', None)

# skk-num-alist-type1
NUM_WIDE_LATIN_TABLE = {u'0': u'０', u'1': u'１', u'2': u'２', u'3': u'３',
                        u'4': u'４', u'5': u'５', u'6': u'６', u'7': u'７',
                        u'8': u'８', u'9': u'９', u'.': u'．', u' ': u''}

# skk-num-alist-type2
NUM_KANJI_TABLE1 = {u'0': u'〇', u'1': u'一', u'2': u'二', u'3': u'三',
                    u'4': u'四', u'5': u'五', u'6': u'六', u'7': u'七',
                    u'8': u'八', u'9': u'九', u' ': u''}

# skk-num-alist-type5
NUM_KANJI_TABLE2 = {u'0': u'零', u'1': u'壱', u'2': u'弐', u'3': u'参',
                    u'4': u'四', u'5': u'伍', u'6': u'六', u'7': u'七',
                    u'8': u'八', u'9': u'九', u' ': u''}

# skk-num-alist-type3
NUM_KANJI_KURAIDORI_TABLE1 = {1: u'十', 2: u'百', 3: u'千',
                              4: u'万', 8: u'億', 12: u'兆', 16: u'京'}

# skk-num-alist-type5
NUM_KANJI_KURAIDORI_TABLE2 = {1: u'拾', 2: u'百', 3: u'阡',
                              4: u'萬', 8: u'億', 12: u'兆', 16: u'京'}

# japanese-kana-table
ZENKAKU_TO_HANKAKU_KATAKANA_TABLE = {
    u'ア': u'ｱ', u'イ': u'ｲ', u'ウ': u'ｳ', u'エ': u'ｴ', u'オ': u'ｵ',
    u'カ': u'ｶ', u'キ': u'ｷ', u'ク': u'ｸ', u'ケ': u'ｹ', u'コ': u'ｺ',
    u'サ': u'ｻ', u'シ': u'ｼ', u'ス': u'ｽ', u'セ': u'ｾ', u'ソ': u'ｿ',
    u'タ': u'ﾀ', u'チ': u'ﾁ', u'ツ': u'ﾂ', u'テ': u'ﾃ', u'ト': u'ﾄ',
    u'ナ': u'ﾅ', u'ニ': u'ﾆ', u'ヌ': u'ﾇ', u'ネ': u'ﾈ', u'ノ': u'ﾉ',
    u'ハ': u'ﾊ', u'ヒ': u'ﾋ', u'フ': u'ﾌ', u'ヘ': u'ﾍ', u'ホ': u'ﾎ',
    u'マ': u'ﾏ', u'ミ': u'ﾐ', u'ム': u'ﾑ', u'メ': u'ﾒ', u'モ': u'ﾓ',
    u'ヤ': u'ﾔ', u'ユ': u'ﾕ', u'ヨ': u'ﾖ',
    u'ラ': u'ﾗ', u'リ': u'ﾘ', u'ル': u'ﾙ', u'レ': u'ﾚ', u'ロ': u'ﾛ',
    u'ワ': u'ﾜ', u'ヰ': u'ｲ', u'ヱ': u'ｴ', u'ヲ': u'ｦ',
    u'ン': u'ﾝ',
    u'ガ': u'ｶﾞ', u'ギ': u'ｷﾞ', u'グ': u'ｸﾞ', u'ゲ': u'ｹﾞ', u'ゴ': u'ｺﾞ',
    u'ザ': u'ｻﾞ', u'ジ': u'ｼﾞ', u'ズ': u'ｽﾞ', u'ゼ': u'ｾﾞ', u'ゾ': u'ｿﾞ',
    u'ダ': u'ﾀﾞ', u'ヂ': u'ﾁﾞ', u'ヅ': u'ﾂﾞ', u'デ': u'ﾃﾞ', u'ド': u'ﾄﾞ',
    u'バ': u'ﾊﾞ', u'ビ': u'ﾋﾞ', u'ブ': u'ﾌﾞ', u'ベ': u'ﾍﾞ', u'ボ': u'ﾎﾞ',
    u'パ': u'ﾊﾟ', u'ピ': u'ﾋﾟ', u'プ': u'ﾌﾟ', u'ペ': u'ﾍﾟ', u'ポ': u'ﾎﾟ',
    u'ァ': u'ｧ', u'ィ': u'ｨ', u'ゥ': u'ｩ', u'ェ': u'ｪ', u'ォ': u'ｫ',
    u'ッ': u'ｯ',
    u'ャ': u'ｬ', u'ュ': u'ｭ', u'ョ': u'ｮ',
    u'ヮ': u'ﾜ',
    u'ヴ': u'ｳﾞ',
    #u'ヵ': u'ｶ', u'ヶ': u'ｹ'
}

HANKAKU_TO_ZENKAKU_KATAKANA_TABLE = dict()
for zenkaku, hankaku in ZENKAKU_TO_HANKAKU_KATAKANA_TABLE.iteritems():
    HANKAKU_TO_ZENKAKU_KATAKANA_TABLE[hankaku] = zenkaku

# Map from chars whose hankaku analogues are missing.
HANKAKU_KATAKANA_SUBSTITUTES = {u'ヵ': u'ｶ', u'ヶ': u'ｹ'}

# Map from standalone sonant marks to composable analogues in Unicode.
HANKAKU_KATAKANA_SONANTS = {u'\uff9e': u'\u3099', u'\uff9f': u'\u309a'}

KUTOUTEN_JP, \
KUTOUTEN_EN, \
KUTOUTEN_JP_EN, \
KUTOUTEN_EN_JP = range(4)

KUTOUTEN_RULE = ((u'。', u'、'), (u'．', u'，'), (u'。', u'，'), (u'．', u'、'))

AUTO_START_HENKAN_KEYWORDS = (u'を', u'、', u'。', u'．', u'，', u'？', u'」',
                              u'！', u'；', u'：', u')', u';', u':', u'）',
                              u'”', u'】', u'』', u'》', u'〉', u'｝', u'］',
                              u'〕', u'}', u']', u'?', u'.', u',', u'!')

CONV_STATE_NONE, \
CONV_STATE_START, \
CONV_STATE_SELECT = range(3)

INPUT_MODE_NONE, \
INPUT_MODE_HIRAGANA, \
INPUT_MODE_KATAKANA, \
INPUT_MODE_LATIN, \
INPUT_MODE_WIDE_LATIN, \
INPUT_MODE_HANKAKU_KATAKANA = range(6)

INPUT_MODE_TRANSITION_RULE = {
    u'q': {
        INPUT_MODE_HIRAGANA: INPUT_MODE_KATAKANA,
        INPUT_MODE_KATAKANA: INPUT_MODE_HIRAGANA
        },
    u'shift+l': {
        INPUT_MODE_HIRAGANA: INPUT_MODE_WIDE_LATIN,
        INPUT_MODE_KATAKANA: INPUT_MODE_WIDE_LATIN
        },
    u'l': {
        INPUT_MODE_HIRAGANA: INPUT_MODE_LATIN,
        INPUT_MODE_KATAKANA: INPUT_MODE_LATIN
        },
    u'ctrl+j': {
        INPUT_MODE_HIRAGANA: INPUT_MODE_HIRAGANA,
        INPUT_MODE_KATAKANA: INPUT_MODE_KATAKANA,
        INPUT_MODE_WIDE_LATIN: INPUT_MODE_HIRAGANA,
        INPUT_MODE_LATIN: INPUT_MODE_HIRAGANA
        },
    u'ctrl+q': {
        INPUT_MODE_KATAKANA: INPUT_MODE_HANKAKU_KATAKANA,
        INPUT_MODE_HANKAKU_KATAKANA: INPUT_MODE_KATAKANA
        }
    }

ROM_KANA_NORMAL, \
ROM_KANA_KZIK = range(2)

ROM_KANA_RULES = (ROM_KANA_RULE, KZIK_RULE)

TRANSLATED_STRINGS = {
    u'dict-edit-prompt': u'DictEdit',
    u'kuten-prompt': u'Kuten([MM]KKTT) '
}

class DictBase(object):
    ENCODING = 'EUC-JP'

    def split_candidates(self, line):
        '''Parse a single candidate line into a list of candidates.'''
        def seperate_annotation(candidate):
            index = candidate.find(u';')
            if index >= 0:
                return (candidate[0:index], candidate[index + 1:])
            else:
                return (candidate, None)
        return map(seperate_annotation, line.strip()[1:-1].split(u'/'))

    def join_candidates(self, candidates):
        '''Make a single candidate line from a list of candidates.'''
        def append_annotation(candidate_annotation):
            candidate, annotation = candidate_annotation
            if annotation is not None:
                return candidate + u';' + annotation
            else:
                return candidate
        return u'/'.join(map(append_annotation, candidates))

    def reload(self):
        '''Reload the dictionary.'''
        raise NotImplemented

    def lookup(self, midasi, okuri=False):
        '''Lookup MIDASI in the dictionary.'''
        raise NotImplemented
        
    def completer(self, midasi):
        '''Return an iterator to complete MIDASI.'''
        raise NotImplemented

class EmptyDict(DictBase):
    def reload(self):
        pass

    def lookup(self, midasi, okuri=False):
        return list()
        
    def completer(self, midasi):
        return iter(list())

class SysDict(DictBase):
    def __init__(self, path, encoding=DictBase.ENCODING):
        self.__path = path
        self.__mtime = 0
        self.__encoding = encoding
        self.reload()

    path = property(lambda self: self.__path)

    def reload(self):
        try:
            mtime = os.path.getmtime(self.__path)
        except OSError:
            mtime = 0
        if mtime <= self.__mtime:
            return
        try:
            self.__load()
        except IOError:
            pass
        self.__mtime = mtime

    def __load(self):
        self.__okuri_ari = list()
        self.__okuri_nasi = list()
        with open(self.__path, 'r') as fp:
            # Skip headers.
            while True:
                pos = fp.tell()
                line = fp.readline()
                if not line or not line.startswith(';'):
                    break

            offsets = self.__okuri_ari
            offsets.append(pos)
            while True:
                pos = fp.tell()
                line = fp.readline()
                if not line:
                    break
                # A comment line seperating okuri-ari/okuri-nasi entries.
                if line.startswith(';'):
                    offsets = self.__okuri_nasi
                else:
                    offsets.append(pos)
            self.__okuri_ari.reverse()

    def __search_pos(self, fp, offsets, _cmp):
        fp.seek(0)
        begin, end = 0, len(offsets) - 1
        pos = begin + (end - begin) / 2
        while begin <= end:
            fp.seek(offsets[pos])
            line = fp.next()
            r = _cmp(line)
            if r == 0:
                return (pos, line)
            elif r < 0:
                end = pos - 1
            else:
                begin = pos + 1
            pos = begin + (end - begin) / 2
        return None
        
    def __lookup(self, midasi, offsets):
        with open(self.__path, 'r') as fp:
            midasi = midasi.encode(self.__encoding)
            def _lookup_cmp(line):
                _midasi, candidates = line.split(' ', 1)
                return cmp(midasi, _midasi)
            r = self.__search_pos(fp, offsets, _lookup_cmp)
            if not r:
                return list()
            pos, line = r
            _midasi, candidates = line.split(' ', 1)
            candidates = candidates.decode(self.__encoding)
            return self.split_candidates(candidates)

    def lookup(self, midasi, okuri=False):
        if okuri:
            offsets = self.__okuri_ari
        else:
            offsets = self.__okuri_nasi
        if len(offsets) == 0:
            self.reload(self.__path, self.__encoding)
        try:
            return self.__lookup(midasi, offsets)
        except IOError:
            return list()

    def __completer(self, midasi):
        with open(self.__path, 'r') as fp:
            midasi = midasi.encode(self.__encoding)
            def _completer_cmp(line):
                if line.startswith(midasi):
                    return 0
                return cmp(midasi, line)
            r = self.__search_pos(fp, self.__okuri_nasi, _completer_cmp)
            if r:
                pos, line = r
                while pos >= 0:
                    fp.seek(self.__okuri_nasi[pos])
                    line = fp.next()
                    if not line.startswith(midasi):
                        pos += 1
                        break
                    pos -= 1
                while pos < len(self.__okuri_nasi):
                    fp.seek(self.__okuri_nasi[pos])
                    line = fp.next()
                    _midasi, candidates = line.split(' ', 1)
                    yield _midasi.decode(self.__encoding)
                    pos += 1
                
    def completer(self, midasi):
        try:
            return self.__completer(midasi)
        except IOError:
            return iter(list())

class UsrDict(DictBase):
    PATH = '~/.skk-ibus-jisyo'
    HISTSIZE = 128

    __encoding_to_coding_system = {
        'UTF-8': 'utf-8',
        'EUC-JP': 'euc-jp',
        'Shift_JIS': 'shift_jis',
        'ISO-2022-JP': 'iso-2022-jp'
        }

    __coding_system_to_encoding = dict()
    for encoding, coding_system in __encoding_to_coding_system.items():
        __coding_system_to_encoding[coding_system] = encoding

    def __init__(self, path=PATH, encoding=DictBase.ENCODING):
        self.__path = os.path.expanduser(path)
        self.__encoding = encoding
        self.reload()

    path = property(lambda self: self.__path)

    __coding_cookie_pattern = \
        re.compile('\A\s*;+\s*-\*-\s*coding:\s*(\S+?)\s*-\*-')
    def reload(self):
        self.__dict = dict()
        try:
            with open(self.__path, 'a+') as fp:
                line = fp.readline()
                if line:
                    match = re.match(self.__coding_cookie_pattern, line)
                    if match:
                        encoding = self.__coding_system_to_encoding.\
                            get(match.group(1))
                        if encoding:
                            self.__encoding = encoding
                fp.seek(0)
                for line in fp:
                    if line.startswith(';'):
                        continue
                    line = line.decode(self.__encoding)
                    midasi, candidates = line.split(' ', 1)
                    self.__dict[midasi] = self.split_candidates(candidates)
            self.__read_only = False
        except Exception:
            self.__read_only = True
        self.__dict_changed = False
        self.__selection_history = list()

    read_only = property(lambda self: self.__read_only)

    def lookup(self, midasi, okuri=False):
        return self.__dict.get(midasi, list())

    def completer(self, midasi):
        for _midasi in self.__selection_history:
            if _midasi.startswith(midasi):
                yield _midasi
        # TODO: complete from __dict?
        
    def save(self):
        '''Save the changes to the user dictionary.'''
        if not self.__dict_changed or self.__read_only:
            return
        with open(self.__path, 'w+') as fp:
            coding_system = self.__encoding_to_coding_system.\
                get(self.__encoding)
            if coding_system:
                fp.write(';;; -*- coding: %s -*-\n' % coding_system)
            for midasi in sorted(self.__dict):
                line = midasi + u' /' + \
                    self.join_candidates(self.__dict[midasi]) + '/\n'
                fp.write(line.encode(self.__encoding))

    def select_candidate(self, midasi, candidate):
        '''Mark CANDIDATE was selected as the conversion result of MIDASI.'''
        del(self.__selection_history[self.HISTSIZE:])
        _midasi = None
        for index, _midasi in enumerate(self.__selection_history):
            if _midasi == midasi:
                if index > 0:
                    first = self.__selection_history[0]
                    self.__selection_history[0] =\
                        self.__selection_history[index]
                    self.__selection_history[index] = first
                break
        if _midasi is not midasi:
            self.__selection_history.insert(0, midasi)

        if midasi not in self.__dict:
            self.__dict[midasi] = list()
        elements = self.__dict[midasi]
        for index, (_candidate, _annotation) in enumerate(elements):
            if _candidate == candidate[0]:
                if index > 0:
                    first = elements[0]
                    elements[0] = elements[index]
                    elements[index] = first
                    self.__dict_changed = True
                return
        elements.insert(0, candidate)
        self.__dict_changed = True

class SkkServ(DictBase):
    HOST='localhost'
    PORT=1178
    BUFSIZ = 4096

    def __init__(self, host=HOST, port=PORT, encoding=DictBase.ENCODING):
        self.__host = host
        self.__port = port
        self.__encoding = encoding
        self.__socket = None
        self.reload()

    host = property(lambda self: self.__host)
    port = property(lambda self: self.__port)

    def __close(self):
        if self.__socket:
            self.__socket.close()
            self.__socket = None

    def __del__(self):
        self.__close()
        
    def reload(self):
        self.__close()
        try:
            self.__socket = socket.socket()
            self.__socket.connect((self.__host, self.__port))
            # Request server version.
            self.__socket.send('2')
            assert(len(self.__socket.recv(self.BUFSIZ)) > 0)
        except socket.error, AssertionError:
            self.__close()

    def lookup(self, midasi, okuri=False):
        if self.__socket is None:
            return list()
        try:
            self.__socket.send('1' + midasi.encode(self.__encoding) + ' ')
            candidates = self.__socket.recv(self.BUFSIZ)
            if len(candidates) == 0 or candidates[0] != '1':
                return list()
            return self.split_candidates(candidates.decode(self.__encoding)[1:])
        except socket.error:
            return list()

    def completer(self, midasi):
        return iter(list())

def compile_rom_kana_rule(rule):
    def _compile_rom_kana_rule(tree, input_state, arg):
        hd, tl = input_state[0], input_state[1:]
        if hd not in tree:
            if not tl:
                tree[hd] = arg
                return
            tree[hd] = dict()
        _compile_rom_kana_rule(tree[hd], tl, arg)
    tree = dict()
    for input_state in rule:
        _compile_rom_kana_rule(tree, input_state, rule[input_state])
    return tree

def hiragana_to_katakana(kana):
    diff = ord(u'ア') - ord(u'あ')
    def to_katakana(letter):
        if ord(u'ぁ') <= ord(letter) and ord(letter) <= ord(u'ん'):
            return unichr(ord(letter) + diff)
        return letter
    return ''.join(map(to_katakana, kana)).replace(u'ウ゛', u'ヴ')

def katakana_to_hiragana(kana):
    diff = ord(u'ア') - ord(u'あ')
    def to_hiragana(letter):
        if ord(u'ァ') <= ord(letter) and ord(letter) <= ord(u'ン'):
            return unichr(ord(letter) - diff)
        return letter
    return ''.join(map(to_hiragana, kana.replace(u'ヴ', u'ウ゛')))

def hankaku_katakana(kana):
    def to_hankaku(letter):
        if HANKAKU_KATAKANA_SUBSTITUTES.has_key(letter):
            return HANKAKU_KATAKANA_SUBSTITUTES[letter]
        elif ord(u'ァ') <= ord(letter) and ord(letter) <= ord(u'ン'):
            return ZENKAKU_TO_HANKAKU_KATAKANA_TABLE[letter]
        return letter
    return ''.join(map(to_hankaku, kana))

def zenkaku_katakana(kana):
    def to_zenkaku(letter):
        if HANKAKU_KATAKANA_SONANTS.has_key(letter):
            return HANKAKU_KATAKANA_SONANTS[letter]
        elif ord(u'ｦ') <= ord(letter) and ord(letter) <= ord(u'ﾝ'):
            return HANKAKU_TO_ZENKAKU_KATAKANA_TABLE[letter]
        return letter
    return unicodedata.normalize('NFC', ''.join(map(to_zenkaku, kana)))

def num_to_latin(num):
    return num

def num_to_jisx0208_latin(num):
    return ''.join([NUM_WIDE_LATIN_TABLE[c] for c in num])

def num_to_type2_kanji(num):
    return ''.join([NUM_KANJI_TABLE1[c] for c in num])

def num_to_kanji(num, digit_table, kurai_table):
    ndigits = len(num)
    result = list()
    for index, digit in enumerate(num):
        if int(digit) > 0:
            result.append(digit_table[digit])
            index = ndigits - index - 1
            kurai = kurai_table.get(index, None)
            if kurai:
                result.append(kurai)
            elif index % 4 > 0:
                result.append(kurai_table[index % 4])
    return ''.join(result)

def num_to_type3_kanji(num):
    return num_to_kanji(num,
                        NUM_KANJI_TABLE1,
                        NUM_KANJI_KURAIDORI_TABLE1)

def num_to_type5_kanji(num):
    return num_to_kanji(num,
                        NUM_KANJI_TABLE2,
                        NUM_KANJI_KURAIDORI_TABLE2)

NUM_CONVERTERS = (num_to_latin,
                  num_to_jisx0208_latin,
                  num_to_type2_kanji,
                  num_to_type3_kanji,
                  num_to_latin,
                  num_to_type5_kanji)

def replace_num_with_hash(midasi):
    return (re.sub('[0-9]+', '#', midasi),
            [num.group() for num in re.finditer('[0-9]+', midasi)])

def substitute_num(candidate, num_list):
    if len(num_list) == 0:
        return candidate
    _num_index = [0]
    def replace_hash_with_num(match):
        if len(num_list) == 0:
            return match.group(0)
        converter_index = int(match.group(1))
        if converter_index >= len(NUM_CONVERTERS):
            return match.group(0)
        converter = NUM_CONVERTERS[converter_index]
        result = converter(num_list[_num_index[0]])
        _num_index[0] += 1
        return result
    return re.sub('#([0-9]+)', replace_hash_with_num, candidate)

class CandidateSelector(object):
    PAGE_SIZE = 7
    PAGINATION_START = 4

    def __init__(self, page_size=PAGE_SIZE, pagination_start=PAGINATION_START):
        self.__page_size = page_size
        self.__pagination_start = pagination_start
        self.set_candidates(list())

    page_size = property(lambda self: self.__page_size)
    pagination_start = property(lambda self: self.__pagination_start)

    def set_candidates(self, candidates):
        '''Set the list of candidates.'''
        self.__candidates = candidates
        self.__index = -1

    def next_candidate(self, move_over_pages=True):
        '''Move the cursor forward.  If MOVE_OVER_PAGES is True, skip
        to the next page instead of the next candidate.'''
        if move_over_pages and self.__index >= self.__pagination_start:
            index = self.__index + self.__page_size
            # Place the cursor at the beginning of the page.
            index -= (index - self.__pagination_start) % self.__page_size
        else:
            index = self.__index + 1
        self.set_index(index)
        return self.candidate()

    def previous_candidate(self, move_over_pages=True):
        '''Move the cursor forward.  If MOVE_OVER_PAGES is
        True, skip to the previous page instead of the previous candidate.'''
        if move_over_pages and self.__index >= self.__pagination_start:
            index = self.__index - self.__page_size
            # Place the cursor at the beginning of the page.
            index -= (index - self.__pagination_start) % self.__page_size
        else:
            index = self.__index - 1
        self.set_index(index)
        return self.candidate()

    def candidate(self):
        '''Return the current candidate.'''
        if self.__index < 0:
            return None
        return self.__candidates[self.__index] + (True,)

    def index(self):
        '''Return the current candidate index.'''
        return self.__index

    def candidates(self):
        '''Return the list of candidates.'''
        return self.__candidates[:]

    def set_index(self, index):
        '''Set the current candidate index.'''
        if 0 <= index and index < len(self.__candidates):
            self.__index = index
        else:
            self.__index = -1

class State(object):
    def __init__(self):
        self.reset()
        self.dict_edit_output = u''

    def reset(self):
        self.conv_state = CONV_STATE_NONE
        self.input_mode = INPUT_MODE_NONE

        # Current midasi in conversion.
        self.midasi = None

        # Whether or not we are in the abbrev mode.
        self.abbrev = False

        self.completer = None

        # Last used keyword which triggered auto-start-henkan.
        self.auto_start_henkan_keyword = None

        # rom-kana state is either None or a tuple
        #
        # (OUTPUT, PENDING, TREE)
        #
        # where OUTPUT is a kana string, PENDING is a string in
        # rom-kana conversion, and TREE is a subtree of
        # rom_kana_rule_tree.
        #
        # See skk.Context#__convert_rom_kana() for the state
        # transition algorithm.
        self.rom_kana_state = None
        self.okuri_rom_kana_state = None

        self.candidates = list()
        self.candidate_index = -1

        self.kuten = None

class Key(object):
    __letters = {
#        'return': '\r',
        'escape': '\e',
        'backspace': '\h',
        'tab': '\t'
        }

    def __init__(self, keystr):
        self.__keystr = keystr
        self.__is_ctrl = keystr.startswith('ctrl+')
        if self.__is_ctrl:
            keystr = keystr[5:]
        self.__is_shift = keystr.startswith('shift+')
        if self.__is_shift:
            keystr = keystr[6:]
        self.__keyval = keystr

        if Key.__letters.has_key(keystr.lower()):
            self.__letter = Key.__letters[keystr.lower()]
        elif self.__is_shift:
            self.__letter = keystr.upper()
        else:
            self.__letter = keystr

    def __str__(self):
        return self.__keystr

    letter = property(lambda self: self.__letter)
    keyval = property(lambda self: self.__keyval)

    def is_ctrl(self):
        return self.__is_ctrl

    def is_shift(self):
        return self.__is_shift

class Context(object):
    def __init__(self, usrdict, sysdict, candidate_selector):
        '''Create an SKK context.

        USRDICT is a user dictionary and SYSDICT is a system
        dictionary (or a connection to SKKServ).'''
        self.__usrdict = None
        self.__sysdict = None
        self.__rom_kana_rule = None
        self.__candidate_selector = candidate_selector
        self.__state_stack = list()
        self.__state_stack.append(State())
        self.__kuten_codec = None

        self.usrdict = usrdict
        self.sysdict = sysdict
        self.rom_kana_rule = ROM_KANA_NORMAL
        self.kutouten_type = KUTOUTEN_JP
        self.auto_start_henkan_keywords = AUTO_START_HENKAN_KEYWORDS
        self.translated_strings = dict(TRANSLATED_STRINGS)
        self.reset()

    def __check_dict(self, _dict):
        if not isinstance(_dict, DictBase):
            raise TypeError('bad dict')

    def set_usrdict(self, usrdict):
        '''Set the user dictionary.'''
        self.__check_dict(usrdict)
        self.__usrdict = usrdict

    def set_sysdict(self, sysdict):
        '''Set the system dictionary.'''
        self.__check_dict(sysdict)
        self.__sysdict = sysdict

    usrdict = property(lambda self: self.__usrdict, set_usrdict)
    sysdict = property(lambda self: self.__sysdict, set_sysdict)

    def set_rom_kana_rule(self, rom_kana_rule):
        if self.__rom_kana_rule != rom_kana_rule:
            self.__rom_kana_rule = rom_kana_rule
            self.__rom_kana_rule_tree = \
                compile_rom_kana_rule(ROM_KANA_RULES[self.__rom_kana_rule])

    rom_kana_rule = property(lambda self: self.__rom_kana_rule,
                             set_rom_kana_rule)

    def __current_state(self):
        return self.__state_stack[-1]

    def __previous_state(self):
        return self.__state_stack[-2]

    conv_state = property(lambda self: self.__current_state().conv_state)
    input_mode = property(lambda self: self.__current_state().input_mode)
    abbrev = property(lambda self: self.__current_state().abbrev)

    def reset(self):
        '''Reset the current state of rom-kana/kana-kan conversion.'''
        self.__current_state().reset()
        self.__candidate_selector.set_candidates(self.__current_state().\
                                                     candidates)

    def __enter_dict_edit(self):
        self.__current_state().candidates = \
            self.__candidate_selector.candidates()
        self.__current_state().candidate_index = \
            self.__candidate_selector.index()

        midasi = self.__current_state().midasi
        input_mode = self.__current_state().input_mode
        self.__state_stack.append(State())
        self.reset()
        self.__current_state().midasi = midasi
        self.activate_input_mode(input_mode)

    def __abort_dict_edit(self):
        assert(self.dict_edit_level() > 0)
        self.__state_stack.pop()
        # Stop rom-kana conversion for okuri-kana if it is active.
        if self.__current_state().conv_state == CONV_STATE_START and \
                self.__current_state().okuri_rom_kana_state:
            self.__current_state().rom_kana_state = \
                (self.__current_state().rom_kana_state[0] + \
                     self.__current_state().okuri_rom_kana_state[0], \
                     u'', u'')
            self.__current_state().okuri_rom_kana_state = None
        # Restore candidates.
        self.__candidate_selector.set_candidates(self.__current_state().\
                                                     candidates)
        self.__candidate_selector.set_index(self.__current_state().\
                                                candidate_index)

    def __leave_dict_edit(self):
        dict_edit_output = self.__current_state().dict_edit_output
        self.__abort_dict_edit()
        self.__current_state().candidates.insert(0, (dict_edit_output, None))
        self.__candidate_selector.set_index(0)
        output = self.kakutei()
        if self.dict_edit_level() > 0:
            self.__current_state().dict_edit_output += output
            return None
        return output

    def activate_input_mode(self, input_mode):
        '''Switch the current input mode to INPUT_MODE.'''
        self.__current_state().input_mode = input_mode
        if self.__current_state().input_mode in (INPUT_MODE_HIRAGANA,
                                                 INPUT_MODE_KATAKANA,
                                                 INPUT_MODE_HANKAKU_KATAKANA):
            self.__current_state().rom_kana_state = (u'', u'',
                                                     self.__rom_kana_rule_tree)
        else:
            self.__current_state().rom_kana_state = None

    def kakutei(self):
        '''Fix the current candidate as a commitable string.'''
        if self.__current_state().midasi:
            candidate = self.__candidate_selector.candidate()
            if candidate:
                output = candidate[0]
                if self.__current_state().okuri_rom_kana_state:
                    output += self.__current_state().okuri_rom_kana_state[0]
                if candidate[2]:
                    self.__usrdict.select_candidate(self.__current_state().midasi,
                                                    candidate[:2])
            else:
                output = self.__current_state().rom_kana_state[0]
        else:
            output = self.__current_state().rom_kana_state[0]
        if self.__current_state().auto_start_henkan_keyword:
            output += self.__current_state().auto_start_henkan_keyword
        input_mode = self.__current_state().input_mode
        self.reset()
        self.activate_input_mode(input_mode)
        return output

    def __activate_candidate_selector(self, midasi, okuri=False):
        midasi, num_list = replace_num_with_hash(midasi)
        self.__current_state().midasi = midasi
        usr_candidates = self.__usrdict.lookup(midasi)
        sys_candidates = self.__sysdict.lookup(midasi, okuri)
        candidates = self.__merge_candidates(usr_candidates,
                                             sys_candidates)
        candidates = [(substitute_num(candidate[0], num_list),
                       candidate[1])
                      for candidate in candidates]
        self.__candidate_selector.set_candidates(candidates)
        if self.next_candidate() is None:
            self.__current_state().conv_state = CONV_STATE_START
            self.__enter_dict_edit()

    def press_key(self, keystr):
        '''Process a key press event KEYSTR.

        KEYSTR is in the format of ["ctrl+"]["shift+"]<lower case ASCII letter>.

        The return value is a tuple (HANDLED, OUTPUT) where HANDLED is
        True if the event was handled internally (otherwise False),
        and OUTPUT is a committable string (if any).'''
        key = Key(keystr)
        if str(key) == 'ctrl+g':
            if self.dict_edit_level() > 0 and \
                    self.__current_state().conv_state == CONV_STATE_NONE:
                self.__abort_dict_edit()
            elif self.__current_state().conv_state in (CONV_STATE_NONE,
                                                       CONV_STATE_START):
                input_mode = self.__current_state().input_mode
                self.reset()
                self.activate_input_mode(input_mode)
            else:
                if self.__current_state().okuri_rom_kana_state:
                    self.__current_state().rom_kana_state = \
                        (self.__current_state().rom_kana_state[0] + \
                             self.__current_state().okuri_rom_kana_state[0],
                         u'',
                         self.__rom_kana_rule_tree)
                    self.__current_state().okuri_rom_kana_state = None
                # Stop kana-kan conversion.
                self.__current_state().midasi = None
                self.__candidate_selector.set_candidates(list())
                self.__current_state().conv_state = CONV_STATE_START
            return (True, u'')

        if str(key) in ('ctrl+h', 'backspace'):
            return self.delete_char()

        rom_kana_pending = self.__current_state().rom_kana_state and \
            len(self.__current_state().rom_kana_state[1]) > 0

        if self.__current_state().conv_state == CONV_STATE_NONE:
            input_mode = INPUT_MODE_TRANSITION_RULE.get(str(key), dict()).\
                get(self.__current_state().input_mode)
            if not rom_kana_pending and input_mode is not None:
                self.reset()
                self.activate_input_mode(input_mode)
                return (True, u'')

            if self.dict_edit_level() > 0 and str(key) in ('ctrl+j', 'return'):
                return (True, self.__leave_dict_edit())

            # Ignore ctrl+key and non-ASCII characters.
            if key.is_ctrl() or \
                    str(key) in ('return', 'escape', 'backspace') or \
                    0x20 > ord(key.letter) or ord(key.letter) > 0x7E:
                return (False, u'')

            if self.__current_state().input_mode == INPUT_MODE_LATIN:
                output = key.letter
                if self.dict_edit_level() > 0:
                    self.__current_state().dict_edit_output += output
                    return (True, u'')
                return (True, output)
            elif self.__current_state().input_mode == INPUT_MODE_WIDE_LATIN:
                output = WIDE_LATIN_TABLE[ord(key.letter)]
                if self.dict_edit_level() > 0:
                    self.__current_state().dict_edit_output += output
                    return (True, u'')
                return (True, output)

            # Start KUTEN input.
            if str(key) == '\\':
                if not self.__kuten_codec:
                    import codecs
                    try:
                        self.__kuten_codec = codecs.lookup('EUC-JIS-2004')
                    except LookupError:
                        pass
                if self.__kuten_codec:
                    self.__current_state().kuten = u''
                    self.__current_state().conv_state = CONV_STATE_START
                return (True, u'')

            # Start rom-kan mode with abbrev enabled (/).
            if not rom_kana_pending and key.keyval == '/':
                self.__current_state().conv_state = CONV_STATE_START
                self.__current_state().abbrev = True
                return (True, u'')

            # Start rom-kan mode (shift+q).
            if key.is_shift() and key.keyval == 'q':
                self.__current_state().conv_state = CONV_STATE_START
                return (True, u'')

            # Start rom-kan mode and insert a character which
            # triggered the transition.
            if key.is_shift() and key.keyval.isalpha():
                self.__current_state().conv_state = CONV_STATE_START

            self.__current_state().rom_kana_state = \
                self.__convert_rom_kana(key.keyval,
                                        self.__current_state().rom_kana_state)
            if self.__current_state().conv_state == CONV_STATE_NONE and \
                    len(self.__current_state().rom_kana_state[1]) == 0:
                output = self.kakutei()
                if self.dict_edit_level() > 0:
                    self.__current_state().dict_edit_output += output
                    return (True, u'')
                return (True, output)
            return (True, u'')

        elif self.__current_state().conv_state == CONV_STATE_START:
            input_mode = INPUT_MODE_TRANSITION_RULE.get(str(key), dict()).\
                get(self.__current_state().input_mode)
            if rom_kana_pending or self.__current_state().abbrev:
                input_mode = None
            if self.__current_state().input_mode == INPUT_MODE_HIRAGANA and \
                    input_mode == INPUT_MODE_KATAKANA:
                kana = hiragana_to_katakana(\
                    self.__current_state().rom_kana_state[0])
                self.kakutei()
                if self.dict_edit_level() > 0:
                    self.__current_state().dict_edit_output += kana
                    return (True, u'')
                return (True, kana)
            elif self.__current_state().input_mode == INPUT_MODE_KATAKANA and \
                    input_mode == INPUT_MODE_HIRAGANA:
                kana = katakana_to_hiragana(\
                    self.__current_state().rom_kana_state[0])
                self.kakutei()
                if self.dict_edit_level() > 0:
                    self.__current_state().dict_edit_output += kana
                    return (True, u'')
                return (True, kana)
            elif self.__current_state().input_mode == INPUT_MODE_HANKAKU_KATAKANA and \
                    input_mode == INPUT_MODE_KATAKANA:
                kana = zenkaku_katakana(\
                    self.__current_state().rom_kana_state[0])
                self.kakutei()
                if self.dict_edit_level() > 0:
                    self.__current_state().dict_edit_output += kana
                    return (True, u'')
                return (True, kana)
            elif self.__current_state().input_mode == INPUT_MODE_KATAKANA and \
                    input_mode == INPUT_MODE_HANKAKU_KATAKANA:
                kana = zenkaku_katakana(\
                    self.__current_state().rom_kana_state[0])
                self.kakutei()
                if self.dict_edit_level() > 0:
                    self.__current_state().dict_edit_output += kana
                    return (True, u'')
                return (True, kana)
            elif input_mode is not None and not self.__current_state().abbrev:
                output = self.kakutei()
                if self.dict_edit_level() > 0:
                    self.__current_state().dict_edit_output += output
                    output = u''
                self.activate_input_mode(input_mode)
                return (True, output)

            if str(key) in ('ctrl+j', 'return'):
                kuten = self.__current_state().kuten
                if kuten is not None:
                    input_mode = self.__current_state().input_mode
                    self.reset()
                    self.activate_input_mode(input_mode)
                    try:
                        k = [int(kuten[x:x+2], 16)
                             for x in xrange(0, len(kuten), 2)]
                        euc = ''
                        if len(k) == 2:
                            euc = struct.pack('BB', *k)
                        elif len(k) == 3:
                            euc = struct.pack('BB', *k[1:])
                            if k[0] == 1:
                                euc = '\x8F' + euc
                        return (True, self.__kuten_codec.decode(euc)[0])
                    except ValueError, UnicodeDecodeError:
                        return (True, u'')

                output = self.kakutei()
                if self.dict_edit_level() > 0:
                    self.__current_state().dict_edit_output += output
                    return (True, u'')
                return (True, output)

            if self.__current_state().kuten is not None:
                if len(self.__current_state().kuten) >= 6:
                    input_mode = self.__current_state().input_mode
                    self.reset()
                    self.activate_input_mode(input_mode)
                    return (True, u'')
                if re.match('\A[0-9a-f]\Z', key.letter):
                    self.__current_state().kuten += key.letter.upper()
                return (True, u'')

            # Start TAB(\C-i) completion.
            if key.keyval == '\t' or (key.is_ctrl() and key.letter == 'i'):
                self.__current_state().rom_kana_state = \
                    self.__convert_nn(self.__current_state().rom_kana_state)
                if self.__current_state().completer is None:
                    compkey = self.__current_state().rom_kana_state[0]
                    self.__current_state().completer = \
                        self.__init_completer(compkey)
                    self.__current_state().completion_seen = set((compkey,))
                for midasi in self.__current_state().completer:
                    if midasi not in self.__current_state().completion_seen:
                        self.__current_state().rom_kana_state = (midasi,
                                                                 u'',
                                                                 u'')
                        self.__current_state().completion_seen.add(midasi)
                        break
                return (True, u'')
            # Stop TAB completion.
            self.__current_state().completer = None
            self.__current_state().completion_seen = None

            # Start okuri-nasi conversion.
            auto_start_henkan_keyword = None
            rom_kana_state = tuple(self.__current_state().rom_kana_state)
            rom_kana_state = self.__convert_rom_kana(key.keyval, rom_kana_state)
            for keyword in AUTO_START_HENKAN_KEYWORDS:
                if rom_kana_state[0].endswith(keyword):
                    self.__current_state().auto_start_henkan_keyword = keyword
                    break
            if key.keyval == u' ' or \
                    self.__current_state().auto_start_henkan_keyword:
                self.__current_state().conv_state = CONV_STATE_SELECT
                self.__current_state().rom_kana_state = \
                    self.__convert_nn(self.__current_state().rom_kana_state)
                midasi = katakana_to_hiragana(\
                    zenkaku_katakana(\
                        self.__current_state().rom_kana_state[0]))
                self.__activate_candidate_selector(midasi)
                return (True, u'')

            if key.is_shift() and \
                    len(self.__current_state().rom_kana_state[1]) == 0 and \
                    not self.__current_state().okuri_rom_kana_state:
                self.__current_state().okuri_rom_kana_state = \
                    (u'', u'', self.__rom_kana_rule_tree)

            if self.__current_state().okuri_rom_kana_state:
                okuri = (self.__current_state().okuri_rom_kana_state[1] or \
                             key.keyval)[0]
                self.__current_state().okuri_rom_kana_state = \
                    self.__convert_rom_kana(key.keyval, self.__current_state().okuri_rom_kana_state)

                # Start okuri-ari conversion.
                if len(self.__current_state().okuri_rom_kana_state[1]) == 0:
                    self.__current_state().conv_state = CONV_STATE_SELECT
                    midasi = katakana_to_hiragana(\
                        zenkaku_katakana(\
                            self.__current_state().rom_kana_state[0] + okuri))
                    self.__activate_candidate_selector(midasi, True)
                return (True, u'')

            # Ignore ctrl+key and non-ASCII characters.
            if key.is_ctrl() or str(key) in ('return', 'escape', 'backspace') or \
                    0x20 > ord(key.letter) or ord(key.letter) > 0x7E:
                return (False, u'')

            if self.__current_state().abbrev:
                self.__current_state().rom_kana_state = \
                    (self.__current_state().rom_kana_state[0] + key.keyval,
                     u'',
                     self.__rom_kana_rule_tree)
            else:
                self.__current_state().rom_kana_state = \
                    self.__convert_rom_kana(key.keyval,
                                            self.__current_state().rom_kana_state)
            return (True, u'')

        elif self.__current_state().conv_state == CONV_STATE_SELECT:
            if key.letter.isspace():
                index = self.__candidate_selector.index()
                if self.next_candidate() is None:
                    self.__candidate_selector.set_index(index)
                    self.__enter_dict_edit()
                return (True, u'')
            elif str(key) == 'x':
                if self.previous_candidate() is None:
                    self.__current_state().conv_state = CONV_STATE_START
                return (True, u'')
            else:
                output = self.kakutei()
                if self.dict_edit_level() > 0:
                    self.__current_state().dict_edit_output += output
                    output = u''
                if str(key) in ('ctrl+j', 'return'):
                    return (True, output)
                return (True, output + self.press_key(str(key))[1])

    def __init_completer(self, compkey):
        return itertools.chain(self.__usrdict.completer(compkey),
                               self.__sysdict.completer(compkey))

    def __delete_char_from_rom_kana_state(self, state):
        tree = self.__rom_kana_rule_tree
        output, pending, _tree = state
        if pending:
            pending = pending[:-1]
            for letter in pending:
                tree = tree[letter]
            return (output, pending, tree)
        elif output:
            return (output[:-1], u'', tree)

    def delete_char(self):
        '''Delete a character at the end of the buffer.'''
        if self.__current_state().conv_state == CONV_STATE_SELECT:
            self.__current_state().conv_state = CONV_STATE_NONE
            output = self.kakutei()
            if self.dict_edit_level() > 0:
                self.__current_state().dict_edit_output += output[:-1]
                return (True, u'')
            return (True, output[:-1])
        if self.__current_state().okuri_rom_kana_state:
            state = self.__delete_char_from_rom_kana_state(\
                self.__current_state().okuri_rom_kana_state)
            if state:
                self.__current_state().okuri_rom_kana_state = state
                return (True, u'')
        if self.__current_state().rom_kana_state:
            state = self.__delete_char_from_rom_kana_state(\
                self.__current_state().rom_kana_state)
            if state:
                self.__current_state().rom_kana_state = state
                return (True, u'')
        if self.__current_state().kuten is not None:
            if len(self.__current_state().kuten) > 0:
                self.__current_state().kuten = self.__current_state().kuten[:-1]
                return (True, u'')
        if self.__current_state().conv_state == CONV_STATE_START:
            input_mode = self.__current_state().input_mode
            self.reset()
            self.activate_input_mode(input_mode)
            return (True, u'')
        if self.dict_edit_level() > 0 and \
                len(self.__current_state().dict_edit_output) > 0:
            self.__current_state().dict_edit_output = \
                self.__current_state().dict_edit_output[:-1]
            return (True, u'')
        return (False, u'')

    def next_candidate(self, move_over_pages=True):
        '''Select the next candidate.'''
        return self.__candidate_selector.next_candidate(move_over_pages)

    def previous_candidate(self, move_over_pages=True):
        '''Select the previous candidate.'''
        return self.__candidate_selector.previous_candidate(move_over_pages)

    def select_candidate(self, index):
        '''Select candidate at INDEX.'''
        self.__candidate_selector.set_index(index)
        if self.__candidate_selector.index() < 0:
            return (False, u'')
        output = self.kakutei()
        if self.dict_edit_level() > 0:
            self.__current_state().dict_edit_output += output
            return (True, u'')
        return (True, output)

    def __merge_candidates(self, usr_candidates, sys_candidates):
        return usr_candidates + \
            [candidate for candidate in sys_candidates
             if candidate not in usr_candidates]

    def dict_edit_level(self):
        '''Return the recursion level of dict-edit mode.'''
        return len(self.__state_stack) - 1

    def __dict_edit_prompt(self):
        if self.__previous_state().okuri_rom_kana_state:
            midasi = self.__previous_state().rom_kana_state[0] + \
                u'*' + \
                self.__previous_state().okuri_rom_kana_state[0] + \
                self.__previous_state().okuri_rom_kana_state[1]
        else:
            midasi = self.__previous_state().rom_kana_state[0] + \
                self.__previous_state().rom_kana_state[1]
        return u'%s%s%s %s ' % (u'[' * self.dict_edit_level(),
                                self.translated_strings['dict-edit-prompt'],
                                u']' * self.dict_edit_level(),
                                midasi)

    def preedit_components(self):
        '''Return a tuple representing the current preedit text.  The
format of the tuple is (PROMPT, PREFIX, WORD, SUFFIX).

For example, in okuri-ari conversion (in dict-edit mode level 2) the
elements will be "[[DictEdit]] かんが*え ", "▽", "かんが", "*え" .'''
        if self.dict_edit_level() > 0:
            prompt = self.__dict_edit_prompt()
            prefix = self.__current_state().dict_edit_output
        else:
            prompt = u''
            prefix = u''
        if self.__current_state().conv_state == CONV_STATE_NONE:
            if self.__current_state().rom_kana_state:
                return (prompt,
                        prefix,
                        self.__current_state().rom_kana_state[1],
                        u'')
            else:
                return (prompt, prefix, u'', u'')
        elif self.__current_state().conv_state == CONV_STATE_START:
            if self.__current_state().kuten is not None:
                return (prompt + self.translated_strings['kuten-prompt'],
                        prefix + u'',
                        self.__current_state().kuten,
                        u'')
                
            if self.__current_state().okuri_rom_kana_state:
                return (prompt,
                        prefix + u'▽',
                        self.__current_state().rom_kana_state[0],
                        u'*' + \
                            self.__current_state().okuri_rom_kana_state[0] + \
                            self.__current_state().okuri_rom_kana_state[1])
            else:
                return (prompt,
                        prefix + u'▽',
                        self.__current_state().rom_kana_state[0] + \
                            self.__current_state().rom_kana_state[1],
                        u'')
        else:
            if self.__current_state().okuri_rom_kana_state:
                if self.__current_state().midasi:
                    candidate = self.__candidate_selector.candidate()
                    if candidate:
                        return (prompt,
                                prefix + u'▼',
                                candidate[0],
                                self.__current_state().okuri_rom_kana_state[0])
                return (prompt,
                        prefix + u'▼',
                        self.__current_state().rom_kana_state[0],
                        self.__current_state().okuri_rom_kana_state[0])
            else:
                if self.__current_state().midasi:
                    candidate = self.__candidate_selector.candidate()
                    if candidate:
                        return (prompt,
                                prefix + u'▼',
                                candidate[0],
                                (self.__current_state().\
                                     auto_start_henkan_keyword or u''))
                return (prompt,
                        prefix + u'▼',
                        self.__current_state().rom_kana_state[0],
                        (self.__current_state().\
                             auto_start_henkan_keyword or u''))
        return (prompt, prefix, u'', u'')

    preedit = property(lambda self: ''.join(self.preedit_components()))

    def __convert_nn(self, state):
        output, pending, tree = state
        if pending.endswith(u'n'):
            if self.__current_state().input_mode == INPUT_MODE_HIRAGANA:
                output += u'ん'
            elif self.__current_state().input_mode == INPUT_MODE_KATAKANA:
                output += u'ン'
            elif self.__current_state().input_mode == INPUT_MODE_HANKAKU_KATAKANA:
                output += u'ﾝ'
            return (output, pending[:-1], tree)
        return state
        
    def __convert_rom_kana(self, letter, state):
        output, pending, tree = state
        if letter not in tree:
            output, pending, tree = self.__convert_nn(state)
            index = u'.,'.find(letter)
            if index >= 0:
                return (output + KUTOUTEN_RULE[self.kutouten_type][index],
                        u'', self.__rom_kana_rule_tree)
            if letter not in self.__rom_kana_rule_tree:
                return (output + letter, u'', self.__rom_kana_rule_tree)
            return self.__convert_rom_kana(letter,
                                           (output, u'',
                                            self.__rom_kana_rule_tree))
        if isinstance(tree[letter], dict):
            return (output, pending + letter, tree[letter])
        next_pending, next_output = tree[letter]
        if isinstance(next_output, unicode):
            output += next_output
        else:
            katakana, hiragana = next_output
            if self.__current_state().input_mode == INPUT_MODE_HANKAKU_KATAKANA:
                katakana = hankaku_katakana(katakana)
            if self.__current_state().input_mode == INPUT_MODE_HIRAGANA:
                output += hiragana
            elif self.__current_state().input_mode in (INPUT_MODE_KATAKANA,
                                                       INPUT_MODE_HANKAKU_KATAKANA):
                output += katakana
        next_state = (output, u'', self.__rom_kana_rule_tree)
        if next_pending:
            for next_letter in next_pending:
                next_state = self.__convert_rom_kana(next_letter, next_state)
        return next_state
