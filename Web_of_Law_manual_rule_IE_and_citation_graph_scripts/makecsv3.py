__author__ = 'halley'
import os
import json
from court_listener_directory_name_dict import *
from wol_utilities import *
import xml.etree.ElementTree as ET

global_citations = {}

## district_courts = {'casd':('San Diego', 'California', 'CA')}
party_key_hash = {}

district_court_file = 'district_courts.csv'
district_courts = {}
csv_column_list = ['id1', 'lookup_key','entry_type','folder', 'full_name', 'casename','district_city', 'district_state', 'district_state_abbrev', \
                        'party1', 'party2', 'party1_short','party2_short','docket_number', 'standard_reporter', 'volume', 'page_number', 'year','alternative_case_names']
                        
with open(district_court_file) as instream:
    for line in instream:
        line = line.strip(os.linesep)
        line_list = line.split(',')
        district_courts[line_list[0]]=line_list[1:]


def get_last_name_from_party(name):
    word_pattern = re.compile('[a-z]+',re.I)
    count = 0
    last_word = False
    next_word = word_pattern.search(name)
    found = False
    while next_word:
        if last_word:
            if  next_word.group(0).lower() in after_last_name_words:
                return(last_word.group(0))
            elif next_word.group(0).lower() in POS_dict:
                POS = POS_dict[next_word.group(0).lower()]
                if ('SCONJ' in POS) or ('PREP' in POS):
                    return(last_word.group(0))
                else:
                    last_word = next_word
            last_word = next_word
        elif not next_word.group(0).lower() in POS_dict:
            last_word = next_word
        else:
            POS = POS_dict[next_word.group(0).lower()]
            if ('NOUN' in POS):
                last_word = next_word
        next_word = word_pattern.search(name,next_word.end())
        if last_word and (not next_word):
            return(last_word.group(0))
        elif last_word and next_word and re.search('[,;:]', name[last_word.end():next_word.start()]) and \
          (not (last_word.group(0).lower() in POS_dict)) and (next_word.group(0).lower() in POS_dict):
            return(last_word.group(0))
    last_name_pattern = re.compile(' ([a-z-]+)(,|( *$))',re.I)
    match = last_name_pattern.search(name)
    if match:
        return(match.group(1))
    else:
        return(name)

def string_simplified(instring):
    out_string = re.sub('[^a-z]','',instring.lower())
    return(out_string)

def first_and_last_simplified(instring):
    words = instring.split(' ')
    if len(words)>2:
        first_word = re.sub('[^a-z]','',words[0].lower())
        last_word =  re.sub('[^a-z]','',words[-1].lower())
        return(first_word+last_word)
    else:
        return(instring)

def typo_compatible_substring(long_string,short_string):
    ## returns True if and adjusted short_string is a substring of
    ## long_string. Allowed adjustments include: (1) delete the first
    ## or last letter of short_string; or (b) delete any middle
    ## character; or (c) insert a character in the middle; or (d)
    ## replace one character in the middle for another character
    if (len(long_string)-len(short_string))>2:
        return(False)
    for char in '()[]*+?.@':
        short_string = short_string.replace(char,'')
    for position in range(len(short_string)):
        if position == 0:
            test_string = short_string[1:]
            if test_string in long_string:
                return(True)
        elif position == len(short_string)-1:
            test_string = short_string[:-1]
            if test_string in long_string:
                return(True)
        else:
            test_string1 = short_string[:position]
            test_string2 = short_string[position+1:]
            test_string3 = short_string[position:]
            if re.search(test_string1+'.?'+'('+test_string2+'|'+test_string3+')',long_string):
                return(True)

def possible_word_member(word1,long_list):
    for word2 in long_list:
        real_word2 = word2
        word2 = word2.strip(',.:()')
        if word2.startswith(word1) or typo_compatible_substring(word2,word1):
            return(real_word2)
        elif (len(word2) == 1) and word1.startswith(word2):
            return(real_word2)
        elif (word1 == 'rr') and (word2 == 'railroad'):
            ## this should be more general
            return(real_word2)
        else:
            possible_match = True
            for char in word1[:]:
                if char.isalpha():
                    if (not char in word2):
                        possible_match = False
                    else:
                        position = word2.index(char)
                        word2 = word2[position:]
                        ## this insures characters occur in 
                        ## same order in both words
            if possible_match:
                return(real_word2)
                    
            

