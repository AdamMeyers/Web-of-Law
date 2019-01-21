#! /usr/bin/python3
import codecs 
import json
import unicodedata
import os
from wol_utilities import *

cp1252_to_utf8_chars_decoding_table = {
    '0x80': unicodedata.lookup("EURO SIGN"),            
    '0x81': '',
    '0x82': unicodedata.lookup("SINGLE LOW-9 QUOTATION MARK"),
    '0x83': unicodedata.lookup("LATIN SMALL LETTER F WITH HOOK"),
    '0x84': unicodedata.lookup("DOUBLE LOW-9 QUOTATION MARK"),
    '0x85': unicodedata.lookup("HORIZONTAL ELLIPSIS"),
    '0x86': unicodedata.lookup("DAGGER"),
    '0x87': unicodedata.lookup("DOUBLE DAGGER"), 
    '0x88': unicodedata.lookup("MODIFIER LETTER CIRCUMFLEX ACCENT"),            
    '0x89': unicodedata.lookup("PER MILLE SIGN"),  
    '0x8A': unicodedata.lookup("LATIN CAPITAL LETTER S WITH CARON"), 
    '0x8B': unicodedata.lookup("SINGLE LEFT-POINTING ANGLE QUOTATION MARK"),  
    '0x8C': unicodedata.lookup("LATIN CAPITAL LIGATURE OE"),            
    '0x8D': '', 
    '0x8E': unicodedata.lookup("LATIN CAPITAL LETTER Z WITH CARON"), 
    '0x8F': '',
    '0x90': '',
    '0x91': unicodedata.lookup("LEFT SINGLE QUOTATION MARK"),
    '0x92': unicodedata.lookup("RIGHT SINGLE QUOTATION MARK"),   
    '0x93': unicodedata.lookup("LEFT DOUBLE QUOTATION MARK"),      
    '0x94': unicodedata.lookup("RIGHT DOUBLE QUOTATION MARK"),    
    '0x95': unicodedata.lookup("BULLET"),     
    '0x96': unicodedata.lookup("EN DASH"),   
    '0x97': unicodedata.lookup("EM DASH"),     
    '0x98': unicodedata.lookup("SMALL TILDE"),     
    '0x99': unicodedata.lookup("TRADE MARK SIGN"), 
    '0x9A': unicodedata.lookup("LATIN SMALL LETTER S WITH CARON"),   
    '0x9B': unicodedata.lookup("SINGLE RIGHT-POINTING ANGLE QUOTATION MARK"),   
    '0x9C': unicodedata.lookup("LATIN SMALL LIGATURE OE"), 
    '0x9D': '',         
    '0x9E': unicodedata.lookup("LATIN SMALL LETTER Z WITH CARON"),
    '0x9F': unicodedata.lookup("LATIN CAPITAL LETTER Y WITH DIAERESIS"),
    '0xA0': unicodedata.lookup("NO-BREAK SPACE"),
    '0xA1': unicodedata.lookup("INVERTED EXCLAMATION MARK"),
    '0xA2': unicodedata.lookup("CENT SIGN"),
    '0xA3': unicodedata.lookup("POUND SIGN"),
    '0xA4': unicodedata.lookup("CURRENCY SIGN"),
    '0xA5': unicodedata.lookup("YEN SIGN"),
    '0xA6': unicodedata.lookup("BROKEN BAR"),
    '0xA7': unicodedata.lookup("SECTION SIGN"),
    '0xA8': unicodedata.lookup("DIAERESIS"),
    '0xA9': unicodedata.lookup("COPYRIGHT SIGN"),
    '0xAA': unicodedata.lookup("FEMININE ORDINAL INDICATOR"),
    '0xAB': unicodedata.lookup("LEFT-POINTING DOUBLE ANGLE QUOTATION MARK"),
    '0xAC': unicodedata.lookup("NOT SIGN"),
    '0xAD': unicodedata.lookup("SOFT HYPHEN"),
    '0xAE': unicodedata.lookup("REGISTERED SIGN"),
    '0xAF': unicodedata.lookup("MACRON"),
    '0xB0': unicodedata.lookup("DEGREE SIGN"),
    '0xB1': unicodedata.lookup("PLUS-MINUS SIGN"),
    '0xB2': unicodedata.lookup("SUPERSCRIPT TWO"),
    '0xB3': unicodedata.lookup("SUPERSCRIPT THREE"),
    '0xB4': unicodedata.lookup("ACUTE ACCENT"),
    '0xB5': unicodedata.lookup("MICRO SIGN"),
    '0xB6': unicodedata.lookup("PILCROW SIGN"),
    '0xB7': unicodedata.lookup("MIDDLE DOT"),
    '0xB8': unicodedata.lookup("CEDILLA"),
    '0xB9': unicodedata.lookup("SUPERSCRIPT ONE"),
    '0xBA': unicodedata.lookup("MASCULINE ORDINAL INDICATOR"),
    '0xBB': unicodedata.lookup("RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK"),
    '0xBC': unicodedata.lookup("VULGAR FRACTION ONE QUARTER"),
    '0xBD': unicodedata.lookup("VULGAR FRACTION ONE HALF"),
    '0xBE': unicodedata.lookup("VULGAR FRACTION THREE QUARTERS"),
    '0xBF': unicodedata.lookup("INVERTED QUESTION MARK"),
    '0xC0': unicodedata.lookup("LATIN CAPITAL LETTER A WITH GRAVE"),
    '0xC1': unicodedata.lookup("LATIN CAPITAL LETTER A WITH ACUTE"),
    '0xC2': unicodedata.lookup("LATIN CAPITAL LETTER A WITH CIRCUMFLEX"),
    '0xC3': unicodedata.lookup("LATIN CAPITAL LETTER A WITH TILDE"),
    '0xC4': unicodedata.lookup("LATIN CAPITAL LETTER A WITH DIAERESIS"),
    '0xC5': unicodedata.lookup("LATIN CAPITAL LETTER A WITH RING ABOVE"),
    '0xC6': unicodedata.lookup("LATIN CAPITAL LETTER AE"),
    '0xC7': unicodedata.lookup("LATIN CAPITAL LETTER C WITH CEDILLA"),
    '0xC8': unicodedata.lookup("LATIN CAPITAL LETTER E WITH GRAVE"),
    '0xC9': unicodedata.lookup("LATIN CAPITAL LETTER E WITH ACUTE"),
    '0xCA': unicodedata.lookup("LATIN CAPITAL LETTER E WITH CIRCUMFLEX"),
    '0xCB': unicodedata.lookup("LATIN CAPITAL LETTER E WITH DIAERESIS"),
    '0xCC': unicodedata.lookup("LATIN CAPITAL LETTER I WITH GRAVE"),
    '0xCD': unicodedata.lookup("LATIN CAPITAL LETTER I WITH ACUTE"),
    '0xCE': unicodedata.lookup("LATIN CAPITAL LETTER I WITH CIRCUMFLEX"),
    '0xCF': unicodedata.lookup("LATIN CAPITAL LETTER I WITH DIAERESIS"),
    '0xD0': unicodedata.lookup("LATIN CAPITAL LETTER ETH"),
    '0xD1': unicodedata.lookup("LATIN CAPITAL LETTER N WITH TILDE"),
    '0xD2': unicodedata.lookup("LATIN CAPITAL LETTER O WITH GRAVE"),
    '0xD3': unicodedata.lookup("LATIN CAPITAL LETTER O WITH ACUTE"),
    '0xD4': unicodedata.lookup("LATIN CAPITAL LETTER O WITH CIRCUMFLEX"),
    '0xD5': unicodedata.lookup("LATIN CAPITAL LETTER O WITH TILDE"),
    '0xD6': unicodedata.lookup("LATIN CAPITAL LETTER O WITH DIAERESIS"),
    '0xD7': unicodedata.lookup("MULTIPLICATION SIGN"),
    '0xD8': unicodedata.lookup("LATIN CAPITAL LETTER O WITH STROKE"),
    '0xD9': unicodedata.lookup("LATIN CAPITAL LETTER U WITH GRAVE"),
    '0xDA': unicodedata.lookup("LATIN CAPITAL LETTER U WITH ACUTE"),
    '0xDB': unicodedata.lookup("LATIN CAPITAL LETTER U WITH CIRCUMFLEX"),
    '0xDC': unicodedata.lookup("LATIN CAPITAL LETTER U WITH DIAERESIS"),
    '0xDD': unicodedata.lookup("LATIN CAPITAL LETTER Y WITH ACUTE"),
    '0xDE': unicodedata.lookup("LATIN CAPITAL LETTER THORN"),
    '0xDF': unicodedata.lookup("LATIN SMALL LETTER SHARP S"),
    '0xE0': unicodedata.lookup("LATIN SMALL LETTER A WITH GRAVE"),
    '0xE1': unicodedata.lookup("LATIN SMALL LETTER A WITH ACUTE"),
    '0xE2': unicodedata.lookup("LATIN SMALL LETTER A WITH CIRCUMFLEX"),
    '0xE3': unicodedata.lookup("LATIN SMALL LETTER A WITH TILDE"),
    '0xE4': unicodedata.lookup("LATIN SMALL LETTER A WITH DIAERESIS"),
    '0xE5': unicodedata.lookup("LATIN SMALL LETTER A WITH RING ABOVE"),
    '0xE6': unicodedata.lookup("LATIN SMALL LETTER AE"),
    '0xE7': unicodedata.lookup("LATIN SMALL LETTER C WITH CEDILLA"),
    '0xE8': unicodedata.lookup("LATIN SMALL LETTER E WITH GRAVE"),
    '0xE9': unicodedata.lookup("LATIN SMALL LETTER E WITH ACUTE"),
    '0xEA': unicodedata.lookup("LATIN SMALL LETTER E WITH CIRCUMFLEX"),
    '0xEB': unicodedata.lookup("LATIN SMALL LETTER E WITH DIAERESIS"),
    '0xEC': unicodedata.lookup("LATIN SMALL LETTER I WITH GRAVE"),
    '0xED': unicodedata.lookup("LATIN SMALL LETTER I WITH ACUTE"),
    '0xEE': unicodedata.lookup("LATIN SMALL LETTER I WITH CIRCUMFLEX"),
    '0xEF': unicodedata.lookup("LATIN SMALL LETTER I WITH DIAERESIS"),
    '0xF0': unicodedata.lookup("LATIN SMALL LETTER ETH"),
    '0xF1': unicodedata.lookup("LATIN SMALL LETTER N WITH TILDE"),
    '0xF2': unicodedata.lookup("LATIN SMALL LETTER O WITH GRAVE"),
    '0xF3': unicodedata.lookup("LATIN SMALL LETTER O WITH ACUTE"),
    '0xF4': unicodedata.lookup("LATIN SMALL LETTER O WITH CIRCUMFLEX"),
    '0xF5': unicodedata.lookup("LATIN SMALL LETTER O WITH TILDE"),
    '0xF6': unicodedata.lookup("LATIN SMALL LETTER O WITH DIAERESIS"),
    '0xF7': unicodedata.lookup("DIVISION SIGN"),
    '0xF8': unicodedata.lookup("LATIN SMALL LETTER O WITH STROKE"),
    '0xF9': unicodedata.lookup("LATIN SMALL LETTER U WITH GRAVE"),
    '0xFA': unicodedata.lookup("LATIN SMALL LETTER U WITH ACUTE"),
    '0xFB': unicodedata.lookup("LATIN SMALL LETTER U WITH CIRCUMFLEX"),
    '0xFC': unicodedata.lookup("LATIN SMALL LETTER U WITH DIAERESIS"),
    '0xFD': unicodedata.lookup("LATIN SMALL LETTER Y WITH ACUTE"),
    '0xFE': unicodedata.lookup("LATIN SMALL LETTER THORN"),
    '0xFF': unicodedata.lookup("LATIN SMALL LETTER Y WITH DIAERESIS")}

