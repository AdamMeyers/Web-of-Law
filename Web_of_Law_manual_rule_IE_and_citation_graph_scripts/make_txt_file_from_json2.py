#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## code for converting CourtListener json files into txt and offset annotation

import re
import math
import time
import os
from wol_utilities import *
from xml.sax.saxutils import escape
from xml.sax.saxutils import unescape
from citation_tables import *

standard_citation_pattern = re.compile('([0-9]+)( *)('+court_reporter_rexp+')( +)([0-9]+)',re.I)

suppress_print_html_fields = ['div','center','b','i','u','br','h1','img','figure','article','body','center'\
                              'main','table','textarea','video','pre']
                              
convert_html_fields_to_spaces = ['br']

html_char_dict = {}

for code,char in [['amp','&'],['lt','<'],['gt','>'],['nbsp',' '],['cent','¢'],
                  ['pound','£'],['yen','¥'],['euro','€'],['copy','©'],['reg','®'],
                  ['quot','"'],['iexcl','¡'],['curren','¤'],['brvbar','¦'],['sect','§'],
                  ['uml','¨'],['ordf','ª'],['laquo','«'],['not','¬'],['shy','­'],['macr','¯'],
                  ['deg','°'],['plusmn','±'],['sup2','²'],['sup3','³'],['acute','´'],
                  ['micro','µ'],['para','¶'],['middot','·'],['cedil','¸'],['sup1','¹'],
                  ['ordm','º'],['raquo','»'],['frac14','¼'],['frac12','½'],['frac34','¾'],
                  ['iquest','¿'],['times','×'],['divide','÷'],['ETH','Ð'],['eth','ð'],
                  ['THORN','Þ'],['thorn','þ'],['AElig','Æ'],['aelig','æ'],['OElig','Œ'],
                  ['oelig','œ'],['Aring','Å'],['Oslash','Ø'],['Ccedil','Ç'],['ccedil','ç'],
                  ['szlig','ß'],['Ntilde','Ñ'],['ntilde','ñ'],
                  ['Aacute','Á'], ['Agrave','À'], ['Acirc','Â'], ['Auml','Ä'],
                  ['Atilde','Ã'], ['Aring','Å'], ['aacute','á'], ['agrave','à'],
                  ['acirc','â'], ['auml','ä'], ['atilde','ã'], ['aring','å'],
                  ['Eacute','É'], ['Egrave','È'], ['Ecirc','Ê'], ['Euml','Ë'],
                  ['eacute','é'], ['egrave','è'], ['ecirc','ê'], ['euml','ë'],
                  ['Iacute','Í'], ['Igrave','Ì'], ['Icirc','Î'], ['Iuml','Ï'],
                  ['iacute','í'], ['igrave','ì'], ['icirc','î'], ['iuml','ï'],
                  ['Oacute','Ó'], ['Ograve','Ò'], ['Ocirc','Ô'], ['Ouml','Ö'],
                  ['Otilde','Õ'], ['oacute','ó'], ['ograve','ò'], ['ocirc','ô'],
                  ['ouml','ö'], ['otilde','õ'], ['Uacute','Ú'], ['Ugrave','Ù'],
                  ['Ucirc','Û'], ['Uuml','Ü'], ['uacute','ú'], ['ugrave','ù'],
                  ['ucirc','û'], ['uuml','ü'], ['Yacute','Ý'], ['Yuml','Ÿ'],
                  ['yacute','ý'], ['yuml','ÿ']]:
    html_char_dict[code]=char
        
def get_replacement_for_html_code(number_code,letter_code):
    if number_code and (number_code.isdigit()):
        return(chr(int(number_code)))
    elif letter_code and (letter_code in html_char_dict):
        return(html_char_dict[letter_code])
    else:
        return(False)

def html_to_utf8_char_map(value):
    if not(value):
        return(value)
    html_char_pattern = re.compile('&((\#([0-9]+))|([a-z]+));')
    match = html_char_pattern.search(value)
    output = ''
    start = 0
    while match:
        replacement = get_replacement_for_html_code(match.group(3),match.group(4))
        if replacement:
            output = output+value[start:match.start()]+replacement
        else:
            output = output+value[start:match.end()]
        start = match.end()
        match = html_char_pattern.search(value,start)
    output = output+value[start:]
    return(output)

