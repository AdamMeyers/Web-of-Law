import os
from citation_tables import *
from wol_utilities import *
from xml.sax.saxutils import escape
from xml.sax.saxutils import unescape

prepositions = ['by', 'for', 'from', 'in', 'of', 'on', 'to', 'with', 'within']

year_pattern = re.compile('(^|[^0-9])((17|18|19|20)[0-9][0-9])($|[^0-9])')
initial_role_words = ['plaintiff','prosecutor', 'prosecution','defendant','appellant','appellee','claimant','petitioner','respondent', 'intervenor','complainant','libellant']
         ## there may be additional roles, but not sure if they appear as part of vs case names

in_error_pattern = re.compile('(in err(\.|or)?)([^a-z]|$)',re.I)

## month = '(january|february|march|april|may|june|july|august|september|october|november|december)|((jan|feb|mar|apr|jun|jul|aug|sept?|oct|nov|dec)\.?)' ## moved to wol_utitlities.py

is_month = re.compile('^'+month+'$')

date_pattern = re.compile(full_date,re.I) ## case insensitive version
## requires month and year, with date optional

all_role_words = initial_role_words[:] 
         
role_prefixes = ['counter','cross','counterclaim','crossclaim']
pre_citation_words = ['see','also','cf','compare','later','in']
topic_matter_words = ['issue','matter','subject','topic']

compound_roles = []

id_number = 0
## include productive role combos without going into endless loop and producing, e.g., cross-cross-counter-claimant

for prefix in role_prefixes:
    for role in all_role_words:
        compound_roles.append(prefix+role)
        compound_roles.append(prefix+' '+role)
        compound_roles.append(prefix+'-'+role)

all_role_words.extend(compound_roles)

plural_roles = []

for role in all_role_words:
    plural_roles.append(role+'s')
    ## note there seem to be no irregular plurals for these roles or even roles that need an "es" added
    ## this may change if we find more roles (and the we will need to implement a more complete code for plural)

all_role_words.extend(plural_roles)

### above role settings assume original non-dictionary version
### for dictionary version, we should use the following function to generate the new sets of RANK and ROLES
### for the dictionary (replacing the old set in the dictionary)
### 

### **** revise above to account for more general role system *****

relational_dict = {}

relational_dict_file = 'relational.dict'

time_dict = {}
time_dict_file = 'time_names.dict'

one_word_person_names = {}

def is_role_word(ref_word):
    return((ref_word in relational_dict) and (('LEGAL_ROLE' in relational_dict[ref_word]) or ('PLURAL_LEGAL_ROLE' in relational_dict[ref_word])))

def capitalized_word(word):
    ## istitle and isupper don't work well enough for my purposes
    ## they exclude outliers like cammelcase
    return((len(word)>0) and word[0].isupper())

load_tab_deliniated_dict(relational_dict_file,relational_dict)
load_tab_deliniated_dict(time_dict_file,time_dict)

def add_to_POS_dict(infile,word_class):
    with open(infile) as instream:
        for line in instream:
            line = line.strip(os.linesep).lower()
            if line in POS_dict:
                if not word_class in POS_dict[line]:
                    POS_dict[line].append(word_class)
            else:
                POS_dict[line]=[word_class]

add_to_POS_dict('discourse_words.txt','DISCOURSE')
add_to_POS_dict('firstname.dict','FIRSTNAME')
add_to_POS_dict('person_name_list_short.dict','PERSONNAME')
add_to_POS_dict('location_list.dict','GPE')
add_to_POS_dict('state_abbreviations.dict','GPE')
add_to_POS_dict('org_list.dict','ORG')
add_to_POS_dict('nationalities.dict','NATIONALITY')


roman_value = {'i':1,'v':5,'x':10,'l':50,'c':100,'d':500,'m':1000}

def ok_roman_bigram (pair):
    if pair in ['ii','iv','ix','vi','xi','xv','xx','xl','xc','li','lv','lx','ci','cv','cx','cl','cc','cd','cm','mi','mv','mx','ml','mc','md','mm']:
        return(True)
    else:
        return(False)

def OK_roman_trigram(triple):
    if triple in ['ivi','ixi','xlx','xcx','cdc','cmc']:
        return(False)
    else:
        return(True)

def roman (string):
    lower = string.lower()
    if (type(lower) == str) and re.search('^[ivxlcdm]+$',lower):
        ## lower consists completely of correct characters (unigram)
        ## now check bigrams
        result = True
        for position in range(len(lower)):
            if ((position == 0) or ok_roman_bigram(lower[position-1:position+1])) and \
                    ((position < 2) or OK_roman_trigram(lower[position-2:position+1])):
                pass
            else:
                result = False
        if (len(lower)>2) and (lower in POS_dict):
            return(False)
        else:
            return(result)
    else:
        return(False)

## these next 2 functions were used for generating entries in the role dictionary
def role_word_variations(base_word,prefixes):
    ## unlike basic version, this does not provide two word role names
    ## this does not account for irregular plurals or plurals requiring the adding of "es"
    ## (e.g., those ending in 'z','ch', 'sh' or 's')
    output = [base_word,base_word+'s']
    for prefix in prefixes:
        output.append(prefix+base_word)
        output.append(prefix+'-'+base_word)
        output.append(prefix+base_word+'s')
        output.append(prefix+'-'+base_word+'s')
    return(output)
        
def generate_set_of_entries(outfile):
    entries = []
    for prefix in role_prefixes:
        entries.append([prefix,'LEGAL_RANK'])
    for base_word in initial_role_words:
        for word in role_word_variations(base_word,role_prefixes):
            entries.append([word,'LEGAL_ROLE'])
    entries.sort()
    with open(outfile,'w') as outstream:
        for entry in entries:
            ### assumes all entries have exactly one class
            outstream.write(entry[0]+'\t'+entry[1]+os.linesep)
            

## page_number_pattern = '((([0-9—]+, )*[0-9—]+)|—-|_+)'  ## commas will may cause problems
## for disambiguating borders between citations

standard_citation_pattern = re.compile('([0-9]+)( *)('+court_reporter_rexp+')[ _]*([0-9]+)?',re.I)
at_citation_pattern = re.compile('([0-9]+)( *)('+court_reporter_rexp+'),?( +)(at *)([0-9]+)',re.I)
## fields 1 = volume, 3 = reporter, 54 = page number (under current court_reporter_rexp)
## need second pattern that starts at page number because the size of court_reporter_rexp will not be stable

standard_citation_pattern_extension = re.compile('(([0-9]+(—[0-9]+)?)|—-|_+)(, *([0-9]+( *-[0-9]+)?))?(( *(\([^)^(]+\)))*)',re.I)
## require comma for paragraph? -- paragraph overgenerates -- require date or ignore paragraph?

standard_citation_pattern_short_extension = re.compile(' *(([0-9]+(—[0-9]+)?)|—-|_+)',re.I)

at_page_number = re.compile('at *(([0-9]+(—[0-9]+)?)|—-|_+)',re.I)

def get_year_and_court_from_parentheses_region(instring):
    court_pattern = re.compile('[^a-zA-Z]([A-Za-z0-9][A-Za-z0-9\. ]*[A-Za-z-0-9\.])')
    end_paren_pattern = re.compile('\)')
    year_match = year_pattern.search(instring)
    end = False
    if year_match:
        year = year_match.group(2)
        court_match = court_pattern.search(instring[:year_match.start()])
        if court_match and not (court_match.group(1).lower() in court_abbrev_table):
            court_match = False
        if not court_match:
            court_match = court_pattern.search(instring,year_match.end())
            if court_match and not (court_match.group(1).lower() in court_abbrev_table):
                court_match = False
    else:
        court_match = court_pattern.search(instring)
        if court_match and not (court_match.group(1).lower() in court_abbrev_table):
            court_match = False
        year = False
    if court_match:
        court = court_match.group(1)
    else:
        court = False
    if court:
        if year:
            end = max(court_match.end(1),year_match.end(2))
        else:
            end = court_match.end(1)
    elif year:
        end = year_match.end(2)
    if end:
        end_pat = end_paren_pattern.search(instring,end)
        if end_pat:
            end = end_pat.end()
    return(year,court,end)


def revise_citation_match_extra(line,possible_start,citation_match_extra):
    ## checks to make sure that page number is not really the volume number
    if citation_match_extra.group(5):
        citation_match = standard_citation_pattern.search(line,possible_start)
        at_citation_match = at_citation_pattern.search(line,possible_start)
        if citation_match and (citation_match.start()<=citation_match_extra.start(5)):
            new_pattern = standard_citation_pattern_short_extension.search(line,possible_start)
            return(new_pattern,False)
        elif at_citation_match and (at_citation_match.start()<=citation_match_extra.start(5)): 
            new_pattern = standard_citation_pattern_short_extension.search(line,possible_start)
            return(new_pattern,False)
        else:
            return(citation_match_extra,True)
    else:
        return(citation_match_extra,True)

def add_citation_id(record,file_id,dictionary):
    global id_number
    id_number = id_number+1
    id_string = file_id + '_' + str(id_number)
    record['id']=id_string
    dictionary[id_string]=record

def get_next_standard_citation(line,start=0):
    pattern = standard_citation_pattern.search(line,start)
    while pattern:
        if pattern and (pattern.end()<len(line)) and re.search('[a-zA-Z0-9]',line[pattern.end()]):
            pattern = standard_citation_pattern.search(line,pattern.end())
        else:
            return(pattern)
    
def get_citation_output(line,offset,file_id,citation_dictionary):
    global id_number
    ## to get X v Y
    ## find 2 capitalized sequences surrounding a "v."
    ## Use filters to the beginning of the sequence to not include
    ## "See" and "Cf." and a possibly a larger stop list of words
    ## the end should probably be punctuation and often should precede , + standard citation
    ## once codified as a citation -- the X v Y sequence can be found elsewhere 
    ## in the text
    output = []
    ## first getting standard citation
    citation_match = get_next_standard_citation(line)
    at_citation_match = at_citation_pattern.search(line)
    start = 0
    while citation_match or at_citation_match:
        if at_citation_match and citation_match:
            if citation_match.start()<at_citation_match.start():
                at_citation_match = False
            else:
                citation_match = False
        if at_citation_match:
            citation_start = at_citation_match.start()+offset
            if ('§' in at_citation_match.group(0)):
                out = False
                start = citation_match.end()
                citation_match_extra = False
            else:
                out = {'start':citation_start}
                out['volume'] = at_citation_match.group(1)
                out['reporter'] = at_citation_match.group(3)
                standard_reporter = at_citation_match.group(3).upper()
                if standard_reporter in court_reporter_standard_table:
                    standard_reporter = court_reporter_standard_table[standard_reporter]
                out['standard_reporter'] = standard_reporter
                citation_match_extra = at_page_number.search(line,at_citation_match.end(3))
                if citation_match_extra and ('§' in line[at_citation_match.start():citation_match_extra.end()]):
                    start = citation_match_extra.end()
                    citation_match_extra = False
                    out = False
                if citation_match_extra:
                    out['page_number'] = citation_match_extra.group(1)
        else:
            citation_start = citation_match.start()+offset
            if ('§' in citation_match.group(0)):
                start = citation_match.end()
                out = False
                citation_match_extra = False
            else:
                out = {'start':citation_start}
                out['volume'] = citation_match.group(1)
                out['reporter'] = citation_match.group(3)
                standard_reporter = citation_match.group(3).upper()
                if standard_reporter in court_reporter_standard_table:
                    standard_reporter = court_reporter_standard_table[standard_reporter]
                out['standard_reporter'] = standard_reporter
                citation_match_extra = standard_citation_pattern_extension.search(line,citation_match.end(3))
                if citation_match_extra and ('§' in line[citation_match.start():citation_match_extra.end()]):
                    start = citation_match_extra.end()
                    citation_match_extra = False
                    out = False
                else:
                    possibly_competing_citation_match = get_next_standard_citation(line,citation_match.end(3))
                    if citation_match_extra and possibly_competing_citation_match:
                        if citation_match_extra.start() >= possibly_competing_citation_match.start():
                            citation_match_extra = False
                    if citation_match_extra:
                       citation_match_extra,paragraph_check = revise_citation_match_extra(line,citation_match.end(3),citation_match_extra)
        end = False
        paren_end = False
        year = False
        court = False
        if not out:
            pass
        elif citation_match_extra and not at_citation_match:
            if citation_match_extra.group(1):
                if (len(citation_match_extra.group(1))==4) and (line[citation_match_extra.start(1)-1]=='(')\
                   and year_pattern.search(citation_match_extra.group(1)):
                    out['year'] = citation_match_extra.group(1)
                else:
                    out['page_number'] = citation_match_extra.group(1)
            if paragraph_check:
                paragraph_number = citation_match_extra.group(5)
            else:
                paragraph_number = False
            if paragraph_number:
                out['paragraph_number'] = paragraph_number
                ## the "at" pattern seems not to include year and court info
            if paragraph_check:
                year,court,paren_end = get_year_and_court_from_parentheses_region(citation_match_extra.group(7))
            else:
                year,court,paren_end = False,False,False
                paragraph_number = False
            if paren_end:
                end = paren_end + citation_match_extra.start(7)
                out['end'] = end + offset
                out['string']=line[citation_match.start():end]
            else:        
                end = False        
                out['string']=line[citation_match.start():citation_match_extra.end()]
                out['end'] = citation_match_extra.end()+offset
            if year:
                out['year'] = year
            if court:
                out['court'] = court
            if end:
                start = end
            else:
                start = citation_match_extra.end()
        elif at_citation_match:
            out['end'] = at_citation_match.end()+offset
            out['string']=at_citation_match.group(0)
            start = at_citation_match.end()
        elif citation_match:
            out['end'] = citation_match.end()+offset
            out['string']=citation_match.group(0)
            start = citation_match.end()
        if out and re.search(',$',out['string']):
            ## fix for comma at end
            out['string'] = out['string'][:-1]
            out['end'] = out['end']-1
        if out and ('reporter' in out) and ('volume' in out) and ('page_number' in out):
            output.append(out)
        citation_match = get_next_standard_citation(line,start)
        at_citation_match = at_citation_pattern.search(line,start)
        citation_match_extra = False
    for record in output:
        add_citation_id(record,file_id,citation_dictionary)
    return(output)

def citation_print(outstream,citation):
    if citation['entry_type'] in ['standard_case','case_X_vs_Y','case_citation_other']:
        outstream.write('<citation')
    elif citation['entry_type'] in ['docket']:
        outstream.write('<docket')
    for attribute in ['id','entry_type','start','end','name','reporter','standard_reporter','volume','page_number','paragraph_number','court','year','party1','party2','party1_role','party2_role','line']:
        if attribute in citation:
            outstream.write(' '+attribute+'="'+wol_escape(str(citation[attribute]))+'"')
    outstream.write('>')
    if 'string' in citation:
        outstream.write(wol_escape(citation['string']))
    if citation['entry_type'] in ['standard_case','case_X_vs_Y','case_citation_other']:
        outstream.write('</citation>'+os.linesep)
    elif citation['entry_type'] in ['docket']:
        outstream.write('</docket>'+os.linesep)

def ok_docket(docket):
    if re.search('[0-9]',docket):
        return(True)
    else:
        return(False)

def get_docket_numbers(line,spans,offset,file_id,citation_dictionary):
    docket_pattern = re.compile('(^| )(no\. *([a-z0-9]+[-–][a-z0-9\-–]+))',re.I)
    match = docket_pattern.search(line)
    output = []
    while match:
        target_field = 3
        next_start = match.end()
        for span_start,span_end in spans:
            span_start = span_start-offset
            span_end = span_end-offset
            if match and (match.start(1) >=span_start) and (match.start(target_field)<span_end):
                match = False
        if match and ok_docket(match.group(target_field)):
          out = {'start':match.start(target_field)+offset,'end':match.end(target_field)+offset,'string':match.group(target_field),'offset_start':match.start(0)+offset}
          output.append(out)
        if match:
          match = docket_pattern.search(line,match.end(target_field))
    for record in output:
        add_citation_id(record,file_id,citation_dictionary)
    return(output)

def get_docket_number_sets(line,spans,offset,file_id,citation_dictionary):
    docket_pattern = re.compile('(^| )nos\. *([a-z0-9]+[-–][a-z0-9\-–]+)',re.I)
    docket_pattern2 = re.compile('( and|,) *([a-z0-9]+[-–][a-z0-9\-–]+)',re.I)
    match1 = docket_pattern.search(line)
    match2 = False
    output = []
    while match1 or match2:
        semi_match = False
        if match1 and match2:
            if match1.start() < match2.start():
                match = match1
            else:
                match = match2
        elif match1:
            match = match1
        else:
            match = match2
        next_start = match.end()
        for span_start,span_end in spans:
            span_start = span_start-offset
            span_end = span_end-offset
            if match and (match.start(2) >=span_start) and (match.start(2)<span_end):
                if match and (not semi_match):                
                    semi_match = match
                match = False
        if match and ok_docket(match.group(2)):
          out = {'start':match.start(2)+offset,'end':match.end(2)+offset,'string':match.group(2),'offset_start':match.start(0)+offset}
          output.append(out)
        if not match:
            match = semi_match
        match1 = docket_pattern.search(line,match.end(2))
        match2 = docket_pattern2.search(line,match.end(2))            
    for record in output:
        add_citation_id(record,file_id,citation_dictionary)
    return(output)

def ok_to_delete_left_most_vs_item (matches):
    if (len(matches)>0) and (len(matches[-1].group(1))>0):
        ref_item = matches[-1].group(1).strip(".,'\"").replace('/','')
    else:
        ref_item = False
    if len(matches)> 1:
        penult_ref_item = matches[-2].group(1).strip(".,'\"").replace('/','').lower()
    else:
        penult_ref_item = False
    if len(matches)==0:
        return(False)
    elif (ref_item.lower() in prepositions):
        return(True)
    elif (len(ref_item)>0) and ref_item[0].isupper():
        return(False)
    elif penult_ref_item in (org_ending_words+person_ending_words):
        return(False)
    else:
        return(True)

def ok_to_delete_right_most_vs_item (matches):
    month_match = re.compile(r'^('+month+r')$')
    if len(matches)==0:
        return(False)
    elif (len(matches[-1].group(0))>0) and (not matches[-1].group(0)[0].isupper()) \
      and (matches[-1].group(0).lower() in not_uppercase_part_of_org_names):
        return(True)
    elif month_match.search(matches[-1].group(0).lower()):
        return(True)
    elif (matches[-1].group(0).lower() in POS_dict) and ('PREP' in (POS_dict[matches[-1].group(0).lower()])):
        return(True)
    else:
        return(False)

def OK_comma_follows(word,first_letter):
    if (word == 'state') or (word in relational_dict) or (word in citation_filler_words) or first_letter.isupper() or (word in org_ending_words) or (word in person_ending_words):
        return(True)

def OK_comma_precedes(word):
    if (word in org_ending_words) or (word in person_ending_words) or (word in citation_filler_words) or (word in relational_dict) or (word in alias_words):
        return(True)

def possible_abbrev(word):
    ### may need longer list of abbreviations that do not end named units
    if (len(word)>0) and word[0].isupper() and ((len(word)==1) or (word.lower() in ['assoc', 'asst', 'capt', 'cdr', 'cmdr', 'col', 'dr', 'dr', 'exec', \
                                            'gen', 'gen', 'hon', 'lieut', 'lt', 'maj', 'messrs', 'mr', 'mrs', \
                                            'ms', 'pres', 'rep', 'sgt','nos','ltd','co','inc','corp','sa','cia','gmbh','llp'])):
        return(True)
    elif (word.lower() in relational_dict) and (word.lower()+'.' in relational_dict):
        return(True)