cp1252_punctuation = ['0x91','0x92','0x93','0x94','0x96','0x97']

def decode_json_files_in_directory(indirectory, outdirectory):
    for json_file in list(os.listdir(indirectory)):
        if json_file.endswith('.json'):
            with open(file_name_append(indirectory,json_file),'r') as instream:
                text = instream.read()
                json_obj = json.loads(text)
                for field in ['html_lawbox', 'html_columbia', 'html_with_citations']:
                    if field in json_obj:
                        if json_obj[field]:
                            text_in_field = json_obj[field]
                            tokens = text_in_field.split(' ')
                            for i in range(0,len(tokens)):
                                if (len(tokens[i]) == 1):
                                    if (str(hex(ord(tokens[i]))) in cp1252_to_utf8_chars_decoding_table.keys()):
                                        tokens[i]= cp1252_to_utf8_chars_decoding_table[str(hex(ord(tokens[i])))]
                                elif len(tokens[i])>1:
                                    token = tokens[i]
                                    ## check last character
                                    if (str(hex(ord(token[-1]))) in cp1252_to_utf8_chars_decoding_table):
                                        tokens[i]=token[:-1]+cp1252_to_utf8_chars_decoding_table[str(hex(ord(token[-1])))]
                                    if (len(token)==3) and (token[0] in '({[') and (token[2] in ')}]') \
                                       and (str(hex(ord(token[1]))) in cp1252_to_utf8_chars_decoding_table):
                                        tokens[i] = token[0]+cp1252_to_utf8_chars_decoding_table[str(hex(ord(token[1])))]+token[2]
                                    elif '<' in token:
                                        position = token.find('<')
                                        if (position>0) and (str(hex(ord(token[position-1]))) in cp1252_to_utf8_chars_decoding_table):
                                            token = token[:position-1]+cp1252_to_utf8_chars_decoding_table[str(hex(ord(token[position-1])))]+token[position:]
                                            tokens[i]=token
                                    if str(hex(ord(token[0]))) in cp1252_to_utf8_chars_decoding_table:
                                        tokens[i]=cp1252_to_utf8_chars_decoding_table[str(hex(ord(token[0])))]+token[1:]
                                    elif '>' in token:
                                        position = token.find('>')
                                        if (position<len(token)-1) and \
                                           (str(hex(ord(token[position+1]))) in cp1252_to_utf8_chars_decoding_table):
                                            token = token[:position]+cp1252_to_utf8_chars_decoding_table[str(hex(ord(token[position+1])))]+token[position+1:]
                                            tokens[i]=token
                                    if chr(151) in token:
                                        position = token.find(chr(151))
                                        if position<len(token)-1:
                                            token = token[:position]+'—'+token[position+1]
                                        else:
                                            token = token[:position]+'—'
                                        tokens[i] = token

                            outtext = " ".join(tokens)
                            json_obj[field]=outtext
                with open(file_name_append(outdirectory,json_file),'w',encoding='utf8') as outstream:
                    out_string = json.dumps(json_obj,ensure_ascii=False)
                    outstream.write(out_string)