def get_attributes_and_values(html_content):
    attribute_value_pattern = re.compile('([^ =]+)="([^"]+)"')
    output = {}
    matches = attribute_value_pattern.finditer(html_content)
    for match in matches:
        output[match.group(1)] = match.group(2)
    return(output)

def create_offset_annotation(html_list,text,suppress_print_fields):
    ### fields to add: href, id
    ### maybe just be careful to match all fields and add them
    ### next -- write a generic parameter/value finder and factor into print-out
    html_table = {}
    html_tag_type_pattern = re.compile('^(/)?([^ ]+)')
    for offset,html_content in html_list:
        ## print(offset,html_content)
        html_tag_match = html_tag_type_pattern.search(html_content)
        if html_tag_match:
            html_tag = html_tag_match.group(2)
            html_stop = html_tag_match.group(1)  
            if html_tag in html_table:
                html_entry = html_table[html_tag]
                if html_stop and (len(html_entry[1])>0):
                    started_piece = html_entry[1].pop()
                    started_piece['end']=offset
                    if not html_tag in suppress_print_fields:
                        out_text = text[started_piece['start']:started_piece['end']]
                        started_piece['text']=out_text
                    html_entry[0].append(started_piece)
                else:
                    started_piece = get_attributes_and_values(html_content)
                    started_piece['type']=html_tag
                    started_piece['start']=offset
                    html_entry[1].append(started_piece)                    
            else:
                started_piece = get_attributes_and_values(html_content)
                started_piece['type']=html_tag
                started_piece['start']=offset
                html_entry = [[],[started_piece]]
                html_table[html_tag]=html_entry
    # print(started_piece)
    # print(offset)
    # print(html_content)
    return(html_table)

def eliminate_extra_lines(instring):
    ## eliminate double spacing and lines
    ## uses as padding, i.e., only keeps a carriage return
    ## if followed by an indent
    outstring = ''
    string_length = len(instring)
    for num in range(string_length):
        if (instring[num] == '\n') and (num < (string_length-5)):
            ## print('**',instring[num-2,num+3])
            if (instring[num]=='\t') or (instring[num+1:num+4]=='   '):
                outstring=outstring+instring[num]
            else:
                outstring=outstring+' <newline_ghost/>'
        else:
            outstring=outstring+instring[num]
    outstring=outstring+instring[(len(instring)-2):]
    return(outstring)

separator = re.compile('((\n)|( <newline_ghost/>))+')
separator2 = re.compile('((\n)|( <newline_ghost/>))')

def divide_up_text(instring):
    next_separator_match = separator.search(instring)
    start = 0
    output = []
    double_space_count = 0
    single_space_count = 0
    end_type = False
    while next_separator_match:
        if len(separator2.findall(next_separator_match.group(0))) > 1:
            double_space_count = double_space_count + 1
            if re.search('\n',next_separator_match.group(0)):
                end_type = 'double_paragraph'
            else:
                end_type = 'double'
        else:
            end_type = 'single'
            single_space_count = single_space_count + 1
        next_line =instring[start:next_separator_match.end()]
        output.append([next_line,end_type])
        start = next_separator_match.end()
        next_separator_match = separator.search(instring,start)
    if double_space_count >= (2 * single_space_count):
        spacing = 'double'
    else:
        spacing = 'single'        
    output.append([instring[start:],end_type])
    return(output,spacing)