def advance_left_span(line,left_span,end):
    deletable = re.compile('(cite +as)|(writ of cert.*district,?( +division +[a-z]+)?)|(((Statement +of.*)|(Per +Curiam *))?SUPREME +COURT +OF +THE +UNITED STATES)|(ORDER IN PENDING CASE)',re.I)
    match = deletable.search(line,left_span)
    if match and (match.start()<end):
        return(match.end())
    else:
        return(left_span)

def deletable_middle(middle):
    ## for early lines in file only
    ## should be essentially same criteria as advance_left_function (except for the ^ and $)
    deletable = re.compile('^[^a-z]*((cite +as)|(writ of cert.*district,?( +division +[a-z]+)?)|(((Statement +of.*)|(Per +Curiam *))?SUPREME +COURT +OF +THE +UNITED STATES))[^a-z]*$',re.I)
    if deletable.search(middle):
        return(True)

def title_word(word):
    if (word.lower() in POS_dict) and ('TITLE' in POS_dict[word.lower()]):
        return(True)

def find_left_vs_border(line,end,left_span,one_line_objects,paren_comma,line_number):
    ## if one_line_objects, left border is more likely to be 0
    # if 'holmes' in line.lower():
    ## print(1,line,2,end,3,left_span,4,one_line_objects,5,paren_comma,6,line_number)
    global all_role_words
    pattern = re.compile('([a-z\'\-&/\[\]]+)([^a-z\-&/\[\]]*)$',re.I) ## allow words to contain intermediate hyphens and apostrophes
    roles = []
    current_end = end
    previous_word = pattern.search(line[:current_end])
    matches = []
    finished_roles = False
    if line_number < 5:
        old_left_end = left_span
    else:
        old_left_end = False
    left_span = advance_left_span(line,left_span,end)
    lowercase_parenthetical_commas_left_of_v = False
    lowercase = False
    is_number = False
    if previous_word and (previous_word.group(0).lower() in ['error', 'err']):
        current_end = previous_word.start()
        matches.append(previous_word)
        previous_word = pattern.search(line[:current_end])
        if previous_word and (previous_word.group(1).lower() == 'in'):
            current_end = previous_word.start()
            matches.append(previous_word)
            previous_word = pattern.search(line[:current_end])
            ## skip over "in error" modifier for purposes of finding extent
    first = True
    last_corporate_ending = False
    party_end = end
    last_ref_word = False
    last_word_string = False
    last_is_role = False
    fail = False
    found_name = False
    opened_paren = False
    number_of_words = 0
    while previous_word and (previous_word.start() >= left_span):
        word_string = previous_word.group(1)
        if word_string.strip(".,").replace('/','').islower():
            lowercase = True
        else:
            lowercase = False
        simple_string = word_string.strip(".,'\"").replace('/','')
        ref_word = word_string.lower().strip("\'")
        middle_ground = line[previous_word.end(1):current_end]
        if (')' in middle_ground) and (not '(' in middle_ground):
            opened_paren = True
        is_role = is_role_word(ref_word)
        is_number = ref_word.isdigit()
        if lowercase and "," in middle_ground:
            first = True
        if is_role:
            party_end = previous_word.start()
        if ((len(simple_string)>0) and simple_string[0].isupper()) \
            or is_role \
            or re.search('\[[a-z]',ref_word) \
            or opened_paren \
            or (lowercase and paren_comma and (first or lowercase_parenthetical_commas_left_of_v)) \
            or (ref_word in not_uppercase_part_of_org_names+alias_words) \
            or (ref_word in prepositions) \
            or (last_corporate_ending and re.search('^[a-z\.]+$',ref_word))\
            or ((ref_word in org_ending_words) and ((ref_word != 'limited') or (not '.' in middle_ground))) \
            or (ref_word in person_ending_words)\
            or (is_number and (not found_name))\
            or ((len(ref_word)>0) and (ref_word[0]=="'") and ("'" in middle_ground))\
            or (ref_word in citation_filler_words):
            if re.search('\[[a-z]',ref_word):
                pass
            elif last_corporate_ending and (number_of_words < 2):
                pass
            elif title_word(ref_word):
                pass
            elif lowercase and first and paren_comma:
                lowercase_parenthetical_commas_left_of_v = True
                if opened_paren and ('(' in middle_ground):
                    opened_paren = False
            elif opened_paren and ('(' in middle_ground):
                opened_paren = False
            elif last_is_role and re.search('^[., ]*$',middle_ground):
                pass
            elif is_number and (not found_name):
                pass
            elif ((')' in middle_ground) and word_string.isupper()) or (('(' in middle_ground) and last_word_string and last_word_string.isupper()):
                pass
            elif lowercase and lowercase_parenthetical_commas_left_of_v:
                pass
            elif (ref_word in legislation_part_words) and re.search('[0-9]',middle_ground):
                pass
            elif re.search('[:]', middle_ground):
                previous_word = False
            elif ref_word in relational_dict:
                pass
            elif (ref_word in ['and','&','in','err']) and (last_is_role or (last_ref_word in  ['and','&','in','err'])):
                pass
            elif ref_word in pre_citation_words:
                previous_word = False
            elif ref_word in topic_matter_words:
                previous_word = False
            elif (not first) and (ref_word in latin_reference_words):
                previous_word = False
            elif (not one_line_objects) and (not first) and (not is_role) and re.search('[\(\)0-9]',middle_ground) and (not ref_word in ['no','nos']) and (not opened_paren) and found_name:
                previous_word = False
            elif ((ref_word[0]=="'") and ("'" in middle_ground)):
                pass
            elif (not one_line_objects) and (',' in middle_ground) and not(OK_comma_follows(ref_word,word_string[0])) \
              and (not ((len(matches)>0) and OK_comma_precedes(matches[-1].group(1).lower()))):
                previous_word = False
            elif ("." in middle_ground) and (not "," in middle_ground) and (not word_string.isupper()) and (ref_word in POS_dict) and (not ref_word in org_ending_words+person_ending_words+citation_filler_words+standard_words_with_periods_in_citations) and (not len(ref_word)==1):
                previous_word = False
            if previous_word and lowercase_parenthetical_commas_left_of_v and (not lowercase) and ("," in middle_ground):
                lowercase_parenthetical_commas_left_of_v = False
            if previous_word:
                number_of_words += 1
                current_end = previous_word.start()
                matches.append(previous_word)
                if is_role and previous_word:
                    in_error = in_error_pattern.search(line,previous_word.end())
                    if in_error and not(re.search('[^ ,]',line[previous_word.end():in_error.start()])):
                        ref_word = ref_word+' '+in_error.group(1).lower()
                if is_role and not (ref_word in roles):
                    roles.append(ref_word)
                if roles and (not is_role):
                    finished_roles = True
                if ref_word in org_ending_words:
                    last_corporate_ending = True
                else:
                    last_corporate_ending = False
                last_ref_word = ref_word
                last_word_string = word_string
                if is_role:
                    last_is_role = True
                elif last_is_role:
                    last_is_role = False
                if (not found_name) and (not is_role) and (len(word_string)>0) and word_string[0].isupper():
                    found_name = True
                previous_word = pattern.search(line[:current_end])
        else:
            previous_word = False
        if not (first and (is_role or lowercase_parenthetical_commas_left_of_v)):
            first = False
    if roles:
        roles.sort()
    while (ok_to_delete_left_most_vs_item (matches)):
        matches.pop()
        if len(matches) > 0:
            current_end=matches[-1].start()
        else:
            current_end = end
    if fail or (current_end == end):
        current_end = 'Fail'
        party = False
    else:
        party = line[current_end:party_end].strip(' ')
    return(current_end,roles,party,old_left_end)
    
    
## skip roles, citation_filler_words (currently just et and al)
## in tokenization, assume that apostrophe is part of words
## allow corporate endings (inc, etc) to follow commas 
## allow lowercase and to be part of names (but not if there is preceding punctuation)
## capital (Cf, See, Also, Re) ends a left name boundary (and is not included)
## in addition to normal names
## "The X of Name", e.g., "The State of Texas" are OK as well
## consecutive capitals can include certain lower case words 

## Abbreviations of the form "State, Ind." -- Capitalized word + comma + abbreviation or capital

## other exceptions org_ending_words are not a sufficient "left" name
## e.g., lowercase word would be needed for "investment Co. Institute v. Camp"

## if no left border, there is no citation, e.g., (section numbers that start with V)

def possibly_shorten_right_span(line,start,right_span):
    vs_anchor = re.compile('([^a-z])+(vs?[\. ])+([^a-z])*',re.I)
    ending_match = re.compile('([^ ]+)( {2,})[^ ]+',re.I)
    vs_match = vs_anchor.search(line[:right_span],start)
    if vs_match:
        ending = ending_match.search(line[:vs_match.start()])
        if ending and ((ending.end(1)-start)>10):
            return(ending.end(1))
    return(right_span)

def find_right_vs_border(line,start,right_span):
    global all_role_words
    right_span = possibly_shorten_right_span(line,start,right_span)
    output = []
    pattern = re.compile('[a-z\'\-&/\[\]]+',re.I) ## allow words to contain intermediate hyphens and apostrophes
    roles = []
    current_start=start
    next_word = pattern.search(line,current_start)
    matches = []
    party_end = start
    last_word = False
    date_match = date_pattern.search(line,start)
    vs_anchor = re.compile('([^a-z])+(vs?[\. ]|against|versus)+([^a-z])*',re.I)
    vs_anchor2 = re.compile('([A-Z])+(vs?\.?|against|versus)[A-Z]')
    vs_match = vs_anchor.search(line,start)
    vs_match2 = vs_anchor2.search(line,start)
    if vs_match and vs_match2:
        next_vs = min(vs_match.start(2),vs_match2.start(2))
    elif vs_match:
        next_vs = vs_match.start(2)
    elif vs_match2:
        next_vs = vs_match2.start(2)
    else:
        next_vs = False  
    if next_vs and re.search('[^a-zA-Z0-9][Nn][oO][^a-zA-Z0-9]',line[:next_vs]):
        next_vs = False
    ## not sure how this will deal with numbers as part of names, e.g., X No. 5
    while next_word and (next_word.end()<=right_span):
        word_string = next_word.group(0)
        ref_word = word_string.lower()
        middle_ground = line[current_start:next_word.start()]
        is_role = is_role_word(ref_word)
        if word_string[0].isupper() \
            or is_role \
            or (ref_word in not_uppercase_part_of_org_names) \
            or (ref_word in org_ending_words) \
            or (ref_word in person_ending_words) \
            or (ref_word in citation_filler_words) \
            or re.search('\[[a-z]',ref_word):
            if (len(matches)>0) and ((ref_word in latin_reference_words) or (ref_word in other_non_citation_legal_words) or (ref_word in months)):
                next_word = False
            elif re.search('[:]', middle_ground):
                next_word = False
            elif re.search('^ *, *[0-9]',middle_ground):
                next_word = False
            elif (ref_word in ['no.','no','nos','nos.']) or ((ref_word in ['no','nos']) and middle_ground.startswith('.')):
                next_word = False
            elif (ref_word == 'and') and next_vs and (next_vs > next_word.start()):
                next_word = False
            elif middle_ground.startswith('.') and (len(ref_word)>1) and next_vs and (next_vs > next_word.start()):
                next_word = False
            elif ((',' in middle_ground) or (';' in middle_ground)) and  next_vs and (next_vs > next_word.start()):
                next_word = False
            elif (',' in middle_ground) and not(OK_comma_precedes(ref_word)) \
              and (not((len(matches)>0) and OK_comma_follows(matches[-1].group(0).lower(),(matches[-1].group(0)[0])))):
                next_word = False
                ## multiple commas plus 'and' might be negatively effected, but this would require more look ahead and
                ## these are probably really "et al" cases                                                
            elif (not is_role) and ((last_word in citation_filler_words) and (',' in middle_ground)) or (';' in middle_ground):
                ## assume semi-colons are absolute borders
                next_word = False
            elif date_match and (next_word.start() > date_match.start()):
                next_word = False
            else:
                if not is_role:    
                    party_end = next_word.end()
                matches.append(next_word)
                if (len(matches)>0) and (next_word.end()<right_span) and (line[next_word.end()]==".") and \
                  (possible_abbrev(word_string) or ((len(line)> (next_word.end()+1)) and (line[next_word.end()+1] in ";,"))):
                    current_start = next_word.end()
                  ## not requiring capital for ., combo
                else:
                    current_start = next_word.end()
                if (current_start < right_span) and (line[current_start-1]=='-') and (re.search('^((17|18|19|20)[0-9][0-9])',line[current_start:])):
                    current_start = current_start+4
                    if not is_role:
                        party_end = party_end+4
                if is_role:
                    in_error = in_error_pattern.search(line,current_start)
                    if in_error and not(re.search('[^ ,]',line[current_start:in_error.start()])):
                        ref_word = ref_word+' '+in_error.group(1).lower()
                        current_start = in_error.end(1)
                last_word = ref_word
                next_word = pattern.search(line,current_start)
                if is_role and not (ref_word in roles):
                    roles.append(ref_word)
        else:
            next_word = False
    if roles:
        roles.sort()
    while (ok_to_delete_right_most_vs_item (matches)):
        matches.pop()
        if len(matches) > 0:
            if party_end == current_start:
                party_end = current_start=matches[-1].end()
            current_start=matches[-1].end()
            if (line[current_start-1]=='.') and (possible_abbrev(matches.group(0)) \
                                                 or ((len(line)>current_start+1) and (line[current_start] in ";,"))):
                current_start = current_start+1
                ## not requiring capital for ., combo
        else:
            current_start = start
    if current_start == start:
        current_start = 'Fail'
        party = False
    else:
        party = line[start:party_end].strip(' ')
    if party_end and current_start and isinstance(current_start,int) and (party_end > current_start):
        current_start = party_end
    return(current_start,roles,party)
    ## corporate endings (org_ending_words) can follow commas and be included in name
    ## latin_reference_words can signal that the name is over e.g., 
    ## I have only seen "supra" so far

    ## consecutive capitals can include certain lower case words 
    ## see:  not_uppercase_part_of_org_names

    ## ill-formed right context means no vs citation, e.g., if V is part of a section number in a book
    ## "See Plato, Republic, V, 461; Aristotle, Politics, VII, 1335b 25."

def really_initial_V_in_all_caps(line,match):
    if match:
        vs_anchor = re.compile('([^a-z])+(vs?[\. ]|against|versus)+([^a-z])*',re.I)
        second_vs = vs_anchor.search(line,match.end())
        if ('V' in match.group(0)) and (not re.search('[a-z]',line)) and second_vs:
            return(True)
        

def get_vs_citations(line,spans,offset,file_id,citation_dictionary,one_line_objects,line_number):
    ## if line follows one_line_objects, it is more likely to be a one line object
    vs_anchor = re.compile('([^a-z])+(vs?[\. ]|against|versus)+([^a-z])*',re.I)
    vs_anchor_lower = re.compile('([^a-zA-Z])+(vs?[\. ]|against|versus)+([^a-zA-Z])*')
    vs_anchor2 = re.compile('([A-Z])+(vs?\.?|against|versus)[A-Z]')
    ## vs_anchor2 only applies at the beginning of a file when allcaps might be used
    year_pattern = re.compile('^,? *\(((18|19|20)[0-9][0-9])\)')
    court_year_pattern = re.compile('^ *\(([CD]\. *C\.( *A\.)?) *((18|19|20)[0-9][0-9])?\)')
    match = vs_anchor.search(line)
    if really_initial_V_in_all_caps(line,match):
        match = vs_anchor.search(line,match.end())
    if not match:
        match = vs_anchor2.search(line)
        pattern2 = True
    elif match and ('V' in match.group(0)):
        match2 = vs_anchor_lower.search(line)
        if match2:
            match = match2
        pattern2 = False
    else:
        pattern2 = False
    output = []
    end_border = False
    end_border = False
    left_span = 0
    extended_left_start = False
    while match:
        ## find preceding and following spans
        right_span = len(line)
        for start,end in spans:
            start = start-offset
            end = end-offset
            if end_border and (end_border != 'Fail') and (end_border>end):
                end=end_border
            if (end> left_span) and (end < match.start()):
                left_span = end
            if (start < right_span) and (start > match.end()):
                right_span = start
        if pattern2:
            if "," in match.group(0):
                paren_comma = True
            else:
                paren_comma = False
            start_border,roles1,party1,extended_left_start = find_left_vs_border(line,match.start(2),left_span,one_line_objects,paren_comma,line_number)
            end_border,roles2,party2 = find_right_vs_border(line,match.end(2),right_span)
        else:
            if "," in match.group(0):
                paren_comma = True
            else:
                paren_comma = False
            start_border,roles1,party1,extended_left_start = find_left_vs_border(line,match.start(2),left_span,one_line_objects,paren_comma,line_number)
            end_border,roles2,party2 = find_right_vs_border(line,match.end(),right_span)
        if (start_border != 'Fail') and (end_border != 'Fail'):
            out = {'start':start_border+offset,'end':end_border+offset,'string':line[start_border:end_border],'extended_left_start':extended_left_start}
            out['vs_anchor']=match.group(2).strip(' ')
            add_citation_id(out,file_id,citation_dictionary)
            if party1:
                out['party1']=party1
            if party2:
                out['party2']=party2
            if len(roles1)>0:
                role_string = roles1[0]
                for role in roles1[1:]:
                    role_string = role_string+', '+role
                out['party1_role']=role_string
            if len(roles2)>0:
                role_string = roles2[0]
                for role in roles2[1:]:
                    role_string = role_string+', '+role
                out['party2_role']=role_string
            year_match = year_pattern.search(line[end_border:])
            if year_match:
                out['end']=out['end']+year_match.end()
                out['string']=line[start_border:(end_border+year_match.end())]
                out['year']=year_match.group(1)
            else:
                court_year_match = court_year_pattern.search(line[end_border:])
                if court_year_match:
                    out['court'] = court_year_match.group(1)
                    if court_year_match.group(3):
                        out['year'] = court_year_match.group(3)
            if ('party1' in out) and ('party2' in out):
                output.append(out)
        else:
            pass
        if end_border and (end_border != 'Fail') and (end_border>match.end()):
            match = vs_anchor.search(line,end_border)
            left_span = end_border
        else:
            match = vs_anchor.search(line,match.end())
        pattern2 = False
    return(output)
    
def non_initial_the(line,the_start,spans,offset):
    key_end = 0
    if spans and (len(spans) != 0):
        for start,end in spans:
            end = end-offset
            if (end < the_start) and (end > key_end):
                key_end = end
    if (key_end == 0):
        if re.search('\.[^\. ]*$',line[key_end:the_start]):
        ## This instance of 'The' is non-initial if
        ## it is preceded by some period '.'
        ## and there are non-periods/non-spaces between it and the closest preceding period
            return(True)
        else:
            return(False)
    elif (not '.' in line[key_end:the_start]) or re.search('\.[^\. ]*$',line[key_end:the_start]):
        ### This instance of 'The' is non-initial if there are no periods between
        ### the end of the last object and this instance of 'The', or if
        ### there is at least one non-period/non-space since the last period
        return(True)
    else:
        return(False)