def basically_citation_compatible2 (short_string,long_string):
    if string_simplified(short_string) in string_simplified(long_string):
        return(True)
    elif string_simplified(short_string) in first_and_last_simplified(long_string):
        return(True)
    else:
        short_list = short_string.lower().split(' ')
        long_list = long_string.lower().split(' ')
        new_short_list = []
        new_long_list = []
        abbrev = ''
        other_abbrev = False
        for index in range(len(long_list)):
            word = long_list[index].strip(',.:()')
            if (len(word)>0) and (not word in citation_closed_class):
                long_list[index] = word
                new_long_list.append(word)
            if len(word)>0 and (not word in citation_filler_words):
                if word in optional_abbrev_words:
                    if not other_abbrev:
                        other_abbrev = abbrev
                else:
                    if other_abbrev:
                        other_abbrev = other_abbrev + word[0]
                abbrev = abbrev+word[0]
        for index in range(len(short_list)):
            word = short_list[index].strip(',.:()')
            if (len(word)>0) and (not word in citation_closed_class):
                new_short_list.append(word)
        match = True
        match_count = 0
        non_match_count = 0
        for word1 in short_list:
            word1 = word1.strip(',.:()')
            if possible_word_member(word1,long_list):
                match_count = match_count + 1
            else:
                non_match_count = non_match_count + 1
        if match_count > non_match_count:
            return(True)
            ## checks for the superset case
        elif abbrev.startswith(short_string.lower()) or (other_abbrev and other_abbrev.startswith(short_string.lower())):
            return(True)
            ## abbreviation case
        elif (len(new_long_list)>1) and (len(new_short_list)==1) and (new_short_list[0] in new_long_list):
            return(True)
        elif (len(new_long_list)>1) and (len(new_short_list)>2) and ((new_short_list[0]+new_short_list[-1]) in (new_long_list[0]+new_long_list[-1])):
            return(True)        
                
def basically_citation_compatible (short_string,long_string):
    if basically_citation_compatible2(short_string,long_string):
        return(True)
    elif basically_citation_compatible2(long_string,short_string):
        return(True)
    else:
        found_comma = False
        if ',' in long_string:
            position = long_string.index(',')
            long_string = long_string[:position]
            found_comma = True
        ## remove info after comma to shorten long_string
        if ',' in short_string:
            position = short_string.index(',')
            short_string = short_string[:position]
            found_comma = True        
        ## remove info after comma to shorten short_string
        if found_comma and (basically_citation_compatible2(short_string,long_string) or \
          basically_citation_compatible2(long_string,short_string)):
            return(True)

def overlap_characters(name1,name2):
    ## calculate dice score for character overlap
    ## 2 X overlap / len(name1) + len(name2)
    list2 = list(name2)
    denominator = len(name1)+len(name2)
    matches = 0
    for character in name1:
        if character in list2:
            matches = matches+1
            list2.remove(character)
    return(2 * matches/denominator)

def remove_parenthesized_string (instring):
    parenthesis_pattern = re.compile(' ?\([^\)]*\) ?')
    match = parenthesis_pattern.search(instring)
    while match:
        instring = instring[:match.start()]+instring[match.end():]
        match = parenthesis_pattern.search(instring)
    return(instring)

def other_case_name_citation_compatible(name1,name2):
    name1 = remove_parenthesized_string(name1)
    name2 = remove_parenthesized_string(name2)
    short_name1 = ''
    short_name2 = ''
    word_list1 = []
    word_list2 = []
    for word in name1.split(' '):
        word = word.lower().strip(',.\"\'s-:\(\]\)\[')
        if (word in ['ex','parte','case','in','re','the','matter','of']) or re.search('^[0-9]+$',word) or (word in person_ending_words+org_ending_words):
            pass
        else:
            short_name1 = short_name1+word
            word_list1.append(word)
    for word in name2.split(' '):
        word = word.lower().strip(',.\"\'s-:\(\]\)\[')
        if (word in ['ex','parte','case','in','re','the','matter','of']) or re.search('^[0-9]+$',word) or (word in person_ending_words+org_ending_words):
            pass
        else:
            short_name2 = short_name2+word
            word_list2.append(word)
    if (short_name1 in short_name2): 
        ## name2 may be abbreviated
        ## startswith is more general than ==
        return(True)
    elif typo_compatible_substring(short_name2,short_name1):
        return('Typo')
    elif (len(word_list1)>0) and (len(word_list2)>0) and ((word_list1[-1]==word_list2[-1]) or (word_list1[0]==word_list2[0])):
        return(True)
    else:
        overlap =  overlap_characters(short_name1,short_name2)
        if overlap>.8:
            return(True)
        words_in_common = 0
        missing_words = 0
        ## do a dice score again
        for word in word_list1:
            word_match = possible_word_member(word,word_list2)
            if word_match:
                words_in_common = words_in_common+1
                word_list2.remove(word_match)
            elif not word in citation_closed_class:
                missing_words = missing_words+1
        for word in word_list2:
            if not word in citation_closed_class:
                missing_words = missing_words+1
        ## add in all the words not removed by matching
        ## modified dice score -- only count words not in citation_closed_class
        if (words_in_common>0):
            dice = (2*words_in_common)/((2*words_in_common)+ missing_words)
            if (dice > .8):
                return(True)

def check_text_for_parties(party1,party2,txt_file):
    found1 = False
    found2 = False
    with open(txt_file) as instream:
        for line in instream:
            line = line.upper()
            if (not found1) and (party1 in line):
                found1 = True
            if (not found2) and (party2 in line):
                found2 = True
            if found1 and found2:                
                return(True)