def check_line_for_non_html_properties(instring):
    non_html,html_output = remove_xml_plus2(instring)
    enumerator='(([A-Z]|([0-9]+)|([IVXLDCM]{,4}))\.)'
    if re.search('^('+enumerator+'?)'+'((\t)|(     ))',non_html):
        is_indented = True
    else:
        is_indented = False
    if re.search('[\.\?\!\:][^a-zA-Z- ]* *$',non_html):
        end_sentence = True
    else:
        end_sentence = False
    if re.search('^[^A-Z0-9]*[a-z]',non_html):
        starts_with_lower_case = True
    else:
        starts_with_lower_case = False
    end_of_line_pattern = '(((\n)|([\t ]))*)$'
    footnote_anchor_pattern = re.search('[a-z]([\.\?\!\:\"]{1,2})([0-9]{1,3})',non_html)  ## group 2 is footnote number
    footnote_start_pattern = re.search('^( *)([0-9]{1,})'+end_of_line_pattern,non_html) ## group 2 is footnote number
    page_number_pattern = re.search('^( {20,})-?([0-9]{1,})-?'+end_of_line_pattern,non_html) ## group 2 is page number
    if footnote_anchor_pattern:
        citation_match = standard_citation_pattern.search(non_html)
        if citation_match:
            c_start,c_end = citation_match.start(),citation_match.end()
            f_start,f_end = footnote_anchor_pattern.start(),footnote_anchor_pattern.end()
            if ((f_start>=c_start) and (f_start<=c_end)) or ((f_end>=c_start) and (f_end<=c_end)):
                footnote_anchor_pattern = False
    if page_number_pattern and footnote_start_pattern:
        footnote_start_pattern = False
    ### extend page number pattern to more spaces and make hyphen optional
    if is_indented and re.search('^([\t ])*[vV][\.]?'+end_of_line_pattern,non_html):
        v_line = True
    else:
        v_line = False
    return(is_indented,end_sentence,starts_with_lower_case,footnote_anchor_pattern,footnote_start_pattern,page_number_pattern,v_line)

def stand_alone_line(instring):
    month_string = '((january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december)|(jan\.?)|(feb\.?)|(mar\.?)|(apr\.)|(jun\.?)|(jul\.)|(aug\.)|(sept?\.?)|(oct\.?)|(nov\.?)|(dec\.?))'
    date_string = month_string+'( *)((3[01])|([12][0-9])|[0-9]),( *)((1[789])|(20))([0-9]{2})'
    date_pattern = re.compile('^('+date_string+')$',re.I)
    string,html = remove_xml_plus2(instring)
    string = string.strip(' ')
    ##    string = string.strip(r'\\n')
    string = string.strip('\n')
    string = string.strip(' <newline_ghost/>')
    if date_pattern.search(string):
        return(True)
    elif re.search('^([IVXLD]+\.?)$',string):        
        return(True)
        ## roman numeral with optional period
    elif re.search('^[ ]{20,}(([A-Z])|([0-9]+)|([IVXLDCM]{,4}))\. ([A-Z ]*)(\n*)$',instring):
        ## a very indented (centered) line followed by some enumeration (A., I. ...) and an optional allcaps string
        return(True)
        
def has_possible_sentence_end(instring):
    if stand_alone_line(instring):
        return(True)
    if re.search('[\.\?\!\:]([^a-zA-Z0-9]*)(((\n)|( <newline_ghost/>))*)$',instring):
        return(True)

def has_possible_sentence_begin(instring):
    if stand_alone_line(instring):
        return(True)
    if re.search('^([^a-zA-Z0-9]*)[A-Z]',instring):
        return(True)

def possible_centered_line(instring):
    first_position = re.compile('^((<[^>]+>)*)')
    first_position_match = first_position.search(instring)
    if first_position_match:
        centering_profile = re.search('^([ \t]*)(.*)(((\n)|( <newline_ghost/>))*)$',instring[first_position_match.end():])
        if centering_profile:
            indent = len(centering_profile.group(1))
            possible_centered_length = len(centering_profile.group(2))
            if (indent >= 10) and (possible_centered_length<=30):
                return(True)

def relatively_centered(line1,line2,line2_is_indented):
    no_html1,html1 = remove_xml_plus2(line1)
    no_html2,html2 = remove_xml_plus2(line2)
    if ((not(has_possible_sentence_end(no_html1))) or (not has_possible_sentence_begin(no_html2))) and line2_is_indented:
        return(True)
    
