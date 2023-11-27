__author__ = "Cao Mạnh Hải"

import string
import unicodedata
import unidecode
import re


'''
17 phụ âm đơn: b, c, d, đ, g, h, k, l, m, n, p, q, r, s, t, v, x
10 phụ âm ghép:  ch, gh, gi, kh, ng, ngh, nh, th, tr, qu
https://monkey.edu.vn/ba-me-can-biet/giao-duc/hoc-tieng-viet/phu-am-trong-bang-chu-cai-tieng-viet

Tiếng Việt có bao nhiêu nguyên âm đơn: a, ă, â, e, ê, i/y, o, ô, ơ, u, ư
Tiếng Việt có bao nhiêu nguyên âm đôi: AI, AO, AU, ÂU, AY, ÂY, EO, ÊU, IA, IÊ/YÊ, IU, OA, OĂ, OE, OI, ÔI, ƠI, 
                                       OO, ÔÔ, UA, UĂ, UÂ, ƯA, UÊ, UI, ƯI,UO, UÔ, UƠ, ƯƠ, ƯU, UY
Tiếng Việt có bao nhiêu nguyên âm ba: IÊU/YÊU, OAI, OAO, OAY, OEO, UAO, UÂY, UÔI, ƯƠI, ƯƠU, UYA, UYÊ, UYU
Những nguyên âm bắt buộc phải có nguyên âm hoặc phụ âm cuối: Â, IÊ,UÂ,UÔ,ƯƠ,YÊ
Những nguyên âm bắt buộc phải có phụ âm cuối: Ă, OĂ, OO, ÔÔ, UĂ, UYÊ
Có 4 nguyên âm ghép có thể đứng một mình, có thể thêm âm đầu, âm cuối hoặc cả đầu lẫn cuối: OA, OE, UÊ, UY
29 nguyên âm ghép không được thêm phần âm cuối: AI, AO, AU, ÂU, AY, ÂY, EO, ÊU, IA, IÊU/YÊU, IU, OI, ÔI, ƠI, OAI, OAO, 
                                                OAY, OEO, ƯA, UI, ƯI, ƯU, UƠ, UAI, UÂY, UÔI, ƯƠI, ƯƠU, UYA, UYU
                                                
https://gotiengviet.com.vn/bang-chu-cai-tieng-viet-co-bao-nhieu-nguyen-am/
'''