def bad_text_file(txt_file):
    with open(txt_file) as instream:
        for line in instream:
            if re.search('^ *No +page +to +display *$',line):
                return(True)

def compatible_other_case(attributes,values,trace=False):
    if ('party1' in values) and ('party2' in values) and values['party1'] and values['party2']:
        return(False)
    elif ('casename' in values) and ('name' in attributes):
        compatibility_check =  other_case_name_citation_compatible(values['casename'],attributes['name'])
        if compatibility_check == 'Typo':
            values['casename']=attributes['name']
            ## typos are most likely due to metatags, not due to tags in text
        if compatibility_check:
            return(True)
        else:
            return(False)
    else:
        return(False)

def compatible_X_vs_Y_case(attributes,values,trace=False):
    if not 'party2' in values:
        return(False)
    elif basically_citation_compatible(values['party1'],attributes['party1']) or  basically_citation_compatible(values['party2'],attributes['party2']):
        return(True)
    elif basically_citation_compatible(values['party1'],attributes['party2']) and  basically_citation_compatible(values['party1'],attributes['party2']):
        ## rarely, there is a reversal in roles between the 2 sources
        return(True)

    ## still need to check for bad text file and check_text_for_parties

def check_text_for_casename(namestring,txt_file):
    words = []
    found = []
    for word in namestring.split(' '):
        word = word.lower().strip(',.\"\'s-:\(\]\)\[')
        if (word in ['ex','parte','case','in','re','the','matter','of']) or re.search('^[0-9]+$',word) or (word in person_ending_words+org_ending_words):
            pass
        else:
            words.append(word)
    if not words:
        return(False)
    else:
        with open(txt_file) as instream:
            for line in instream:
                line = line.lower()
                for word in words[:]:
                    if word in line:
                        found.append(word)
                        words.remove(word)
    if len(words)==0:
        return(True)
    else:
        return(False)

def X_v_Y_compatible_with_other_citation(party1_string,party2_string,casename_string):
    ## use existing string compares
    return(other_case_name_citation_compatible(party1_string,casename_string) or \
           other_case_name_citation_compatible(party2_string,casename_string) or \
           basically_citation_compatible(party1_string,casename_string) or \
           basically_citation_compatible(party2_string,casename_string))

def merged_case_other_match(merged_string, first_case_citation_other,citation_dict):
    ## print(merged_string)
    big_other_string = ''
    for citation_id in first_case_citation_other:
        big_other_string = big_other_string + ' ' + citation_dict[citation_id]['name']
    ## print(big_other_string)
    if other_case_name_citation_compatible(merged_string,big_other_string):
        return(True)
    else:
        return(False)

def probably_OK_first_citation(first_citation_object):
    if ('line' in first_citation_object) and (int(first_citation_object['line']) < 3):
        return(True)
    else:
        return(False)

def add_alternative_case_values(first_citation_object,values):
    for key,alt_key in [['name','alternative_case_names'],['party1','alt_party1'],['party2','alt_party2']]:
        if (key in first_citation_object) and (key in values) and (values[key] != first_citation_object[key]):
            if key == 'name':
                if 'alternative_case_names' in values:
                    values[alt_key].append(first_citation_object[key])
                else:
                    values[alt_key] = [first_citation_object[key]]
            else:
                values[alt_key] = first_citation_object[key]