def modify_line_for_paragraphhood(last_line_profile,last_spacing,line,local_spacing,global_spacing,last_footnote_reference,last_realized_footnote,last_page_number,recent_end_sentence_line):
    ## if line ends in <newline_ghost/>\n
    ##    it is double-spaced
    ## if line n ends in period/question-mark etc and
    ## line n+1 starts with indent, then it is a paragraph boundary
    ## if a line ends in  <newline_ghost/>, does not end in  period/question-mark etc
    ## and the subsequent line does not begin with an indent, there is no paragraph boundary
    ## if line N and N+1 both begin with indent and line N ends with \n, not double spaced
    ## and line N does not end in period/question-mark-etc, there is no paragraph boundary
    ## it is however part of an indented region (independent of single/double spacing?)
    ##
    ## also page-number, footnote, footnote-number -- page number -- skip for paragraph purposes
    ## footnote mark -- turn into xml + spaces -- occurs after sentence-ending punctuation 
    ## it should increment preceding footnote by 1
    ##
    ## footnote body = number on line + next line = footnote (single spaced) and can break up paragraph 
    ##
    ## 
                ## leaving an indented block, make a new paragraph, even if not indented
            ## -- possibly mark block as indented
            ## -- example "The letter went on to detail ..."
            ## -- title-ish segments: "A.         Rhode Island Mutual Rescission Law"
            ##                         B.          Relevance of Pruco's Alleged Misrepresentations
    word_pattern = re.compile('[A-Za-z0-9]+')
    started_footnote_division = False
    end_page = False
    paragraph_interuption = False
    first_position = re.compile('^((<[^>]+>)*)')
    separator_match = separator.search(line)
    started_paragraph = False
    if separator_match:
        is_indented,end_sentence,starts_with_lower_case,footnote_anchor_pattern,footnote_start_pattern,page_number_pattern,v_line=check_line_for_non_html_properties(line[:separator_match.start()])
    else:
        is_indented,end_sentence,starts_with_lower_case,footnote_anchor_pattern,footnote_start_pattern,page_number_pattern,v_line=check_line_for_non_html_properties(line)
    if footnote_anchor_pattern:
        potential_footnote_number = int(footnote_anchor_pattern.group(2))
        if (potential_footnote_number > last_footnote_reference) and ((last_footnote_reference+3)>potential_footnote_number):
            ## allows for the program missing some footnotes, but if too many are missing, there is probably a serious error
            ## if it turns out that there are no actual footnotes, this process should be reversed (later processing)
            ## format: <a class=\"footnote\" href=\"#fn1\">1</a>
            href_string = '#fn'+str(potential_footnote_number)
            line = line[:footnote_anchor_pattern.start(2)]+'<a class=\"footnote\" href=\"'+href_string+'\">'+footnote_anchor_pattern.group(2)+'</a>'+line[footnote_anchor_pattern.end(2):]
            last_footnote_reference = potential_footnote_number
    elif footnote_start_pattern:
        potential_realized_footnote = int(footnote_start_pattern.group(2))
        if (potential_realized_footnote > last_realized_footnote) and ((last_realized_footnote+3)>potential_realized_footnote):
            href_string = '#fn'+str(potential_realized_footnote)
            line = line[:footnote_start_pattern.start(2)]+'<div class=\"footnote\" id=\"'+href_string+'\">'+footnote_start_pattern.group(2)+line[footnote_start_pattern.end(1):]
            started_footnote_division = True
            last_realized_footnote = potential_realized_footnote
        ## <p><div class=\"footnotes\">\n </p>
        ## <a class=\"footnote\" href=\"#fn1\">1</a>\n
        ## Text of footnote ...
        ## .. other footnotes
        ## </div></p>
        ## make these endnotes
    elif page_number_pattern:
        current_page = int(page_number_pattern.group(2))
        if (current_page > last_page_number):
            line = line[:page_number_pattern.start(2)-1]+(' '*(len(page_number_pattern.group(0))+2))+line[page_number_pattern.end(2)+1:]
            end_page = current_page
            ## erase page numbers and re-introduce them as meta-language dividing up text
    if footnote_start_pattern or page_number_pattern:
        paragraph_interuption = True
    elif is_indented:
        ## print('last',last_line_profile)
        first_word = word_pattern.search(line)
        if first_word:
            ref_word = first_word.group(0).lower()
        else:
            ref_word = False
        if recent_end_sentence_line and (not v_line) and re.search('^([^a-zA-Z0-9]*)[A-Z]',line) and (not ref_word in ending_words):
            last_line_profile['string']=last_line_profile['string']+'</p>'
            line = '<p>'+line
            ## print(1,line)
            ## input('pause')
        elif last_line_profile and (not ref_word in ending_words) and\
          ((starts_with_lower_case and last_line_profile['is_indented']) or \
           (last_line_profile['v_line'] and last_line_profile['is_indented']) or \
           ((global_spacing == 'double') and \
            (((last_spacing != 'double_paragraph') and (not last_line_profile['end_page']) and last_line_profile['is_indented']) \
              or (v_line and last_line_profile['is_indented'])))):
              ## print(2,line)
              ## input('pause')
            if v_line or last_line_profile['v_line']:
                pass
            elif (not (relatively_centered(last_line_profile['string'],line,True))):
                last_line_profile['string']=last_line_profile['string']+'</p>'
                ## print('2a',line)
                ## input('pause')
                line = '<p>'+line
                started_paragraph = True 
            elif possible_centered_line(last_line_profile['string']) and (not possible_centered_line(line)) \
              and has_possible_sentence_begin(line) and has_possible_sentence_end(last_line_profile['string']):
              ## print('2b',line)
              ## input('pause')
                last_line_profile['string']=last_line_profile['string']+'</p>'
                line = '<p>'+line
                started_paragraph = True 
        elif last_line_profile and  (last_spacing == 'single') and (local_spacing == 'single') and (not last_line_profile['is_indented']) \
           and (has_possible_sentence_end(last_line_profile['string'])) and (has_possible_sentence_begin(line)) and (not ref_word in ending_words):
           ## print(3,line)
            last_line_profile['string']=last_line_profile['string']+'</p>'
            line = '<p>'+line
            started_paragraph = True
        elif (last_line_profile) and (last_line_profile['local_spacing'] == 'double_paragraph') and (global_spacing == 'single') and (local_spacing == 'single'):
            ## print(3.5,line)
            last_line_profile['string']=last_line_profile['string']+'</p>'
            line = '<p>'+line
            started_paragraph = True
        elif (last_line_profile and relatively_centered(last_line_profile['string'],line,True)) or (ref_word in ending_words):
            ## print(4,line)
            pass
        else:
            ## print(5,line)
            ## input('pause')
            if not last_line_profile:
                first_pos_match = first_position.search(line)
                if first_pos_match:
                    line = line[:first_pos_match.end()]+'<p>'+line[first_pos_match.end():]
                else:                
                    line = '<p>'+line
                started_paragraph = True
            elif ((not end_page) or last_line_profile['end_page']):
                last_line_profile['string']=last_line_profile['string']+'</p>'
                line = '<p>'+line
                started_paragraph = True
            # note 'double' and 'double paragraph'
            # for double spaced text, possibly treat 'double' as 'single;
            # make special exception regarding 'v.'
            # -- if on its own line, join to previous line
            # --    even if previous line ends in double_paragraph
    elif last_line_profile and (last_spacing in ['single','double']) and (global_spacing == 'double') and (local_spacing == 'double') and has_possible_sentence_end(last_line_profile['string']) and has_possible_sentence_begin(line) and last_line_profile['is_indented']:
        last_line_profile['string']=last_line_profile['string']+'</p>'
        line = '<p>'+line
        started_paragraph = True    
    elif not last_line_profile:
        start_pattern = re.search('^((<[^>]+>)*)[^<]',line)
        if start_pattern:
            line = line[:start_pattern.end(1)]+'<p>'+line[start_pattern.end(1):]
            started_paragraph = True
    line_profile = {'string':line,'is_indented':is_indented,'v_line':v_line,'local_spacing':local_spacing,'end_page':end_page,'end_sentence':end_sentence}
    return(line_profile,last_line_profile,last_footnote_reference,last_realized_footnote,started_footnote_division,end_page,paragraph_interuption,started_paragraph)

