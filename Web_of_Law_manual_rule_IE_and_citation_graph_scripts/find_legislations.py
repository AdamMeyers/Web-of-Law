import re
from wol_utilities import capture_roman

# Captures amendments to the US constitution
# TODO: capture references to Amendments as antecedents from later, proximal references like
#   "from the Amendment [mentioned earlier]"

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


def get_states_dict():
    """Returns a dict of abbreviation of state names to full state name

    :return:
    """
    states_dict = {}
    with open('STATES.dict') as instream:
        for line in instream:
            states_dict[line.split('\t')[0]] = line.split('\t')[1].strip()
    states_dict['U.S.'] = 'Federal'
    return states_dict


states_rexp = ''
for o in get_states_dict():
    states_rexp += '(?:{0})|'.format(o.replace('.', '\.'))
states_rexp = states_rexp[:len(states_rexp) - 1]
body_rexp = states_rexp + '|(?:U\.S\.)'

roman_num_rexp = '(?:[MCLDXVI]+)'
numeral_rexp = roman_num_rexp + '|(?:\d+)'

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
state_statute_cit_rexp = '({0}) ((?:\w{{2,}}?\W? ){{0,5}})(?:c\. ((?:\w+?)|(?:\d+?)), ?)?§§? (\d+(?:\W?\d+)*)*' \
    .format(states_rexp)

###########################################
# NATURAL CONSTITUTIONAL REFERENCE REGEX: #
###########################################

informal_const_rexp = '(?:United States)?(?: the)? Constitution (?:of the United States)?'


def capture_informal_amendment_ordinals(in_string):
    """Returns list of strings matching the informal amendments rexp in given string

    Returns a list of strings, the 0th of which is the whole string
    The 1st and last elements are the first and last listed ordinals per the informal_amend_rexp
    The middle elements are the 2nd group from the informal_amend_rexp split and spread into a list
    :param in_string: (str) the string to search in
    :return: a list of strings
    """

    matches = []
    full_amend_pattern = re.compile(informal_amend_rexp)
    amend_match = full_amend_pattern.search(in_string)
    if amend_match:
        matches.append(amend_match.group(0))
        matches.append(amend_match.group(1))
        # The middle group is a string of the comma separated amendment
        # mentions between the first and last mentions
        # It will be split such that empty strings are possible
        # Thus they are filtered out
        if amend_match.group(2):
            matches.extend(list(filter(lambda x: x, amend_match.group(2).split(", "))))
        if amend_match.group(3):
            matches.append(amend_match.group(3))
    return matches


def capture_const_cits(in_string):
    """Returns a list of strings, each corresponding to the match groups in the constitutional amendment/article
    citation rexp

    :param in_string:
    :return:
    """

    const_pattern = re.compile(const_cit_rexp)
    match = const_pattern.search(in_string)
    if match:
        return [
            match.group(0),  # matched string
            match.group(1),  # jurisdiction
            match.group(2),  # article | amendment?
            match.group(3),  # article/amend num
            match.group(4),  # section
            # match.group(5),  # clause
        ]
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
    match = const_ref_pattern.search(in_string)
    if match:
        return [
            match.group(0),  # matched string
        ]
    else:
        return []


def capture_federal_statute_cits(in_string):
    """Returns a list of strings, each corresponding to match groups in the federal statute citation rexp

    :param in_string:
    :return:
    """
    const_pattern = re.compile(federal_statute_cit_rexp)
    match = const_pattern.search(in_string)
    if match:
        return [
            match.group(0),  # matched string
            match.group(1),  # article
            # match.group(2),  # chapter
            match.group(2),  # section
            match.group(3),  # subsection
        ]
    else:
        return []


def capture_state_statute_cits(in_string):
    """Returns a list of strings, each corresponding to match groups in the state statute citation rexp

    :param in_string:
    :return:
    """
    const_pattern = re.compile(state_statute_cit_rexp)
    match = const_pattern.search(in_string)
    if match:
        return [
            match.group(0),  # matched string
            match.group(1),  # state
            match.group(2),  # article
            match.group(3),  # chapter
            match.group(4),  # section
            # match.group(5),  # subsection
        ]
    else:
        return []


def find_legislations_in_line(in_string):
    """Return a list of strings matching all current leglislation rexps from a given line

    :param in_string:
    :return: (list<str>) A list of strings
    """
    if not in_string or in_string == '\n':
        return

    rexps = [
        informal_amend_rexp,
        const_cit_rexp,
        federal_statute_cit_rexp,
        state_statute_cit_rexp,
        informal_const_rexp
    ]
    legs = []
    for exp in rexps:
        pattern = re.compile(exp)
        matches = list(pattern.finditer(in_string))
        if matches:
            legs.extend(list(map(lambda x: x.group(0), matches)))

    return legs


def ordinal_to_number(ordinal_string):
    """Returns numerical value of given ordinal string

    :param ordinal_string:
    :return: the numerical value of the ordinal
    """
    if ordinal_string in ordinal_variants:
        return ordinal_variants[ordinal_string]
    else:
        return 0