def make_citation_values_compatible(values,citation_dict,first_X_v_Y,first_case_citation_other,txt_file,trace=False):
    ## values = features based on meta-data
    ## attributes = features based on IE
    ## 
    docket_pattern = re.compile('(^| )(no\. *([a-z0-9]+-[a-z0-9-]+))',re.I)
    use_first_ie_case = False
    matches = []
    earliest_start_position = 'False' ## avoids problems of boolean False being the same as integer 0
    first_citation = False
    if (not 'party2' in values) and (not well_formed_non_v_case_name(values['casename'])) and docket_pattern.search(values['casename']):
        use_first_ie_case = True
    else:
        use_first_ie_case = False
    X_v_Y_first = False
    if first_X_v_Y:
        for citation_id in first_X_v_Y:
            start = int(citation_dict[citation_id]['start'])
            if isinstance(earliest_start_position,str) or (earliest_start_position > start):
                    earliest_start_position = start
                    first_citation = citation_id
            if compatible_X_vs_Y_case(citation_dict[citation_id],values,trace=trace):
                matches.append(citation_id)
            X_v_Y_first = True
    if first_case_citation_other:
        for citation_id in first_case_citation_other:
            start = int(citation_dict[citation_id]['start'])
            if isinstance(earliest_start_position,str) or (earliest_start_position > start):
                    earliest_start_position = start
                    first_citation = citation_id
                    X_v_Y_first = False
            if (not X_v_Y_first) and compatible_other_case(citation_dict[citation_id],values,trace=trace):
                matches.append(citation_id)
    if (not matches) and first_citation and (first_citation in first_X_v_Y) and (not 'party2' in values) \
      and X_v_Y_compatible_with_other_citation(citation_dict[first_citation]['party1'],citation_dict[first_citation]['party2'],values['casename']):
        values['alternative_case_names'] = [values['casename'].replace(',','')]
        full_citation = citation_dict[first_citation]
        if 'party1' in full_citation:
            values['party1'] = full_citation['party1']
        if 'party2' in full_citation:
            values['party2'] = full_citation['party2']
        if 'name' in full_citation:
            values['casename'] = full_citation['name']
        return(True)
    elif (not matches) and first_citation and use_first_ie_case:
        full_citation = citation_dict[first_citation]
        if 'party1' in full_citation:
            values['party1'] = full_citation['party1']
        if 'party2' in full_citation:
            values['party2'] = full_citation['party2']
        if 'name' in full_citation:
            values['casename'] = full_citation['name']
        return(True)
    elif (not matches) and (not 'party2' in values) and ('casename' in values) and \
      first_citation and (first_citation in first_case_citation_other) and (len(first_case_citation_other)>1) and \
      merged_case_other_match(values['casename'],first_case_citation_other,citation_dict):
        return(True)
    elif len(matches) == 1:
        if matches[0] == first_citation:
            return(True)
        elif (first_citation in first_case_citation_other) and (len(first_X_v_Y) > 1):
            first_case = citation_dict[first_citation]
            values['casename']=first_case['name']
            if 'party1' in values:
                values.pop('party1')
            if 'party2' in values:
                values.pop('party2')   
            return(True)
        elif (first_citation in first_case_citation_other) and merged_case_other_match(values['casename'],first_case_citation_other,citation_dict):
            return(True)
        elif ((('party2' in values) and check_text_for_parties(values['party1'],values['party2'],txt_file)) or \
          ((not 'party2' in values) and  check_text_for_casename(values['casename'],txt_file))) and \
          ((not first_citation) or (not probably_OK_first_citation(citation_dict[first_citation])) or (len(values['casename'])< 100)):
            print('First citation may be ill-formed.')
            print('first',citation_dict[first_citation])
            for match in matches:
                print('match',citation_dict[match])
            print('meta',values)
            if trace:
                input('pausing')
        else:
            ## metadata is probably incorrect -- switch to first case found by IE
            correct_citation = citation_dict[first_citation]
            if 'party1' in correct_citation:
                values['party1_short'] = get_last_name_from_party(correct_citation['party1'])
            if 'party2' in correct_citation:
                values['party2_short'] = get_last_name_from_party(correct_citation['party2'])
            elif 'name' in correct_citation:
                values['casename'] = correct_citation['name']
            else:
                print('No parties or casename?')
                print('attributes',attributes)
                print('values',values)
                if trace:
                    input('pause')
                return(False)
            return(True)
    elif first_citation in matches:
        ## index case by first citation?
        ## not sure if this is a good way to do this
        return(True)
    elif bad_text_file(txt_file):
        print('No Real Text in file',txt_file)
        return(False)            
    elif ('party1' in values) and ('party2' in values) and check_text_for_parties(values['party1'],values['party2'],txt_file):
        if first_citation:
            first_citation_object = citation_dict[first_citation]
            if probably_OK_first_citation(first_citation_object):
                add_alternative_case_values(first_citation_object,values)
            elif trace:
                print('1, Possibly missed first case mention in file')
                print('Meta Data',values)
                if first_citation:
                    print('IE first citation',citation_dict[first_citation])
        return(True)
    elif ('casename' in values) and check_text_for_casename(values['casename'],txt_file):
        if (not first_citation) or (first_citation in first_case_citation_other):
            if trace:
                print('2, Possibly missed first case mention in file')
                print('Meta Data',values)            
                if first_citation:
                    print('IE first citation',citation_dict[first_citation])
                if trace:
                    input('pausing')            
        elif first_citation and (first_citation in first_X_v_Y) and (len(first_X_v_Y)>1):
            return(True)
        else:
            print('Problematic Results 2')
            print('metadata:',values)
            print('IE:')
            if first_X_v_Y:
                for citation_id in first_X_v_Y:
                    print(citation_dict[citation_id])
            if first_case_citation_other:
                for citation_id in first_case_citation_other:
                    print(citation_dict[citation_id])
            return(False)
    elif first_citation:
        ## ** 57 ** 
        correct_citation = citation_dict[first_citation]
        if 'party1' in correct_citation:
            values['party1_short'] = get_last_name_from_party(correct_citation['party1'])
        if 'party2' in correct_citation:
            values['party2_short'] = get_last_name_from_party(correct_citation['party2'])
        elif 'name' in correct_citation:
            values['casename'] = correct_citation['name']
        else:
            print('No parties or casename?')
            print('attributes',attributes)
            print('values',values)
            if trace:
                input('pause')                
    else:        
        print('Problematic Results 3')
        print('metadata:',values)
        print('IE:')
        if first_X_v_Y:
            for citation_id in first_X_v_Y:
                print(citation_dict[citation_id])
        if first_case_citation_other:
            for citation_id in first_case_citation_other:
               print(citation_dict[citation_id])
        return(False)  

