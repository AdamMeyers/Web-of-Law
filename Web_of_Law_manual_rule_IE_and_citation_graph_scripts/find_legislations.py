import re

import roman

## from wol_utilities import *
from find_case_citations5 import *

court_reporter_check = re.compile('^('+court_reporter_rexp+')$')

##################
# GENERAL REGEX: #
##################

roman_num_rexp = '(?:[MCLDXVI]+)'
numeral_rexp = roman_num_rexp + '|(?:\d+)'
section_numeral_rexp = '((?:{0}-?\.?:?)+)'.format(numeral_rexp)
section_numeral_rexp_noncap = '(?:(?:{0}-?\.?:?)+)'.format(numeral_rexp)


def get_states_dict():
    """Returns a dict of abbreviation of state names to full state name

    :return:
    """
    states_dict = {}
    with open('STATES.dict') as instream:
        for line in instream:
            states_dict[re.sub(' +','',line.split('\t')[0].replace('. ', '.'))] = line.split('\t')[1].strip()
            ## added an additional replace to get rid of multiple spaces
    # states_dict['U.S.'] = 'Federal'
    return states_dict


states_rexp = ''
for o in get_states_dict():
    # states_rexp += '(?:{0})|'.format(o.replace('.', '\.'))
    states_rexp += '(?:{0})|'.format(re.sub(r'(\w)\.(\w)\.', r'\1. ?\2.', o).replace('.', '\.'))

states_rexp = states_rexp[:len(states_rexp) - 1]
body_rexp = states_rexp + '|(?:U\.S\.)'

title_rexp = 'Tit\. ?({0})'.format(section_numeral_rexp)
part_rexp = 'pt\. ?({0})'.format(section_numeral_rexp)
division_rexp = 'div\. ?({0})'.format(section_numeral_rexp)
paragraph_rexp = 'par\. ?({0})'.format(section_numeral_rexp)
article_rexp = 'Arts?\. ?({0})'.format(section_numeral_rexp)
chapter_rexp = 'ch?\. ?({0})'.format(section_numeral_rexp)
clause_rexp = 'cl\. ?({0})'.format(section_numeral_rexp)
section_rexp = r'(?:(?:§§? ?(?:(?:(?:(?:pp?\. ?)|(?:c\. ?)|(?:subc\. ?))?\d+[A-Za-z]{0,2}(?: ?\(\d{1,3}\))?(?:\. ?|, |-| to | at |,? and |:|; ?| ))+))+)'

document_location_rexp = r'(?:(?:(?:(?:(?:Tit\.)|(?:ch?\.)|(?:subc\.)|(?:pt\.)|(?:par\.)|(?:Arts?\.)|(?:cl\.)|(?:div\.)) ?(?:[MCLDXVI]+|\d+-?\.?:?)*),? ?(?:,? ?and )?)+)'

############################
# NATURAL AMENDMENT REGEX: #
############################

ordinals = {
    'First': '1',
    'Second': '2',
    'Third': '3',
    'Fourth': '4',
    'Fifth': '5',
    'Sixth': '6',
    'Seventh': '7',
    'Eighth': '8',
    'Ninth': '9',
    'Tenth': '10',
    'Eleventh': '11',
    'Twelfth': '12',
    'Thirteenth': '13',
    'Fourteenth': '14',
    'Fifteenth': '15',
    'Sixteenth': '16',
    'Seventeenth': '17',
    'Eighteenth': '18',
    'Nineteenth': '19',
    'Twentieth': '20',
    'Twenty-first': '21',
    'Twenty-second': '22',
    'Twenty-third': '23',
    'Twenty-fourth': '24',
    'Twenty-fifth': '22',
    'Twenty-sixth': '23',
    'Twenty-seventh': '24'
}

amends = (
    'amend\.',
    'Amendment',
    'amendment'
)

# create a regex for capturing ordinals
ordinal_variants = dict()
# create mappings of lowercase ordinals too
ordinal_rexp = ''
for o in ordinals:
    ordinal_rexp += '(?:{0})|(?:{1})|'.format(o, o.lower())
    ordinal_variants[o.lower()] = ordinals[o]
    ordinal_variants[o] = ordinals[o]
ordinal_rexp = ordinal_rexp[:-1]  # remove extra '|' symbol