def satisfies_the_case_constraints(case_string):
    case_string = case_string.lower()
    ## print(case_string)
    if re.search('(court)|(agreement)',case_string):
        return(False)
    elif re.search('^the *united *states( *of *america)? *$',case_string):
        return(False)
    else:
        return(True)

def edit_end_of_other_case_citations(line,start,end):
    last_word = re.search(' *([^ ]+) *$',line[:end])
    number_pattern = re.compile('[0-9]+(, [0-9]+)*( +and +[0-9]+)?',re.I)
    number_key_pattern = re.compile('(amendment|rule)?',re.I)
    while last_word:
        ref_word = last_word.group(0).strip(' .-,').lower()
        if ref_word in latin_reference_words + other_non_citation_legal_words + months + ['no']:
            end = last_word.start()
            if line[end]==' ':
                non_space = re.search('([^ ]) *$',line[:end])
                if non_space:
                    end = non_space.end(1)
            if start == end:
                return(end)
            else:
                last_word = re.search('[^ ]+ *$',line[:end])
        else:
            last_word = False
    if (end<len(line)) and line[end]==',':
        next_word = re.search('[^ ,\.]+',line[end:])
        if next_word and (next_word.group(0).lower() in org_ending_words+person_ending_words):
            end = end+next_word.end()
    if number_key_pattern.search(line[start:end]):
        number_match = number_pattern.search(line,end)
        if number_match and not re.search('[A-Za-z]',line[end:number_match.start()]):
            end = number_match.end()            
    if line[end-1] in '.,: ':
        end=end-1
    return(end)

def possibly_extend_other_case_end(rest_of_line):
    if re.search(';',rest_of_line):
        return(False)
    word_pattern = re.compile('[A-Za-z0-9]+')
    start = 0
    match = word_pattern.search(rest_of_line)
    while match:
        ref_word = match.group(0).lower()
        if ref_word in latin_reference_words+other_non_citation_legal_words+months:
            return(False)
        if ref_word == 'no':
            return(False)
        elif ('.' in rest_of_line[start:match.start()]) and ((ref_word in POS_dict) and (not ref_word in standard_words_with_periods_in_citations)):
            return(False)
        else:
            start = match.end()
            match = word_pattern.search(rest_of_line,start)
    return(start)
            
def no_other_significant_words(instring):
    instring = instring.lower()
    special_word = False
    other_words = ['ex','parte','the','matter','application','claim','estate','ex','parte','petitioner','claimant','s',\
                   'matters','applications','claims','estates','petitioners','claimants']
    other_words.extend(prepositions)
    for word in re.split('[^a-zA-Z0-9]',instring):
        if special_word or (word in other_words) or (len(word)<4):
            pass
        else:
            special_word = True
    if special_word:
        return(False)
    else:
        return(True)

def other_case_citation_OK(entry):
    if 'name' in entry:
        case_name = entry['name'].lower()
        words = []
        for word in case_name.split(' '):
            if word not in ['ex','parte','case','in','re','the','matter','of']:
                words.append(word)
        if len(words)>0:
            return(True)

def get_other_case_citations(line,spans,offset,file_id,citation_dictionary,one_line_objects):
    ### new patterns
    pre_cap_noun = '(((Ex [Pp]arte)|(The)|(In [Rr]e)|((In )?(the )?[mM]atter of( the)?)|(Application of)|(Claims of)|Estate of|(EX PARTE)|(THE)|(IN RE)|((IN )?(THE )?MATTER OF)|(APPLICATION OF)|(CLAIMS OF)|ESTATE OF)((( +[\'"]?[A-Z][\&A-Za-z-—\./]*)( of)?(( +[\'"]?[\&A-Z][\&A-Za-z-—\./]*,?[\'"]?){0,3})[\'"]?)|(( [\'"]?[A-Z-—]+)(( +\'[\&A-Z-—\./]+,?[\'"]?){0,3}))))' 
    post_cap_noun = '(([0-9]{1,3} )?((([A-Z][\&A-Za-z-—]*(\'[Ss])? ){1,4})|(([\&A-Z-—]+ ){1,10}))((Cases?)|(CASES?)))'
    petitioner_pattern = '((Re|RE)((( +[\'"]?[A-Z][\&A-Za-z-—\.]*)(( +[A-Z][\&A-Za-z-—\.]*){0,3})[\'"]?)|(( [\'"]?[A-Z-—]+)(( +[\&A-Z-\.]+){0,3}[\'"]?)))(, *)(Petitioners?|PETITIONERS?|Claimants?|CLAIMANTS?))'
    possessive_pattern = '((^| +)([A-Z][A-Za-z]*\'[Ss] +[A-Za-z\&]+)(( *$)|\.))' ## must end line or be followed by a period
    other_citation_pattern = re.compile(pre_cap_noun+'|'+post_cap_noun+'|'+petitioner_pattern+'|'+possessive_pattern)
    ## group 47 matches petitioner
    ## other group numbers are also fixed -- need to modify code if
    ## regex for other_citation_pattern is modified
    short_all_caps_line = re.compile('^ *(([A-Z]+)(( [A-Z\.]+){0,3})) *$')
    court_year_pattern = re.compile('^ *\(([CD]\. *C\.( *A\.)?) *((18|19|20)[0-9][0-9])?\)')
    extra_petitioner_pattern = re.compile(',? *(Petitioners?|PETITIONERS?|Claimants?|CLAIMANTS?)')
    all_caps_match = False
    ### change this so that we only search in between spans
    ### editing afterwards loses some instances
    last_span = False
    search_spans = []
    if not spans:
        search_spans = [[0,len(line)]]
    for span in spans:
        if not last_span:
            start = 0
        else:
            start = last_span[1]-offset
        end = span[0]-offset
        search_spans.append([start,end])
        last_span = span
    if last_span:
        start = last_span[1]-offset
        search_spans.append([start,len(line)])
    output = []
    for span_start,span_end in search_spans:
        match = other_citation_pattern.search(line[:span_end],span_start)
        if not match:
            match = short_all_caps_line.search(line[:span_end],span_start)
            if match and one_line_objects and member_if_attribute(one_line_objects,'entry_type','standard_case'):
                all_caps_match = True
            else:
                match = False
                all_caps_match = False
        while match:
            court = False
            year = False
            party1 = False
            party1_role = False
            start = match.start()
            end = match.end()
            end = edit_end_of_other_case_citations(line[:span_end],start,end)
            start_boost = re.search('[^ ]',line[start:])
            if start_boost:
                start = start+start_boost.start()
            if end-start<5:
                match = False
            if not match:
                pass
            elif (not all_caps_match) and match.group(2) and ((match.group(2).lower() !='the') or satisfies_the_case_constraints(match.group(0))):
                if start == end:
                    match = False
                if match:
                    ## these group numbers are sensitive to changes
                    ## in the above regexs
                    if no_other_significant_words(match.group(0)):
                        match = False
                        petitioner_match = False
                        extended_match = False
                    else:
                        case_name = line[start:end]
                        extended_match = court_year_pattern.search(line[end:span_end])
                        petitioner_match = extra_petitioner_pattern.search(line[end:span_end])
                else:
                    extended_match = False
                    petitioner_match = False
                if match and petitioner_match:
                    if petitioner_match.end() == end:
                        pass
                    else:
                        extend_end = possibly_extend_other_case_end(line[end:end+petitioner_match.start()])
                        if extend_end:
                            end = end + extend_end
                        elif not re.search('[A-Za-z0-9]',line[end:end+petitioner_match.start()]):
                            pass
                        else:
                            petitioner_match = False
                    if petitioner_match:
                        party1_role = petitioner_match.group(1)
                        party1 = line[match.start(20):end]  ##
                        case_name = line[start:end]
                        end = end+(petitioner_match.end()-petitioner_match.start())
                if match and not petitioner_match:
                    petitioner_match = extra_petitioner_pattern.search(match.group(0))
                    if petitioner_match and not re.search('[A-Za-z0-9]',match.group(0)[petitioner_match.end():]):
                        party1_role = petitioner_match.group(0)
                        party1 = line[match.start(20):start+petitioner_match.start()].strip(' ')
                        case_name = line[start:start+petitioner_match.start()]
                if extended_match:
                    court = extended_match.group(1)
                    if extended_match.group(3):
                        year = extended_match.group(3)
                    end = end+extended_match.end()
                if match and match.group(2) and (match.group(2).lower()=='the'):
                    if (not extended_match) and (not non_initial_the(line,match.start(),spans,offset)) and (not one_line_objects):
                        match = False
                    ## + offset
                ## 'year'
                ## 'court'
                ## 'end'
                ## additional conditions on 'The' cases (group(2) = 'The')
                if match:
                    ## print(1,match.group(0))
                    out = {'start': start+offset, 'end': end+offset,'string':line[start:end],'name':case_name}
                    if court:
                        out['court'] = court
                    if year:
                        out['year'] = year
                    if party1:
                        out['party1']=party1
                    if party1_role:
                        out['party1_role']=party1_role
                    if other_case_citation_OK(out):
                        add_citation_id(out,file_id,citation_dictionary)
                        output.append(out)
            elif (not all_caps_match) and  match.group(53) and (len(match.group(53))>0):
                start = match.start()
                end = match.end()
                if start !=end:
                    case_name = line[start:match.start(52)]
                    party1_role = match.group(53)
                    party1 = match.group(43)
                    out = {'start': start+offset, 'end': end+offset,'string':line[start:end],'name':case_name,'party1':party1,'party1_role':party1_role}
                    if other_case_citation_OK(out):
                        add_citation_id(out,file_id,citation_dictionary)
                        output.append(out)
                else: 
                    match = False
            elif all_caps_match:
                start = match.start()
                end = match.end()
                if start !=end:
                   case_name = match.group(1)
                   out = {'start': start+offset, 'end': end+offset,'string':line[start:end],'name':case_name}
                   if other_case_citation_OK(out):
                       add_citation_id(out,file_id,citation_dictionary)
                       output.append(out)
                else:
                    match = False
            elif match.group(30):
                case_name = match.group(0)
                out = {'start': start+offset, 'end': end+offset,'string':line[start:end],'name':case_name}
                if other_case_citation_OK(out):
                    add_citation_id(out,file_id,citation_dictionary)
                    output.append(out)
            elif match.group(54):
                case_name = match.group(56)
                start = match.start(56)
                end = match.end(56)
                out = {'start': start+offset, 'end': end+offset,'string':case_name,'name':case_name}
                if other_case_citation_OK(out):
                    add_citation_id(out,file_id,citation_dictionary)
                    output.append(out)
            else:
                extended_match = False
                petitioner_match = False
            if end:
                match = other_citation_pattern.search(line[:span_end],end)
    return(output)
    
def fill_dictionary_from_xml(all_text,previous_info_fields,previous_info_dictionary):
    ## currently only gets functional values -- if info is repeated, last value is kept
    ## currently assumes no embeddings
    ## currently only gets simple values (between start and end xml)
    ## more elaborate to get other stuff
    xml_pattern = re.compile('<([^>]+)>')
    unary_pattern = re.compile('/$')
    end_pattern = re.compile('^/')
    key = re.compile('^[^> /]+')
    start = 0
    match = xml_pattern.search(all_text)
    while match:
        interior = match.group(1)
        if unary_pattern.search(interior):
            ## current version does not use these
            pass
        elif end_pattern.search(interior):
            end_key_match = key.search(interior[1:])
            if (key_match.group(0) in previous_info_fields) and (end_key_match.group(0) == key_match.group(0)):
                value = all_text[start_end:match.start()]
                previous_info_dictionary[key_match.group(0)]=value
        else:
            key_match = key.search(interior)
            start_end = match.end()
        start = match.end()
        match = xml_pattern.search(all_text,start)

def word_overlap(string1,string2):
    set_1 = re.split('[^a-z]',string1.lower())
    set_2 = re.split('[^a-z]',string2.lower())
    for word in set_1:
        if word in set_2:
            return(True)

def OK_vs_filter(citation,previous_info_dictionary):
    simple_vs_pattern = re.compile('^ *(.*) *(vs?\.?|against) *(.*)$')
    string = citation['string']
    if 'vs_anchor' in citation:
        vs_anchor = citation['vs_anchor']
    else:
        vs_anchor = False
    if 'party1' in citation:
        party1 = citation['party1']
    else:
        party1 = False
    if 'party2' in citation:
        party2 = citation['party2']
    else:
        party2 = False
    if vs_anchor in ['V','V.']:
        if string.isupper() and party1 and party2 and ('citation_case_name' in previous_info_dictionary):
            match = simple_vs_pattern.search(previous_info_dictionary['citation_case_name'])
            if match:
                dictionary_party1 = match.group(1)
                dictionary_party2 = match.group(3)
            else:
                dictionary_party1 = False
                dictionary_party2 = False
            if dictionary_party1 and dictionary_party2 and word_overlap(party1,dictionary_party1) and word_overlap(party2,dictionary_party2):
                return(True)
            else:
                return(False)
        else:
            ## capital V can only be used for all uppercase, otherwise it is an initial
            return(False)
    elif vs_anchor.lower() == 'against':
        if ('party1_role' in citation) and ('party2_role' in citation):
            return(True)
        else:
            return(False)
    else:
        return(True)

def edit_vs_citations(out3,previous_info_dictionary):
    output = []
    for out in out3:
        if OK_vs_filter(out,previous_info_dictionary):
            output.append(out)
    return(output)

def merge_relational_entries(word,entry):
    if len(entry)==1:
        return(entry[0])
    if len(entry)>2:
        print('Too many classes for',word+':',entry)
        return(entry[0])
    elif ('RANK' in entry) and ('PROFESSIONAL' in entry):
        return('PROFESSIONAL_OR_RANK')
    else:
        print('Unexpected class combo for',word+':',entry)
        return(entry[0])
        

def next_word_is_sentence_likely_starter(rest_of_line):
    pattern = re.compile('[a-z\'\-&/\[\]]+',re.I) ## allow words to contain intermediate hyphens and apostrophes
    rest_of_line = rest_of_line.lstrip(' ')
    if len(rest_of_line)<1:
        pass
    elif rest_of_line[0].isupper():
        match = pattern.search(rest_of_line)
        if match:
            word = match.group(0)
            if word.lower() in POS_dict:
                for POS in POS_dict[word.lower()]:
                    if POS in ['ORDINAL', 'CARDINAL', 'WORD','PRONOUN', 'QUANT', 'AUX', 'DET', 'SCOPE']:
                        return(True)

def end_of_sentence_heuristic (word,line,next_position):
    end_of_sent_pattern = re.search('^ *[.?!]',line[next_position:])
    if end_of_sent_pattern:
        rest_of_line = line[next_position+len(end_of_sent_pattern.group(0)):]
    if end_of_sent_pattern and not (possible_abbrev(word)):        
        if next_word_is_sentence_likely_starter(rest_of_line):
            return(True)
        elif re.search('^ *[a-z]',rest_of_line):
            ## if the next word is lowercase, it is not the end of the sentence
            return(False)
            ## if beginning of next sentence is uppercase word and member of a list of likely sentence beginnings
            ## it is likely to be a sentence boundary
        elif next_word_is_sentence_likely_starter(rest_of_line):
            return(True)
        elif possible_abbrev(word):
            ## if the word is a possible abbrevation, this may not be the end of the sentence
            return(False)
        else:
            return(True)
    elif end_of_sent_pattern and rest_of_line and next_word_is_sentence_likely_starter(rest_of_line):
        return(True)
    else:
        return(False)


def start_sentence_heuristic(word,line,start):
    if start == 0:
        return(True)
    previous_word_match = re.search('([A-Za-z0-9]+)[^A-Za-z0-9]*$',line[:start])
    if not previous_word_match:
        return(True)
    elif end_of_sentence_heuristic(previous_word_match.group(1),line[previous_word_match.end(1):],0):
        return(True)
    else:
        return(False)

def reprocess_role_phrase(line,start,end,offset,in_or_out):
    word_pattern = re.compile('[1-4]?[A-Z-]+',re.I)
    match = word_pattern.search(line,start)
    so_far = start
    sequence = []
    out = {}
    words = []
    while match and (so_far < end):
        word = match.group(0)
        if len(sequence)==0:
            out['start']=match.start()+offset
        if word.lower() in relational_dict:
            sequence.append(merge_relational_entries(word.lower(),relational_dict[word.lower()]))
            words.append(word)
            so_far = match.end()
        elif word.lower() in not_uppercase_part_of_org_names:
            sequence.append('FILLER')
            words.append(word)
            so_far = match.end()
        elif (match.end()+1<len(line)) and (line[match.end()+1]=='.') and ((word.lower()+'.') in relational_dict):
            sequence.append(merge_relational_entries(word.lower()+'.',relational_dict[word.lower()+'.']))
            words.append(word)
            so_far = match.end()+1
        elif word.lower() in time_dict:
            sequence.append('TIME_NAME')
            words.append(word)
            so_far = match.end()
        elif (match.end()+1<len(line)) and (line[match.end()+1]=='.') and ((word.lower()+'.') in time_dict):
            sequence.append('TIME_NAME')
            words.append(word)
            so_far = match.end()+1
        elif capitalized_word(word):
            sequence.append('CAPITALIZED_WORD')
            words.append(word)
            if ((match.end()+1<len(line)) and (line[match.end()+1]=='.')  and (possible_abbrev(word))) \
               or ((match.end()+2<len(line)) and (line[match.end()+1]=='.') and (line[match.end()+2] in ';,')):
                so_far = match.end()+1
            else:
                so_far = match.end()
            add_on = True
        else:
            words.append(word)
            so_far = match.end()
        match = word_pattern.search(line,so_far)
        if match and (match.end()>end):
            match = False
    if not 'start' in out:
        return(False,False,False)
    if line[:so_far].endswith('-'):
        so_far = so_far-1
    out['end']=so_far+offset
    if in_or_out == 'internal':
        if ('FAMILY' in sequence) or ('LEGAL_ROLE' in sequence) or ('PROFESSIONAL' in sequence) or \
          ('PROFESSIONAL_OR_RANK' in sequence) or ('ORGANIZATION' in sequence) or \
          ('PLURAL_FAMILY' in sequence) or ('PLURAL_LEGAL_ROLE' in sequence) or ('PLURAL_PROFESSIONAL' in sequence)\
          or ('PLURAL_ORGANIZATION' in sequence):
            return(out,sequence,words)
        else:
            return(False,False,False)            
    else:
        return(out,sequence,words)

def trim_right_edge_of_role_phrase(out,sequences,offset,words,line):
    if (not sequences) or (len(sequences)<1):
        return(False,False,False,False)
    new_out = out.copy()
    new_sequences = sequences[:]
    new_words = words[:]
    done = False
    while (len(new_sequences)>0) and not done:
        if new_sequences[-1] in ['FAMILY','PLURAL_FAMILY','LEGAL_ROLE','PLURAL_LEGAL_ROLE',\
                                 'PROFESSIONAL','PLURAL_PROFESSIONAL','PROFESSIONAL_OR_RANK',\
                                 'PLURAL_ORGANIZATION','ORGANIZATION']:
            done = True
        elif new_sequences[-1] in ['CAPITALIZED_WORD']:
            ### may want to refine this
            done = True
        elif sequences[-1] in ['FILLER','TIME_NAME']:
            new_sequences.pop()
            new_words.pop()
        else:
            done = True
    if new_sequences == sequences:
        return(False,False,False,False)
    elif len(new_sequences) == 0:
        return(False,False,True,False)
    else:
        string_approx = ''
        for index in range(len(new_words)):
            word = new_words[index]
            if index<(len(new_words)-1):
                string_approx = string_approx+word+'(?:[^a-zA-Z]+)'
            else:
                string_approx = string_approx+word
        string_pattern = re.compile(string_approx)
        string_match = string_pattern.search(line,(out['start']-offset))
        if string_match:
            new_out['end']=string_match.end()+offset
            return(new_out,new_sequences,False,new_words)
        else:
            return(False,False,False,False)

