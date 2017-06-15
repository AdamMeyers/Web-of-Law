import os
import re
from xml.sax.saxutils import escape
from xml.sax.saxutils import unescape
DICT_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) + os.sep

POS_dict = {}

POS_dict_file = DICT_DIRECTORY+'POS.dict'

ending_words = ['corp','inc','sa','cia','ltd','gmbh','co','llp','s.a.', '&c','sr','jr','jr.','sr.','md','m.d.','esq','esq.','rn','et','etc','al']

org_ending_words = ['corp','inc','sa','cia','ltd','gmbh','co','llp','limited','s.a.', '&c']

person_ending_words = ['sr','jr','jr.','sr.','md','m.d.','esq','esq.','rn','deceased']

not_uppercase_part_of_org_names = ['the','a','an','and','but','as','at','by','for','from','of','to', 'all','&','under','its','his','her','their','etc','de','el','e','por','la','le']

alias_words = ['aka','a.k.a','alias','d/b/a','dba']

citation_filler_words = ['et','al','ux','others','another','ex','rel','etc','vir']

latin_reference_words = ['supra', 'ibid', 'idem', 'id', 'op', 'loc','per','curiam'] ## op and loc are followed by 'cit' (op cit, loc cit)

optional_abbrev_words = ['and']

other_non_citation_legal_words = ['certiorari','syllabus','writ','petition']

months = month = ['january','february','march','april','may','june','july','august','september','october','november','december','jan','feb','mar','apr','jun','jul','aug','sept?','oct','nov','dec']

standard_words_with_periods_in_citations = ['corp','inc','ltd','co','s.a.','a.k.a','et','al','etc','no']

citation_closed_class = org_ending_words + person_ending_words + not_uppercase_part_of_org_names + alias_words + citation_filler_words + latin_reference_words + other_non_citation_legal_words+months

after_last_name_words = ending_words+alias_words+citation_filler_words+optional_abbrev_words

legislation_part_words = ['chapter','section','division','paragraph','code','chapters','sections','divisions','paragraphs','codes']

def load_tab_deliniated_dict(dict_file,dictionary):
    with open(dict_file) as instream:
        for line in instream:
            line = line.strip(os.linesep)
            line_list = line.split('\t')
            entry = []
            ## standard for dictionary
            ## attributes are uppercase and
            ## words to lookup are lowercase
            for value in line_list[1:]:
                entry.append(value.upper())
            dictionary[line_list[0].lower()] = entry

load_tab_deliniated_dict(POS_dict_file,POS_dict)

def wol_escape(instring):
    return(escape(instring).replace('"','&quot;'))

def wol_unescape(instring):
    return(unescape(instring.replace('&quot;','"')))
    
def alpha_check(instring):
    pattern = re.compile('[a-zA-Z]')
    if isinstance(instring,str):
        return(pattern.search(instring))

def get_dir_plus_file(infile):
    divider = re.search('('+os.sep+')'+'[^'+os.sep+']*$',infile)
    if divider:
        return(infile[:divider.end(1)],infile[divider.end(1):])
    else:
        return('',infile)

def file_name_append(path, file):
    if path.endswith(os.sep):
        return(path+file)
    else:
        return(path+os.sep+file)

def find_duplicate_in_record_list(records):
    so_far = []
    for record in records:
        start_end = [record['start'],record['end']]
        if start_end in so_far:
            print('duplicates',start_end)
            print(record)
        so_far.append(start_end)
        
def detect_garbage_line(line):
    import string
    number_of_letters = 0
    if len(line)>1000:
        for char in line:
            if char in string.ascii_letters:
                number_of_letters = number_of_letters+1
        if (number_of_letters/len(line)) < .4:
            return(True)

def boolean_check(object):
    ## distinguishes between 0 and False or None
    if (type(object) == int) or object:
        return(True)
    else:
        return(False)

def remove_xml_plus(instring):
    ## returns just text
    xml_key_pattern = re.compile(r'<[^>]+>',re.I)
    out = xml_key_pattern.sub('',instring)
    return(out)

