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
ordinal_rexp = ordinal_rexp[:-1]  # remove superfluous '|' symbol

amend_rexp = ''
for o in amends:
    amend_rexp += o + '|'
amend_rexp = amend_rexp[:-1]  # remove superfluous '|' symbol

# add the two rexps for a natural language mention (eg. "the First Amendment")
natural_single_amend_rexp = '(({0}) (?:{1}))'.format(ordinal_rexp, amend_rexp)

# TODO: rexp for a formal citation of the amendments
formal_amend_rexp = ''

def capture_single_amendment(inString):
    # cap any simple ordinal
    # full_amend_pattern = re.compile(natural_amend_rexp + '|' + formal_amend_rexp)
    full_amend_pattern = re.compile(natural_single_amend_rexp)
    amend_match = full_amend_pattern.search(inString)
    if amend_match:
        return amend_match

def find_amendments_in_line(inString):
    # full_amend_pattern = re.compile(natural_amend_rexp + '|' + formal_amend_rexp)
    full_amend_pattern = re.compile(natural_single_amend_rexp)
    amend_match = full_amend_pattern.findall(inString)
    if amend_match:
        return amend_match

def get_single_amendment_number(amend_string):
    # get the amendment number
    return ordinal_variants[capture_single_amendment(amend_string.group(0)).group(2)]

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
            amendment_matches = find_amendments_in_line(line) # get list of matches

            if amendment_matches:
                # get the matches in order
                for match_group in amendment_matches:

                    match = re.compile(match_group[0]).search(line)
                    line_offset -= len(match.group(0))
                    offset += match.start()
                    # create a citation
                    amendment_num = get_single_amendment_number(match)
                    amendment_cit = generate_single_amendment_citation(
                            offset,
                            offset+len(match.group(0)),
                            line_num,
                            file_id[1:]+'_'+str(len(legs)+1),
                            amendment_num,
                            match.group(0)
                    )
                    # offset += start point
                    offset += len(match.group(0))
                    print(amendment_cit)
                    legs.append(amendment_cit)

                    # substr the line from start point of match to end of line
                    # this is so we don't capture only the first ref to repeated amendments
                    line = line[match.start():]

            line_num = line_num + 1
            offset += line_offset

    return legs