def unprefixed_word(word):
    prefix_pattern = re.compile('^(p?re|un|anti|co|de|post|ex|extra|fore|non|over|pro|super|tri|bi|uni|ultra)')
    prefix_match = prefix_pattern.search(word)
    if prefix_match:
        return(word[prefix_match.end():])
    else:
        return(False)

def prefixed_non_name_word(word):
    unprefixed = unprefixed_word(word)
    if unprefixed and (unprefixed in POS_dict) and (not ('PERSONNAME' in POS_dict[unprefixed]) or ('GPE' in POS_dict[unprefixed])):
        return(True)

def name_word(word):
    lower = word.lower()
    if lower in POS_dict:
        if ('PERSONNAME' in POS_dict[lower]) or ('GPE' in POS_dict[lower]):
            return(True)
        else:
            return(False)
    elif prefixed_non_name_word(lower):
        return(False)
    elif possible_abbrev(word):
        return(False)
    elif word.istitle():
        return(True)
    else:
        return(False)

def one_word_restriction(sequence,words):
    if (len(sequence)==1) and (sequence[0] in ['CAPITALIZED_WORD']) and (not name_word(words[0])):
        return(True)

def ok_role_phrase2(out,sequence,spans,string,line,offset):
    ## 1st check if it overlaps with any spans
    new_items = []
    if ((out['end']-out['start']) <2) or ([out['start'],out['end']] in spans):
        ## do not allow completely duplicate spans
        return(False,False)
    for span_start,span_end in spans:
        if (out['start']>=span_start):
            if out['end'] <=span_end:
                ## if it is totally inside of a span, it is only OK if it can be one of our select name types
                if (('FAMILY' in sequence) or ('LEGAL_ROLE' in sequence) or ('PROFESSIONAL' in sequence) or \
                  ('PROFESSIONAL_OR_RANK' in sequence) or ('PLURAL_FAMILY' in sequence) or \
                  ('PLURAL_LEGAL_ROLE' in sequence) or ('PLURAL_PROFESSIONAL' in sequence) or \
                  ('ORGANIZATION' in sequence) or ('PLURAL_ORGANIZATION' in sequence)):
                    return(False,True)
                else:
                    return(False,False)
            elif out['start']<span_end:
                ## overlap case 1 -- start of item is "part" of existing span
                new_phrase1,new_sequence1,words1=reprocess_role_phrase(line,out['start']-offset,span_end-offset,offset,'internal')
                new_phrase2,new_sequence2,words2=reprocess_role_phrase(line,span_end-offset,out['end']-offset,offset,'external')
                if new_phrase2:
                    new_phrase2a,new_sequence2a,fail,words2a=trim_right_edge_of_role_phrase(new_phrase2,new_sequence2,offset,words2,line)
                    if fail:
                        new_phrase2 = False
                    elif new_phrase2a:
                        new_phrase = new_phrase2a
                        new_sequence2=new_sequence2a
                        words2 = words2a
                output = []
                if new_phrase1 and (not one_word_restriction(new_sequence1,words1)):
                    output.append([new_phrase1,new_sequence1,words1])
                if new_phrase2 and (not one_word_restriction(new_sequence2,words2)):
                    output.append([new_phrase2,new_sequence2,words2])
                if (len(output)>0):
                    return(output,False)
                else:
                    return(False,False)
            else:
                ## no overlap
                pass
        elif (out['end']<=span_end) and (out['end']>span_start):
            ## overlap case 2 -- end of item is "part" of existing span
            new_phrase1,new_sequence1,words1=reprocess_role_phrase(line,out['start']-offset,span_start-offset,offset,'external')
            new_phrase2,new_sequence2,words2=reprocess_role_phrase(line,span_start-offset,out['end']-offset,offset,'internal')
            if new_phrase1:
                new_phrase1a,new_sequence1a,fail,words1a=trim_right_edge_of_role_phrase(new_phrase1,new_sequence1,offset,words1,line)
                if fail:
                    new_phase1 = False
                elif new_phrase1a:
                    new_phrase1 = new_phrase1a
                    new_sequence1=new_sequence1a
                    words1=words1a
            output = []
            if new_phrase1 and (not one_word_restriction(new_sequence1,words1)):
                output.append([new_phrase1,new_sequence1,words1])
            if new_phrase2 and (not one_word_restriction(new_sequence2,words2)):
                output.append([new_phrase2,new_sequence2,words2])
            if len(output)>0:
                return(output,False)
            else:
                return(False,False)
        elif (out['start']<=span_start) and (out['end']>=span_end):
            ## what if an existing span is part of a proposed name
            new_phrase1,new_sequence1,words1=reprocess_role_phrase(line,out['start']-offset,span_start-offset,offset,'external')
            new_phrase2,new_sequence2,words2=reprocess_role_phrase(line,span_end-offset,out['end']-offset,offset,'external')
            if new_phrase1:
                new_phrase1a,new_sequence1a,fail,words1a=trim_right_edge_of_role_phrase(new_phrase1,new_sequence1,offset,words1,line)
                if fail:
                    new_phase1 = False
                elif new_phrase1a:
                    new_phrase1 = new_phrase1a
                    new_sequence1=new_sequence1a
                    words1=words1a
            output = []
            if new_phrase1 and (not one_word_restriction(new_sequence1,words1)):
                output.append([new_phrase1,new_sequence1,words1])
            if new_phrase2 and (not one_word_restriction(new_sequence2,words2)):
                output.append([new_phrase2,new_sequence2,words2])
            if len(output)>0:
                return(output,False)
            else:
                return(False,False)
    return(False,True)

def possibly_split_role_phrase(out,sequence,offset,words,line):
    triples = [] ## new sequences of out,sequence,words
    infixed_role_position = False
    if len(sequence) == 0:
        return(False)
    elif (sequence[-1] in ['CAPITALIZED_WORD']):
        split_point = False
        for num in range(1,len(sequence)+1):
            index = len(sequence)-num
            item = sequence[index]
            if (item in ['FAMILY','PLURAL_FAMILY','LEGAL_ROLE','PLURAL_LEGAL_ROLE',\
                        'PROFESSIONAL','PROFESSIONAL_OR_RANK','ORGANIZATION']) and \
                        (sequence[index+1] in ['CAPITALIZED_WORD']):
                        ## plural_professional ignored for now (caused some errors)
                if ((index==0) or (not sequence[index-1] in ['CAPITALIZED_WORD'])):
                    split_point = index+1
                elif sequence[index-1] in ['CAPITALIZED_WORD']:
                    infixed_role_position = index
                    out['name_with_infixed_role'] = True
                break
        if split_point:
            seq1 = sequence[:split_point:]
            seq2 = sequence[split_point:]
            words1 = words[:split_point]
            words2 = words[split_point:]
            string_approx = ''
            for word in words1:
                string_approx = string_approx+word+'([^a-zA-Z]*)'
            match = re.search(string_approx,line[out['start']-offset:out['end']-offset])
            if not match:
                ## these are not likely to be correct, e.g., these cases have lots of
                ## intervening punctuation
                # print('error',out,sequence,offset,words,line,sep=os.linesep)
                # input(' ')
                return(False)
            else:
                end1 = out['start']+match.start(len(words1))
                ## end the first phrase at the beginning of the space between the last
                ## word in word1 and the first word in words2
                start2 = out['start']+match.end(len(words1))
                ## start the 2nd phrase at the end of this same space
                out1={'start':out['start'],'end':end1}
                out2={'start':start2,'end':out['end']}
                return([out1,seq1,words1],[out2,seq2,words2])
        elif infixed_role_position:
            infixed_seq = [sequence[infixed_role_position]]
            infixed_words = [words[infixed_role_position]]
            string_approx = ''
            for word in words[:infixed_role_position]:
                string_approx = string_approx+word+'([^a-zA-Z]*)'
            match = re.search(string_approx,line[out['start']-offset:out['end']-offset])
            if not match:
                return(False)
            else:
                start1 = out['start']+match.end(index)
                string_approx = string_approx+infixed_words[0]
                match = re.search(string_approx,line[out['start']-offset:out['end']-offset])
                if not match:
                    return(False)
                else:
                    end1 = out['start']+len(match.group(0))
                    out1 = {'start':start1,'end':end1}
                    return([out,sequence,words],[out1,infixed_seq,infixed_words])
        else:
            return(False)
    elif (sequence[-1] in ['RANK']) and (not ('PROFESSION' in sequence)) and (not ('PROFESSIONAL_OR_RANK' in sequence)):
        new_end = re.search(' *'+words[-1],line[:out['end']],re.I).start()
        out['end']=new_end
        sequence = sequence[:-1]
        words = words[:-1]
        return([out,sequence,words],[False,False,False])
    else:
        return(False)

def check_items_in_list(items_to_check,big_list):
    for item in items_to_check:
        if item in big_list:
            return(True)
    else:
        return(False)

def really_ambigous_name_word(lower,word,start_sentence):
    ## applies only to one word cases
    entry = []
    if lower in POS_dict:
        entry.extend(POS_dict[lower])
    if lower in relational_dict:
        entry.extend(relational_dict[lower])
    if (lower in pre_citation_words) or (lower in topic_matter_words) or (lower in citation_closed_class):
        return(True)
    elif check_items_in_list(['DISCOURSE','NATIONALITY','TITLE','ORDINAL', 'CARDINAL', 'WORD','PRONOUN', 'QUANT', 'AUX', 'DET', 'SCOPE'],entry):
        return(True)
    elif start_sentence and word.istitle() and name_word(word):
        for classification in entry:
            if not classification in ['FIRSTNAME','GPE','PERSONNAME','ORG']:
                return(True)
    return(False)

def ok_role_phrase(out,sequence,spans,string,line,offset,words):
    if ('sentence_start' in out) and out['sentence_start']:
        start_sentence = True
    else:
        start_sentence = False
    if not out:
        return(False,False)
    triples=possibly_split_role_phrase(out,sequence,offset,words,line)
    if triples:
        new_triples = []
        for new_out,new_sequence,new_words in triples:
            new_out2,new_sequence2,fail,new_words2=trim_right_edge_of_role_phrase(new_out,new_sequence,offset,new_words,line)
            if fail:
                pass
            elif new_out2:
                new_triples.append([new_out2,new_sequence2,new_words2])
            else:
                new_triples.append([new_out,new_sequence,new_words])
        if len(new_triples)>0:
            triples = new_triples[:]
    elif (len(sequence) == 1) and (sequence[0] in ['CAPITALIZED_WORD']) and (not name_word(words[0])):
        ## possibly add to list of unsuitable cases
        ## print('OUT1:',1)
        return(False,False)
    elif (len(sequence) ==1) and really_ambigous_name_word(words[0].lower(),words[0],start_sentence):
        if words[0].lower() in one_word_person_names:
            ## keep only if previously used as a party in a case
            return(False,True) 
        else:
            return(False,False)
    else:
        new_out,new_sequence,fail,new_words=trim_right_edge_of_role_phrase(out,sequence,offset,words,line)
        if new_out:
            triples = possibly_split_role_phrase(new_out,new_sequence,offset,new_words,line)
    if fail:
        ## print('OUT1:',2)
        return(False,False)
    elif triples and (len(triples)>0):
        new_phrases = []
        new_word_sequences = []
        for new_out2,new_sequence2,new_words2 in triples:
            if new_out2:
                new_phrases2,good = ok_role_phrase2(new_out2,new_sequence2,spans,line[new_out2['start']-offset:new_out2['end']-offset],line,offset)
                if good:
                    new_phrases.append([new_out2,new_sequence2,new_words2])
                elif new_phrases2:
                    new_phrases.extend(new_phrases2)
    elif new_out:
        new_phrases,good = ok_role_phrase2(new_out,new_sequence,spans,string,line,offset)
    else:
        new_phrases,good = ok_role_phrase2(out,sequence,spans,string,line,offset)
    if new_phrases and (len(new_phrases)>0):
        return(new_phrases,False)
    elif new_out:
        if good:
            return([[new_out,new_sequence,new_words]],False)
        else:
            ## print('OUT1:',5)
            return(False,False)
    else:
        ## print('OUT1:',6)
        return(new_phrases,good)
    
def OK_family_pattern(sequence,words):
    if 'FAMILY' in sequence:
        position = sequence.index('FAMILY')
    else:
        position = sequence.index('PLURAL_FAMILY')
    before = words[:position]
    after = words[position+1:]
    if len(words) == 1:
        return(True)
    elif len(before)>0 and ((before[-1].lower() in ['his','her','my','your','their','our']) \
                          or (before[-1].lower().endswith('\'s')) or (before[-1].lower().endswith('s\''))):
        return(True)
    if ('of' in after):
        position2 = after.index('of')
    elif ('OF' in after):
        position2 = after.index('OF')
    else:
        return(False)
    position = position + position2
    ### possibility for stronger or weaker requirement
    if 'PERSONNAME' in sequence[position:]:
        return(True)
    else:
        return(False)

def find_unambig_person(words):
    OK = False
    BAD = False
    for word in words:
        word = word.lower()
        if (word in POS_dict):
            entry = POS_dict[word]
            for item in entry:
                if item in ['FIRSTNAME']:
                    OK =True
                elif item in ['PERSONNAME']:
                    pass
                else:
                    BAD = True
        elif not re.search('^[a-z\.]+$',word):
            BAD = True
    if (OK and (not BAD)):
        ## print(words)
        return(True)
    else:
        return(False)
                    
    
def person_pattern(sequence,words):
    if ('Filler' in sequence) or (len(words) < 1) or (len(sequence)< 1) or ('&' in words):
        return(False)
    elif (words[-1].lower() in person_ending_words) and (len(words) > 2) and (len(words) <= 5):
        return(True)
    elif (sequence.count('INITIAL') == 1) and  (sequence[-1] != 'INITIAL') and (len(words) > 1) and (len(words)<=3):
        return(True)
    elif 'INITIAL' in sequence:
        return(False)
    elif (words[0].lower() in POS_dict) and ('TITLE' in (POS_dict[words[0].lower()])) and (len(words) > 1) and (len(words) <= 5):
        return(True)
    elif (len(sequence) > 1) and (len(sequence)<=3) and (('PERSONNAME' in sequence) or find_unambig_person(words)):
        return(True)
    else:
        return(False)


def find_phrase_type_from_sequence(sequence,words):
    ### need to include word sequences as argument
    ## print(sequence,words)
    if len(sequence) != len(words):
        print('Bad input for find_phrase_type_from_sequence')
        print(sequence)
        print(words)
    if 'LEGISLATIVE' in sequence:
        return('NAME',False)
    elif 'LEGAL_ROLE' in sequence:
        return('LEGAL_ROLE',False)
    elif 'ORGANIZATION' in sequence:
        return('ORGANIZATION', False)
    elif 'PLURAL_ORGANIZATION' in sequence:
        return('ORGANIZATION', True)
    elif 'PROFESSIONAL' in sequence:
        return('PROFESSION',False)
    elif 'PROFESSIONAL_OR_RANK' in sequence:
        return('PROFESSION',False)
    elif ('FAMILY' in sequence) and OK_family_pattern(sequence,words):
        return('FAMILY',False)
    if 'PLURAL_LEGAL_ROLE' in sequence:
        return('LEGAL_ROLE',True)
    elif 'PLURAL_PROFESSIONAL' in sequence:
        return('PROFESSION',True)
    elif ('PLURAL_FAMILY' in sequence) and OK_family_pattern(sequence,words):
        ## ** 57 
        return('FAMILY',True)
    elif person_pattern(sequence,words):
        return('PERSON',True)
    elif 'CAPITALIZED_WORD' in sequence:
        return('NAME',False)
    elif 'TIME_NAME' in sequence:
        return('DATE',True)
    else:
        return(False,False)

def ok_non_vocab_word_start_sequence(word,start_sentence):
    if (word.lower() in not_uppercase_part_of_org_names):
        return(False)
    elif (word.lower() in POS_dict):
        keep = False
        toss = False
        confident_keep = False
        confident_toss = False
        if is_month.search(word.lower()):
            ## precedes other checks
            ## print('*',word)
            return(False)
        for POS in POS_dict[word.lower()]:
            if POS in ['NOUN','ADJECTIVE']:
                keep = True
            elif POS in ['ADVERB','ORDINAL', 'CARDINAL', 'PREP', 'WORD','PRONOUN', 'QUANT', \
                         'AUX', 'CCONJ', 'DET', 'ADVPART', 'SCOPE','SCONJ']:
                confident_toss = True
            elif POS in ['ADVERB', 'ORDINAL', 'CARDINAL', 'PREP', 'WORD', 'PRONOUN', 'SCONJ', 'QUANT', \
                         'AUX', 'CCONJ', 'DET', 'ADVPART', 'SCOPE','DISCOURSE','VERB']:
                toss = True
            elif (POS in ['PERSONNAME','GPE']) and word[0].isupper():
                confident_keep = True
            # elif (not start_sentence) and (POS in ['VERB']):
            #     ### possible random capitalized verb same as name
            #     ### less likely to be a problem if not at sentence beginning
            #     keep = True (not a good idea) 7/21/17 AM
        if confident_toss:
            result = False
        elif confident_keep:
            result = True
        else:
            result = keep and not toss
        return(result)
    else:
        return(True)

def object_within_spans(object,spans):
    if (not object) or (not spans):
        return(False)
    output = False
    for start,end in spans:
        if (object['start']>=start) and (object['end']<=end):
            output = True
    return(output)

def remove_extra_spaces(instring):
    return(re.sub(' +',' ',instring))

def check_entry(entry,check_list):
    found = False
    for item in check_list:
        if item in entry:
            found = True
    return(found)

def non_name(word):
    if word in POS_dict:
        for POSclass in POS_dict[word]:
            if POSclass not in ['PERSONNAME','GPE_word','ORG_word','NATIONALITY','LEGISLATIVE_word','FIRSTNAME','ORG','GPE']:
                return(True)

def person_test(string,has_title=False):
    if re.search('et\.? +al',string):
        et_al = True
    else:
        et_al = False
    word_list = string.split(' ')
    unperson = False
    person = False
    num = 0
    if len(word_list) == 1:
        single_word = True
    else:
        single_word = False
    for word in word_list:
        word_strip = word.strip('.')
        if (word in POS_dict) and ('PERSONNAME' in POS_dict[word]) and \
          (not check_entry(POS_dict[word],['GPE_word','ORG_word','NATIONALITY','LEGISLATIVE_word'])):
           if (not single_word) and (non_name(word) and (not (has_title or et_al))):
               pass
           else:
               person = True
        elif (word_strip in citation_filler_words) or (word_strip in person_ending_words):
            pass
        elif (word in POS_dict) and ('TITLE'in POS_dict[word]):
            if num == 0:
                person = True
                ## otherwise pass
        elif (word_strip in POS_dict) and ('TITLE'in POS_dict[word_strip]):
            pass
        elif (word_strip in relational_dict) and ('PROFESSIONAL' in relational_dict[word_strip]):
            pass
        elif (len(word) == 1) or (len(word_strip) ==1): ## initials
            pass
        elif word == 'and':
            pass
        else:
            unperson = True
    if person and not unperson:
        return(True)
    else:
        return(False)