def later_date_string(date_string1,date_string2):
    if date_string1 and (not date_string2):
        return(True)
    elif date_string2 and (not date_string1):
        return(False)
    elif "_" in date_string1:
        return(True)
    elif "_" in date_string2:
        return(False)
    elif (not re.search('^[ 0-9]$',date_string1)):
        return(False)
    elif (not re.search('^[ 0-9]$',date_string2)):
        return(True)
    elif int(date_string1)>int(date_string2):
        return(True)
    else:
        return(False)

def fill_in_data_from_IE_outfile(IE_file,values,txt_file,trace=False):
    ## first citation in the file tends to be the citation for file,
    ## in particular, typically, the first set of citations, 1 of which
    ## is of the X_v_Y variety.
    ## 
    ## strategy: 1) find first X_v_Y citation and all the "equivalent" standard citations
    ##           2) If not compatible with current info in values, print warning and question it,
    ##              but merge it otherwise
    first_citation = False
    citations = {}
    first_X_v_Y = []
    first_case_citation_other = []
    first_standard_cases = []
    citation_line_numbers = []
    first_equiv_relations_type = False
    current_line = False
    local_dict = {}
    latest_date = False
    ## 'case_citation_other'
    ## check the first equivalence relation
    ## one of the arguments should be the "very" first citation
    ## if the first equiv relation is multiline, consecutive multiline
    ##   items are still part of the "first block"
    ## otherwise, only consider "first" citations that are on the same line as each other
    docket_relations = {}
    if os.path.isfile(IE_file):
        with open(IE_file) as instream:
            for line in instream:
                try:
                    type_FS = ET.fromstring(line) 
                except:
                    if trace:
                        print('FS problem')
                        print(line)
                        input('pause')
                if 'line' in type_FS.attrib:
                    current_line = int(type_FS.attrib['line'])
                if type_FS.tag == 'citation':
                    attributes = type_FS.attrib
                    citations[attributes['id']]=attributes
                    if not 'entry_type' in attributes:
                        print('error in case8 file')
                        print(attributes)
                        input('pause')
                    if (current_line <10) and (attributes['entry_type'] in ['case_X_vs_Y','case_citation_other','standard_case']) and \
                      (((not first_X_v_Y) and (not first_case_citation_other)) or (not current_line) or (current_line in citation_line_numbers)):
                        local_dict[attributes['id']] = attributes
                        if not current_line in citation_line_numbers:
                            citation_line_numbers.append(current_line)
                        if attributes['entry_type'] == 'case_X_vs_Y':
                            first_X_v_Y.append(attributes['id'])
                            if 'year' in attributes:
                                latest_date = attributes['year']
                        elif attributes['entry_type'] == 'case_citation_other':
                            first_case_citation_other.append(attributes['id'])
                            if 'year' in attributes:
                                latest_date = attributes['year']
                elif (first_X_v_Y or first_case_citation_other) and (type_FS.tag == 'RELATION') and citation_line_numbers:
                    attributes = type_FS.attrib
                    if ('standard_case' in attributes) and \
                      ((('X_vs_Y' in attributes) and (attributes['X_vs_Y'] in first_X_v_Y))\
                       or (('case_citation_other' in attributes) and (attributes['case_citation_other'] in first_case_citation_other))):
                        if not first_equiv_relations_type:
                            if attributes['gram_type'] == 'multi_line':
                                first_equiv_relations_type = 'multi_line'
                            else:
                               first_equiv_relations_type = 'same_line'
                        if attributes['standard_case'] in first_standard_cases:
                            pass
                        else:
                            first_standard_cases.append(attributes['standard_case'])
                    elif ('includes_docket_string' in type_FS.attrib):
                         attributes = type_FS.attrib
                         if 'theme' in attributes:
                             docket_relations[attributes['theme']]=attributes['includes_docket_string']
    if not make_citation_values_compatible(values,citations,first_X_v_Y,first_case_citation_other,txt_file,trace=trace):
        print('Warning: Something is wrong with input files. This input document may be ill-formed.') 
        print(values)       
    if first_case_citation_other:
        for case_id in first_case_citation_other:
            if case_id in docket_relations:
                values['docket_number'] = docket_relations[case_id]
    if first_X_v_Y:
        for case_id in first_X_v_Y:
            if case_id in docket_relations:
                values['docket_number'] = docket_relations[case_id]
    if len(first_standard_cases)>0:
        output = []
        for standard_case in first_standard_cases:
            new_case = values.copy()
            next_citation = citations[standard_case]
            ## if 'standard reporter' matches, they are assumed to be the same citation
            ## (or a conflict).  Otherwise, they are assumed to be another "version"
            if ('standard_reporter' in next_citation) and  ('standard_reporter' in values) \
              and (next_citation['standard_reporter']==values['standard_reporter']):
                for attrib in ['volume','page_number','year']:
                    if (attrib in next_citation) and (not attrib in values):
                        new_case[attrib]=next_citation[attrib]
            elif not 'standard_reporter' in next_citation:
                raise exception('No standard reporter in citation:'+str(next_citation))
            else:
                for attrib in ['standard_reporter','volume','page_number','year']:
                    if attrib in next_citation:
                        if (attrib == 'year') and ((not latest_date) or later_date_string(next_citation[attrib],latest_date)):
                            latest_date = next_citation[attrib]
                        new_case[attrib]=next_citation[attrib]
                if next_citation['id'] in docket_relations:
                    new_case['docket_number'] = docket_relations[next_citation['id']]
            output.append(new_case)
        return(output,latest_date)
    else:
        return([values],latest_date)