# create a regex for the word "Amendment" + variations
amend_rexp = ''
for o in amends:
    amend_rexp += '(?:{0})|'.format(o)
amend_rexp = amend_rexp[:-1]  # remove extra '|' symbol

# add the two rexps for a natural, verbal listing of amendment references
# (eg. "the First, Second and Third Amendments")
#
# The regex is structured as follows:
# Group 1: 1st ordinal (From above example, "First"
# Group 3: Last ordinal after "and" if present (From above, Third)
# Group 2: The list of comma-separated (accepting Oxford comma as well) middle ordinals

informal_amend_rexp = '({0})' \
                      '(?:((?:, (?:{0}))*)(?:,? and ({0})))* ' \
                      '(?:{1})' \
    .format(ordinal_rexp, amend_rexp)

##################################
# CONSTITUTIONAL CITATION REGEX: #
##################################

const_cit_rexp = '({0}) ' \
                 '(?:(?:Const\.)|(?:CONST\.)) ' \
                 '((?:art\.)|(?:amend\.)|(?:ART\.)|(?:AMEND\.)|(?:Art\.)|(?:Amend\.)) ' \
                 '({1})' \
                 '(?:, § ?({1})' \
                 '(?:, cl. ?({1}))?)?' \
    .format(body_rexp, numeral_rexp)

###########################
# STATUTE CITATION REGEX: #
###########################

federal_statute_cit_rexp = '(\d+) U\. ?S\. ?C\. § ?(\d+)((?:\(.\))+)?'
# state_statute_cit_rexp = '({0}) (?:\w+\W+ )?(?:Code)? (\w+\W )+§§? (\d+\W? ?)+ ' \
# state_statute_cit_rexp = (r'({0}) '  # state
#                           r'((?: ?\w{{0,}}\W*? ){{1,7}}?)'  # doc title
#                           r'(?:'  # start alternating so we can get either doc loc, doc section or both
#                           r'({2})'  # doc location
#                           r'|'  # OR
#                           r'({1})'  # section
#                           r'){{1,2}} ?'  # capt either doc location, section or both
#                           r'(?:\((?: ?\w{{0,}}\W*? ){{0,3}}?(\d{{4}})\))?'  # date
#                           ) \
#     .format(
#     states_rexp,
#     section_rexp,
#     document_location_rexp,
# )

state_statute_cit_rexp = (r'({0}) '  # state
                          r'((?: ?\w+\W* ){{0,7}})'  # doc title
                          r'(?:'  # start alternating so we can get either doc loc, doc section or both
                          r'({2})'  # doc location
                          r'|'  # OR
                          r'({1})'  # section
                          r'){{1,2}} ?'  # capt either doc location, section or both
                          r'(?:\((?: ?\w*\W* ){{0,3}}(\d{{4}})\))?'  # date
                          ) \
    .format(
    states_rexp,
    section_rexp,
    document_location_rexp,
)

###### AM July 2017 ##############
# Acts, Treaties, Codes, and Rules
##################################

of_date_pattern = '(of *((('+month+')'+'(( ([1-9]|[0-2][0-9]|3[01]),)|,)?'+' ((17|18|19|20)[0-9][0-9]))|((17|18|19|20)[0-9][0-9])))'

of_phrase = '(of( *[A-Z][a-z]+){1,3})|'+of_date_pattern
## of date_pattern = of = date_pattern (see find_case_citations5, but make case sensitive?

rule_word = '([Cc]ode|[aA]ct|[tT]reaty|[rR]ule)'

rule_word_filter = re.compile('[ -]'+rule_word+'([ —-]|$)')

act_name1 = '(([tT]he *)?(([A-Z][a-z\.]*)[ —-]*)+'+rule_word+')'

act_name2 = '(([tT]he *)?(([A-Z][a-z\.]*)[ —-]*)+of *(([A-Z][a-z\.]*) *)+'+rule_word+')'

act_name3 = '(([tT]he *)?([A-Z][a-z\.]*[ —-]*)+'+rule_word+' *('+of_phrase+'))'


act_name = '('+act_name3+'|'+act_name2+'|'+act_name1+')'

section_pattern = '(§ [0-9]+,?)'

legislation_id = '((ch?\. *[0-9]+, *)*([0-9]+(, [0-9]+)* [sS]tat\. [0-9]+(, [0-9-]+)?))'