def add_to_one_person_names(string):
    if string in one_word_person_names:
        one_word_person_names[string]+=1
    else:
        one_word_person_names[string]=1

def get_last_person_word(string):
    word_match = re.compile('([a-zA-Z]+)[^a-zA-Z]*$')
    last_word = word_match.search(string)
    while last_word: 
        word = last_word.group(1)
        if (word in POS_dict):
            if ('PERSONNAME' in POS_dict[word]):
                return(word)
            else:
                last_word = word_match.search(string[:last_word.start()])
        elif not word in relational_dict:
            return(word)
        else:
            last_word = word_match.search(string[:last_word.start()])
            
def split_phrase_record(record,file_id,dictionary):
    start = 0
    and_pattern = re.compile(' +and +',re.I)
    triples = []
    string_list  = []
    while (start< len(record['string'])):
        and_match = and_pattern.search(record['string'],start)
        if and_match:
            end = and_match.start()
            next_triple =[record['string'][start:end],start,end]
            string_list.append(next_triple[0])
            triples.append(next_triple)
            start = and_match.end()
        else:
            end = len(record['string'])
            next_triple = [record['string'][start:end],start,end]
            string_list.append(next_triple[0])
            triples.append(next_triple)
            start = end
    if len(triples) == 0:
        return(False,False)
    else:
       output = []
       first = True
       for instring,start,end in triples:
            out = {}
            out['start']=start+record['start']
            out['end']=end+record['start']
            out['string']=instring
            out['phrase_type'] = 'NAME'
            if ('sentence_start' in record) and record['sentence_start'] and first:
                out['sentence_start'] = True
            first = False
            add_citation_id(out,file_id,dictionary)
            output.append(out)
    return(output,string_list)
                                   
    
    
def make_conjoined_phrase_relation(record1,record2,file_id,dictionary):
    relation = {'gram_type':'conj','conj1':record1,'conj2':record2,'start':record1['start'],'end':record2['end'],'relation_type':'conj'}
    add_citation_id(relation,file_id,dictionary)
    return(relation)

def unambig_org(entry,string):
    if len(entry) == 1:
        return(True)
    elif string.isupper():
        return(True)
    
def possibly_adjust_phrase_type(record,file_id,citation_dictionary,party=False,conj=False,string_list = False):
    string = remove_extra_spaces(record['string'].lower())
    ## not using string_list yet, but could use it to ensure parallel NE types across conjunctions
    change = False
    person_words = 0
    has_profession = False
    has_unknown = False
    other = False
    has_title = False
    words = False        
    conj_relations = []
    if (string in POS_dict) and record['string'][0].isupper():
        if ('ORG' in POS_dict[string]) and unambig_org(POS_dict[string],record['string']):
            change = True
            record['phrase_type']='ORGANIZATION'
        elif ('GPE' in POS_dict[string]):
            change = True
            record['phrase_type']='GPE'
    if (not change) and re.search('^the ',string):
        substring = string[4:]
        if substring in POS_dict:
            if ('ORG' in POS_dict[substring]):
                change = True
                record['phrase_type']='ORGANIZATION'
            elif ('GPE' in POS_dict[substring]):
                change = True
                record['phrase_type']='GPE'
    if not change:
        words = string.split(' ')
    if (not change) and words and (len(words)>1) and (words[-1].strip('.') in org_ending_words):
        record['phrase_type']='ORGANIZATION'
        change = True
    if ('&' in string) and (not change) and (record['phrase_type']=='NAME'):
        ## could be PERSON (authors) or ORGANIZATION
        organization = False
        person = True
        for word in words:
            if word in POS_dict:
                entry = POS_dict[word]
                if 'ORG_word' in entry:
                    organization = True
                elif 'PERSONNAME' in entry:
                    person = True
                else:
                    organization = True
                    ## dictionary items that are not first names
                    ## are indicators of non-person
        if organization or (not person):
            record['phrase_type']='ORGANIZATION'
        else:
            record['phrase_type']='PERSON'
        change = True
    if (not change) and person_test(string,has_title=has_title):
        record['phrase_type']='PERSON'
        if (not ' ' in string):
            add_to_one_person_names(string)
        else:
            last_person_word = get_last_person_word(string.lower())
            if last_person_word:
                add_to_one_person_names(last_person_word)
        change = True
    if party and (not change):
        apposition = False
        for word in words:
            if word.endswith(','):
                apposition = True
            stripped_word = word.strip('.,-')
            if (stripped_word in POS_dict) and ('PERSONNAME' in POS_dict[stripped_word]):
                person_words += 1
            elif (stripped_word in relational_dict) and ('PROFESSIONAL' in relational_dict[stripped_word]):
                has_profession = True
            elif (word in POS_dict) and ('TITLE' in POS_dict[word]):
                has_title = True
            elif (not stripped_word in relational_dict) and (not stripped_word in POS_dict):
                has_unknown = True
            else:
                other = True
        if ((person_words >= 1) and has_profession and apposition):
            record['phrase_type']='PERSON'
            change = True
        elif has_title and ((person_words >=1) or has_unknown):
            record['phrase_type']='PERSON'
            change = True
    elif not change:
        if not words:
            words = string.split(' ')
        legislative = False
        position = 0
        for word in words:
            stripped_word = word.strip('.,-')
            if (position == 0) and (word in POS_dict) and ('TITLE' in POS_dict[word]):
                has_title = True
            elif (stripped_word in relational_dict) and ('PROFESSIONAL' in relational_dict[stripped_word]):
                has_profession = True
            elif (stripped_word in POS_dict) and ('PERSONNAME' in POS_dict[stripped_word]):
                person_words += 1
            elif (not stripped_word in relational_dict) and (not stripped_word in POS_dict):
                has_unknown = True
            elif stripped_word in POS_dict:
                entry = POS_dict[stripped_word]
                if ('LEGISLATIVE_word' in entry):
                    legislative = True
                else:
                    other = True
            else:
                other = True
            position = 1+position
        if has_title and ((person_words >=1) or has_unknown) and (not legislative):
            record['phrase_type']='PERSON'
            change = True
        elif legislative:
            record['phrase_type'] = 'NAME'
            change = True
    if not change:
        position = 0
        organization = False
        legislative = False
        person = False
        gpe = False
        gpe_count = 0
        oov_word = False
        for word in words:
            entry = []
            if word in POS_dict:
                entry.extend(POS_dict[word])
            if word in relational_dict:
                entry.extend(relational_dict[word])
            if (position == len(word)-1) and (word in org_ending_words):
                record['phrase_type']='ORGANIZATION'
                change = True
            elif word in POS_dict:
                if 'ORG_word' in entry:
                    organization = True
                if 'LEGISLATIVE_word' in entry:
                    legislative = True
                if ('GPE_word' in entry) or ('GPE' in entry):
                    gpe = True
                    gpe_count +=1
                if ('PERSONNAME' in entry):
                    person = True
            elif len(entry) == 0:
                oov_word = True                
        if (not change) and gpe and has_profession:
            record['phrase_type']='PROFESSION'
            change = True
        elif (not change) and person and has_profession:
            record['phrase_type']='PERSON'
            change = True
        elif (not change) and organization and (not legislative):
            record['phrase_type']='ORGANIZATION'
            change = True
        elif gpe and (not organization) and (not legislative) and (oov_word or (gpe_count>1)):
            record['phrase_type']='GPE'
            change = True
    if (' and ' in string) and (not conj):
        ## if conj -- change even if already changed
        ## recursive calls -- only allow one layer of recursion
        record_list,record_string_list = split_phrase_record(record,file_id,citation_dictionary)
        ## print(record_list)
        phrase_type = False
        fail = False
        for phrase in record_list:
            possibly_adjust_phrase_type(phrase,file_id,citation_dictionary,party=party,conj=True,string_list=record_string_list)
            if not phrase_type:
                phrase_type = phrase['phrase_type']
            elif phrase_type == phrase['phrase_type']:
                pass
            else:
                fail = True
        if fail:
            record['phrase_type']='NAME'
            ## do not allow conjoined phrases of different name types
        if (not fail) and phrase_type and (phrase_type != record['phrase_type']):
            record['phrase_type'] = phrase_type
        if not fail and (phrase_type in ['PERSON','GPE']):
            for phrase in record_list:
                rel = make_conjoined_phrase_relation(phrase,record,file_id,citation_dictionary)
                conj_relations.append(rel)
            change = True
        else:
            conj_relations = False
        # else:
        #     conj_relations = False
        if conj_relations:
            conj_relations.extend(record_list)
            return(conj_relations)
        else:
            return(False)

def probably_person(previous_words):
    if (len(previous_words)> 5):
        return(False)
    person_words = 0
    title = 0
    bad = False
    for word in previous_words:
        if ((len(word)>1) and (word[0].isupper()) and (word[1].islower())) or ((len(word)==1) and word.isupper()):
            is_capital = True
        else:
            is_capital = False
        word = word.lower()
        if not is_capital:
            return(False)
        elif word in POS_dict:
            entry = POS_dict[word]
            if ('PERSONNAME' in entry) or ('TITLE' in entry):
                person_words += 1
            else:
                bad = True
        elif is_initial(word):
            person_words += 1
    if (person_words > 0) and (not bad):
        return(True)
    else:
        return(False)
    
def get_role_phrases(line,spans,offset,file_id,citation_dictionary,individual_spans,line_number):
    # if '262 So. 2d' in line:
    #     print(1,line,2,spans,3,offset,4,file_id,5,{},6,individual_spans,7,line_number)
    ## detect sequences that are either in capital format (consec capital sequences, with allowances for lowercase func words)
    ##        and are not in current spans
    ## detect similar sequences that contain role words, even if not capital or if inside of current spans
    ##
    conj_output = []
    word_pattern = re.compile('[1-4]?[A-Z-]+',re.I)
    year_pattern = re.compile('([^a-zA-Z0-9]|^)((18|19|20)[0-9][0-9])([^a-zA-Z0-9]|$)')
    match = word_pattern.search(line)
    deletable_early = re.compile('[^a-z]*((cite +as)|(writ of cert.*district,?( +division +[a-z]+)?)|(((Statement +of.*)|(Per? *Curiam *))?SUPREME +COURT +OF +THE +UNITED STATES))[^a-z]*',re.I)
    if line_number <= 5:
        deletable_match = deletable_early.search(line)
    else:
        deletable_match = False
    if match and deletable_match and (match.start()>=deletable_match.start(1)) and (match.end()<=deletable_match.end(1)):
        start = deletable_match.end(1)
        match = word_pattern.search(line,deletable_match.end(1))
    else:
        start = 0
    if match and deletable_match and (deletable_match.end(1)<match.start()):
        deletable_match = deletable_early.search(line,match.start())
    output = []
    out = {}
    sequence = []
    words = []
    word_ends_in_hyphen = False
    end_of_sentence = False
    start_sentence = False
    while match:
        if match and deletable_match and (match.start() >= deletable_match.start(1)) and (match.start() <= deletable_match.end(1)):
            out = {}
            match = word_pattern.search(line,deletable_match.end(1))
            start = deletable_match.end(1)
        previous_start = start
        add_on = False
        if match:
            word = match.group(0)
            word_ends_in_hyphen = word.endswith('-')
            if word_ends_in_hyphen:
                word = word[:-1]
            end_of_sentence = end_of_sentence_heuristic(word,line,match.end())
            if end_of_sentence:
                start_sentence = False
            else:
                start_sentence = start_sentence_heuristic(word,line,match.start())
                ## print(start_sentence,word)
            not_added_to_sequence = False
        if not match:
            pass
        # elif (len(sequence) == 0) and ((word.lower() in prepositions) or (word.lower() in ['and','or'])):
        #     add_on = False
        #     start = match.end()+1
        #     print('** blah **')
        #     print(1,word)
        #     print(2,words)
        elif word.lower() in ['nos','nos.','no','no.']:
            add_on = False
        elif (word.lower() in relational_dict):
            if len(sequence)==0:
                out['start']=match.start()+offset
            entry = relational_dict[word.lower()]
            entry = merge_relational_entries(word.lower(),entry)
            if entry in ['LEGAL_ROLE','PLURAL_LEGAL_ROLE']:
                entry_type = 'LEGAL_ROLE'
            elif (entry in ['ORGANIZATION','PLURAL_ORGANIZATION']):
                entry_type = 'ORGANIZATION'
            elif entry in ['FAMILY','PLURAL_FAMILY']:
                entry_type = 'FAMILY'
            elif entry in ['PROFESSIONAL','PLURAL_PROFESSIONAL','PROFESSIONAL_OR_RANK']:
                entry_type = 'PROFESSIONAL'
            else:
                entry_type = 'OTHER'
            if ('start' in out) and (len(sequence)>0) and (entry_type in ['LEGAL_ROLE','FAMILY','PROFESSION','ORGANIZATION']) and \
              (sequence[-1] in ['FILLER','CAPITALIZED_WORD']) and \
              (((entry_type == 'ORGANIZATION') and (('ORGANIZATION' in sequence) or  ('PLURAL_ORGANIZATION' in sequence))) or \
               ((entry_type == 'LEGAL_ROLE') and (('LEGAL_ROLE' in sequence) or ('PLURAL_LEGAL_ROLE' in sequence))) or \
               ((entry_type == 'FAMILY') and (('FAMILY' in sequence) or ('PLURAL_FAMILY' in sequence))) or \
               ((entry_type == 'PROFESSIONAL') and (('PROFESSIONAL' in sequence) or ('PLURAL_PROFESSIONAL' in sequence) or \
                                                    ('PROFESSIONAL_OR_RANK' in sequence)))):
                if word_ends_in_hyphen:
                    end = start-1
                else:
                    end = start
                out['end']=end+offset
                out['sentence_start'] = start_sentence
                new_phrases,good = ok_role_phrase(out,sequence,spans,line[out['start']-offset:start],line,offset,words)
                if new_phrases:
                    for phrase,seq,phrase_words in new_phrases:
                        abort_phrase = False
                        if 'name_with_infixed_role' in phrase:
                            phrase['phrase_type'] = 'NAME'
                            plural = False
                        else:
                            value,plural = find_phrase_type_from_sequence(seq,phrase_words)
                            if value:
                                phrase['phrase_type']=value
                            else:
                                abort_phrase = True
                        if plural and (not abort_phrase):
                            phrase['plural']=True
                        if not abort_phrase:
                            phrase['string'] = line[phrase['start']-offset:phrase['end']-offset]
                            output.append(phrase)
                elif good:
                    value,plural = find_phrase_type_from_sequence(sequence,words)
                    if value:
                        out['phrase_type'] = value
                        if plural:
                            out['plural']=True                    
                            out['string']=line[out['start']-offset:out['end']-offset]
                            output.append(out)
                sequence = [entry]
                words = [word]
                out = {'start':match.start()+offset}
            else:
                sequence.append(entry)
                words.append(word)
            add_on = True
            start = match.end()
        elif (word.lower() in POS_dict) and (len(sequence)>0) and ('LEGISLATIVE_word' in POS_dict[word.lower()]):
            add_on = True
            sequence.append('LEGISLATIVE')
            words.append(word)
            start = match.end()
        elif is_initial(word) and ((len(sequence)==0) or (((match.start() == 0) or (" " ==line[match.start()-1])) and (sequence[-1] in ['PERSONNAME','CAPITALIZED_WORD','INITIAL']))):
            add_on = True
            sequence.append('INITIAL')
            words.append(word)
            start = match.end()
        elif (word.lower() in not_uppercase_part_of_org_names) and (len(sequence)==0) and \
          not((word.lower() in ['for']) and (((len(words)>1) and (probably_person(words))) or \
                                             ((len(words)>0) and (words[-1].lower() in POS_dict) and ('LEGISLATIVE_word' in POS_dict[words[-1].lower()])))):
            if len(sequence)>0:
                add_on = True
                if False and is_initial(word) and (match.start()>0) and (" " ==line[match.start()-1]):
                    sequence.append('INITIAL')
                else:
                    sequence.append('FILLER')
                words.append(word)
                start = match.end()
        elif (match.end()+1<len(line)) and (line[match.end()+1]=='.') and ((word.lower()+'.') in relational_dict):
            if len(sequence)==0:
                out['start']=match.start()+offset
            entry = relational_dict[word.lower()+'.']
            sequence.append(merge_relational_entries(word.lower(),entry))
            words.append(word)
            add_on = True
            start = match.end()+1
        elif (len(sequence) == 0) and ((len(word)<2) or (roman(word.lower()))) and \
          (re.search('^[\.]?[ \t]{2,}',line[match.end():]) or (not re.search('[a-zA-Z]',line[match.end():]))):
            not_added_to_sequence = True
        elif len(sequence)==0 and (word.lower() in pre_citation_words):
            not_added_to_sequence = True
        elif capitalized_word(word):
            if len(sequence)==0 and (ok_non_vocab_word_start_sequence(word,start_sentence)) or title_word(word):
                out['start']=match.start()+offset
                out['sentence_start'] = start_sentence
                add_on = True
            elif len(sequence)>0:
                add_on = True
            else:
                add_on = False
            if add_on:
                sequence.append('CAPITALIZED_WORD')
                words.append(word)
                if ((match.end()+1<len(line)) and (line[match.end()+1]=='.') and possible_abbrev(word)) \
                  or ((match.end()+2<len(line)) and (line[match.end()+1]=='.') and (line[match.end()+2] in ';,')):
                    start = match.end()+1
                else:
                    start = match.end()
            ## if immediately followed by period use heuristic and/or
            ## abbrev list to differentiate end of sentence with
            ## abbreviation
        else:
            not_added_to_sequence = True
        if not match:
            pass
        elif add_on and (not (re.search('[?";:\(\)\[\]]',line[previous_start:match.start()]))) and (not end_of_sentence) and \
          ((not ',' in line[previous_start:match.start()]) or (word.lower() in org_ending_words) or (word.lower() in person_ending_words)):
            start = match.end()
        elif add_on and end_of_sentence and (len(sequence) > 1):
            start = match.end()
            if word_ends_in_hyphen:
                end = start-1
            else:
                end = start
            out['end']=end+offset
            if 'start' in out:
                new_phrases,good = ok_role_phrase(out,sequence,spans,line[out['start']-offset:start],line,offset,words)
            else:
                new_phrases = False
                good = False
            if good:
                phrase_type,plural = find_phrase_type_from_sequence(sequence,words)
                if phrase_type:
                    out['phrase_type'] = phrase_type
                    if plural:
                        out['plural']=True
                    out['string']=line[out['start']-offset:out['end']-offset]
                    output.append(out)
            elif new_phrases:
                for phrase,seq,phrase_words in new_phrases:
                    if 'name_with_infixed_role' in phrase:
                        phrase_type = 'NAME'
                        plural = False
                    else:
                        phrase_type,plural = find_phrase_type_from_sequence(seq,phrase_words)
                    if phrase_type:
                        phrase['phrase_type'] = phrase_type
                        if plural:
                            phrase['plural']=True
                        phrase['string'] = line[phrase['start']-offset:phrase['end']-offset]
                    new2,good2 = ok_role_phrase(phrase,seq,spans,phrase['string'],line,offset,phrase['string'].split(' '))
                    if good2:
                        output.append(phrase)
            sequence = []
            words = []
            out = {}
        else:
            ### conditions on last stored item as potential item to record
            ### if item is relational/occupation category, keep
            ### if simple allcap, keep only if not already part of a span
            if ('start' in out):
                if not_added_to_sequence:
                    pass
                else:
                    ## print(1,sequence,words)
                    sequence = sequence[:-1]
                    words = words[:-1]
                    ## print(2,sequence,words)
                if line[start-1]=='-':
                    start = start-1
                year_match = year_pattern.search(line,previous_start)
                if year_match and (not re.search('[a-zA-Z0-9\,\.]',line[previous_start:year_match.start()])):
                    if (line[year_match.start()-1]=='(') and (line[year_match.end()]==')'):
                        previous_start = year_match.end()
                    else:
                        previous_start = year_match.end(2)
                out['end']=previous_start+offset
                ## words can be incorrect here ** 57 ***
                new_phrases,good = ok_role_phrase(out,sequence,spans,line[out['start']-offset:previous_start],line,offset,words)
                if new_phrases:
                    for phrase,seq,phrase_words in new_phrases:
                        if 'name_with_infixed_role' in phrase:
                            phrase_type = 'NAME'
                            plural = False
                        else:
                            phrase_type,plural = find_phrase_type_from_sequence(seq,phrase_words)
                        if phrase_type:
                            phrase['phrase_type'] = phrase_type
                            if plural:
                                phrase['plural']=True
                            phrase['string'] = line[phrase['start']-offset:phrase['end']-offset]
                            output.append(phrase)
                            ## if no phrase type, not a valid phrase
                elif good:
                    phrase_type, plural = find_phrase_type_from_sequence(sequence,words)
                    if phrase_type:
                        out['phrase_type'] = phrase_type
                        if plural:
                            out['plural']=True
                        out['string']=line[out['start']-offset:previous_start]
                        output.append(out)
                if (not re.search('[a-zA-Z]',line[match.end():])) or end_of_sentence:
                    if word_ends_in_hyphen:
                        end = match.end()-1
                    else:
                        end = match.end()
                    out={'start':match.start()+offset,'end':end+offset}
                    out['string']=line[match.start():end]
                    if match.group(0).lower() in relational_dict:
                        words = [word]
                        sequence = [merge_relational_entries(match.group(0),relational_dict[match.group(0).lower()])]
                        phrase_type,plural = find_phrase_type_from_sequence(sequence,words)
                        ## words = [word]
                    else:
                        phrase_type = 'OTHER'
                        sequence = ['OTHER']
                        words = [word]
                    if phrase_type in ['LEGAL_ROLE','PROFESSION','FAMILY','ORGANIZATION']:
                        out['phrase_type'] = phrase_type
                        if plural:
                            out['plural'] = True
                    elif object_within_spans(out,spans):
                        out = False
                    elif (len(match.group(0)) > 1) and capitalized_word(match.group(0)):
                        out['phrase_type'] = 'NAME'
                    else:
                        out = False
                    if out:
                        # print('sequence',sequence,offset,words)
                        # print(spans)
                        # print(77,line[out['start']-offset:start])
                        # print(777,line)
                        # print(offset)
                        if len(words) == 1:
                            new_phrases,good = ok_role_phrase(out,sequence,spans,out['string'],line,offset,words)
                            if good:
                                output.append(out)
                        else:
                            output.append(out)
                    start = match.end()
                    ## match=False
                    ## print(out)
                else:
                    start = match.start()
            else:
                start = match.end()
            # print(3)
            # print(match)
            # print(end_of_sentence)
            sequence = []
            words = []
            out = {}
        if match:
            match = word_pattern.search(line,start)
    if ('start' in out):
        if line[start-1]=='-':
            start = start-1
        year_match = year_pattern.search(line,start)
        if year_match and (not re.search('[a-zA-Z0-9\,\.]',line[start:year_match.start()])):
            if (line[year_match.start()-1]=='(') and (line[year_match.end()]==')'):
                start = year_match.end()
            else:
                start = year_match.end(2)
        if word_ends_in_hyphen:
            end = start-1
        else:
            end = start
        out['end']=end+offset
        new_phrases,good = ok_role_phrase(out,sequence,spans,line[out['start']-offset:start],line,offset,words)
        if new_phrases:
            for phrase,seq,phrase_words in new_phrases:
                if 'name_with_infixed_role' in phrase:
                    phrase['phrase_type'] = 'NAME'
                    plural = False
                else:
                    value,plural = find_phrase_type_from_sequence(seq,phrase_words)
                    if value:
                        phrase['phrase_type'] = value
                if plural:
                    phrase['plural']=True
                phrase['string'] = line[phrase['start']-offset:phrase['end']-offset]
                if 'phrase_type' in phrase:
                    output.append(phrase)
        elif good:
            value,plural = find_phrase_type_from_sequence(sequence,words)
            if value:
                out['phrase_type'] = value
            if plural:
                out['plural']=True
            out['string']=line[out['start']-offset:out['end']-offset]
            if 'phrase_type' in out:
                output.append(out)
    final_output=[]
    remove = []
    for record in output:
        if (record['phrase_type']=='NAME') or re.search(' +(and|AND|And) +',record['string']):
            conj_out = possibly_adjust_phrase_type(record,file_id,citation_dictionary)
            if conj_out:
                conj_output.extend(conj_out)
        elif ((record['phrase_type'] in ['ORGANIZATION','GPE','PERSON']) \
              and record['string'][0].islower() \
              and (not ' ' in record['string']) and (record['string'].lower() in POS_dict) \
              and (len(POS_dict[record['string'].lower()])>1)):
            remove.append(record)
        if (not [record['start'],record['end']] in individual_spans) and (not record in remove):
            ## prevents duplicates
            add_citation_id(record,file_id,citation_dictionary)
            final_output.append(record)
    return(final_output,conj_output)
    