def modify_footnote_output(footnote_output):
    output = []
    is_div = False
    is_indented = False
    previous_profile = False
    ## add </p> before </div> if needed *** 57 ***
    for line_profile in footnote_output:
        if re.search('<div',line_profile['string']):
            is_div = True
            if previous_profile and not re.search(' *</p>$',previous_profile['string']):
                previous_profile['string']=previous_profile['string']+'</p>'
            if previous_profile:
                output.append({'string':'</div>','html_only':True})
            output.append(line_profile)
        elif is_div and not re.search('<p>',line_profile['string']):
            line_profile['string']='<p>'+line_profile['string']
            is_div = False
            output.append(line_profile)         
        elif re.search('^((\t)|(     ))',line_profile['string']):
            if previous_profile and not re.search(' *</p>$',previous_profile['string']):
                previous_profile['string']=previous_profile['string']+'</p>'
            line_profile['string']='<p>'+line_profile['string']
            output.append(line_profile) 
        else:
            output.append(line_profile)
        previous_profile = line_profile
    if previous_profile and not re.search(' *</p>$',previous_profile['string']):
        previous_profile['string']=previous_profile['string']+'</p></div>'
    return(output)

def reform_divisions(valuelist,global_spacing):
    ## print(global_spacing)
    ## next add </div> for footnotes
    ##      and other footnote structure (paragraph markers?)
    ## for output, move <p> after certain initial html (span, pre, div, ???)
    ## -- new paragraph if previous line centered and current line indented and begin with capital
    ## see June 28, 2013 (similar with Roman Numerals)
    started_page_structure = {'string':'<span class=\"page\" id=\"#page1\">','html_only':True}
    output = [started_page_structure]
    first_position = re.compile('^(<[^>]+>)*')
    footnote_output = []
    last_line_profile = False
    last_spacing = False
    last_footnote_reference = 0
    last_realized_footnote = 0
    last_page_number = 0
    started_page = 1
    footnote_on = False
    next_page_html = False
    current_page_html = False
    recent_end_sentence_line = False
    for line,local_spacing in valuelist:
        line_profile,last_line_profile,last_footnote_reference,last_realized_footnote,\
          started_footnote_division,end_page,paragraph_interuption,started_paragraph = \
          modify_line_for_paragraphhood(last_line_profile,last_spacing,line,local_spacing,\
                                        global_spacing,last_footnote_reference,last_realized_footnote,last_page_number,recent_end_sentence_line)
        # print(1,line)
        # print(2,line_profile)
        # print(3,last_line_profile)
        # input('pause')
        if end_page:
            ## output.append([{'string':'<\span>','html_only':True}])
            if end_page !=started_page:
                revised_page_number_string = '#page'+str(started_page)+'-'+str(end_page)
                started_page_structure['string']='<span class=\"page\" id=\"'+revised_page_number_string+'">'
            last_page_number = end_page
            started_page = end_page+1
            next_page_string = '<span class=\"page\" id=\"#page'+str(started_page)+'\">'
            next_page_html = {'string':next_page_string,'html_only':True}
        ## choices: 1) add line to output; 2) add line to footnote_output;
        if started_footnote_division:
            footnote_on = True
        if footnote_on and end_page:
            footnote_on = False
        if footnote_on:
            line_profile['footnote'] = True
        else:
            line_profile['footnote'] = False
        if last_line_profile and last_line_profile['footnote']:
            footnote_output.append(last_line_profile)
        else:
            if last_line_profile:
                output.append(last_line_profile)
            if current_page_html:
                output.append({'string':'</span>','html_only':True})
                output.append(current_page_html)
                current_page_html = False
            if (not line_profile['v_line']) and (not line_profile['end_page']) and (not line_profile['footnote']):
                recent_end_sentence_line = line_profile['end_sentence']
        last_line_profile = line_profile
        last_spacing = local_spacing
        if next_page_html:
            current_page_html = next_page_html
            started_page_structure = current_page_html
            next_page_html = False
    if last_line_profile['footnote']:
        footnote_output.append(last_line_profile)
    else:
        output.append(last_line_profile)
    if (len(output)>1) and (output[-1]['string'] == started_page_structure['string']):
        output.pop()
    if (len(output)>2) and (re.search('^((<(/?)[^>]+>)*)$',output[-1]['string'])) and (output[-2]['string'] == started_page_structure['string']):
        output.pop(-2)
    footnote_output = modify_footnote_output(footnote_output)
    return(output,footnote_output)
    