pub_pattern = '(Pub L. No [0-9-]+(,?) *)?'

optional_year = '( *\([0-9]{4}\))?'

optional_full_date = '(('+full_date+'),? *)*'

## act_pattern = act_name + ' *' + section_pattern + ' *'+ legislation_id
act_pattern = '('+ section_pattern+' *of *)?'+act_name + '(,? *' + optional_full_date + pub_pattern + section_pattern +'?' +'( *' + legislation_id +')?' + optional_year+')?'
## group 3 = name
## 52 = Pub L. No X-Y
## 2 or 54 = section number
## 57 = chapter group
## 58 = leg ID including "number Stat. numbers, numbers"
## 12, 23, 39, 61 -- possible date slots


act_expression = re.compile(act_pattern)

###AM 7/2018 #############################
# Regulations with sections
##########################################

# number + initials of acgency + optional § + section number + (optional modifier + optional year)

regulation_with_section = '([0-9]+) *([A-Z\.]+) *§? *([0-9]+)'+' *(\(([A-Z][a-z]+)? *([0-9]{4})\))?'
regulation_expression = re.compile(regulation_with_section)
## 1 title number
## 2 agency (agency is required)
## 3 section number
## 5 publisher
## 6 date

###########################################
# NATURAL CONSTITUTIONAL REFERENCE REGEX: #
###########################################

informal_const_rexp = '((?:[tT]he)|(?:[oO]ur))?(?: (?:Federal)|(?:United States))? Constitution(?: of the United States)?'


###################
# UTIL FUNCTIONS: #
###################


def ordinal_to_number(ordinal_string):
    """Returns numerical value of given ordinal string

    :param ordinal_string:
    :return: the numerical value of the ordinal
    """
    if ordinal_string in ordinal_variants:
        return ordinal_variants[ordinal_string]
    else:
        return 0


def replace_roman_nums_with_ints(num_string):
    """Returns the given string with Roman numerals converted to Hindu-Arabic Numerals

    :param num_string:
    :return:
    """

    if not num_string:
        return ''

    roman_num_rexp_cap = '({0})'.format(roman_num_rexp)
    arabized_num_string = re.sub(
        roman_num_rexp_cap,
        lambda matchobj: '{}'.format(roman.fromRoman(matchobj.group(1))),
        num_string,
    )

    return arabized_num_string


def body_abbrev_to_full(abbrev):
    """Returns a full state name given an abbreviation, or "U.S." if "U.S." is given

    :param abbrev:
    :return:
    """
    bodies = get_states_dict()
    bodies['U.S.'] = 'Federal'
    bodies['U. S.'] = 'Federal'
    ## return bodies[abbrev.replace(' ', '')]
    return bodies[re.sub(' +','',abbrev)]


##################
# CAPTURE LOGIC: #
##################


def capture_informal_amendment_ordinals(in_string):
    """Returns list of strings matching the informal amendments rexp in given string

    Returns a list of strings, the 0th of which is the whole string
    The 1st and last elements are the first and last listed ordinals per the informal_amend_rexp
    The middle elements are the 2nd group from the informal_amend_rexp split and spread into a list
    :param in_string: (str) the string to search in
    :return: a list of strings
    """

    result = []
    full_amend_pattern = re.compile(informal_amend_rexp)
    amend_matches = full_amend_pattern.finditer(in_string)
    for amend_match in amend_matches:
        result.append({'ordinal': amend_match.group(1), 'match': amend_match.group(0),
                       'start': amend_match.start()})
        # The middle group is a string of the comma separated amendment
        # mentions between the first and last mentions
        # It will be split such that empty strings are possible
        # Thus they are filtered out
        if amend_match.group(2):
            result.extend(
                list(map(lambda x: {'ordinal': x, 'match': amend_match.group(0), 'start': amend_match.start()},
                         filter(lambda x: x, amend_match.group(2).split(", ")))))
        if amend_match.group(3):
            result.append({'ordinal': amend_match.group(3), 'match': amend_match.group(0),
                           'start': amend_match.start()})
    return result