def role_print(outstream,role_phrase):
        ## if no phrase_type don't do anything
        ## print(role_phrase)
    if 'phrase_type' in role_phrase:
        outstream.write('<'+role_phrase['phrase_type'])
        for attribute in ['id','start','end','plural','party1_of','party2_of']:
            if attribute in role_phrase:
                outstream.write(' '+attribute+'="'+wol_escape(str(role_phrase[attribute]))+'"')
        outstream.write('>')
        if 'string' in role_phrase:
            outstream.write(wol_escape(role_phrase['string']))
        outstream.write('</'+role_phrase['phrase_type']+'>'+os.linesep)

def find_dates(line,offset,file_id,citation_dictionary):
    output = []
    match = date_pattern.search(line)
    while match:
        out = {'start':match.start()+offset,'end':match.end()+offset}
        out['string']=match.group(0)
        out['phrase_type']='date'
        ## we could regularize this based on the time ISO
        output.append(out)
        start = match.end()
        match = date_pattern.search(line,start)
    for record in output:
        add_citation_id(record,file_id,citation_dictionary)
    return(output)

def sort_records(records,use_ids=False):
    import random
    ## sorting first by start and then by negative 1 X end this sorts
    ## first by the beginning and then puts larger spans first if they
    ## start first, so infixed items will follow surrounding ones
    sort_list= []
    for record in records:
        ## ran_num = random.randint(1,1000000)
        ## sort_list.append([record['start'],record['end'],ran_num,record])
        ## above possible fix if there are duplicate entries for a span
        if not 'start' in record:
            print(record)
            print('Warning: No start')
        elif use_ids:
            sort_list.append([record['start'],(-1 * record['end']),record['id'],record])
        else:
            sort_list.append([record['start'],(-1 * record['end']),record])
    sort_list.sort()
    output = []
    for record in sort_list:
        if use_ids:
            output.append(record[3])
        else:
            output.append(record[2])
    return(output)

def bad_name(string):
    words = string.lower().split(' ')
    OK = False
    for word in words:
        if word in POS_dict:
            entry = POS_dict[word]
        else:
            entry = []
        if word in relational_dict:
            entry.extend(relational_dict[word])
        if is_month.search(word) or (not re.search('[a-z]',word)):
            pass
        else:
            OK = True
        # elif not entry:
        #     OK = True
        # else:
        #     for classification in entry:
        #         if OK:
        #             pass
        #         elif classification in ['PERSONNAME','LEGAL_ROLE','PROFESSIONAL','PROFESSIONAL_OR_RANK',\
        #                                 'PLURAL_LEGAL_ROLE','PLURAL_PROFESSIONAL']:
        #             OK = True
    if not OK:
        return(True)
    
def get_party_names_and_roles_from_cases(vs_cases,file_id,citation_dictionary):
    output = []
    remove_citations = []
    conj_output = []
    for case in vs_cases:
        if 'party1' in case:
            party1 = case['party1']
            party2 = case['party2']
            if 'party1_role' in case:
                party1_role = case['party1_role']
            else:
                party1_role = False
            if 'party2_role' in case:
                party2_role = case['party2_role']
            else:
                party2_role = False
            found_party1 = False
            for party,party_type in [[party1,'party1'],[party2,'party2']]:
                if party in case['string']:
                    if found_party1 and (party_type == 'party2'):
                        local_start = case['string'].index(party,local_end) 
                        ## deals with cases where parties have the same name
                    else:
                        local_start = case['string'].index(party)
                        found_party1 = True
                    local_end = local_start+len(party)
                    start = local_start+case['start']
                    end = local_end+case['start']
                    out = {'start':start,'end':end,'string':party,'phrase_type':'NAME'}
                    conj_out = possibly_adjust_phrase_type(out,file_id,citation_dictionary,party=True)
                    if conj_out:
                        conj_output.extend(conj_out)
                    if party_type == 'party1':
                        out['party1_of']=case['id']
                    else:
                        out['party2_of']=case['id']
                    if (out['phrase_type']=='NAME') and  (bad_name(party)):
                        if (not case in remove_citations):
                            remove_citations.append(case) 
                        if party == 'party1':
                            party1_role = False
                        else:
                            party2_role = False
                        ## don't add out to output
                    elif case in remove_citations:
                        ## don't add if other party nixed citation
                        if party == 'party1':
                            party1_role = False
                        else:
                            party2_role = False
                    else:
                        if (out['phrase_type']=='PERSON') and (not ' ' in out['string']):
                            add_to_one_person_names(out['string'].lower())
                        add_citation_id(out,file_id,citation_dictionary)
                        output.append(out)                    
            for party_role in [party1_role,party2_role]:
                if party_role:
                    for role in party_role.split(', '):
                        match = re.search(role,case['string'].lower())
                        if match:
                            start = case['start']+match.start()
                            end = case['start']+match.end()
                            string = case['string'][match.start():match.end()]
                            ## party_role in case regularized to lowercase
                            ## searches must be in lowercase, but actual string can be any case
                            out = {'start':start,'end':end,'string':string,'phrase_type':'LEGAL_ROLE'}
                            add_citation_id(out,file_id,citation_dictionary)
                            output.append(out)
    return(remove_citations,output,conj_output)

def get_type_from_entity(entity):
    if 'phrase_type' in entity:
        return(entity['phrase_type'])
    elif 'entry_type' in entity:
        return(entity['entry_type'])
    else:
        return('NAME')

def get_one_line_object_relations(entities,offset,file_id,citation_dictionary,line_number,max_line_number,relation_pair_dict):
    entity_dictionary = {}
    ## we currently only look for: entities of these types: 'standard_case','case_X_vs_Y','case_citation_other','docket','date'
    relation = False
    output = []
    for entity in entities:
        entity_type = get_type_from_entity(entity)
        if entity_type in entity_dictionary:
            entity_dictionary[entity_type].append(entity)
        else:
            entity_dictionary[entity_type]=[entity]
    if ('case_X_vs_Y' in entity_dictionary):
        ## for each 'case_X_vs_Y', do all combinations
        ## of standard_case and case_citation_other that exist
        ## previously assumed only 1 X vs Y case
        ## but will allow more than one given
        ## what actually occurs:
        ## -- may need to fine tune
        ## -- 2 situations: A) multiple instances of the same name (just variations)
        ##                  B) multiple cases that have been grouped together (companion cases)
        ##                     -- there may be some subtlties missed in the B cases, e.g., if
        ##                        there is a 1 to 1 relation with some standard citations
        for case_X_vs_Y in entity_dictionary['case_X_vs_Y']:
            for attribute in ['case_citation_other','standard_case','docket','date']:
                if attribute in entity_dictionary:
                    for other_entity in entity_dictionary[attribute]:
                        if (case_X_vs_Y['id'] in relation_pair_dict) and \
                          (other_entity['id'] in relation_pair_dict[case_X_vs_Y['id']]):
                            pass
                        else:
                            fail = False
                            relation = {'gram_type':'multi_line'}
                            relation['start']=min(case_X_vs_Y['start'],other_entity['start'])
                            relation['end']=max(case_X_vs_Y['end'],other_entity['end'])
                            if attribute in ['docket','date']:
                                relation['theme']=case_X_vs_Y
                                relation['relation_type']='asymmetric'
                            else:
                                relation['X_vs_Y']=case_X_vs_Y
                                relation['relation_type']='equivalence'
                            if attribute == 'docket':
                                relation['includes_docket']=other_entity
                            elif attribute == 'date':
                                relation['at_date']=other_entity
                                if (other_entity['start']<case_X_vs_Y['start']) or (line_number>(5+max_line_number)):
                                    fail = True
                            elif attribute == 'standard_case':
                                relation['standard_case']=other_entity
                            elif attribute == 'case_citation_other':
                                relation['case_citation_other']=other_entity
                            if not fail:
                                add_citation_id(relation,file_id,citation_dictionary)
                                output.append(relation)
        if output and (len(output)>0):
            return(output)
    elif 'case_citation_other' in entity_dictionary:
        for other_citation in entity_dictionary['case_citation_other']:
            for attribute in ['standard_case','docket','date']:
                if attribute in entity_dictionary:
                    for other_entity in entity_dictionary[attribute]:
                        if (other_citation['id'] in relation_pair_dict) and \
                           (other_entity['id'] in relation_pair_dict[other_citation['id']]):
                            pass
                        else:
                            fail = False
                            relation = {'gram_type':'multi_line'}
                            relation['start']=min(other_citation['start'],other_entity['start'])
                            relation['end']=max(other_citation['end'],other_entity['end'])
                            if attribute in ['docket','date']:
                                relation['theme']=other_citation
                                relation['relation_type']='asymmetric'
                            else:
                                relation['case_citation_other']=other_citation
                                relation['relation_type']='equivalence'
                            if attribute == 'docket':
                                relation['includes_docket']=other_entity
                            elif attribute == 'date':
                                relation['at_date']=other_entity
                                if (other_entity['start']<other_entity['start']) or (line_number>(5+max_line_number)):
                                    fail = True
                            elif attribute == 'standard_case':
                                relation['standard_case']=other_entity
                            if not fail:
                                add_citation_id(relation,file_id,citation_dictionary)
                                output.append(relation)
        if output and (len(output)>0):
            return(output)

def optional_period(entity):
    string = entity['string'].lower()
    if (string in relational_dict) and (string+'.' in relational_dict):
        entry1 = relational_dict[string]
        entry2 = relational_dict[string+'.']
        for item in ['PROFESSIONAL','PLURAL_PROFESSIONAL','LEGAL_ROLE','PLURAL_LEGAL_ROLE']:
            if (item in entry1) and (item in entry2):
                return(True)
    return(False)
    
def get_gram_type_from_inbetween(inbetween,current_type,last_type,line_number,line,first_entity,offset):
    preposition = False
    period_abbrev = False
    loc_temp = ['afore','after','at','before','during','following', 'till', 'til', 'until']
    preposition_disjunct = prepositions[0]
    for prep in prepositions[1:]:
        preposition_disjunct=preposition_disjunct+'|'+prep 
    loc_temp_disjunct = loc_temp[0]
    for prep in loc_temp[1:]:
        loc_temp_disjunct = loc_temp_disjunct+'|'+prep
    other_prep_pattern = re.compile('^ *('+preposition_disjunct+') *$',re.I)
    loc_temp_pattern = re.compile('^ *('+loc_temp_disjunct+') *$',re.I)
    if (current_type == 'docket'):
        stub = re.search(' *([Nn]os?[\. ]+)$',inbetween)
        if stub:
            inbetween = inbetween[:(-1*len(stub.group(1)))]
        stub = re.search(' *[Aa]ppeal *docketed,',inbetween)
        if stub:
            inbetween = inbetween[:(-1*len(stub.group(0)))]
    loc_temp_match = loc_temp_pattern.search(inbetween)
    other_prep_match = other_prep_pattern.search(inbetween)
    if ";" in inbetween:
        return(False,False,False) 
    elif re.search('^ *$',inbetween) or ((line_number<5) and deletable_middle(inbetween)):
        ## if the entities are adjacent
        gram_type = 'pre_nom'
    elif (re.search('^\. *$',inbetween)) and optional_period(first_entity):
        period_abbrev = True
        gram_type = 'pre_nom'
    elif re.search('^[ ,:\-\(\.]*$',inbetween):
        ## possible apposition or parentheses (or "as")
        ## beware of conjunction -- possibly handled        
        gram_type = 'apposition'
    elif re.search('^[ ,:\-\(\.]*(and|&)[ ,:\-\(\.]*$',inbetween):
        gram_type = 'conj'
    elif re.search('^ *(as|AS) *',inbetween):
        gram_type = 'as_predication'
    elif re.search('\'s *$',inbetween) or (re.search('\' *$',inbetween) and (len(line)>2) and (line[first_entity['end']-offset] in 'sS')):
        gram_type = 'possessive'
    elif loc_temp_match:
        gram_type='preposition'
        preposition = loc_temp_match.group(1).lower()
    elif other_prep_match: 
        gram_type='preposition'
        preposition = other_prep_match.group(1).lower()
    else:
        return(False,False,False)
    return(gram_type,preposition,period_abbrev)

def get_borrowed_argument(relation,used_role):
    for role in ['legal_role','profession','standard_case','X_vs_Y','case_citation_other','at_date',\
                      'includes_docket','family','party1','party2']:
        ## 'theme' is not in list -- we don't borrow themes only other items
        if (role in relation) and (role != used_role):
            return(relation[role])
    print('something wrong with get_borrowed_argument')
    input('pause')
    return(False)

def get_new_date_relation(last_date_relation,theme,file_id,citation_dictionary):
    old_start = last_date_relation['start']
    old_end = last_date_relation['end']
    at_date = last_date_relation['at_date']
    gram_type = last_date_relation['gram_type']
    relation_type = last_date_relation['relation_type']
    start = min(old_start,theme['start'])
    end = max(old_end,theme['end'])
    relation = {'start':start,'end':end,'at_date':at_date,'gram_type':gram_type,'theme':theme,'relation_type':relation_type}
    add_citation_id(relation,file_id,citation_dictionary)
    return(relation)

