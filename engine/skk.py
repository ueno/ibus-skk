# vim:set et sts=4 sw=4:
# -*- coding: utf-8 -*-
#
# ibus-skk - The SKK engine for IBus
#
# Copyright (C) 2009 Daiki Ueno <ueno@unixuser.org>
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

class Dict:
    ENCODING = 'EUC-JP'

    def __init__(self, filename='/usr/share/skk/SKK-JISYO.L', mode='r',
                 encoding=ENCODING):
        self.__fp = open(filename, mode)
        self.__okuri_ari = list()
        self.__okuri_nasi = list()

        # Skip headers.
        while True:
            pos = self.__fp.tell()
            line = self.__fp.readline()
            if not line or not line.startswith(';'):
                break

        offsets = self.__okuri_ari
        offsets.append(pos)
        while True:
            pos = self.__fp.tell()
            line = self.__fp.readline()
            if not line:
                break
            # A comment line seperating okuri-ari/okuri-nasi entries.
            if line.startswith(';'):
                offsets = self.__okuri_nasi
            else:
                offsets.append(pos)
        self.__okuri_ari.reverse()

    def __candidate_list(self, line):
        candidates = line.strip()[1:-1].split('/')
        candidates = [candidate.decode(self.ENCODING)
                      for candidate in candidates]
        def seperate_annotation(candidate):
            index = candidate.find(u';')
            if index >= 0:
                return (candidate[0:index], candidate[index + 1:])
            else:
                return (candidate, None)
        return map(seperate_annotation, candidates)

    def lookup(self, key, okuri=False):
        if okuri:
            offsets = self.__okuri_ari
        else:
            offsets = self.__okuri_nasi
        self.__fp.seek(0)
        begin, end = 0, len(offsets) - 1
        pos = begin + (end - begin) / 2
        key = key.encode(self.ENCODING)
        while begin <= end:
            self.__fp.seek(offsets[pos])
            line = self.__fp.next()
            word, candidates = line.split(' ', 1)
            r = cmp(key, word)
            if r == 0:
                return self.__candidate_list(candidates)
            elif r < 0:
                end = pos - 1
            else:
                begin = pos + 1
            pos = begin + (end - begin) / 2
        return list()

