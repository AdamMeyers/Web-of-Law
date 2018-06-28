import re

import roman

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
            states_dict[line.split('\t')[0].replace('. ', '.')] = line.split('\t')[1].strip()
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
    return bodies[abbrev.replace(' ', '')]


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
        document = '{} {}'.format(state, match.group(2))
        section = (match.group(4) or '').strip()
        date = match.group(5)
        doc_loc = match.group(3)
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


# def find_legislations_in_line(in_string):
#     """Return a list of strings matching all current leglislation rexps from a given line
#
#     :param in_string:
#     :return: (list<str>) A list of strings
#     """
#     if not in_string or in_string == '\n':
#         return
#
#     rexps = [
#         informal_amend_rexp,
#         const_cit_rexp,
#         federal_statute_cit_rexp,
#         state_statute_cit_rexp,
#         informal_const_rexp
#     ]
#     legs = []
#     for exp in rexps:
#         pattern = re.compile(exp)
#         matches = list(pattern.finditer(in_string))
#         if matches:
#             legs.extend(list(map(lambda x: x.group(0), matches)))
#
#     return legs


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


def generate_citation_strings_from_pseudo_cits(file_id, id_index, cits):
    def cit_convert(cit):
        if cit['type'] == 'amend_ref':
            del cit['type']
            return generate_amendment_reference(**cit)
        elif cit['type'] == 'const_cit':
            del cit['type']
            return generate_const_citation(**cit)
        elif cit['type'] == 'const_ref':
            del cit['type']
            return generate_const_reference(**cit)
        elif cit['type'] == 'state_statute' or cit['type'] == 'federal_statute':
            del cit['type']
            return generate_statute_citation(**cit)

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
                file_id.strip('\\') + "_"
            )

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