def modify_print_formatted_text(value):
    value = eliminate_extra_lines(value)
    ## value = re.sub('<newline_ghost/><newline_ghost/>','<double_space_ghost/>')
    valuelist,spacing = divide_up_text(value)
    output,footnote_output = reform_divisions(valuelist,spacing)
    return(output,footnote_output)

    ######## 1. Turn footnotes into endnotes #########
    ## -- look for patterns like: a) number on its own line followed by a single spaced paragraph
    ## --                         b) a matching number at the end of a previous nearby paragraph
    ## --                         c) a sentence broken in the middle by this numbered paragraph -- this should happen repeatedly
    ##    Change this into a separate section at the end called Endnotes
    ##    Add references to the footnotes in html form
    ## Pointer to Footnote
    ## <sup><a href="#fn2" id="ref2">
    ## Text of Footnote
    ## <sup id="fn2">2. [Text of footnote 2]<a href="#ref2" title="Jump back to footnote 2 in the text.">↩</a></sup>

def backwards_balanced_xml(html_list,types):
    balance_lookup = {}
    for typ in types:
        balance_lookup[typ]=0
    for pair in html_list:
        ref_list = pair[1].split(' ')
        ref = ref_list[0]
        if ref in balance_lookup:
            balance_lookup[ref]=balance_lookup[ref]+1
        elif (ref[0]=='/') and (ref[1:] in balance_lookup):
            ref = ref[1:]
            balance_lookup[ref]=balance_lookup[ref]-1
    balanced = True
    for key in balance_lookup:
        if balance_lookup[key] != 0:
            balanced = False
    return(balanced)