def well_formed_non_v_case_name(casename):
    if re.search('ex parte|the|in re|in the matter|application|claims|case',casename.lower()):
        return(True)

def key_compatible_with_entry(entry_type,key):
    ## the same party and casename occur with multiple standard_key entries
    if (entry_type != 'standard_key') and (key in ['standard_reporter','volume','page_number']):
        return(False)
    ## occasionally several cases (with different names) are combined together into one case
    ## this could make having party and case names with standard keys difficult
    elif (entry_type == 'standard_key') and (key in ['party1','party2','casename','party1_short','party2_short']):
        return(False)
    else:
        return(True)

def add_one_to_party_key(party_key):
    position = party_key.rfind('#')
    number = int(party_key[position+1:])
    return(party_key[:position+1]+str(number+1))

def score_party_similarities(party1a,party2a,party1b,party2b):
    if (len(party1b)>=len(party1a)):
        if (party1a in party1b):
            party1_score = 1
        elif (first_and_last_simplified(party1a) in party1b):
            party1_score = .9  
        elif (typo_compatible_substring(party1b,party1a)):
            party1_score = .9
        else:
            party1_score = 0
    else:
        if (party1b in party1a):
            party1_score = 1
        elif (first_and_last_simplified(party1b) in party1a):
            party1_score = .9  
        elif (typo_compatible_substring(party1a,party1b)):
            party1_score = .9
        else:
            party1_score = 0
    if (len(party2b)>=len(party2a)):
        if (party2a in party2b):
            party2_score = 1
        elif (first_and_last_simplified(party2a) in party2b):
            party2_score = .9  
        elif (typo_compatible_substring(party2b,party2a)):
            party2_score = .9
        else:
            party2_score = 0
    else:
        if (party2b in party2a):
            party2_score = 1
        elif (first_and_last_simplified(party2b) in party2a):
            party2_score = .9  
        elif (typo_compatible_substring(party2a,party2b)):
            party2_score = .9
        else:
            party2_score = 0
    return((party1_score+party2_score)/2)

def increment_party_key(party_key,info):
    global global_citations
    global party_key_hash
    out_key = False
    if party_key in party_key_hash:
        if 'id1' in info:
            id1 = info['id1']
        else:
            id1 = False
        full_party1 = info['party1']
        full_party2 = info['party2']
        possible_keys = []
        different_key = False
        for other_party_key in party_key_hash[party_key]:
            other_entry = global_citations[other_party_key]
            if out_key or different_key:
                pass
            elif id1 and ('id1' in other_entry):
                if (id1 == other_entry['id1']) or (('no_current_file' in other_entry) and ('no_current_file' in info)):
                    out_key = other_party_key
            elif (not id1):
                possible_keys.append([score_party_similarities(full_party1.lower(),full_party2.lower(),other_entry['party1'].lower(),other_entry['party2'].lower()),other_party_key])
            else:
                different_key = True
        if different_key:
            out_key = add_one_to_party_key(party_key_hash[party_key][-1])
        if out_key:
            return(out_key)
        elif len(possible_keys)>0:
            pair = max(possible_keys)
            if (pair[0] > .5):
                return(pair[1])
            else:
                out_key = add_one_to_party_key(party_key_hash[party_key][-1])
        else:
            out_key = add_one_to_party_key(party_key_hash[party_key][-1])
        if not out_key in  party_key_hash[party_key]:
            party_key_hash[party_key].append(out_key)
        if out_key:
            return(out_key)
    else:
        out_key = party_key+'#1'
        party_key_hash[party_key] = [out_key]
    return(out_key)

def score_case_similarities(casename1,casename2):
    word_list1 = []
    word_list2 = []
    for word in casename1.split(' '):
        if (word in ['ex','parte','case','in','re','the','matter','of']) or re.search('^[0-9]+$',word) or (word in person_ending_words+org_ending_words):
            pass
        else:
            word_list1.append(word)
    for word in casename2.split(' '):
        if (word in ['ex','parte','case','in','re','the','matter','of']) or re.search('^[0-9]+$',word) or (word in person_ending_words+org_ending_words):
            pass
        else:
            word_list2.append(word)
    overlap_length = 0
    length = min(len(word_list1),len(word_list2))
    for word in word_list1:
        if word in word_list2:
            overlap_length += 1
            word_list2.remove(word)
    return(overlap_length/length)