def remove_xml_plus2(instring):
    ## returns text and extracted XML tags starging positions
    xml_key_pattern = re.compile(r'<([^>]+)>',re.I)
    outstring = ''
    match = xml_key_pattern.search(instring)
    if not match:
        return(instring,[])
    start = 0
    offset = 0
    html_hash = {}
    while match:
        new_piece = instring[start:match.start()]
        outstring = outstring+new_piece
        offset = offset+len(new_piece)
        start = match.end()
        html_hash[match.start()]=[offset,match.group(1)]
        match = xml_key_pattern.search(instring,start)
    outstring = outstring+instring[start:]
    keys = list(html_hash.keys())
    keys.sort()
    html_out_list = []
    for key in keys:
        html_out_list.append(html_hash[key])
    return(outstring,html_out_list)

def short_file(file_string):
    last_slash_pattern = re.compile(os.sep+'[^'+os.sep+']*$')
    last_dot_pattern = re.compile('\.[^\.]*$')
    last_slash_match = last_slash_pattern.search(file_string)
    last_dot_match = last_dot_pattern.search(file_string)
    if last_slash_match and last_dot_match and (last_slash_match.start()<last_dot_match.start()):
        return(file_string[last_slash_match.start()+1:last_dot_match.start()])
    elif last_slash_match:
        return(file_string[last_slash_match.start()+1:])
    elif (not last_slash_match) and last_dot_match:
        ## last_slash_match is only used if it precedes last_dot_match
        return(file_string[:last_dot_match.start()])
    else:
        return(file_string)

def member_if_attribute(list_of_dictionaries,key,value):
    ## returns True if one of the dictionaries in the list has the specified key/value pair
    for dictionary in list_of_dictionaries:
        if (key in dictionary) and (dictionary[key]==value):
            return(True)
    
def get_valid_dict_value(key,dictionary):
    if (key in dictionary) and (not dictionary[key] in ['None','Unknown']):
        return(dictionary[key])
    else:
        return(False)

def cleanup(line, commas = False):
    cleaned = ''
    for char in line:
        if char.isalnum() or char in ':? ><,./;{}[]\|+=_-)(*&^$%#@!$~`':
            cleaned += char
        elif char in '"' or char in "'" and commas:
            cleaned += char
    return cleaned

def almostEquals(name1, name2, printNames = False):
    name1 = name1.upper()
    name2 = name2.upper()

    name1 = name1.strip('.')
    name1 = name1.strip(',')
    name2 = name2.strip('.')
    name2 = name2.strip(',')

    if name1.strip(' ') == name2.strip(' '):
        return True

    if name1.strip('.') == name2.strip('.'):
        return True


    name1 = name1.split()
    name2 = name2.split()

    if name1[-2:] == ['ET', 'AL']:
        name1 = name1[:-2]
    if name2[-2:] == ['ET', 'AL']:
            name2 = name2[:-2]
    if name1[-1:] in ['COMPANY', 'CO', 'CO.']:
        name1 = name1[:-1]
    if name2[-1:] in ['COMPANY', 'CO', 'CO.']:
        name2 = name2[:-1]

    if printNames:
        print(name1)
        print(name2)

    if name1 == name2:
        return True
    if len(name1) > 1 and len(name2) == 1:
        if name1[-1] == name2[-1]:
            return True
    elif len(name2) > 1 and len(name1) == 1:
        if name1[-1] == name2[-1]:
            return True
    elif len(name2) > 1 and len(name1) > 1:
        if name2[-2:] == name1[-2:]:
            return True
    return False

def concat(xss):
    new = []
    for xs in xss:
        new.extend(xs)
    return new


def standardize(name):
    standard = ''
    name = name.upper()
    for letter in name:
        if not (letter == '.' or letter == ','):
            standard += letter
    standard = standard.split()
    standard = filter(lambda i: i not in ['ET','AL','APPELLANT','APPELLANTS','APPELLEE','APPELLEES'], standard)
    return ' '.join(standard)