def look_for_close_relations(entities,line,offset,file_id,citation_dictionary,line_number,found_initial_equivalent_relations):
    relations = []
    last_entity = False
    last_entity_type = False
    finished_stack =[]
    new_stack = []
    loc_temp = ['afore','after','at','before','during','following', 'till', 'til', 'until']
    preposition_disjunct = prepositions[0]
    conjoined_entity ={}
    conjunction_relations = []
    last_date_relation = False
    for preposition in prepositions[1:]:
        preposition_disjunct=preposition_disjunct+'|'+preposition 
    loc_temp_disjunct = loc_temp[0]
    for preposition in loc_temp[1:]:
        loc_temp_disjunct = loc_temp_disjunct+'|'+preposition 
    other_prep_pattern = re.compile('^ *('+preposition_disjunct+') *$',re.I)
    loc_temp_pattern = re.compile('^ *('+loc_temp_disjunct+') *$',re.I)
    current_type = False
    last_entity = False
    finished_entity = False
    finished_type = False
    ## phrase_type values: ['date','LEGAL_ROLE','PROFESSIONAL','FAMILY','ORGANIZATION', 'CAPITALIZED_WORD','NAME'
    ## type (citation type): ['standard_case','case_X_vs_Y','docket','case_citation_other']
    ## note docket on a line by itself is going to be a dockets/dates for the MAIN_CASE
    ## particularly if no case has been mentioned yet (or the most recent -- dockets/dates
    ## don't occur by themselves)
    ## single line with one or two words plus date -- similar
    ## other dates linked to important events (maybe later)
    ## -- automatic timeline?
    ## possible features:
    ## 'legal_role','relation_type','gram_type','preposition',
    ## 'profession','theme','arg1','arg2','reference_word','at_date',
    ## 'includes_docket','family','standard','X_vs_Y','case_citation_other'
    num = 0
    inside_relations = {}
    entity_right_after = {}
    equiv_relations = {}
    list_of_same_type = []
    standard_case_related = {} # associates a standard ID with either 'left' or 'right' 
    ## an entity can be inside exactly 1 other entity
    ## an entity can immediately_follow exactly 1 other entity
    ## entities are presorted before this function
    ## relations that carry over based on next_to: (1) equivalence, (2) legal_role(e.g., party1_of X is party1_of X'),
    ## (3) at_date; (4) docket -- all of these are only if one of the items is a citation 
    last_entity = False
    last_entity_small = False
    ## do infixed relations first and then do prenom and apposition relations later
    for entity in entities:
        entity_type = get_type_from_entity(entity)
        if (not last_entity):
            last_entity = entity
        elif ((entity['start']>=last_entity['start']) and (entity['end']<=last_entity['end'])):
            ## given the sort order, the outside entity will precede the inside entity
            ## condition 1 (inclusion)
            gram_type = 'infix'
            relation_type = 'asymmetric'
            start,end=last_entity['start'],last_entity['end']
            theme = False
            party2 = False
            party1 = False
            at_date = False
            ### New for roles of people
            profession = False
            legal_role = False
            if (('party2_of' in entity) and (entity['party2_of']== last_entity['id'])):
                theme = last_entity
                party2 = entity
                relation_type = 'asymmetric'
                ## this should only get extended if there is only one X_vs_Y case
                ## in the equivalence group
            elif (('party1_of' in entity) and (entity['party1_of']== last_entity['id'])):
                theme = last_entity
                party1 = entity
                relation_type = 'asymmetric'
                ## this should only get extended if there is only one X_vs_Y case
                ## in the equivalence group
            elif entity_type == 'date':
                theme = last_entity
                at_date = entity
                ## this should only get extended if:
                ## the other new object does not already have a date associated
                ## with it directly
            if (entity_type == 'PERSON') and (last_entity_type == 'PROFESSION'):
                theme = entity
                profession = last_entity
            elif (last_entity_type == 'PERSON'):
                if entity_type == 'PROFESSION':
                    profession = entity
                    theme = last_entity
                elif entity_type == 'LEGAL_ROLE':
                    legal_role = entity
                    theme = last_entity
            if theme:
                relation = {}
                for att_name,att_value in [['gram_type',gram_type],['relation_type',relation_type],\
                                       ['theme',theme],['at_date',at_date],['party1',party1],\
                                       ['party2',party2],['start',start],['end',end], \
                                       ['profession',profession],['legal_role',legal_role]]:
                    if att_value or (type(att_value)==int): 
                        ## type statement deals with the fact that 0 is interpretted as False
                        relation[att_name]=att_value
                add_citation_id(relation,file_id,citation_dictionary)
                relations.append(relation)
                current_relation_id = relation['id']
                last_entity_id = last_entity['id']
                if last_entity_id in inside_relations:
                    inside_relations[last_entity_id].append(current_relation_id)
                else:
                    inside_relations[last_entity_id] = [current_relation_id]
            if last_entity_small and (last_entity_small['end'] < entity['start']):
                last_type  = get_type_from_entity(last_entity_small)
                inbetween =  line[last_entity_small['end']-offset:entity['start']-offset]
                gram_type,preposition,period_abbrev = get_gram_type_from_inbetween(inbetween,entity_type,last_type,line_number,line,last_entity_small,offset)
                family = False
                theme = False
                relation_type = False
                legal_role = False
                profession = False
                if not gram_type:
                    relation = False
                if (gram_type == 'possessive') and (last_type == 'FAMILY') and (current_type in ['PERSON','NAME']):
                    family = last_entity_small
                    theme = entity
                    relation_type = 'asymmetric'
                elif (last_type == 'LEGAL_ROLE') and (current_type in ['ORGANIZATION','PROFESSION','FAMILY','NAME','PERSON']) and (gram_type in ['pre_nom']):
                    legal_role = last_entity_small
                    theme = entity
                    relation_type = 'asymmetric'
                elif (current_type == 'LEGAL_ROLE') and (last_type in ['ORGANIZATION','PROFESSION','FAMILY','NAME','PERSON']) \
                          and (gram_type in ['apposition','as_predication','preposition']):
                    legal_role = entity
                    theme = last_entity_small
                    relation_type = 'asymmetric'
                elif (last_type == 'PROFESSION') and (current_type in ['NAME','PERSON']) and (gram_type in ['pre_nom']):
                    profession = last_entity_small
                    theme = entity
                    relation_type = 'asymmetric'
                elif (current_type == 'PROFESSION') and (last_type in ['NAME','PERSON']) \
                  and (gram_type in ['apposition','as_predication','preposition']):
                    profession = entity
                    theme = last_entity_small
                    relation_type = 'asymmetric'                    
                elif (last_type == 'FAMILY') and (current_type in ['NAME','PERSON']) and (gram_type in ['pre_nom']):
                    family = last_entity_small
                    theme = entity
                    relation_type = 'partly_asymmetric'
                elif (current_type == 'FAMILY') and (last_type in ['NAME','PERSON'])\
                  and (gram_type in ['apposition','as_predication','preposition']):
                    family = entity
                    theme = last_entity_small
                    relation_type = 'partly_asymmetric'
                if theme:
                    relation = {}
                    for att_name,att_value in [['gram_type',gram_type],['preposition',preposition],['relation_type',relation_type],\
                                       ['theme',theme],['legal_role',legal_role], ['profession',profession],['family',family],\
                                       ['start',start],['end',end]]:
                        if att_value or (type(att_value)==int): 
                        ## type statement deals with the fact that 0 is interpretted as False
                            relation[att_name]=att_value
                    add_citation_id(relation,file_id,citation_dictionary)
                    relations.append(relation)
                    ## don't record these relations for future derived relations
                    ## deal with unembedded cases
                    ## record next_to cases and make transitive relations
            last_entity_small = entity
            ### last_entity_small could be in an equivalence relation with the next entity (if also small)
        elif (entity['start'] >= last_entity['end']):
            last_type  = get_type_from_entity(last_entity)
            current_type = get_type_from_entity(entity)
            last_id = last_entity['id']
            inbetween =  line[last_entity['end']-offset:entity['start']-offset]
            partner_tuples = []
            if ('extended_left_start' in entity) and (entity['extended_left_start']<entity['start']) \
              and (not ";" in inbetween) and ((not found_initial_equivalent_relations) or (not re.search('[a-zA-Z]',inbetween))):
              ## only extend the inbetween if dealing with initial relations defining citation for file
                inbetween =  line[last_entity['end']-offset:entity['extended_left_start']-offset]
            gram_type,preposition,period_abbrev = get_gram_type_from_inbetween(inbetween,current_type,last_type,line_number,line,last_entity,offset)
            if period_abbrev:
                ## expand person entity to include abbreviated profession as title, e.g., Dr. Smith
                    gram_type = 'infix'
                    entity['start']=last_entity['start']
                    entity['string'] = line[entity['start']-offset:entity['end']-offset]
                    partner_tuples.append([last_entity,gram_type,preposition])
            different_type = False
            if not gram_type:
                list_of_same_type = []                
            else:
                if (last_type == current_type) and (gram_type in ['prenom', 'apposition','conj']):
                    if not last_entity in list_of_same_type:
                        list_of_same_type.append(last_entity)
                    if last_date_relation and (last_date_relation['theme']==last_entity):
                        new_date_relation = get_new_date_relation(last_date_relation,entity,file_id,citation_dictionary)
                        if new_date_relation:
                            relations.append(new_date_relation)                        
                else:
                    last_date_relation = False
                    different_type = True
                    partner_tuples = [[last_entity,gram_type,preposition]]
                    ## list_of_same_type should all be the same type as last_type
                    if list_of_same_type:
                        for other_entity in list_of_same_type:
                            if not [other_entity,gram_type,preposition] in partner_tuples:
                                partner_tuples.append([other_entity,gram_type,preposition])
                        list_of_same_type = []
                if gram_type in ['prenom', 'apposition','as_predication']:
                    if last_id in inside_relations:
                        for rel_id in inside_relations[last_id]:
                            old_relation = citation_dictionary[rel_id]
                            argument = get_borrowed_argument(old_relation,'theme')
                            old_gram_type = 'indirect_infix'
                            if 'preposition' in old_relation:
                                old_preposition = old_relation['preposition']
                            else:
                                old_preposition = False    
                            if not [argument,old_gram_type,old_preposition] in partner_tuples:
                                partner_tuples.append([argument,old_gram_type,old_preposition])
                    if last_id in equiv_relations:
                        for rel_id in equiv_relations[last_id]:
                            old_relation = citation_dictionary[rel_id]
                            argument = get_borrowed_argument(old_relation,current_type)
                            old_gram_type = gram_type ## assume same gram_type as main one
                            if 'preposition' in old_relation:
                                old_preposition = old_relation['preposition']
                            else:
                                old_preposition = False  
                            if not [argument,old_gram_type,old_preposition] in partner_tuples:
                                partner_tuples.append([argument,old_gram_type,old_preposition])
                for partner,gram_type,preposition in partner_tuples:
                    last_type = get_type_from_entity(partner)
                    start = min(partner['start'],entity['start'])
                    end = max(partner['end'],entity['end']) ## span of entities may be misleading
                    theme,at_date,includes_docket,legal_role,profession = False,False,False,False,False
                    family,standard_case,X_vs_Y,case_citation_other,party1,party2 = False,False,False,False,False,False
                    relation = {}
                    if (gram_type == 'conj'):
                        relation_type = False
                    elif (gram_type in ['possessive']):
                        if (last_type == 'FAMILY') and (current_type in ['NAME','PERSON']):
                            family = partner
                            theme = entity
                            relation_type = 'asymmetric'
                        else:
                            relation_type = False
                    elif (last_type == 'date') and (current_type in ['standard_case','case_X_vs_Y','docket','case_citation_other']) \
                      and (gram_type != 'preposition'):
                        at_date = partner
                        theme = entity
                        relation_type = 'asymmetric'
                    elif current_type == 'date' and (last_type in ['standard_case','case_X_vs_Y','docket','case_citation_other']):
                        at_date = entity
                        theme = partner
                        relation_type = 'asymmetric'
                    elif (current_type == 'docket') and (last_type in ['standard_case','case_X_vs_Y','case_citation_other']):
                        includes_docket = entity
                        theme = partner
                        relation_type = 'asymmetric'
                        ## assume 'dockets' must follow when they occur appositively
                    elif (last_type == 'docket') and (current_type in ['standard_case','case_X_vs_Y','case_citation_other']) \
                      and (gram_type in ['pre_nom']):
                        includes_docket = partner
                        theme = entity
                        relation_type = 'asymmetric'
                    elif (last_type == 'LEGAL_ROLE') and (current_type in ['ORGANIZATION','PROFESSION','FAMILY','NAME','PERSON']) and (gram_type in ['pre_nom']):
                        legal_role = partner
                        theme = entity
                        relation_type = 'asymmetric'
                    elif (current_type == 'LEGAL_ROLE') and (last_type in ['ORGANIZATION','PROFESSION','FAMILY','NAME','PERSON']) \
                      and (gram_type in ['apposition','as_predication','preposition','indirect_infix']):
                        legal_role = entity
                        theme = partner
                        relation_type = 'asymmetric'                    
                    elif (last_type == 'PROFESSION') and (current_type in ['NAME','PERSON']) and (gram_type in ['pre_nom','infix']):
                        profession = partner
                        theme = entity
                        relation_type = 'asymmetric'
                    elif (current_type == 'PROFESSION') and (last_type in ['NAME','PERSON']) \
                      and (gram_type in ['apposition','as_predication','preposition']):
                        profession = entity
                        theme = partner
                        relation_type = 'asymmetric'                    
                    elif (last_type == 'FAMILY') and (current_type in ['NAME','PERSON']) and (gram_type in ['pre_nom']):
                        family = partner
                        theme = entity
                        relation_type = 'partly_asymmetric'
                    elif (current_type == 'FAMILY') and (last_type in ['NAME','PERSON']) \
                      and (gram_type in ['apposition','as_predication','preposition']):
                        family = entity
                        theme = partner
                        relation_type = 'partly_asymmetric'
                    elif (last_type in ['case_X_vs_Y','case_citation_other','standard_case']) and \
                      (current_type in ['case_X_vs_Y','case_citation_other','standard_case']) and \
                      (last_type != current_type):
                        relation_type = 'equivalence'
                        if last_type == 'standard_case':
                            if (partner['id'] in standard_case_related) and (standard_case_related[partner['id']] == 'left'):
                                standard_case = 'Fail'
                                ## equivalence not allowed on both sides
                            else:
                                standard_case = partner
                                standard_case_related[partner['id']] = 'right'
                        elif last_type == 'case_X_vs_Y':
                            X_vs_Y = partner
                        elif last_type == 'case_citation_other':
                            case_citation_other = partner
                        if current_type == 'standard_case':
                            if (partner['id'] in standard_case_related) and (standard_case_related[partner['id']] == 'right'):
                                standard_case = 'Fail'
                                ## equivalence not allowed on both sides
                            else:
                                standard_case = entity
                                standard_case_related[entity['id']] = 'left'
                        elif current_type == 'case_X_vs_Y':
                            X_vs_Y = entity
                        elif current_type == 'case_citation_other':
                            case_citation_other = entity
                        if standard_case == 'Fail':
                            relation_type = False
                    else:
                        relation_type = False
                    if relation_type:
                        for att_name,att_value in [['gram_type',gram_type],['preposition',preposition],
                                                   ['relation_type',relation_type],['theme',theme],['at_date',at_date],\
                                                   ['includes_docket',includes_docket],['legal_role',legal_role], \
                                                   ['profession',profession],['family',family],['standard_case',standard_case],\
                                                   ['case_citation_other',case_citation_other],['X_vs_Y',X_vs_Y],\
                                                   ['party1',party1],['party2',party2],['start',start],['end',end]]:
                            if att_value or (type(att_value)==int): 
                        ## type statement deals with the fact that 0 is interpretted as False
                                relation[att_name]=att_value
                    else:
                        relation = False
                    if (len(relations)>0) and relation:
                        last_relation = relations[-1]
                        if (current_type in ['NAME','PERSON']):
                            if ('theme' in last_relation) and (last_entity == last_relation['theme']) and \
                              (last_type == 'PROFESSION') and ('legal_role' in last_relation):
                                last_relation['theme'] = entity
                                last_relation['end']= entity['end']
                                ## if last_relation connected a legal_role to a profession
                                ##    and the current relation linked the same professional to a name
                                ##        alter last_relation to link to the name
                                ## possible problem caused by "family" relations
                        if ('theme' in relation) and (relation['theme']==last_entity) and ('theme' in last_relation) and \
                          (get_type_from_entity(last_relation['theme'])in ['NAME','PERSON']) and ('legal_role' in relation) and (last_type == 'PROFESSION'):
                            relation['theme']=last_relation['theme']
                            relation['start']=relation['theme']['start']
                            ## if current relation connected a legal role to a profession
                            ##    and the last relation connected the same professional to a name
                            ##        alter the current relation to be connected to that name
                            ## possible problem caused by "family" relations
                    ## in orriginal version, there were elifs related to bridging relations here (removed for other mechanisms)
                    ## also removed special treatment of conjoined relations
                    if relation:
                        add_citation_id(relation,file_id,citation_dictionary)
                        relations.append(relation)
                        if 'at_date' in relation:
                            last_date_relation = relation
                        if relation['relation_type']=='equivalence':
                            rel_id = relation['id']
                            entity_id = entity['id']
                            if entity_id in equiv_relations:
                                equiv_relations[entity_id].append(rel_id)
                            else:
                                equiv_relations[entity_id] = [rel_id]
            last_entity = entity
            last_entity_type = entity_type
    return(relations)

def relation_print(outstream,relation):
    outstream.write('<RELATION')
    for attribute in ['id','legal_role','relation_type','gram_type','preposition','profession','theme',\
                      'standard_case','X_vs_Y','case_citation_other','reference_word','at_date',\
                      'includes_docket','family','party1','party2','conj1','conj2']:
                      ## don't print out 'start' and 'end' -- useful for internal purposes, but not appropriate for output
        if attribute in relation:
            if isinstance(relation[attribute],dict):
                outstream.write(' '+attribute+'="'+relation[attribute]['id']+'"')
                outstream.write(' '+attribute+'_string="'+wol_escape(relation[attribute]['string'])+'"')
            else:
                outstream.write(' '+attribute+'="'+wol_escape(str(relation[attribute]))+'"')
    outstream.write('>')
    if 'string' in relation:
        outstream.write(wol_escape(relation['string']))
    outstream.write('</RELATION>'+os.linesep)

def merge_spans(spans):
    ## input = set of spans sorted first by start and then by end
    output = []
    last_span = False
    for span in spans:
        if not last_span:
            last_span = span[:]
        elif last_span[0] == span[0]:
            last_span[1] = span[1]
        elif last_span[1]==span[1]:
            pass
        elif (last_span[0]<span[0]) and (last_span[1]>=span[1]):
            pass
        else:
            output.append(last_span)
            last_span = span[:]
    if last_span:
        output.append(last_span)
    return(output)

def non_zero_subtract(first_num,second_num):
    difference = first_num-second_num
    if difference != 0:
        return(difference)

def merge_spans2(spans,types,line,offset):
    ## input = set of spans sorted first by start and then by end
    ## modified for use with one_line_object to allow for an initial (capitalized) string
    output = []
    num = 0
    last_span = False
    last_type = False
    current_type = False
    for span in spans:
        if not last_span:
            last_span = span[:]
            last_type = types[num]
        elif last_span[0] == span[0]:
            last_span[1] = span[1]
        elif last_span[1]==span[1]:
            pass
        elif (last_span[0]<span[0]) and (last_span[1]>=span[1]):
            pass
        elif last_span and (num > 0) and (last_type in ['NAME','PERSON','ORGANIZATION']) \
           and (last_span[1]<span[0]) \
           and re.search('^ *$',line[last_span[1]-offset:non_zero_subtract(span[0],offset)]):
            pass
        else:
            if last_span:
                output.append(last_span)
            last_span = span[:]
            last_type = types[num]
        num = num + 1
    if last_span:
        output.append(last_span)
    return(output)

def remove_out_words_from_extra(extra):
    cue_pattern = re.compile('nos?|and|[0-9]',re.I)
    ## no is the number marker for docket numbers
    ## possibly other stuff doesn't matter as well
    match = cue_pattern.search(extra)
    while match:
        extra = extra[:match.start(0)]+extra[match.end():]
        match = cue_pattern.search(extra)
    return(extra)