def increment_case_key(case_key,info):
    global global_citations
    global party_key_hash
    out_key = False
    if case_key in party_key_hash:
        if 'id1' in info:
            id1 = info['id1']
        else:
            id1 = False
        possible_keys = []
        different_key = False
        for other_case_key in party_key_hash[case_key]:
            other_entry = global_citations[other_case_key]
            if out_key or different_key:
                pass
            elif id1 and ('id1' in other_entry):
                if (id1 == other_entry['id1']) or (('no_current_file' in other_entry) and ('no_current_file' in info)):
                    out_key = other_case_key
            elif (not id1):
                if 'casename' in other_entry:
                    name1 = other_entry['casename']
                elif 'name' in other_entry:
                    name1 = other_entry['name']
                else:
                    name1 = False
                if 'casename' in info:
                    name2 = info['casename']
                elif 'name' in info:
                    name2 = info['name']
                else:
                    name2 = False
                if (not name1):
                    ## possible if entered as an alternate key only
                    possible_keys.append([score_case_similarities(case_key,other_case_key),other_case_key])
                else: 
                    possible_keys.append([score_case_similarities(name1.lower(),name2.lower()),other_case_key])
            else:
                different_key = True
        if different_key:
            out_key = add_one_to_party_key(party_key_hash[case_key][-1])
        if out_key:
            return(out_key)
        elif len(possible_keys)>0:
            pair = max(possible_keys)
            if (pair[0] > .6):
                if (pair[1] in global_citations):
                    entry = global_citations[pair[1]]
                    if (not 'casename' in entry) and ('casename' in info):
                        global_citations[pair[1]] = info                        
                return(pair[1])
            else:
                out_key = add_one_to_party_key(party_key_hash[case_key][-1])
        else:
            out_key = add_one_to_party_key(party_key_hash[case_key][-1])
        if not out_key in party_key_hash[case_key]:
            party_key_hash[case_key].append(out_key)
        if out_key:
            return(out_key)
    else:
        out_key = case_key+'#1'
        party_key_hash[case_key] = [out_key]
    return(out_key)
        

def generate_key_words_from_case_record(info,trace=False):
    if ('party1' in info) and (not 'party1_short' in info):
        info['party1_short']= get_last_name_from_party(info['party1'])
    if ('party2' in info) and (not 'party2_short' in info):
        info['party2_short']= get_last_name_from_party(info['party2'])
    party1 = get_valid_dict_value('party1_short',info)
    party2 = get_valid_dict_value('party2_short',info)
    if not party1:
        party1 = get_valid_dict_value('party1',info)
        if party1:
            party1 = (get_last_name_from_party(party1))
    if not party2:
        party2 = get_valid_dict_value('party2',info)
        if party2:
            party2 = (get_last_name_from_party(party2))
    casename = get_valid_dict_value('casename',info)
    if not casename:
        casename = get_valid_dict_value('name',info)
    reporter = get_valid_dict_value('standard_reporter',info)
    volume = get_valid_dict_value('volume',info)
    page_number = get_valid_dict_value('page_number',info)
    output = []
    if party1 and party2:
        party_key = party_key = re.sub('[ ,\.]','',(party1+party2).lower())
        party_key = increment_party_key(party_key,info)
        output.append(['party_key',party_key])
    elif casename:
        if len(casename)>20:
            case_key = standardize(casename).lower()
            if trace:
                print('Long casename:',casename)
                input('pause')
        else:
            case_key = standardize(casename).lower() 
        case_key = increment_case_key(case_key,info)
        output.append(['case_key',case_key])
    if reporter and volume and page_number:
        standard_key = (reporter+'_'+volume+'_'+page_number).lower()
        output.append(['standard_key',standard_key])
    return(output)

def separate_versions_and_add_keys(case_records,latest_date,trace=False):
    global global_citations
    output = []
    for record in case_records:
        key_word_pairs = generate_key_words_from_case_record(record,trace=trace)
        for key_type,key_word in key_word_pairs:
            if not key_word in global_citations:
                new_record = record.copy()
                new_record['lookup_key']=key_word
                new_record['entry_type']=key_type
                if (key_type != 'standard_key') and latest_date:
                    new_record['year']=latest_date
                global_citations[key_word]=new_record
                output.append(new_record)
            else:
                old_entry = global_citations[key_word]
                if trace and ('id1' in old_entry) and ('id1' in record) and (not (old_entry['id1'] == record['id1'])):
                    print('key phrase:',key_word,'is not unique')
                    print(old_entry)
                    print(record)
                    input('pause')                    
    return(output)

def get_casename_from_meta_data_path(path):
    path_items = path.split('/')
    phrase = path_items[-2]
    words = phrase.split('-')
    output = words[0]
    for word in words[1:]:
        output = output+' '+word
    return(output)