class VNMarkNormalization(object):
    def __init__(self):
        self.accent_norm = {
            'à': 'à',
            'ặ': 'ặ',
            'á': 'á',
            'ầ': 'ầ',
            'ề': 'ề',
            'ế': 'ế',
            'ũ': 'ũ',
            'a`': 'à',
            'ă`': "ằ",
            'â`': "ầ",
            "e`": "è",
            "ê`": "ề",
            "i`": "ì",
            "o`": "ò",
            "ô`": "ồ",
            "ơ`": "ờ",
            "u`": "ù",
            "ư`": "ừ",
            "a'": "á",
            "ă'": 'ắ',
            "â'": "ấ",
            "e'": "é",
            "ê'": "ế",
            "i'": "í",
            "o'": "ó",
            "ô'": "ố",
            "ơ'": "ớ",
            "u'": "ú",
            "ư'": "ứ",
            'ϲ': 'c'
        }

        self.uChar = ["u", "ú", "ù", "ũ", "ủ", "ụ"]
        self.iChar = ["i", "í", "ì", "ĩ", "ỉ", "ị"]

        # Nguyên âm
        self.vowels = [
            "a", "á", "à", "ả", "ã", "ạ",
            "ắ", "ặ", "ă", "ằ", "ẳ", "ẵ",
            "ậ", "â", "ấ", "ầ", "ẩ", "ẫ",
            "u", "y", "e", "o", "i",
            "é", "è", "ẻ", "ẽ", "ẹ",
            "ê", "ế", "ề", "ể", "ễ", "ệ",
            "í", "ì", "ỉ", "ĩ", "ị",
            "ó", "ò", "ỏ", "õ", "ọ",
            "ô", "ố", "ồ", "ổ", "ỗ", "ộ",
            "ơ", "ớ", "ờ", "ở", "ỡ", "ợ",
            "ú", "ù", "ủ", "ụ", "ũ",
            "ư", "ứ", "ữ", "ự", "ừ", "ử",
            "ý", "ỳ", "ỷ", "ỵ", "ỹ"
        ]

        # Phụ âm
        self.consonants = [
            "b", "c", "d", "đ", "g", "h", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "x"
        ]

        # Dấu
        self.marks = [
            "á", "à", "ả", "ã", "ạ",
            "ậ", "ấ", "ầ", "ẩ", "ẫ",
            "ắ", "ặ", "ằ", "ẳ", "ẵ",
            "é", "è", "ẻ", "ẽ", "ẹ",
            "ế", "ề", "ể", "ễ", "ệ",
            "í", "ì", "ỉ", "ĩ", "ị",
            "ó", "ò", "ỏ", "õ", "ọ",
            "ố", "ồ", "ổ", "ỗ", "ộ",
            "ớ", "ờ", "ở", "ỡ", "ợ",
            "ú", "ù", "ủ", "ụ", "ũ",
            "ứ", "ữ", "ự", "ừ", "ử",
            "ý", "ỳ", "ỷ", "ỵ", "ỹ"
        ]

        # Dấu sắc
        self.acute = ["á", "ấ", "ắ", "é", "ế", "í", "ó", "ố", "ớ", "ú", "ứ", "ý"]
        # Dấu huyền
        self.graveAccent = ["à", "ầ", "ằ", "è", "ề", "ì", "ò", "ồ", "ờ", "ù", "ừ", "ỳ"]
        # Dấu ngã
        self.tilde = ["ã", "ẫ", "ẵ", "ẽ", "ễ", "ĩ", "õ", "ỗ", "ỡ", "ũ", "ữ", "ỹ"]
        # Dấu hỏi
        self.questionMark = ["ả", "ẩ", "ẳ", "ẻ", "ể", "ỉ", "ỏ", "ổ", "ở", "ủ", "ử", "ỷ"]
        # Dấu nặng
        self.dot = ["ạ", "ậ", "ặ", "ẹ", "ệ", "ị", "ọ", "ộ", "ợ", "ụ", "ự", "ỵ"]

        self.exception1 = ["u", "ư", "ú", "ứ", "ù", "ừ", "ủ", "ử", "ũ", "ữ", "ụ", "ự"]
        self.exception2 = ["o", "ơ", "ó", "ớ", "ò", "ờ", "ỏ", "ở", "õ", "ỡ", "ọ", "ợ"]
        self.exception3 = ["ê", "ế", "ề", "ể", "ễ", "ệ", "ơ", "ớ", "ờ", "ở", "ỡ", "ợ"]

        self.punctuation = string.punctuation

        self.acuteDict = {
            "a": "á", "â": "ấ", "ă": "ắ",
            "e": "é", "ê": "ế",
            "i": "í",
            "o": "ó", "ô": "ố", "ơ": "ớ",
            "u": "ú", "ư": "ứ",
            "y": "ý"
        }
        self.acuteInverseDict = {}
        for item in self.acuteDict:
            self.acuteInverseDict[self.acuteDict[item]] = item

        self.graveAccentDict = {
            "a": "à", "â": "ầ", "ă": "ằ",
            "e": "è", "ê": "ề",
            "i": "ì",
            "o": "ò", "ô": "ồ", "ơ": "ờ",
            "u": "ù",
            "ư": "ừ",
            "y": "ỳ"
        }
        self.graveAccentInverseDict = {}
        for item in self.graveAccentDict:
            self.graveAccentInverseDict[self.graveAccentDict[item]] = item

        self.tildeDict = {
            "a": "ã", "â": "ẫ", "ă": "ẵ",
            "e": "ẽ", "ê": "ễ",
            "i": "ĩ",
            "o": "õ", "ô": "ỗ", "ơ": "ỡ",
            "u": "ũ",
            "ư": "ữ",
            "y": "ỹ"
        }
        self.tildeInverseDict = {}
        for item in self.tildeDict:
            self.tildeInverseDict[self.tildeDict[item]] = item

        self.questionMarkDict = {
            "a": "ả", "â": "ẩ", "ă": "ẳ",
            "e": "ẻ", "ê": "ể",
            "i": "ỉ",
            "o": "ỏ", "ô": "ổ", "ơ": "ở",
            "u": "ủ",
            "ư": "ử",
            "y": "ỷ"
        }
        self.questionMarkInverseDict = {}
        for item in self.questionMarkDict:
            self.questionMarkInverseDict[self.questionMarkDict[item]] = item

        self.dotDict = {
            "a": "ạ", "â": "ậ", "ă": "ặ",
            "e": "ẹ", "ê": "ệ",
            "i": "ị",
            "o": "ọ", "ô": "ộ", "ơ": "ợ",
            "u": "ụ",
            "ư": "ự",
            "y": "ỵ"
        }
        self.dotInverseDict = {}
        for item in self.dotDict:
            self.dotInverseDict[self.dotDict[item]] = item

        self.exceptionDict1 = {
            "u": "ư", "ú": "ứ", "ù": "ừ", "ủ": "ử", "ũ": "ữ", "ụ": "ự",
            "o": "ơ", "ó": "ớ", "ò": "ờ", "ỏ": "ở", "õ": "ỡ", "ọ": "ợ"
        }

        self.exceptionDict2 = {
            "oo": "ô",
            "oó": "ố",
            "óo": "ố",
            "oò": "ồ",
            "òo": "ồ",
            "oỏ": "ổ",
            "ỏo": "ổ",
            "oõ": "ỗ",
            "õo": "ỗ",
            "oọ": "ộ",
            "ọo": "ộ"
        }

        self.exceptionDict3 = {
            "ee": "ê",
            "eé": "ế",
            "ée": "ế",
            "eè": "ề",
            "èe": "ề",
            "eẻ": "ể",
            "ẻe": "ể",
            "eẽ": "ễ",
            "ẽe": "ễ",
            "eẹ": "ệ",
            "ẹe": "ệ"
        }

        self.exceptionDict4 = {
            "aa": "â",
            "aá": "ấ",
            "áa": "ấ",
            "àa": "ầ",
            "aà": "ầ",
            "ảa": "ẩ",
            "aả": "ẩ",
            "ãa": "ẫ",
            "aã": "ẫ",
            "ạa": "ậ",
            "aạ": "ậ"
        }

        self.ooDict = {
            "ó": "ố",
            "ò": "ồ",
            "ỏ": "ổ",
            "õ": "ỗ",
            "ọ": "ộ"
        }

        self.eeDict = {
            "é": "ế",
            "è": "ề",
            "ẻ": "ể",
            "ẽ": "ễ",
            "ẹ": "ệ"
        }

        self.aaDict = {
            "á": "ấ",
            "à": "ầ",
            "ả": "ẩ",
            "ã": "ẫ",
            "ạ": "ậ"
        }

        self.awDict = {
            "á": "ắ",
            "à": "ằ",
            "ả": "ẳ",
            "ã": "ẵ",
            "ạ": "ặ",
            "a": "ă"
        }

        self.specialWord = [
            "google", "batoong", "bazooka", "bloom", "book", "books", "facebook"
                                                                      "boots", "brook", "brooks", "choose", "clooney",
            "cooke", "cookie", "cookies", "cooking",
            "cool", "cooper", "daewoo", "door", "doosan", "food", "foody", "foote", "goodbye", "good", "hoocmon",
            "hood", "hoop", "indoor", "joon", "look", "macbook", "moon", "moore", "mooz", "netbook",
            "poodle", "poo", "room", "rooney", "school", "shampoo", "shoo", "shoot", "sook", "soon",
            "soo", "tattoo", "too", "wood", "woods", "woody", "woo", "yahoo", "yoo", "yoona", "yoon", "zoom",
            "kazuo", "mitsuo", "quota", "uoat", "yasuo", "youtuber", "muoio", "quoin"
        ]

        self.viSpecialWord = [
            'thuở', 'quới', 'xoong', 'boong', 'moong', 'quơ', 'huơ', 'thoong', 'loong', 'quở', 'quơn', 'toong', 'coong',
            'noong', 'quờ', 'choong', 'hoong', 'roong', 'quớ', 'oong', 'goong', 'soong', 'phoong', 'nhoong', 'doong',
            'quớt', 'khoong', 'đoòng', 'hoóc', 'moóc', 'voọc', 'soóc', 'coóng', 'voóc', 'moọc', 'choọng', 'poọng',
            'loóng', 'soọng', 'khoòng', 'loỏng', 'xoọng', 'phoóc', 'goòng', 'soọc', 'troóc', 'choóng', 'voòng', 'noọc',
            'roóng', 'poọc', 'coỏng', 'roòng', 'noọng', 'coóc', 'toòng', 'nhoóng', 'boóc', 'đoóc', 'doóc', 'gioóc',
            'goóc',
            'oóc', 'phoóc', 'poóc', 'roóc', 'moon', 'thoọng', 'toóc', 'troong', 'voo', 'xoòng', 'noóc', 'huot', 'suon',
            'thuot', 'boo', 'boom', 'boon', 'boop', 'boot', 'choo', 'choon', 'coo', 'coon', 'coop', 'coot', 'doo',
            'doom',
            'goo', 'goon', 'goop', 'hoo', 'hoon', 'hoot', 'khoo', 'loo', 'loom', 'loon', 'loop', 'loot', 'moo', 'moot',
            'noon', 'oop', 'poon', 'poop', 'roop', 'root', 'soot', 'toon', 'toot', 'troon', 'troop'
        ]

        self.engWord = [
            "hoop", "poo", "room", "soon", "soo", "too", "uoat", "muoio", "quoin"
        ]

        self.non_printable_character = ['', '', '﻿', ' ', "­", "​", '\u200b', '\u200e', '\u202a', '&nbsp;',
                                        '&lt;', '&gt', '\uf644', '\uf624', '\x08t', "\uf602", "\uf614", "\uf622",
                                        '\uf633', '\U0001f972', '\uf612', '\uf60c', '\uf61d', '\uf0e0', '', '',
                                        '', '', '']
        self.eng_dict = None

        self.special_characters = {
            "ð": "đ",
            "½": "1/2",
            "ç": "c",
            "¾": "3/4",
            "Ð": "Đ",
            "ē": "ẽ",
            "，": ",",
            "’": "'",
            "“": "\"",
            "…": "...",
            "–": "-",
            "—": "-",
            "？": "?",
            "♫": "",
            "®": "",
            "♪": "",
            "«": "",
            "”": "\"",
            "❤": "",
            "❓": "?",
            "❇": "*",
            "✳": "*",
            "☎": "",
            "⭕": "",
            "‘": "'",
            "•": "",
            "↑": "",
            "": "",
            "": "",
            "¹": "",
            "☞": "",
            "": "",
            "═": "=",
            "★": "*",
            "►": "",
            "✦": "",
            "✮": "",
            "✪": "",
            "✩": "",
            "♡": "",
            "✥": "",
            "｡": "",
            "～": "",
            "ˆ": "",
            "д": "",
            "̶": "-",
            "»": "",
            "̳": "_",
            "√": "",
            "±": "",
            "͡": "",
            "°": "",
            "͜": "",
            "ʖ": "",
            "︵": "",
            "✿": "",
            "๖ۣۜ": "",
            "❆": "",
            "●": "",
            "─": "-",
            "·": "",
            "кыонг": "",
            "хунг": "",
            "нгуен": "",
            "٩": "",
            "◕": "",
            "‿": "",
            "۶": "",
            "》": "",
            "・": "",
            "♬": "",
            "ö": "o",
            "²": "",
            "×": "",
            "τ": "",
            "「": "",
            "」": "",
            "（": "",
            "ω": "",
            "！": "",
            "）": "",
            "æ": "",
            "ß": ""
        }

    @staticmethod
    def removeAccent(text):
        return unidecode.unidecode(text)

    def wordPreprocess(self, word):
        word = self.remove_non_printable_character(word)
        word = unicodedata.normalize('NFC', word)

        for c in word:
            if c in self.accent_norm:
                word = word.replace(c, self.accent_norm[c])

        return word

    def isNumber(self, word):
        word = self.wordPreprocess(word)

        if not word[-1].isnumeric():
            return False

        if not word[0].isnumeric():
            if word[0] != "-":
                return False
            else:
                if len(word) > 1:
                    if not word[1].isnumeric():
                        return False
                else:
                    return False

        for c in word[:-1]:
            if not c.isnumeric() and c not in [".", ",", "/", "-"]:
                return False

        return True

    def isVietnamese(self, word, isCorrect=False, fullRule=False):
        word = self.wordPreprocess(word)

        if isCorrect:
            for c in word:
                if self.findAccent(c) != "unMark":
                    return True

        # y không đi với 1 phụ âm ở liền sau (trừ phụ âm t, ch, nh, p): hym (not huyên); exception: xuỵt
        # word_tmp = self.removeAccent(word)
        # y_index = word_tmp.find("y")
        # del word_tmp
        #
        # if y_index != -1 and y_index != len(word)-1:
        #     if self.isConsonant(word[y_index + 1]) and word[y_index + 1] != "t":
        #         return False
        # del y_index

        # Từ tiếng Việt có ít nhất 1 nguyên âm
        isVowel = False
        for w in word:
            if self.isVowel(w):
                isVowel = True
                break

        if not isVowel:
            return False

        if fullRule:
            # Từ tiếng Việt có nhiều nhất 3 nguyên âm
            count = 0
            for w in word:
                if self.isVowel(w):
                    count += 1

            if count > 3:
                return False

        # w, f, j, z không có trong từ tiếng Việt
        if "w" in word or "f" in word or "j" in word or "z" in word:
            return False

        # Từ tiếng việt không có các phụ âm Q, R, S, D, Đ, K, L, X, V, B ở cuối
        if word[-1] in "qrsdđklxvb":
            return False

        if len(word) > 2:
            # Từ tiếng việt nếu có 2 phụ âm đứng đầu thì bắt buộc phải là: TH, TR, PH, KH, NH, CH, GH, NG
            check = ['th', 'tr', 'ph', 'kh', 'nh', 'ch', 'gh', 'ng']
            if self.isConsonant(word[0]) and self.isConsonant(word[1]):
                if word[:2] not in check:
                    return False

            # Từ tiếng việt nếu có 2 phụ âm đứng cuối thì bắt buộc phải là: NH, NG, CH
            check = ['nh', 'ng', 'ch']
            if self.isConsonant(word[-1]) and self.isConsonant(word[-2]):
                if word[len(word) - 2:] not in check:
                    return False

        # Từ tiếng Việt có tối đa 5 phụ âm
        count = 0
        for c in word:
            if self.isConsonant(c):
                count += 1

        if count > 5:
            return False

        # Một từ chỉ có thể có nhiều nhất 1 cặp phụ âm - nguyên âm - phụ âm
        index = 0
        first = -1
        if self.isConsonant(word[0]):
            first = 1
            index = -1
        if self.isVowel(word[0]):
            first = 0

        if first == -1:
            return False
        else:
            for c in word[1:]:
                tmp = 0
                if self.isConsonant(c):
                    tmp = 1

                if tmp != first:
                    first = tmp
                    index += 1

        if index > 1:
            return False

        # Từ tiếng Việt không chứa các cặp ký tự: och, ooe, ooi, oy, oh, og, thr, ko, yo, uo
        if "och" in word or "ooe" in word or "ooi" in word or "oy" in word or "oh" in word or "og" in word \
                or "thr" in word or "ko" in word or "yo" in word or "uo" == word[len(word) - 2:]:
            return False

        return True

    def isEnglish(self, word, path_to_dict="/home/haicm3nxt/PycharmProjects/data-processing/vn/mark/english_dict.txt"):
        word = self.wordPreprocess(word)

        if self.eng_dict is None:
            import os
            if not os.path.isfile(path_to_dict) or not path_to_dict.endswith(".txt"):
                raise Exception('Missing English dictionary!!!')

            # use dict to make faster
            self.eng_dict = {}
            with open(path_to_dict, 'r') as f:
                for line in f:
                    line = line.strip()

                    if line:
                        self.eng_dict[line] = 0

        if word.lower() in self.eng_dict:
            return True

        return False

    def findAccent(self, vowel):
        if vowel in self.acute:
            return "acute"
        elif vowel in self.graveAccent:
            return "graveAccent"
        elif vowel in self.tilde:
            return "tilde"
        elif vowel in self.questionMark:
            return "questionMark"
        elif vowel in self.dot:
            return "dot"
        else:
            return "unMark"

    def isVowel(self, character):
        if character in self.vowels:
            return True

        return False

    def isConsonant(self, character):
        if character in self.consonants:
            return True

        return False

    def countVowel(self, word):
        count = 0
        for c in word:
            if self.isVowel(c):
                count += 1

        return count

    def normalize_(self, word):
        # not Vietnamese language
        if len(word) > 8:
            return word

        # two special cases
        for item in self.viSpecialWord:
            if item == word:
                return word

        if word[0] != "q":
            condition1 = False
            condition2 = False
            u_index = -1
            o_index = -1

            for i, c in enumerate(word):
                if c in self.exception1:
                    condition1 = True

                    if u_index == -1:
                        u_index = i
                    else:
                        u_index = -2
                        break
                if c in self.exception2:
                    condition2 = True

                    if o_index == -1:
                        o_index = i
                    else:
                        o_index = -2
                        break

            if condition1 and condition2 and u_index > -1 and o_index > -1 and ((o_index - u_index) == 1):
                for key in self.exceptionDict1:
                    word = word.replace(key, self.exceptionDict1[key])

        for key in self.exceptionDict2:
            word = word.replace(key, self.exceptionDict2[key])

        return word

    def isNormalize(self, word):
        if self.countVowel(word) < 2 and word[-1] != "w":
            return False

        for c in word:
            if self.isVowel(c):
                if c in self.marks:
                    return True

        return False

    def convert(self, character, mark):
        if mark == "acute":
            return self.acuteDict[character]
        elif mark == "graveAccent":
            return self.graveAccentDict[character]
        elif mark == "tilde":
            return self.tildeDict[character]
        elif mark == "questionMark":
            return self.questionMarkDict[character]
        elif mark == "dot":
            return self.dotDict[character]
        else:
            return str(character)

    def convertInverse(self, character, mark):
        if mark == "acute":
            return self.acuteInverseDict[character]
        elif mark == "graveAccent":
            return self.graveAccentInverseDict[character]
        elif mark == "tilde":
            return self.tildeInverseDict[character]
        elif mark == "questionMark":
            return self.questionMarkInverseDict[character]
        elif mark == "dot":
            return self.dotInverseDict[character]
        else:
            return str(character)

    def normalize__(self, word):
        # Thanh ngang
        mark = "unMark"

        for c in word:
            if self.isVowel(c):
                mark = self.findAccent(c)

                if mark != "unMark":
                    break

        # hiẹpe -> hiệp; hòmo -> hồm; hàma -> hầm; hùomw -> hườm; hàmw -> hằm
        if mark != "unMark":
            # Kết thúc bằng e
            if word[-1] == "e":
                for ee in self.eeDict:
                    if ee in word[:-1]:
                        word = word[:-1].replace(ee, self.eeDict[ee])
                        break

            # Kết thúc bằng o
            if word[-1] == "o":
                for oo in self.ooDict:
                    if oo in word[:-1]:
                        word = word[:-1].replace(oo, self.ooDict[oo])
                        break

            # Kết thúc bằng a
            if word[-1] == "a":
                for aa in self.aaDict:
                    if aa in word[:-1]:
                        word = word[:-1].replace(aa, self.aaDict[aa])
                        break

            # Kết thúc bằng w
            if word[-1] == "w":
                first = True
                for c in self.exceptionDict1:
                    # print (c, word)
                    if c in word[:-1]:
                        if first:
                            word = word[:-1]
                            first = False
                        word = word.replace(c, self.exceptionDict1[c])

                for c in self.awDict:
                    if c in word[:-1]:
                        if first:
                            word = word[:-1]
                            first = False
                        word = word.replace(c, self.awDict[c])

                if word[-1] == "w":
                    word = word[:-1]

        first_vowel = True
        new_word = ""
        second_vowel = False
        last_vowel = self.countVowel(word)

        # Nếu từ kết thúc bằng ê, ơ => dấu đánh vào ê, ơ
        if word[-1] in self.exception3:
            for c in word:
                if self.isVowel(c):
                    if last_vowel != 1:
                        if c in self.marks:
                            new_word += self.convertInverse(c, self.findAccent(c))
                        else:
                            new_word += c

                        last_vowel -= 1
                    else:
                        if c in self.marks:
                            new_word += c
                        else:
                            new_word += self.convert(c, mark)

                else:
                    new_word += c

            return new_word

        # print (word)
        # Nếu từ có 3 nguyên âm và kết thúc bằng 1 nguyên âm => dấu đánh và nguyên âm thứ 2
        # Nếu từ bắt đầu bằng "qu" hoặc "gi" và có 2 nguyên âm => dấu đánh vào nguyên âm thứ 2
        if (last_vowel == 3 and self.isVowel(word[-1])) or \
                ((word[0] == "q" and word[1] in self.uChar) or
                 (word[0] == "g" and word[1] in self.iChar)) and \
                last_vowel == 2:
            for c in word:
                if self.isVowel(c):
                    if first_vowel:
                        if c in self.marks:
                            new_word += self.convertInverse(c, self.findAccent(c))
                        else:
                            new_word += c

                        first_vowel = False
                        second_vowel = True
                    else:
                        if second_vowel:
                            if c in self.marks:
                                new_word += c
                            else:
                                new_word += self.convert(c, mark)

                            second_vowel = False
                        else:
                            if c in self.marks:
                                new_word += self.convertInverse(c, self.findAccent(c))
                            else:
                                new_word += c
                else:
                    new_word += c

            return new_word

        # Nếu từ kết thúc bằng 1 nguyên âm => dấu đánh vào nguyên âm đầu tiên
        if self.isVowel(word[-1]):
            for c in word:
                if self.isVowel(c):
                    if first_vowel:
                        if c in self.marks:
                            new_word += c
                        else:
                            new_word += self.convert(c, mark)

                        first_vowel = False
                    else:
                        if c in self.marks:
                            new_word += self.convertInverse(c, self.findAccent(c))
                        else:
                            new_word += c

                else:
                    new_word += c

            return new_word

        # Nếu từ kết thúc bằng 1 phụ âm => dấu đánh vào nguyên âm cuối cùng
        if self.isConsonant(word[-1]):
            for c in word:
                if self.isVowel(c):
                    if last_vowel != 1:
                        if c in self.marks:
                            new_word += self.convertInverse(c, self.findAccent(c))
                        else:
                            new_word += c

                        last_vowel -= 1
                    else:
                        if c in self.marks:
                            new_word += c
                        else:
                            new_word += self.convert(c, mark)
                else:
                    new_word += c

            return new_word

        return word

    def remove_non_printable_character(self, text):
        for non_printable in self.non_printable_character:
            text = text.replace(non_printable, "")

        return text

    def normalizeWord(self, word, useViDetect=False, isCorrect=False, keep_origin=False):
        # word = self.remove_non_printable_character(word)
        # word = unicodedata.normalize('NFC', word)
        #
        # for c in word:
        #     if c in self.accent_norm:
        #         word = word.replace(c, self.accent_norm[c])
        word = self.wordPreprocess(word)

        if useViDetect:
            if not self.isVietnamese(word.lower(), isCorrect):
                return word

        haicm = []
        if keep_origin:
            wordUp = word.upper()
            haicm = []
            for idx, c in enumerate(word):
                if c == wordUp[idx]:
                    haicm.append(1)
                else:
                    haicm.append(0)

            del wordUp

        word = word.lower()
        # special words
        if useViDetect:
            for w in self.engWord:
                if word == w:
                    return word
        else:
            for w in self.specialWord:
                if word == w:
                    return word

        word = self.normalize_(word)
        # print (word)
        if self.isNormalize(word):
            word = self.normalize__(word)

        # print (word)
        if keep_origin:
            newWord = ""
            for idx, item in enumerate(haicm[:len(word)]):
                if item == 0:
                    newWord += word[idx]
                else:
                    newWord += word[idx].upper()

            del word
            del haicm

            return newWord

        del haicm
        return word

    def specialCharacterNormalize(self, sentence):
        for item in self.special_characters:
            if item in sentence:
                sentence = sentence.replace(item, self.special_characters[item])

        return sentence

    def normalizeSentence(self, sentence, useViDetect=False, isCorrect=False,
                          debug=False, keep_origin=False, special_norm=True):
        if special_norm:
            sentence = self.specialCharacterNormalize(sentence)

        tmp = []
        for word in sentence.split():
            if "https" in word or "http" in word or "/" == word[0]:
                tmp.append(word)
                continue

            is_keep_origin = True
            for c in word:
                if not c.isnumeric() and (c not in [":", "%", "-", ".", ",", "/", "'", "\""]):
                    is_keep_origin = False
                    break

            if is_keep_origin:
                tmp.append(word)
                continue

            is_split = True
            is_more_punc = 0
            if word[0].isnumeric():
                h = 1
                for c in word[1:]:
                    if c in [".", ","]:
                        is_more_punc += 1
                    if not c.isnumeric() and c not in [".", ","]:
                        break

                    h += 1

                if h == len(word):
                    is_split = False

            if is_split:
                for punc in self.punctuation:
                    word = word.replace(punc, " " + punc + " ")

                replace_word = ""
                if is_more_punc:
                    is_first = 1
                    for c in word:
                        if c in [",", "."] and is_first == 1:
                            replace_word = replace_word[:-1] + c
                            is_first += 1
                        else:
                            if is_first == 2:
                                is_first = 3
                                if c == " ":
                                    continue

                            replace_word += c

                    tmp += replace_word.split()
                else:
                    tmp += word.split()
            else:
                tmp.append(word)

        sentence = " ".join(tmp)

        new_sentence = ""
        tmp = sentence.split()

        for word in tmp:
            new_word = self.normalizeWord(word, useViDetect, isCorrect, keep_origin)
            if debug:
                if word != new_word:
                    print(word + ": " + new_word)
            new_sentence += new_word + " "

        new_sentence = new_sentence[:-1]
        for number in "0123456789":
            new_sentence = new_sentence.replace(number + ", ", number + " , ")
            new_sentence = new_sentence.replace(number + ". ", number + " . ")

        new_sentence = re.sub(r'(\d) , (\d)', r'\1,\2', new_sentence)

        if len(new_sentence) > 5:
            if new_sentence[-1] == ".":
                new_sentence = new_sentence[:-1] + " ."

        return new_sentence
            # .replace("< ", "<")
            # .replace(" >", ">").replace("( ", "(").replace(" )", ")").\
            # replace(" | ", "|").replace(". *", ".*")


if __name__ == "__main__":
    vnMarkNormalize = VNMarkNormalization()

    text = "hoá 124. kgjn kadsfm 124.515"
    print (vnMarkNormalize.normalizeSentence(text.lower(), isCorrect=False, useViDetect=True))