def capture_const_cits(in_string):
    """Returns a list of strings, each corresponding to the match groups in the constitutional amendment/article
    citation rexp

    :param in_string:
    :return:
    """
    const_pattern = re.compile(const_cit_rexp)
    matches = const_pattern.finditer(in_string)
    if matches:
        # return [
        #     match.group(0),  # matched string
        #     match.group(1),  # jurisdiction
        #     match.group(2),  # article | amendment?
        #     match.group(3),  # article/amend num
        #     match.group(4),  # section
        #     # match.group(5),  # clause
        # ]
        return matches
    else:
        return []


def capture_informal_constitutional_refs(in_string):
    """Returns list of strings matching the informal amendments rexp in given string

    Returns a list of strings, the 0th of which is the whole string
    The 1st and last elements are the first and last listed ordinals per the informal_amend_rexp
    The middle elements are the 2nd group from the informal_amend_rexp split and spread into a list
    :param in_string: (str) the string to search in
    :return: a list of strings
    """

    const_ref_pattern = re.compile(informal_const_rexp)
    matches = const_ref_pattern.finditer(in_string)
    if matches:
        return matches
        # match.group(0),  # matched string
        # ]
    else:
        return []


def capture_federal_statute_cits(in_string):
    """Returns a list of strings, each corresponding to match groups in the federal statute citation rexp

    :param in_string:
    :return:
    """
    const_pattern = re.compile(federal_statute_cit_rexp)
    matches = const_pattern.finditer(in_string)
    if matches:
        return matches
    else:
        return []

def extract_chapter_from_state_name(instring):
    chapter_match = re.search('ch?\. *[0-9]+, *',instring)
    if chapter_match:
        state_piece = instring[:chapter_match.start()]
        chapter_piece = instring[chapter_match.start():]
    else:
        state_piece = instring
        chapter_piece = ''
    return(state_piece,chapter_piece)

def capture_state_statute_cits(in_string):
    """Returns a list of strings, each corresponding to match groups in the state statute citation rexp

    :param in_string:
    :return:
    """
    const_pattern = re.compile(state_statute_cit_rexp)
    matches = list(const_pattern.finditer(in_string))

    res = []

    for match in matches:
        state = match.group(1)
        state_piece,chapter_piece = extract_chapter_from_state_name(match.group(2))
        document = '{} {}'.format(state, state_piece)
        section = (match.group(4) or '').strip()
        date = match.group(5)
        if match.group(3):
            doc_loc = chapter_piece + match.group(3) 
        else:
            doc_loc = chapter_piece
        article_match = re.compile(article_rexp).search(doc_loc) if doc_loc else ''
        chapter_match = re.compile(chapter_rexp).search(doc_loc) if doc_loc else ''
        title_match = re.compile(title_rexp).search(doc_loc) if doc_loc else ''

        res.append([
            match.group(0),  # matched string
            state,  # state
            document,
            article_match.group(1) if article_match else '',  # article
            chapter_match.group(1) if chapter_match else '',  # chapter
            title_match.group(1) if title_match else '',  # title
            section,  # section
            doc_loc,
            date if date else '',
            match.start()
        ])
    return res

def get_publ_from_string(instring):
    if instring:
        number_match = re.search('[0-9-]+',instring)
        if number_match:
            return(number_match.group(0))
        else:
            return(False)
    else:
        return(False)

def adjust_act_output_for_final_chars(name,name_end,match):
    name2 = name.rstrip(' ,')
    diff = match.end()-name_end
    if (name2 != name) and (name_end == match.end()):
        whole_string = match.group(0).rstrip(' ,')
        diff = len(match.group(0))-len(whole_string)
        match_end = match.end()-diff
    elif (name_end != match.end()) and (not re.search('[0-9a-zA-Z]',match.group(0)[-1*diff:])):
        match_end = name_end
        whole_string = match.group(0)[:(-1 * diff)]
    else:
        whole_string = match.group(0)
        match_end = match.end()
    return(name2,whole_string,match.start(),match_end)

def adjust_act_output_for_pre_citation_words(name,output_string,start_offset,end_offset):
    pre_citation_regexp = ''
    for word in pre_citation_words:
        pre_citation_regexp += word + '|'
    pre_citation_regexp.strip('|') ## remove final disjunction 
    pre_citation_pattern = re.compile('^'+'('+pre_citation_regexp+')[ \.]+',re.I)
    match = pre_citation_pattern.search(name)
    if output_string.startswith(name) and match:
        change = len(match.group(0))
        name = name[change:]
        output_string = output_string[change:]
        start_offset = start_offset + change
    return(name,output_string,start_offset,end_offset)