def numeral_to_int(num_string):
    """Returns an int corresponding to the given numeral string

    :param num_string:
    :return:
    """

    if not num_string:
        return 0
    num = 0
    roman_match = capture_roman(num_string)
    if roman_match:
        num = roman_match
    elif re.search('\d+', num_string):
        num = int(re.search('(\d+)', num_string).group(1))

    return num


def body_abbrev_to_full(abbrev):
    """Returns a full state name given an abbreviation, or "U.S." if "U.S." is given

    :param abbrev:
    :return:
    """
    bodies = get_states_dict()
    return bodies[abbrev]


def generate_legislation_citations_from_string(in_string, offset, line_num, leg_count, file_id):
    """Returns an array of citation strings from a given string of natural references to amendments

    :param in_string: string that matches natural amendment format
    :param offset: byte offset in file in_string starts from
    :param line_num: line number in file
    :param leg_count: index of the current legislation citation created from this file
    :param file_id: id of the file being read
    :return: list of citation strings
    """

    matches = {
        'amendment': capture_informal_amendment_ordinals(in_string) or [],
        'const_cit': capture_const_cits(in_string) or [],
        'const_ref': capture_informal_constitutional_refs(in_string),
        'federal_statute': capture_federal_statute_cits(in_string),
        'state_statute': capture_state_statute_cits(in_string)
    }

    cits = []
    if len(matches['amendment']):
        cits.extend(list(map(lambda x: generate_amendment_reference(
            offset,
            offset + len(matches['amendment'][0]),
            line_num,
            file_id + str(leg_count + matches['amendment'].index(x)),
            ordinal_to_number(x),
            str.strip(matches['amendment'][0])
        ), matches['amendment'][1:])))

    if len(matches['const_cit']):
        cits.extend([generate_const_citation(
            offset,
            offset + len(matches['const_cit'][0]),
            line_num,
            file_id + str(leg_count + 1),
            body_abbrev_to_full(matches['const_cit'][1]),
            matches['const_cit'][2],
            numeral_to_int(matches['const_cit'][3]),
            numeral_to_int(matches['const_cit'][4]),
            numeral_to_int(matches['const_cit'][5]),
            str.strip(matches['const_cit'][0])
        )])

    if len(matches['const_ref']):
        cits.extend([generate_const_reference(
            offset,
            offset + len(matches['const_ref'][0]),
            line_num,
            file_id + str(leg_count + 1),
            str.strip(matches['const_ref'][0])
        )])

    if len(matches['federal_statute']):
        cits.extend([generate_statute_citation(
            offset,
            offset + len(matches['federal_statute'][0]),
            line_num,
            file_id + str(leg_count + 1),
            'federal',
            numeral_to_int(matches['federal_statute'][1]),
            '',
            numeral_to_int(matches['federal_statute'][2]),
            matches['federal_statute'][3],
            str.strip(matches['federal_statute'][0])
        )])

    if len(matches['state_statute']):
        cits.extend([generate_statute_citation(
            offset,
            offset + len(matches['state_statute'][0]),
            line_num,
            file_id + str(leg_count + 1),
            body_abbrev_to_full(matches['state_statute'][1]),
            matches['state_statute'][2],  # article
            numeral_to_int(matches['state_statute'][3]),  # chapter
            numeral_to_int(matches['state_statute'][4]),  # section
            # matches['state_statute'][5],  # subsection
            "",  # subsection
            str.strip(matches['state_statute'][0])  # full match text
        )])

    return cits


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
               '</citation>' \
        .format(
        cit_id,
        start_index,
        end_index,
        line_num,
        text
    )

    return citation


def generate_statute_citation(start_index, end_index, line_num, cit_id, body, article, chapter, section, subsection,
                              text):
    """Returns a citation string for a statute citation

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
               'article="{5}" ' \
               'chapter="{6}" ' \
               'section="{7}" ' \
               'subsection="{8}">' \
               '{9}' \
               '</citation>' \
        .format(
        cit_id,
        start_index,
        end_index,
        line_num,
        body,
        article,
        chapter,
        section,
        subsection or '',
        text
    )

    return citation


def find_legislations(txt, file_id):
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

            line_offset = len(line)
            legis_matches = find_legislations_in_line(line)  # get list of matches

            if legis_matches:
                # get the matches in order
                for matched_string in legis_matches:
                    match_index = line.find(matched_string)
                    offset += match_index
                    line_offset -= len(matched_string)
                    line_offset -= match_index
                    # create a citation
                    cits = generate_legislation_citations_from_string(
                        matched_string,
                        offset,
                        line_num,
                        len(legs),
                        file_id[0:] + "_"
                    )
                    offset += len(matched_string)
                    for x in cits: print(x)
                    legs.extend(cits)

                    # substr the line from start point of match to end of line
                    # this is so we don't capture only the first ref to repeated amendments
                    line = line[match_index + len(matched_string):]

            line_num = line_num + 1
            offset += line_offset
    # print(legs)
    return legs
