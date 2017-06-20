from wol_utilities import *

def printable_entry(entry):
    ## for relations,
    ## choose FROM according to the following preference list
    ## Theme, standard_case, X_vs_Y, case_citation_other
    ## choose TO as the other item from the list:
    ## standard_case, X_vs_Y, case_citation_other,
    ## 'legal_role','profession','at_date','includes_docket','family','party1','party2'
    ## not sure of status of 'reference_word' -- may not be used
    relational_feature_hierarchy = ['theme', 'standard_case', 'X_vs_Y', 'case_citation_other']
    relational_features = ['theme', 'standard_case', 'X_vs_Y', 'case_citation_other','legal_role',\
                           'profession','at_date','includes_docket','family','party1','party2']
    label = entry['label']
    #fromID, fromText, toID, toText
    from_label = False
    to_label = False
    from_label_string = False
    to_label_string = False    
    if label in ['RELATION']:
        for from_item in relational_feature_hierarchy:
            if (not from_label) and (from_item in entry):
                from_label = from_item
                from_label_string = from_item + '_string'
        for to_item in relational_features:
            if (to_item != from_label) and (not to_label) and (to_item in entry):
                to_label = to_item
                to_label_string = to_item + '_string'
    output_string = '<'+label+' '+'id="'+entry['id']+'"'
    features = list(entry.keys())
    features.sort()
    if from_label and to_label:
        from_local_id = entry[from_label]
        to_local_id = entry[to_label]
        from_id = entry_dictionary[from_local_id]['id']
        to_id = entry_dictionary[to_local_id]['id']
        from_string = wol_unescape(entry[from_label_string])
        to_string = wol_unescape(entry[to_label_string])
        for feature,value in [['fromID',from_id],['fromText',from_string],['toID',to_id],['toText',to_string]]:
            output_string += ' '+feature+'="'+value+'"'
    for feature in features:
        if feature in ['id','label',from_label,to_label,from_label_string,to_label_string]:
            pass
        else:
           output_string += ' '+feature+'="'+entry[feature]+'"'
    output_string += '/>'+os.linesep
    return(output_string)

def get_entry_from_line(line):
    ## entry types: NAME, PROFESSION, ORGANIZATION, QUOTE, FAMILY, LEGAL_ROLE, MESSAGE, docket, ATTRIBUTION, RELATION
    ## initials: N, P, O, Q, F, L, M, d, A, R
    global entry_dictionary
    global mae_id_number
    entry = {}
    entry_pattern = re.compile('<([^>]+)>(.*)(</[^>]+>)')
    position = 0
    feature_value_pattern = re.compile('([A-Za-z_0-9]+)="([^"]+)"')
    match = entry_pattern.search(line)
    if match:
        feature_structure = match.group(1)
        text = match.group(2)
        label_match = re.search('([^ ]*) ',feature_structure)
        entry['label']=label_match.group(1)
        if text!= '':
            entry['text'] = text
        body = feature_structure[label_match.end(1):]
        feature_match = feature_value_pattern.search(body,position)
        while feature_match:
            feature,value =feature_match.group(1),feature_match.group(2)
            if feature == 'id':
                feature = 'local_id'
                entry_dictionary[value]=entry
            entry[feature]=value
            position = feature_match.end()
            feature_match = feature_value_pattern.search(body,position)
        mae_id = entry['label'][0]+str(mae_id_number)
        entry['id']=mae_id
        mae_id_number += 1
        return(entry)
    else:
        return(False)

def pre_process_web_of_law_IE(txt_file,case_file,quote_file,out_file,\
                              field_replacement=[['quote','string','text',True]]):
    global mae_id_number
    global entry_dictionary
    mae_id_number = 0
    entry_dictionary = {}
    out_hash1 = {}
    out_hash2 = {}
    replacement_dictionary = {}
    ## label,in_attribute,out_attribute,yes_no_escape
    for quad  in field_replacement:
        replacement_dictionary[quad[0]] = quad[1:]
    with open(out_file,'w') as outstream:
        with open(txt_file) as instream:
            txt = instream.read()
        outstream.write('''<?xml version="1.0" encoding="UTF-8" ?>
<AttributionTask>
<TEXT><![CDATA['''+txt+''']]></TEXT>
<TAGS>'''+os.linesep)
        with open(case_file) as instream:
            for line in instream:
                entry = get_entry_from_line(line)
                label = entry['label']
                if label in replacement_dictionary:
                    in_attribute,out_attribute,yes_no_escape = replacement_dictionary[label]
                    if in_attribute in entry:
                        value = entry[in_attribute]
                        if yes_no_escape:
                            value = wol_unescape(value)
                        value = annotation_quote_fix(value) 
                        ## for annotation purposes,
                        ## replace quote with left double quote
                        value = re.sub('"',chr(171),value)
                        entry.pop(in_attribute)
                        entry[out_attribute]=value                        
                if entry and ('start' in entry):
                    start = int(entry['start'])
                    if start in out_hash1:
                        out_hash1[start].append(entry)
                    else:
                        out_hash1[start]=[entry]
                elif entry and ('id' in entry):
                    key = entry['id']
                    out_hash2[key] = entry
        with open(quote_file) as instream:
            for line in instream:
                entry = get_entry_from_line(line)
                label = entry['label']
                if label in replacement_dictionary:
                    in_attribute,out_attribute,yes_no_escape = replacement_dictionary[label]
                    if in_attribute in entry:
                        value = entry[in_attribute]
                        if yes_no_escape:
                            value = wol_unescape(value)
                        entry.pop(in_attribute)
                        ## for annotation purposes,
                        ## replace quote with left double quote
                        value = re.sub('"',chr(171),value)
                        entry[out_attribute]=value  
                if entry and ('start' in entry):
                    start = int(entry['start'])
                    if start in out_hash1:
                        out_hash1[start].append(entry)
                    else:
                        out_hash1[start]=[entry]
                elif entry and ('local_id' in entry):
                    key = entry['local_id']
                    out_hash2[key] = entry 
        offsets = list(out_hash1.keys())
        offsets.sort()
        for offset in offsets:
            for entry in out_hash1[offset]:
                outstream.write(printable_entry(entry))
        keys = list(out_hash2.keys())
        keys.sort()
        for key in keys:
            entry = out_hash2[key]
            outstream.write(printable_entry(entry))
        outstream.write('''</TAGS>
</AttributionTask>''')

## pre_process_web_of_law_IE('108713.txt', '108713.case8', '108713.quotes', '108713_annotate.xml')