def pages_check(pages):
    ## if comma is in string, makes sure that
    ## pages are in sort order
    page_list = pages.split(',')
    consec = True
    last_page = False
    out_string = ''
    for page in page_list:
        if not consec:
            pass
        elif ('-' in page):
            pages2 = page.split('-')
            one_page = pages2[-1].strip(' ')
            if one_page.isdigit():
                one_page = int(one_page)
                if (not last_page) or (one_page>last_page):
                    last_page = one_page
                    out_string += page+','
                else:
                    consec = False
        else:
            one_page = page.strip(' ')
            if one_page.isdigit():
                one_page = int(one_page)
                if (not last_page) or (one_page>last_page):
                    last_page = one_page
                    out_string +=page+','
                else:
                    consec = False
    out_string = out_string.strip(',')
    if consec:
        return(pages,0)
    elif pages.startswith(out_string):
        diff = len(pages)-len(out_string)
        return(out_string,diff)
    else:
        print('pages_check worked wrong')
        print('input:','*'+pages+'*')
        print('output:','*'+out_string+'*')
        return(pages,0)
    
           

def get_volume_and_pages_from_stat_text(intext,volume_end,match_end):
    ## example: 89 Stat. 801
    ##  volume 89, page 801
    ## edited version of legislation_id pattern above
    pattern_match = re.compile('(c\. *)?([0-9]+(, [0-9]+)*) [sS]tat\. ([0-9]+(, [0-9-]+)?)')
    match = pattern_match.search(intext)
    end_modifier = 0
    if match:
        volume = match.group(2)
        pages = match.group(4)
        pages1 = pages
        if (volume_end == match_end) and (',' in pages):
            pages,end_modifier = pages_check(pages)
            # print(intext)
            # print(1,volume)
            # print(2.1,'*'+pages1+'*',2.2,'*'+pages+'*')
            # print(3,end_modifier)
        ## input('pause')
        return(volume,pages,end_modifier)
    else:
        return(False,False,end_modifier)
    
def get_chapters_from_text(intext):
    if intext:
        output = ''
        chapters = re.finditer('[0-9]+',intext)
        for chapter in chapters:
            output +=chapter.group(0)+', '
        return(output.strip(', '))
    else:
        return(False)
    
def make_act_xml(match,line,offset,file_id,cit_num):
    ## need to find out more for c. and ch.
    ## possibly other abbreviations missing 57 **
    anaphoric_check = re.compile('^[tT](he|hat|his) *'+rule_word+'$')
    if match:
        name = match.group(3)
        end_modifier = False
        if anaphoric_check.match(name): ## match looks for exact match
            anaphoric_act='True' ## must be string for print out
        else:
            anaphoric_act=False
        name,output_string,start_offset,end_offset = adjust_act_output_for_final_chars(name,match.end(3),match)
        name,output_string,start_offset,end_offset = adjust_act_output_for_pre_citation_words(name,output_string,start_offset,end_offset)
        start_offset = start_offset + offset
        end_offset = end_offset + offset
        publ = get_publ_from_string(match.group(52))
        if match.group(2) and re.search('[0-9]',match.group(2)):
            section_number = match.group(2).strip(' §')
        elif match.group(54) and re.search('[0-9]',match.group(54)):
            section_number = match.group(54).strip(' §')
        else:
            section_number = False
        if match.group(57):
            chapters = get_chapters_from_text(match.group(57))
        else:
            chapters = False
        if match.group(58):
            volume,pages,end_modifier = get_volume_and_pages_from_stat_text(match.group(58),match.end(58),match.end())
            ## ** 57 ** add constraint on pages here
            ## a) divide pages by comma
            ## b) if pages after comma are less than before comma
            ##    then: i) pages after comma should be ruled out
            ##          ii) final endpoint should be adjusted
            ## 80 Stat. 931, 944-47
            ## volume stat pages
        else:
            volume = False
            pages = False
        date = False
        for position in [12,23,39,61]:
            if match.group(position) and re.search('[0-9]',match.group(position)):
                temp_date = match.group(position)
                if not date:
                    date = temp_date
                elif (date.lower() != temp_date.lower()) and (date.lower() in temp_date.lower()):
                    date = temp_date
        if date:
            date = date.strip(' ').upper()
        else:
            date = False
        cit_id = file_id + str(cit_num)
        output = '<citation id=\"'+cit_id+'\"'
        if end_modifier:
            end_offset = end_offset-end_modifier
            output_string = output_string[:-1*end_modifier]
        for key,value in [['entry_type','act_treaty_code_rule'],
                          ['start',str(start_offset)],
                          ['end',str(end_offset)],
                          ['line',str(line)],
                          ['document',name],
                          ['anaphoric_act',anaphoric_act],
                          ['public_law_number',publ],
                          ['section',section_number],
                          ['volume',volume],
                          ['chapter',chapters],
                          ['pages',pages],
                          ['date',date]]:
            if value and re.search('[a-zA-Z0-9]',value):
                output = output+' '+key+'="'+value+'"'
        output = output+'>'+output_string+'</citation>'
        return(output)

