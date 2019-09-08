import regex
from PIL import Image, ImageChops
consonants = "mnŋɲptkbdgfvθðl"
vowels = "aeiouɪʊʌæəʔ"
#dear linguists, i know the glottal stop isn't a vowel, but in order for the program to parse it like one
#since it's the only consonant to be put in the main segment of a syllable blocks (as it is only allowed between vowels
#and is the only time where a syllable block can actually be two syllables), i'm putting it here
character_translations = {
    "η" : "ŋ",
    "?" : "ʔ",
    "y" : "ɪ",
    "ø" : "ʊ",
    "à" : "ʌ",
    "á" : "ʌ",
    "ä" : "æ",
    "è" : "ə",
    "é" : "ə",

    "m" : "m",
    "n" : "n",
    "ń" : "ŋ",
    "ñ" : "ɲ",

    "s" : "θ",
    "z" : "ð",
    "'" : "ʔ"

}


ipa_file = {
    "m" : "m",
    "n" : "consonant_n",
    "ŋ" : "ng",
    "ɲ" : "ny",
    "p" : "p",
    "t" : "t",
    "k" : "k",
    "b" : "b",
    "d" : "d",
    "g" : "g",
    "f" : "f",
    "v" : "v",
    "θ" : "s",
    "ð" : "z",
    "l" : "l",
    "ʔ" : "glottal",
    "a" : "a",
    "e" : "e",
    "i" : "i",
    "o" : "o",
    "u" : "u",
    "ɪ" : "r",
    "ʊ" : "w",
    "ʌ" : "n",
    "æ" : "c",
    "ə" : "schwa"
}

widths = {
    "m" : 20,
    "n" : 20,
    "ŋ" : 20,
    "ɲ" : 20,
    "p" : 20,
    "t" : 10,
    "k" : 20,
    "b" : 20,
    "d" : 20,
    "g" : 20,
    "f" : 20,
    "v" : 20,
    "θ" : 20,
    "ð" : 20,
    "l" : 20,
    "ʔ" : 14,
    "a" : 40,
    "e" : 40,
    "i" : 13,
    "o" : 40,
    "u" : 40,
    "ɪ" : 40,
    "ʊ" : 40,
    "ʌ" : 40,
    "æ" : 40,
    "ə" : 40
}



def block_width(chars):
    return sum(calculate_width(i) for i in chars)

def calculate_width(char):
    return widths[char]

def split_word(word):
    syllables = word.split(".")
    syllables = [regex.split(r"([aeiouɪʊʌæəʔ]+)", syllable) for syllable in syllables]
    return syllables


def render_number(number):
    digits = []
    numberimage = Image.open("cmdimages/glyphs/digits.png")

    while number != 0:
        digits.append(number % 36)
        number = number//36
    if digits == []: digits = [0]
    digits = digits[::-1]

    image_width = 40 * len(digits)
    image = Image.new("RGB",(image_width,40),(255,255,255))

    pos = 0
    for d in digits:
        row = d // 6
        column = d % 6
        digit = numberimage.crop((40*column, 40*row, 40*(column+1), 40*(row+1)))
        image.paste(digit,(40*pos, 0))
        pos += 1

    return image


def render_word(word):
    syllables = split_word(word)
    #calculate the full width of the image
    image_width = 0
    for s in syllables:
        head_width = block_width(s[0])
        main_width = block_width(s[1])
        tail_width = block_width(s[2])
        image_width += max(head_width,tail_width,main_width)

    has_head = any(len(i[0]) != 0 for i in syllables)
    has_tail = any(len(i[2]) != 0 for i in syllables)
    head_y = 0
    main_y = 20
    tail_y = 60

    image_height = 40
    if has_head:
        image_height += 20
    else:
        main_y -= 20
        tail_y -= 20

    if has_tail: image_height += 20

    image = Image.new("RGB",(image_width,image_height),(255,255,255))

    total_offset = 0

    for s in syllables:
        h_width = block_width(s[0])
        m_width = block_width(s[1])
        t_width = block_width(s[2])

        s_width = max(h_width,t_width,m_width)

        head_offset = abs(h_width - s_width)//2
        main_offset = abs(m_width - s_width)//2
        tail_offset = abs(t_width - s_width)//2

        for n,char in enumerate(s[0]):
            glyph = Image.open("cmdimages/glyphs/glyph_" + ipa_file[char] + ".png")
            image.paste(glyph,(total_offset + block_width(s[0][:n]) + head_offset,head_y))

        for n,char in enumerate(s[1]):
            glyph = Image.open("cmdimages/glyphs/glyph_" + ipa_file[char] + ".png")
            image.paste(glyph,(total_offset + block_width(s[1][:n]) + main_offset,main_y))

        for n,char in enumerate(s[2]):
            glyph = Image.open("cmdimages/glyphs/glyph_" + ipa_file[char] + ".png")
            image.paste(glyph,(total_offset + block_width(s[2][:n]) + tail_offset,tail_y))

        total_offset += s_width
        #image.save(word + ".png")
    return image

def render_line(words):
    words = words.split(" ")
    images = [render_number(int(w)) if w.isdigit() else render_word(w) for w in words]

    full_width = sum([i.size[0] for i in images]) + 40*(len(images)-1)
    full_height = max([i.size[1] for i in images])

    image = Image.new("RGB",(full_width,full_height),(255,255,255))

    total_offset = 0
    for i in images:
        height_offset = (full_height - i.size[1])//2
        image.paste(i,(total_offset,height_offset))
        total_offset += 40 + i.size[0]


    return image



def render(text):
    lines = text.splitlines()
    images = [render_line(l) for l in lines]
    if len(images) == 1: return images[0]
    width = max(i.size[0] for i in images)
    height = sum(i.size[1] for i in images)

    image = Image.new("RGB",(width,height),(255,255,255))
    total_offset = 0
    for i in images:
        image.paste(i,(0,total_offset))
        total_offset += i.size[1]
    return image