# Converted from skk-rom-kana-base-rule in skk-vars.el.
rom_kana_rule = {
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
    u'.': (None, u'．'),
    u',': (None, u'，'),
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

# skk-jisx0208-latin-vector
wide_latin_table = (None, None, None, None, None, None, None, None, 
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

CONV_STATE_NONE, \
CONV_STATE_START, \
CONV_STATE_SELECT = range(3)

INPUT_MODE_HIRAGANA, \
INPUT_MODE_KATAKANA, \
INPUT_MODE_LATIN, \
INPUT_MODE_WIDE_LATIN = range(4)

input_mode_transition_rule = {
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
        INPUT_MODE_WIDE_LATIN: INPUT_MODE_HIRAGANA,
        INPUT_MODE_LATIN: INPUT_MODE_HIRAGANA
        }
    }

class CandidateSelectorBase(object):
    def __init__(self):
        self.set_candidates(list())

    def set_candidates(self, candidates):
        self.__candidates = candidates
        self.__candidate_index = -1

    def next_candidate(self):
        if self.__candidates:
            self.__candidate_index += 1
            self.__candidate_index %= len(self.__candidates)
            return self.__candidates[self.__candidate_index]

    def previous_candidate(self):
        if self.__candidates:
            self.__candidate_index -= 1
            self.__candidate_index %= len(self.__candidates)
            return self.__candidates[self.__candidate_index]

class Context:
    def __init__(self, sysdict=Dict()):
        self.__sysdict = sysdict
        self.__rom_kana_rule_tree = compile_rom_kana_rule(rom_kana_rule)
        self.set_candidate_selector(CandidateSelectorBase())
        self.reset()
        self.activate_input_mode(INPUT_MODE_HIRAGANA)

    def set_candidate_selector(self, candidate_selector):
        self.__candidate_selector = candidate_selector

    def reset(self):
        # The rom-kana state is either None or a tuple (OUTPUT,
        # PENDING, TREE) where OUTPUT is a kana string, PENDING is a
        # string is in rom-kana conversion, and TREE is a subtree of
        # __ROM_KANA_RULE_TREE.
        self.__rom_kana_state = None
        self.__okuri_rom_kana_state = None

        self.__kana_kan_state = None
        self.conv_state = CONV_STATE_NONE
        self.clear_candidates()

    def __hiragana_to_katakana(self, kana):
        return kana             # XXX

    def __katakana_to_hiragana(self, kana):
        return kana             # XXX

    def activate_input_mode(self, input_mode):
        self.input_mode = input_mode
        if self.input_mode == INPUT_MODE_HIRAGANA or \
                self.input_mode == INPUT_MODE_KATAKANA:
            self.__rom_kana_state = (u'', u'', self.__rom_kana_rule_tree)

    def kakutei(self):
        input_mode = self.input_mode
        if self.__kana_kan_state:
            candidate = self.__kana_kan_state[1]
            if candidate:
                output = candidate[0]
                if self.__okuri_rom_kana_state:
                    output += self.__okuri_rom_kana_state[0]
            else:
                output = self.__rom_kana_state[0]
        else:
            output = self.__rom_kana_state[0]
        self.reset()
        self.activate_input_mode(input_mode)
        return output

    def append(self, key):
        keyval = key
        is_ctrl = keyval.startswith('ctrl+')
        if is_ctrl:
            keyval = keyval[5:]
        is_shift = keyval.startswith('shift+')
        if is_shift:
            keyval = keyval[6:]
        if is_shift:
            letter = keyval.upper()
        else:
            letter = keyval

        if key == 'ctrl+g':
            self.reset()
            return u''

        if self.conv_state == CONV_STATE_NONE:
            input_mode = \
                input_mode_transition_rule.get(key, dict()).get(self.input_mode)
            if input_mode is not None:
                self.reset()
                self.activate_input_mode(input_mode)
                return u''

            if self.input_mode == INPUT_MODE_LATIN:
                return letter
            elif self.input_mode == INPUT_MODE_WIDE_LATIN:
                return wide_latin_table[ord(letter)]

            if is_shift:
                self.conv_state = CONV_STATE_START

            self.__rom_kana_state = \
                self.__convert_rom_kana(keyval, self.__rom_kana_state)
            if self.conv_state == CONV_STATE_NONE and \
                    len(self.__rom_kana_state[1]) == 0:
                return self.kakutei()
            return u''

        elif self.conv_state == CONV_STATE_START:
            input_mode = \
                input_mode_transition_rule.get(key, dict()).get(self.input_mode)
            if self.input_mode == INPUT_MODE_HIRAGANA and \
                    input_mode == INPUT_MODE_KATAKANA:
                kana = self.__hiragana_to_katakana(skk.__rom_kana_state[0])
                self.kakutei()
                self.activate_input_mode(input_mode)
                return kana
            elif self.input_mode == INPUT_MODE_KATAKANA and \
                    input_mode == INPUT_MODE_HIRAGANA:
                kana = self.__katakana_to_hiragana(skk.__rom_kana_state[0])
                self.kakutei()
                self.activate_input_mode(input_mode)
                return kana
            elif input_mode is not None:
                output = self.kakutei()
                self.activate_input_mode(input_mode)
                return output

            # Start okuri-nasi conversion.
            if letter.isspace():
                self.conv_state = CONV_STATE_SELECT
                self.__rom_kana_state = self.__convert_nn(self.__rom_kana_state)
                self.__kana_kan_state = (self.__rom_kana_state[0], None)
                candidates = self.__sysdict.lookup(self.__kana_kan_state[0])
                self.__candidate_selector.set_candidates(candidates)
                self.next_candidate()
                return u''

            if is_shift and \
                    len(self.__rom_kana_state[1]) == 0 and \
                    not self.__okuri_rom_kana_state:
                self.__okuri_rom_kana_state = \
                    (u'', u'', self.__rom_kana_rule_tree)

            if self.__okuri_rom_kana_state:
                okuri = (self.__okuri_rom_kana_state[1] or keyval)[0]
                self.__okuri_rom_kana_state = \
                    self.__convert_rom_kana(keyval, \
                                            self.__okuri_rom_kana_state)

                # Start okuri-ari conversion.
                if len(self.__okuri_rom_kana_state[1]) == 0:
                    self.conv_state = CONV_STATE_SELECT
                    self.__kana_kan_state = \
                        (self.__rom_kana_state[0] + okuri, None)
                    candidates = \
                        self.__sysdict.lookup(self.__kana_kan_state[0], \
                                                  okuri=True)
                    self.__candidate_selector.set_candidates(candidates)
                    self.next_candidate()
                return u''

            self.__rom_kana_state = \
                self.__convert_rom_kana(keyval, self.__rom_kana_state)
            return u''

        elif self.conv_state == CONV_STATE_SELECT:
            if letter.isspace():
                self.next_candidate()
            elif key == 'x':
                self.previous_candidate()
            elif key == 'ctrl+j' or key == 'return':
                return self.kakutei()
            else:
                return self.kakutei() + self.append(key)
            return u''

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
        if self.__okuri_rom_kana_state:
            state = self.__delete_char_from_rom_kana_state(\
                self.__okuri_rom_kana_state)
            if state:
                self.__okuri_rom_kana_state = state
                return True
        state = self.__delete_char_from_rom_kana_state(self.__rom_kana_state)
        if state:
            self.__rom_kana_state = state
            return True
        return False

    def clear_candidates(self):
        self.__candidate_selector.set_candidates(list())
        self.__kana_kan_state = None
        
    def next_candidate(self):
        candidate = self.__candidate_selector.next_candidate()
        self.__kana_kan_state = (self.__kana_kan_state[0], candidate)
            
    def previous_candidate(self):
        self.__candidate = self.__candidate_selector.previous_candidate()
        self.__kana_kan_state = (self.__kana_kan_state[0], candidate)

    def preedit(self):
        if self.conv_state == CONV_STATE_NONE:
            if self.__rom_kana_state:
                return self.__rom_kana_state[1]
            return u''
        elif self.conv_state == CONV_STATE_START:
            if self.__okuri_rom_kana_state:
                return u'▽' + self.__rom_kana_state[0] + u'*' + \
                    self.__okuri_rom_kana_state[0] + \
                    self.__okuri_rom_kana_state[1]
            else:
                return u'▽' + self.__rom_kana_state[0] + \
                    self.__rom_kana_state[1]
        else:
            if self.__okuri_rom_kana_state:
                if self.__kana_kan_state:
                    candidate = self.__kana_kan_state[1]
                    if candidate:
                        return u'▼' + candidate[0] + \
                            self.__okuri_rom_kana_state[0]
                return u'▼' + self.__rom_kana_state[0] + \
                    self.__okuri_rom_kana_state[0]
            else:
                if self.__kana_kan_state:
                    candidate = self.__kana_kan_state[1]
                    if candidate:
                        return u'▼' + candidate[0]
                return u'▼' + self.__rom_kana_state[0]

    def __convert_nn(self, state):
        output, pending, tree = state
        if pending.endswith(u'n'):
            if self.input_mode == INPUT_MODE_HIRAGANA:
                output += u'ん'
            elif self.input_mode == INPUT_MODE_KATAKANA:
                output += u'ン'
            return (output, pending, tree)
        return state
        
    def __convert_rom_kana(self, letter, state):
        output, pending, tree = state
        if letter not in tree:
            output, pending, tree = self.__convert_nn(state)
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
            if self.input_mode == INPUT_MODE_HIRAGANA:
                output += hiragana
            else:
                output += katakana
        next_state = (output, u'', self.__rom_kana_rule_tree)
        if next_pending:
            for next_letter in next_pending:
                next_state = self.__convert_rom_kana(next_letter, next_state)
        return next_state