def agency_check(agency):
    if not re.search('[A-Za-z].*[A-Za-z]',agency):
        ## there must be at least 2 letters in an agency name
        return(False)
    elif court_reporter_check.search(agency):
        ## if a court reporter abbreviation, we assume it cannot also
        ## be an agency abbreviation
        return(False)
    else:
        return(True)

def make_reg_xml(match,line,offset,file_id,cit_num):
    if match:
        if match.group(1) and re.search('[0-9]',match.group(1)):
            title_number = match.group(1)
        else:
            title_number = False
        if match.group(2) and re.search('[^ ]', match.group(2)):
            agency = match.group(2)
            if not agency_check(agency):
                agency = False
        else:
            agency = False
        if not agency:
            return(False)
        if match.group(3) and re.search('[0-9]',match.group(3)):
            section_number = match.group(3)
        else:
            section_number = False
        if match.group(5) and re.search('[0-9]',match.group(5)):
            publisher = match.group(5)
        else:
            publisher = False
        if match.group(6) and re.search('[0-9]',match.group(6)):
            date = match.group(6)
        else:
            date = False
        start_offset = match.start() + offset
        end_offset = match.end() + offset
        cit_id = file_id + str(cit_num)
        output = '<citation id=\"'+cit_id+'\"'
        for key,value in [['entry_type','regulation'],
                          ['start',str(start_offset)],
                          ['end',str(end_offset)],
                          ['line',str(line)],
                          ['agency',agency],
                          ['publisher',publisher],
                          ['title',title_number],
                          ['section',section_number],
                          ['date',date]]:
            if value:
                output = output+' '+key+'="'+value+'"'
        output = output+'>'+match.group(0)+'</citation>'
        return(output)
    

def generate_other_leg_citations_from_string(line,offset,line_num,leg_count,file_id):
    acts = act_expression.finditer(line)
    regs = regulation_expression.finditer(line)
    output = []
    new_cits = 0
    for match in acts:
        if rule_word_filter.search(match.group(0)):
            act_xml = make_act_xml(match,line_num,offset,file_id,leg_count+new_cits)
            if act_xml:
                new_cits = new_cits+1
                output.append(act_xml)
    for match in regs:
        reg_xml = make_reg_xml(match,line_num,offset,file_id,leg_count+new_cits)
        if reg_xml:
            new_cits = new_cits+1
            output.append(reg_xml)
    return(output)
            


