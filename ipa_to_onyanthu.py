import regex
from PIL import Image
consonants = "mnŋɲptkbdgfvθðl"
vowels = "aeiouɪʊʌæəʔ"
#dear linguists, i know the glottal stop isn't a vowel, but in order for the program to parse it like one
#since it's the only consonant to be put in the main segment of a syllable blocks (as it is only allowed between vowels
#and is the only time where a syllable block can actually be two syllables), i'm putting it here
character_translations = {
    "η" : "ŋ",
    "?" : "ʔ"
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

def split_word(word):
    syllables = word.split(".")
    syllables = [regex.split(r"([aeiouɪʊʌæəʔ]+)", syllable) for syllable in syllables]
    return syllables

def render_word(word):
    syllables = split_word(word)
    #calculate the full width of the image
    image_width = 0
    for s in syllables:
        head_width = 20 * len(s[0])
        main_width = 40 * len(s[1])
        tail_width = 20 * len(s[2])
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
        h_width = 20 * len(s[0])
        m_width = 40 * len(s[1])
        t_width = 20 * len(s[2])

        s_width = max(h_width,t_width,m_width)

        head_offset = abs(h_width - s_width)//2
        main_offset = abs(m_width - s_width)//2
        tail_offset = abs(t_width - s_width)//2

        for n,char in enumerate(s[0]):
            glyph = Image.open("glyphs/glyph_" + ipa_file[char] + ".png")
            image.paste(glyph,(total_offset + (20*n) + head_offset,head_y))

        for n,char in enumerate(s[1]):
            glyph = Image.open("glyphs/glyph_" + ipa_file[char] + ".png")
            if char != "":
                image.paste(glyph,(total_offset + (40*n) + main_offset,main_y))
            else:
                image.paste(glyph, (total_offset + (40 * n) + main_offset + 10, main_y + 10))

        for n,char in enumerate(s[2]):
            glyph = Image.open("glyphs/glyph_" + ipa_file[char] + ".png")
            image.paste(glyph,(total_offset + (20*n) + tail_offset,tail_y))

        total_offset += s_width
        #image.save(word + ".png")
    return image

def render(words):
    words = words.split(" ")
    images = [render_word(w) for w in words]

    full_width = sum([i.size[0] for i in images]) + 40*(len(images)-1)
    full_height = max([i.size[1] for i in images])

    image = Image.new("RGB",(full_width,full_height),(255,255,255))

    total_offset = 0
    for i in images:
        height_offset = (full_height - i.size[1])//2
        image.paste(i,(total_offset,height_offset))
        total_offset += 40 + i.size[0]


    return image
