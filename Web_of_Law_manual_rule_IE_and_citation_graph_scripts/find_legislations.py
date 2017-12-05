import re

### Capturing amendments to the US constitution

body = (
    'US',
)

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
    'Tenth': '10'
}

amends = (
    'amend.',
    'Amendment',
    'amendment'
)

ordinal_variants = dict()

for o in ordinals:
    ordinal_variants[o] = ordinals[o]
    ordinal_variants[o.lower()] = ordinals[o]

ordinal_rexp = ''
for o in ordinal_variants:
    ordinal_rexp += o + '|'
ordinal_rexp = ordinal_rexp[:-1] # remove superfluous '|' symbol

amend_rexp = ''
for o in amends:
    amend_rexp += o + '|'
amend_rexp = amend_rexp[:-1] # remove superfluous '|' symbol

def capture_single_amendment(inString):
    # cap any simple ordinal
    full_amend_pattern = re.compile('({0}) (?:{1})'.format(ordinal_rexp, amend_rexp))
    amend_match = full_amend_pattern.search(inString)
    if amend_match:
        return amend_match

def get_single_amendment_number(amend_match):
    # get the amendment number
    return ordinal_variants[amend_match.group(1)]

def generate_single_amendment_citation(
        start_index,
        end_index,
        line_num,
        cit_id,
        amend_num,
        text):

    # create citation
    citation = '<citation ' \
               'id="{0}" ' \
               'entry_type="amendment" ' \
               'start="{1}" ' \
               'end="{2}" ' \
               'line="{3}" ' \
               'amendment="{4}>' \
               '{5}' \
               '</citation>'\
        .format(
                cit_id,
                start_index,
                end_index,
                line_num,
                amend_num,
                text)

    return citation

def find_legislations(txt,case8,file_id):

    legs = []
    with open(txt) as instream:

        offset = 0
        line_num = 0
        for line in instream:
            line_offset = len(line)
            amendment_match = capture_single_amendment(line)
            if(amendment_match):
                line_offset = line_offset - len(amendment_match.group(0))
                offset += len(amendment_match.group(0))
                amendment_num = get_single_amendment_number(amendment_match)
                amendment_cit = generate_single_amendment_citation(
                        offset,
                        0,
                        line_num,
                        file_id,
                        amendment_num,
                        amendment_match.group(0))
                print(amendment_cit)
                legs.append(amendment_cit)
            line_num = line_num + 1
            offset = offset + line_offset

    return legs