def generate_legislation_citations_from_string(in_string, offset, line_num, leg_count, file_id):
    """Returns an array of citation strings from a given string

    :param in_string: string that matches natural amendment format
    :param offset: byte offset in file in_string starts from
    :param line_num: line number in file
    :param leg_count: index of the current legislation citation created from this file
    :param file_id: id of the file being read
    :return: list of citation strings
    """
    matches = {
        'amend_ref': list(capture_informal_amendment_ordinals(in_string)) or [],
        'const_cit': list(capture_const_cits(in_string)) or [],
        'const_ref': list(capture_informal_constitutional_refs(in_string)) or [],
        'federal_statute': list(capture_federal_statute_cits(in_string)) or [],
        'state_statute': list(capture_state_statute_cits(in_string)) or []
    }

    cits = []

    # 1. create pseudo citation object
    # 2. turn all into that
    # 3. sort list of pseudo cits
    # 4. THEN CONVERT TO CITATIONS!

    cits.extend(list(map(lambda x: {
        'type': 'amend_ref',
        'start_index': offset + x['start'],
        'end_index': offset + x['start'] + len(x['match']),
        'line_num': line_num,
        'cit_id': -1,
        'amend_num': ordinal_to_number(x['ordinal']),
        'text': str.strip(x['match'])
    }, matches['amend_ref'])))

    cits.extend(list(map(lambda x: {
        'type': 'const_cit',
        'start_index': offset + x.start(),
        'end_index': offset + x.start() + len(x.start(0)),
        'line_num': line_num,
        'cit_id': -1,
        'jurisdiction': body_abbrev_to_full(x.group(1)),
        'art_type': x.group(2),
        'article_num': replace_roman_nums_with_ints(x.group(3)),
        'section_num': replace_roman_nums_with_ints(x.group(4)),
        'clause_num': replace_roman_nums_with_ints(x.group(5)),
        'text': str.strip(x.group(0))
    }, matches['const_cit'])))

    cits.extend(list(map(lambda x: {
        'type': 'const_ref',
        'start_index': offset + x.start(),
        'end_index': offset + x.start() + len(x.group(0)),
        'line_num': line_num,
        'cit_id': -1,
        'text': str.strip(x.group(0))
    }, matches['const_ref'])))

    cits.extend(list(map(lambda x: {
        'type': 'federal_statute',
        'start_index': offset + x.start(),
        'end_index': offset + x.start() + len(x.group(0)),
        'line_num': line_num,
        'cit_id': -1,
        'body': 'federal',
        'article': replace_roman_nums_with_ints(x.group(1)),
        'chapter': '',
        'section': replace_roman_nums_with_ints(x.group(2)),
        'subsection': x.group(3),
        'text': str.strip(x.group(0)),
        'document': 'United States Code'
    }, matches['federal_statute'])))

    cits.extend(list(map(lambda x: {  # this one still processes a list not a match objet
        'type': 'state_statute',
        'start_index': offset + int(x[9]),  # temp: get offset from last list element of capture func
        'end_index': offset + int(x[9]) + len(x[0]),
        'line_num': line_num,
        'cit_id': -1,
        'body': body_abbrev_to_full(x[1]),
        'article': x[3],  # article
        'chapter': replace_roman_nums_with_ints(x[4]),  # chapter
        'section': replace_roman_nums_with_ints(x[6]),  # section
        'subsection': x[7],  # subsection
        'text': str.strip(x[0]),  # full match text
        'document': x[2],
        'date': x[8],
    }, matches['state_statute'])))

    cits.sort(key=lambda cit: cit['start_index'])

    return generate_citation_strings_from_pseudo_cits(file_id, leg_count, cits)

def empty_feature_filter(instring):
    return(re.sub(' [a-z]+=""','',instring))

def generate_citation_strings_from_pseudo_cits(file_id, id_index, cits):
    def cit_convert(cit):
        if cit['type'] == 'amend_ref':
            del cit['type']
            return empty_feature_filter(generate_amendment_reference(**cit))
        elif cit['type'] == 'const_cit':
            del cit['type']
            return empty_feature_filter(generate_const_citation(**cit))
        elif cit['type'] == 'const_ref':
            del cit['type']
            return empty_feature_filter(generate_const_reference(**cit))
        elif cit['type'] == 'state_statute' or cit['type'] == 'federal_statute':
            del cit['type']
            return empty_feature_filter(generate_statute_citation(**cit))

    new_cits = []

    for index, cit in enumerate(cits, start=1):
        cit['cit_id'] = file_id + str(id_index + index)
        new_cits.append(cit_convert(cit))

    return new_cits


def generate_amendment_reference(
        start_index,
        end_index,
        line_num,
        cit_id,
        amend_num,
        text):
    """Return a citation string for an informal reference to an amendment

    :param start_index: (int) Byte offset of text from beginning of file
    :param end_index: (int) end of text
    :param line_num: (int) line number from read file
    :param cit_id: (int) the id num of this citation
    :param amend_num: (int) the number of the amendment being referred to
    :param text: (str) the text holding the amendment reference
    :return: (str) the citation string in XML style
    """

    citation = '<reference ' \
               'id="{0}" ' \
               'entry_type="amendment" ' \
               'start="{1}" ' \
               'end="{2}" ' \
               'line="{3}" ' \
               'amendment="{4}">' \
               '{5}' \
               '</reference>' \
        .format(
        cit_id,
        start_index,
        end_index,
        line_num,
        amend_num,
        text
    )

    return citation