def possibly_ammend_paragraphs(value):
    repeating_middle = '((((<(/?)(P|p|DIV|div)([^>]*))*>(( |'+os.linesep+')*))|((<span class="num">[0-9]+</span>( |'+os.linesep+')*)))+)'
    pattern = re.compile('[a-zA-Z][^A-Za-z]+[vV][Ss]?\.?[^a-z]*'+repeating_middle+'[A-Z]')
    match = pattern.search(value)
    if match:
        text,html = remove_xml_plus2(match.group(1))
        if backwards_balanced_xml(html,['p','P','div','DIV']):
            return(value[:match.start(1)]+(len(remove_xml_plus(match.group(1)))*' ')+value[match.end(1):])
        else:
            return(value)
    else:
        return(value)

def print_meta_field(field,value):
    output_string = ''
    if type(value) == dict:
        for sub_field in value:
            output_string = output_string+print_meta_field(field+'_'+sub_field,value[sub_field])
    elif type(value) == list:
        for item in value:
            output_string = output_string+'<'+field+'>'+str(item)+'</'+field+'>'+os.linesep
    elif value == None:
        pass
    else:
        output_string = '<'+field+'>'+str(value)+'</'+field+'>'+os.linesep
    return(output_string)

def parse_out_txt_file2(infile,field_override=False,outfile_mod=False,map_html_characters_to_utf8=True):
    import json
    output_table  = {}
    base = infile.rstrip('json')
    dir,base = get_dir_plus_file(base)
    field_list = ['plain_text', 'html','html_lawbox', 'html_columbia', 'html_with_citations']
    text = False
    meta_fields = ['citation']
    with open(infile) as instream:
        json_dict = json.load(instream)
        if field_override and (field_override in json_dict) and alpha_check(json_dict[field_override]):
            value = json_dict[field_override]
            ## remove return characters from dos text
            value = value.replace('\r\n','\n')
            value = value.replace(chr(12),' ')
            if map_html_characters_to_utf8:
                value = html_to_utf8_char_map(value)
            field = field_override
            output_table[field] = value
        else:
            for field in field_list:
                if field in json_dict:
                    value = json_dict[field]
                    ## remove return characters from dos text
                    if value:
                        value = value.replace('\r\n','\n')
                        value = value.replace(chr(12),' ')
                    if map_html_characters_to_utf8:
                        value = html_to_utf8_char_map(value)
                    if not(alpha_check(value)):
                        pass
                    else:
                        output_table[field] = value
    last_end_in_case_middle = False
    text,html_outlist = '',False
    while ((len(field_list)>0) or field) and not text:
        if field_override and (field in output_table):
            field = field_override
        elif len(field_list)>0:
            field = field_list.pop()
        else:
            field = False
            ### print(infile,field,field in output_table)
        if field and (field in output_table):
            value = output_table[field]
            if not(re.search('<p>',value)):
                text_value,footnote_value = modify_print_formatted_text(value)
                value = ''
                for item in text_value:
                    ## print(item)
                    value = value+item['string']
                if len(footnote_value)>0:
                    value=value+'<div class=\"footnotes\">'
                    for item in footnote_value:
                        value=value+item['string']
                    value=value+'</div>'
            value = possibly_ammend_paragraphs(value)
            value = re.sub('<newline_ghost/></p>','\n</p>',value)
            value = re.sub('<newline_ghost/>','',value)
            value = re.sub('</?br>',' ',value)
            # if '''"case_cite">''' in value:
            #     print(value)
            #     input('pause')
            text,html_outlist = remove_xml_plus2(value)
    if html_outlist:
        html_out_table = create_offset_annotation(html_outlist,text,suppress_print_html_fields)
    else:
        html_out_table = False
    if outfile_mod:
        outfile_name = dir+outfile_mod+base+'html-list'
    else:
        outfile_name = dir+base+'html-list'
    with open(outfile_name,'w') as outstream:
        for field in meta_fields:
            if field in json_dict:
                value = json_dict[field]
                outstream.write(print_meta_field(field,value))
        if html_out_table:
            for key in html_out_table:
                completed,partially_completed = html_out_table[key]
                for annotation in completed:
                    output_string = '<'+key
                    for attrib in ['start','end']:
                        if (attrib in annotation) and boolean_check(annotation[attrib]):
                            ## rules out instances of False
                            output_string=output_string+' '+attrib+'="'+str(annotation[attrib])+'"'
                    for attrib in annotation:
                        if not attrib in ['start','end','text','type']:
                            if annotation[attrib]: 
                                ### attrib is not equal to False
                                output_string=output_string+' '+attrib+'="'+str(annotation[attrib])+'"'
                    if 'text' in annotation:
                        if (annotation['type']=='p') and ('start' in annotation) and \
                          ('end' in annotation) and ('text' in annotation) and (annotation['start'] < annotation['end']):
                            ## replace_newlines_between_paragraph_boundaries(text,html_outlist)
                            annotation['text'] = re.sub('\n',' ',annotation['text'][:-1])+annotation['text'][-1]
                            text=text[:annotation['start']]+annotation['text']+text[annotation['end']:]
                    ## first replace newlines with spaces, unless they reflect paragraph boundaries.
                    ## the last character in each paragraph is not changed (it is assumed to be a newline
                    ## character, except, perhaps for the last one in the file).                        
                        output_string=output_string+'>'+wol_escape(annotation['text'])+'</'+key+'>'
                    else:
                        output_string = output_string + '/>'
                    output_string = output_string+os.linesep
                    outstream.write(output_string)
                for annotation in partially_completed:
                    output_string = '<'+key
                    for attrib in annotation:
                        if not attrib in ['start','end','text']:
                            if annotation[attrib]: 
                                ### attrib is not equal to False
                                output_string=output_string+' '+attrib+'="'+str(annotation[attrib])+'"'
                    if 'text' in annotation:
                        output_string=output_string+'>'+wol_escape(annotation['text'])+'</'+key+'>'
                    else:
                        output_string = output_string + '/>'
                    output_string = output_string+os.linesep
                    outstream.write(output_string)
    if outfile_mod:
        outfile_name = dir+outfile_mod+base+'txt'
    else:
        outfile_name = dir+base+'txt'
    with open(outfile_name,'w') as outstream:
        outstream.write(text)


            