def merge_spans_if_take_up_whole_line(spans,line,offset):
    if len(spans) <= 1:
        return(spans)
    extra = ''
    spans.sort()
    start = 0
    for span in spans:
        extra = extra + line[start:span[0]-offset]
        start = span[-1]-offset
    if start:
        extra = extra + line[start:]
    extra = remove_out_words_from_extra(extra)
    if re.search('[a-zA-Z0-9]',extra):
        return(spans)
    else:
        return([[spans[0][0],spans[-1][1]]])

def OK_after_one_line_object(right_string):
    if not re.search('[A-Za-z]',right_string):
        return(True)
    elif re.search('^ *CERTIORARI( [A-Z]*)* *$',right_string):
        ### may want to eventually go after CERTIORIARI TO strings
        return(True)
    elif re.search('^[^a-zA-Z]*(Per )?Curiam[^a-zA-Z]*$',right_string):
        return(True)

def skippable_beginning (line_start):
    slip_opinion = re.search('(Slip +Opinion)|(SLIP +OPINION)',line_start)
    if slip_opinion:
        line_start = line_start[:slip_opinion.start()]+line_start[slip_opinion.end():]
    cite_as = re.search('Cite +as:?|CITE +AS:?',line_start)
    if cite_as:
        line_start = line_start[:cite_as.start()]+line_start[cite_as.end():]
    if re.search('[A-Za-z]',line_start):
        return(False)
    else:
        return(True)

def one_line_object(entity_set,line,offset):
    spans = []
    types = []
    citation_spans = []
    citation_types = []
    for entity in entity_set:
        spans.append([entity['start'],entity['end']])
        this_type = get_type_from_entity(entity)
        types.append(this_type)
        if this_type in ['standard_case','case_X_vs_Y','case_citation_other','docket']:
            citation_spans.append([entity['start'],entity['end']])
            citation_types.append(this_type)
    spans = merge_spans2(spans,types,line,offset)
    spans = merge_spans_if_take_up_whole_line(spans,line,offset)
    if (len(spans) == 1):
        if (not (re.search('[A-Za-z]',remove_out_words_from_extra(line[:spans[0][0]-offset])))) and OK_after_one_line_object(remove_out_words_from_extra(line[spans[0][1]-offset:])):
            return(True)
        else:
            return(False)
    elif citation_spans:
        spans = merge_spans2(citation_spans,citation_types,line,offset)
        spans = merge_spans_if_take_up_whole_line(spans,line,offset)
        if (len(spans) == 1) and skippable_beginning(line[:spans[0][0]-offset]) \
          and OK_after_one_line_object(line[spans[0][1]-offset:]):
            return(True)
        else:
            return(False)            
    else:
        return(False)

def multiline_objects(line_output):
    line_numbers = []
    for obj in line_output:
        line_number = obj['line']
        if not line_number in line_numbers:
            line_numbers.append(line_number)
    if len(line_numbers)>1:
        return(True)
    else:
        return(False)

def deletable_line(line):
    slip1 = re.compile('\(Slip +Opinion.*?done +in +connection +with +this +case, +at +the +time +the +opinion +is +issued\.',re.I)
    slip2 = re.compile('The +syllabus +constitutes +no +part +of +the +opinion.*?convenience +of +the +reader\.',re.I)
    slip3 = re.compile('See +United +States +v\. +Detroit +Timber +& +Lumber +Co\., +200 +U\. *S\. +321, +337\.',re.I)
    slip3a = re.compile(' *SUPREME.*?Syllabus',re.I) ## without greedy operator, it takes out to much
    one_liner = re.compile('(^ *(((Statement +of.*)|(NOTICE:.*))?SUPREME +COURT +OF +THE +UNITED STATES)|(ORDER IN PENDING CASE))',re.I) ## might be useful for finding author of opinion
    position = 0
    match1 = slip1.search(line)
    if match1:
        position = match1.end()
    match2 = slip2.search(line,position)
    if match2:
        position = match2.end()
    match3 = slip3.search(line,position)
    if match3:
        position = match3.end()
        position2 = slip3a.search(line,position)
        if position2:
            position = position2.end()
    match4 = one_liner.search(line)
    if match4:
        position = match4.end()
    if position and (position != 0):
        return(position)

def merge_spans_if_conjoined(spans,line,offset):
    big_start = spans[0][0]
    start,end = spans[0]
    Fail = False
    for next_start,next_end in spans[1:]:
        in_between = line[end-offset:next_start-offset].lower()
        in_between = re.sub('[;,]',' ',in_between) ## ignore inbetween separator punctuation
        in_between = re.sub('and','',in_between) ## ignore the word and
        if re.search('[^ ]',in_between):
            Fail = True
    if Fail:
        return(spans)
    else:
        ## keep the last end
        return([[big_start,next_end]])
    
def weak_one_line_object(entity_set,line,offset,one_line_objects):
    if not one_line_objects:
        return(False)
    name_citation_spans = []
    n_types = []
    other_spans = []
    for entity in entity_set:
        if get_type_from_entity(entity) in ['case_X_vs_Y','case_citation_other']:
            name_citation_spans.append([entity['start'],entity['end']])
            n_types.append(get_type_from_entity(entity))
        else:
            other_spans.append([entity['start'],entity['end']])
    name_citation_spans = merge_spans2(name_citation_spans,n_types,line,offset)
    name_citation_spans = merge_spans_if_take_up_whole_line(name_citation_spans,line,offset)
    if name_citation_spans and (len(name_citation_spans)>1):
        name_citation_spans = merge_spans_if_conjoined(name_citation_spans,line,offset)
    answer = True
    if len(name_citation_spans)==1:
        big_start,big_end = name_citation_spans[0]
        for span in other_spans:
            if span[0] < big_start:
                answer=False
    else:
        answer = False
    return(answer)

def remove_objects_for_line_N(output,relations,line_number,relation_pair_dict):
    new_output = []
    new_relations = []
    removed = []
    for obj in output:
        if obj['line'] != line_number:
            new_output.append(obj)
        else:
            removed.append(obj)
    for rel in relations:
        rel_pair = []
        if ('line' in rel) and (rel['line'] == line_number):
            pass
        else:
            remove_this_one = False
            for slot in ['legal_role','profession','theme','standard_case','X_vs_Y',\
                         'case_citation_other','reference_word','at_date',\
                         'includes_docket','family','party1','party2']:
                if slot in rel:
                    rel_pair.append(rel[slot])
                    if remove_this_one:
                        pass
                    elif (slot in rel) and (rel[slot] in removed):
                        remove_this_one = True
            if remove_this_one:
                if (rel_pair[0]['id'] in relation_pair_dict):
                    relation_pair_dict[rel_pair[0]['id']].pop(rel_pair[1]['id'])
                    if len(relation_pair_dict[rel_pair[0]]) == 0:
                        relation_pair_dict.pop(rel_pair[0])
                if (rel_pair[1]['id'] in relation_pair_dict):
                    relation_pair_dict[rel_pair[1]['id']].pop(rel_pair[0]['id'])
                    if len(relation_pair_dict[rel_pair[1]]) == 0:
                        relation_pair_dict.pop(rel_pair[1])
            else:
                new_relations.append(rel)
    return(new_output,new_relations,removed)

def make_other_citation_from_name(possible_other_citation,line_number,file_id,citation_dictionary):
    out = {'entry_type':'case_citation_other','line':line_number}
    ## 'start', 'end','name','string', line, type
    for key in ['start','end','string']:
        out[key] = possible_other_citation[key]
    out['name']=possible_other_citation['string']
    add_citation_id(out,file_id,citation_dictionary)
    return(out)


def span_takes_up_whole_line(line,offset,span):
    extra = line[:span[0]-offset]+line[span[1]-offset:]
    extra = remove_out_words_from_extra(extra)
    if re.search('[a-zA-Z0-9]',extra):
        return(False)
    else:
        return(True)

def begin_v(line):
    line = line.strip(os.linesep)
    match = re.search('^[ \t]*(.*)v\. +[A-Z]',line)
    if match:
        if match.group(1):
            first_word_match = re.search('[a-zA-Z]+',match.group(1))
            if first_word_match:
                if first_word_match.group(0).lower() in relational_dict:
                    return(True)
                else:
                    return(False)
            else:
                return(True)
        else:
           return(True)
    else:
        return(False)

def update_relation_pair_dict(relation_pair_dict,line_relations):
    for relation in line_relations:
        pair = []
        for slot in ['legal_role','profession','theme','standard_case','X_vs_Y','case_citation_other',\
                     'reference_word','at_date','includes_docket','family','party1','party2']:
            if slot in relation:
                pair.append(relation[slot]['id'])
        object1,object2 = pair
        if object1 in relation_pair_dict:
            relation_pair_dict[object1].append(object2)
        else:
            relation_pair_dict[object1]=[object2]
        if object2 in relation_pair_dict:
            relation_pair_dict[object2].append(object1)
        else:
            relation_pair_dict[object2]=[object1]

def ambiguous_person_entry(word):
    entry = []
    if word in relational_dict:
        entry.extend(relational_dict[word])
    if word in POS_dict:
        entry.extend(POS_dict[word])
    if 'PERSONNAME' in entry:
        entry.remove('PERSONNAME')
    if len(entry)>0:
        return(True)
    else:
        return(False)
  
def find_case_citations(txt_file,case_file,file_id,previous_information_file,previous_info_fields=['citation_case_name','citation_docket_number','citation_id']):
    global id_number
    global one_word_person_names
    one_word_person_names = {}
    id_number = 0
    citation_output = []
    docket_output = []
    vs_output = []
    dates = []
    role_phrase_output = []
    citation_dictionary = {}
    previous_info_dictionary ={}
    line_output = []
    line_relations = []
    output = []
    relations = []
    one_line_objects = False
    possible_other_citation = False
    found_initial_equivalent_relations = False
    relation_pair_dict = {}
    if previous_information_file != False:
        with open(previous_information_file) as instream:
            all_text = instream.read()
            fill_dictionary_from_xml(all_text,previous_info_fields,previous_info_dictionary)
    line_number = 0
    max_multi_line_number = 5
    with open(txt_file) as instream:
        offset = 0
        last_line = False
        last_line_one_line_object = False
        line_combo = False
        old_one_line_objects = False
        standard_case_lines = []
        conj_output = []
        for line in instream:
            line_output=[]
            line_number = line_number+1
            out = []
            out2 = []
            out3 = []
            out3_prime = []
            out4 = []
            out5 = []
            out6 = []
            if line_number <=4:
                deletable_line_position = deletable_line(line)
            elif deletable_line_position:
                deletable_line_position = False
            if (deletable_line_position and (deletable_line_position > 0)):
                line = line[deletable_line_position:]
                offset = offset + deletable_line_position
            garbage = detect_garbage_line(line)
            if garbage:
                out = []
                last_line_one_line_object = False
            elif last_line and ((re.search('[ \t]*([vV][sS]?[\.]?|versus|against)[ \t]*$',line.strip(os.linesep))) or \
              (begin_v(line) and line_number<=max_multi_line_number)):        
                line_combo = True
                if not one_line_objects:
                    one_line_objects = old_one_line_objects
                line = last_line.strip(os.linesep) + ' ' + line
                offset = last_offset
                output,relations,removed_output = remove_objects_for_line_N(output,relations,line_number-1,relation_pair_dict)
                if one_line_objects:
                    for item in removed_output:
                        if item in one_line_objects:
                            one_line_objects.remove(item)
                possible_other_citation = False
                max_multi_line_number = max_multi_line_number + 1
                ## if current line ends in v. 
                ## also one_line_object status is maintained
            elif line_combo:
                possible_other_citation = False
                line = last_line.strip(os.linesep) + ' ' + line
                line_combo = False
                offset = last_offset
                out = get_citation_output(line,offset,file_id,citation_dictionary)
                line_output.extend(out)
                max_multi_line_number = max_multi_line_number + 1
                ## if last line (ends in  v.) and continuing one_line_object thing
            else:
                if (not last_line) and re.search('[ \t]*([vV][sS]?[\.]?|versus|against)[ \t]*$',line.strip(os.linesep)):
                    line_combo = True
                    out = []
                    possible_other_citation = False
                    max_multi_line_number = max_multi_line_number + 1
                else:
                    if possible_other_citation:
                        out_prime = make_other_citation_from_name(possible_other_citation,line_number-1,file_id,citation_dictionary)
                        line_output.append(out_prime)
                        possible_other_citation = False
                        if old_one_line_objects and not one_line_objects:
                            one_line_objects = old_one_line_objects 
                            one_line_objects.append(out_prime)   
                    out = get_citation_output(line,offset,file_id,citation_dictionary)
                    line_output.extend(out)
            if out:
                standard_case_lines.append(line_number)
            spans = []
            last_offset = offset
            for item in out:
                item['line']=line_number
                item['entry_type']='standard_case'
                spans.append([item['start'],item['end']])
            if (not garbage) and (not line_combo):
                out2 = get_docket_numbers(line,spans,offset,file_id,citation_dictionary)
            if (not garbage) and out2:
                line_output.extend(out2)
                for item in out2:
                    item['line']=line_number
                    item['entry_type']='docket'
                    spans.append([item['offset_start'],item['end']])
                    ## offset_start is the start before the signal (no., nos., and., ...), rather than the span of the actual docket no.
                spans.sort()
            if (not garbage) and (not line_combo):
                out2 = get_docket_number_sets(line,spans,offset,file_id,citation_dictionary)
            if (not garbage) and out2:
                line_output.extend(out2)
                for item in out2:
                    item['line']=line_number
                    item['entry_type']='docket'
                    spans.append([item['offset_start'],item['end']])
                spans.sort()
            if (not garbage) and (not line_combo):
                out3 = get_vs_citations(line,spans,offset,file_id,citation_dictionary,one_line_objects,line_number)
                out3 = edit_vs_citations(out3,previous_info_dictionary)
                remove_citations,parties,conj_out = get_party_names_and_roles_from_cases(out3,file_id,citation_dictionary)
                for cit in remove_citations:
                    out3.remove(cit)
                if conj_out:
                    conj_output.extend(conj_out)
            else:
                parties = False
            if (not garbage) and (not line_combo):
                out4 = find_dates(line,offset,file_id,citation_dictionary)
            if (not garbage) and out4:
                line_output.extend(out4)
                for item in out4:
                    item['line']=line_number
                    spans.append([item['start'],item['end']])
                spans.sort()
            if parties:
                line_output.extend(parties)
            if (not garbage) and out3:
                line_output.extend(out3)
                for item in out3:
                    item['line']=line_number
                    item['entry_type']='case_X_vs_Y'
                    spans.append([item['start'],item['end']])
                spans.sort()
            if (not garbage) and (not line_combo):
                out3_prime = get_other_case_citations(line,spans,offset,file_id,citation_dictionary,one_line_objects)
                line_output.extend(out3_prime)
                if out3_prime:
                    for item in out3_prime:
                        item['line']=line_number
                        item['entry_type']='case_citation_other'
                        spans.append([item['start'],item['end']])
                    spans.sort()
            if parties:
                for item in parties:
                    item['line']=line_number
                    spans.append([item['start'],item['end']])
                spans.sort()
            spans2 = spans[:]
            spans2 = merge_spans(spans2)
            if (not garbage) and (not line_combo):
                out5,conj_out = get_role_phrases(line,spans2,offset,file_id,citation_dictionary,spans,line_number)
                if out5 and (len(out5)==1) and (not (out3 or out4 or out2 or out)) and (line_number < max_multi_line_number) and \
                  ((line_number == 1) or (standard_case_lines and ((standard_case_lines[-1]+1) == line_number))) and \
                  (out5[0]['phrase_type']=='NAME') and span_takes_up_whole_line(line,offset,[out5[0]['start'],out5[0]['end']]):
                    possible_other_citation = out5[0]
                if conj_out:
                    conj_output.extend(conj_out)
            if (not garbage) and out5:
                for item in out5:
                    item['line']=line_number
                line_output.extend(out5)
            offset = offset + len(line)
            line_output=sort_records(line_output,use_ids=True)
            output.extend(line_output)
            if (not garbage) and (not line_combo):
                line_relations = look_for_close_relations(line_output,line,last_offset,file_id,citation_dictionary,line_number,found_initial_equivalent_relations)
                update_relation_pair_dict(relation_pair_dict,line_relations)
                count = 0
                while (not found_initial_equivalent_relations) and (count < len(line_relations)) and (line_number < 10):
                    if line_relations[count]['relation_type']=='equivalence':
                        found_initial_equivalent_relations = True
                    count = count+1
            else:
                line_relations = []
            line_relations = sort_records(line_relations,use_ids=True)
            if line_relations:
                for relation in line_relations:
                    relation['line']=line_number
                relations.extend(line_relations)
            if line_combo:
                pass
            if (not line_output) and (not re.search('[A-Za-z]',line)) and deletable_line_position:
                pass
            elif one_line_object(line_output,line,last_offset) or weak_one_line_object(line_output,line,last_offset,one_line_objects):
                if one_line_objects:
                    one_line_objects.extend(line_output)
                else:
                    one_line_objects = line_output
            elif one_line_objects and (not line_combo):
                old_one_line_objects = one_line_objects
                last_line_one_line_object = True
                line_relations2 = False
                if  multiline_objects(one_line_objects):
                    line_relations2 = get_one_line_object_relations(one_line_objects,offset,file_id,citation_dictionary,line_number,max_multi_line_number,relation_pair_dict)
                if line_relations2:
                    line_relations2 = sort_records(line_relations2,use_ids=True)
                    count = 0
                    while (not found_initial_equivalent_relations) and (count < len(line_relations2)):
                        if line_relations2[count]['relation_type']=='equivalence':
                            found_initial_equivalent_relations = True
                        count = count + 1                        
                one_line_objects = False
                if line_relations2:
                    for relation in line_relations2:
                        relation['line']=line_number
                    relations.extend(line_relations2)
            last_line = line
        if one_line_objects and not line_combo:
            line_relations2 = get_one_line_object_relations(line_output,offset,file_id,citation_dictionary,line_number,max_multi_line_number,relation_pair_dict)
            if line_relations2:
                line_relations2 = sort_records(line_relations2,use_ids=True)
            if not line_combo:
                one_line_objects = False
            if line_relations2:
                for relation in line_relations2:
                    relation['line']=line_number
                relations.extend(line_relations2)
        ## fix_one_word_person_names(line_output)
        if conj_output:
            for item in conj_output:
                if 'phrase_type' in item:
                    output.append(item)
                else:
                    relations.append(item)
            ## we could sort these (later)
        for out in output:
            if 'string' in out:
                refstring = out['string'].lower()
            else:
                refstring = False
            if refstring and ('phrase_type' in out) and (out['phrase_type']=='PERSON') and (not ' ' in out['string']) \
              and (not 'party1_of' in out) and (not ('party2_of' in out)) and (refstring in one_word_person_names) \
              and ambiguous_person_entry(refstring) and (one_word_person_names[refstring] == 1):
                out['phrase_type']='NAME'
    with open(case_file,'w') as outstream:
        for out in output:
            if ('entry_type' in out) and (out['entry_type'] in ['case_X_vs_Y','docket','standard_case','case_citation_other']):
                citation_print(outstream,out)
            elif 'phrase_type' in out:
                role_print(outstream,out)
        for relation in relations:
            relation_print(outstream,relation)