def generate_const_citation(start_index, end_index, line_num, cit_id, jurisdiction, art_type, article_num, section_num,
                            clause_num, text):
    """Return a citation string for a constitutional amendment or article citation

    :param start_index:
    :param end_index:
    :param line_num:
    :param cit_id:
    :param jurisdiction:
    :param art_type:
    :param article_num:
    :param section_num:
    :param clause_num:
    :param text:
    :return:
    """

    art = re.search('((?:art\.)|(?:ART\.)|(?:Art\.))', art_type)
    if art:
        art_type = 'article'
    else:
        art_type = 'amendment'
    citation = '<citation ' \
               'id="{0}" ' \
               'entry_type="constitutional_{1}" ' \
               'start="{2}" ' \
               'end="{3}" ' \
               'line="{4}" ' \
               'jurisdiction="{5}" ' \
               'article="{6}" ' \
               'section="{7}" ' \
               'clause="{8}">' \
               '{9}' \
               '</citation>' \
        .format(
        cit_id,
        art_type,
        start_index,
        end_index,
        line_num,
        jurisdiction,
        article_num,
        section_num or '',
        clause_num or '',
        text
    )

    return citation


def generate_const_reference(start_index, end_index, line_num, cit_id, text):
    """Return a citation string for a constitutional amendment or article citation

    :param start_index:
    :param end_index:
    :param line_num:
    :param cit_id:
    :param text:
    :return:
    """

    citation = '<reference ' \
               'id="{0}" ' \
               'entry_type="constitution" ' \
               'start="{1}" ' \
               'end="{2}" ' \
               'line="{3}">' \
               '{4}' \
               '</reference>' \
        .format(
        cit_id,
        start_index,
        end_index,
        line_num,
        text
    )

    return citation


def generate_statute_citation(start_index, end_index, line_num, cit_id, body, article, chapter, section, subsection,
                              text, document, date=''):
    """Returns a citation string for a statute citation

    :param document:
    :param date:
    :param start_index:
    :param end_index:
    :param line_num:
    :param cit_id:
    :param body:
    :param article:
    :param chapter:
    :param section:
    :param subsection:
    :param text:
    :return:
    """

    citation = '<citation ' \
               'id="{0}" ' \
               'entry_type="statute" ' \
               'start="{1}" ' \
               'end="{2}" ' \
               'line="{3}" ' \
               'body="{4}" ' \
               'document="{10}" ' \
               'article="{5}" ' \
               'chapter="{6}" ' \
               'section="{7}" ' \
               'date="{11}" ' \
               'location="{8}">' \
               '{9}' \
               '</citation>' \
        .format(
        cit_id,
        start_index,
        end_index,
        line_num,
        body.strip(),
        article.strip(),
        chapter.strip(),
        section.strip(),
        subsection.strip() if subsection else '',
        text.strip(),
        document.strip(),
        date.strip(),
    )

    return citation


def find_legislations(txt, file_id,quiet = True):
    """Returns a list of citation strings created from citations and informal amendment references in the given file

    :param txt:
    :param file_id:
    :return: (str) A list of citation strings
    """

    legs = []
    with open(txt, 'r', -1, 'utf-8') as instream:

        offset = 0
        line_num = 1

        for line in instream:

            # line_remainder = len(line)
            # legis_matches = find_legislations_in_line(line)  # get list of matches

            # get the matches in order
            # for matched_string in (legis_matches if legis_matches else ()):

            # get the start offest of the match
            # start_index = line.find(matched_string)

            # increment the global offset by the start offset
            # offset += start_index

            # create a citation
            cits = generate_legislation_citations_from_string(
                line,
                offset,
                line_num,
                len(legs),
                file_id.strip('\\/') + "_")
            cits2 = generate_other_leg_citations_from_string(line,
                offset,
                line_num,
                len(legs)+len(cits),
                file_id.strip('\\/') + "_")
            cits.extend(cits2)

            # decrement the line remainder by (the match length + start offset) to cut out "the line so far"
            # line_remainder -= last_cit_offset
            # offset += last_cit_offset
            if not quiet:
                for x in cits: print(x)
            legs.extend(cits)

            line_num = line_num + 1
            offset += len(line)
    # print(legs)
    return legs