def writeCSV(file, filename, folder,matching_IE_file,trace=False):
    global csv_column_list
    ## filename ends with json ##
    ## this strips off the json and adds txt
    txt_file = filename[:-4]+'txt'
    party_pattern = re.compile('parties\">(.*)</p>')
    values = {}
    try:
        data = json.load(file)
        values['id1'] = filename.split('/')[-1][:-5]
        values['folder'] = folder
        values['full_name'] = full_names[folder]
        if folder in district_courts:
            court = district_courts[folder]
            values['district_city'],values['district_state'],values['district_state_abbrev']=court
        casename = get_casename_from_meta_data_path(data['absolute_url'])
        values['casename']=casename
        parties = casename.upper()
        found_v = False
        party1 = False
        for i in range(1, len(parties) - 1):
            if parties[i] == 'V':
                if (i > 0) and (i<len(parties)) and (parties[i-1] == ' ') and (parties[i+1] in [' ','.']):
                    found_v = True
                    party1 = parties[:i]
                    break
        if not party1:
            party1 = parties
        if found_v:
            if party1[-1] == ' ':
                party1 = party1[:-1]
            party2 = parties[i + 1:]
        elif well_formed_non_v_case_name(casename):
            party1 = 'Unknown'
            party2 = 'Unknown'
        else:
            found_html = True
            if 'html' in data and data['html'] != None:
                html = data['html']
            elif 'html_with_citations' in data and data['html_with_citations'] != None:
                html = data['html_with_citations']
            else:
                found_html = False
            if found_html:
                found_parties = party_pattern.search(html)
                if found_parties:
                    parties = remove_xml_plus(found_parties.group(1).upper())
                else:
                    parties = ''
                if len(parties) > 2 and len(parties) < 1000:
                    party1 = parties[0]
                    for i in range(1, len(parties) - 1):
                        if (parties[i] == 'V') and ((parties[i + 1] == '.') or (parties[i + 1] == ' ')):
                            found_v = True
                            break
                        else:
                            party1 += parties[i]
                    party2 = parties[i + 1:]
                    party1 = party1.replace(',', '')
                    party2 = party2.replace(',', '')
                    if not found_v:
                        party1 = 'Unknown'
                        party2 = 'Unknown'
                else:
                    party1 = 'Unknown'
                    party2 = 'Unknown'
            else:
                party1 = 'Unknown'
                party2 = 'Unknown'
        if party1:
            party1 = party1.strip('.,/?"-`')
        if party2:
            party2 = party2.strip('.,/?"-`')
        if party2 == '':
            party2 = 'Unknown'
        if party1 == '':
            party1 = 'Unknown'
        if party1[-1] == ' ':
                party1 = party1[:-1]
        if party2[-1] == ' ':
            party2 = party2[:-1]
        if party1 == 'UnitedStates':
            party1 = 'United States'
        if party1[-5:] == 'ET AL':
            party1 = party1[:-6]
        if party1[-4:] == 'ETAL':
            party1 = party1[:-5]
        if party1 and (not party1 in ['','Unknown']):
            values['party1'] = party1
        if party2 and (not party2 in  ['','Unknown']):
            values['party2'] = party2
        out_dicts,latest_date = fill_in_data_from_IE_outfile(matching_IE_file,values,txt_file,trace=trace)
        out_dicts  = separate_versions_and_add_keys(out_dicts,latest_date,trace=trace)
        out_strings = []
        for out_dict in out_dicts:
            cstr = ''
            entry_type = out_dict['entry_type']
            for key in csv_column_list:
                if (key in out_dict) and (key_compatible_with_entry(entry_type,key)):
                    if isinstance(out_dict[key],list):
                        cstr += out_dict[key][0]
                        for item in out_dict[key][1:]:
                            cstr += ';'+item
                        cstr +='\t'
                    else:
                        cstr += out_dict[key]+'\t'
                elif key in ['district_city','district_state','district_state_abbrev','docket number']:
                    cstr += 'None'+'\t'
                else:
                    cstr += 'Unknown'+'\t'
            out_strings.append(cstr)
        return(out_strings)
    except ValueError:
        print('error in csv for file',filename)
        return(False)
        
#traverse all json files

def create_csv_file(output_file,input_directories,IE_infile_type,trace=False):
    print('Creating csv file')
    global global_citations
    global_citations.clear()
    text = csv_column_list[0]
    for key in csv_column_list[1:]:
        text=text+'\t'+key
    text = text+'\n'
    ## labeled columns
    for input_dir in input_directories:
        full_dir = input_dir
        for infile in os.listdir(full_dir):
            if infile.endswith('.json'):
                print(infile)
                filename = file_name_append(full_dir,infile)
                matching_IE_file = filename[:-5]+IE_infile_type
                with open(filename) as instream:
                    folder = input_dir.rstrip(os.sep)
                    if 'test' in folder:
                        folder = 'scotus'
                    out = writeCSV(instream,filename,folder,matching_IE_file,trace=trace) 
                    if out:
                        for line in out:
                            text +=line+'\n'
    with open(output_file,'w') as csv:
        csv.write(text)

