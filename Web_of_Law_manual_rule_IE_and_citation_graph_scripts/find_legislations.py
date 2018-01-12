import re

# Captures amendments to the US constitution
# TODO: capture references to Amendments as antecedents from later, proximal references like
#   "from the Amendment [mentioned earlier]"

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
                              '(?:{1})'\
    .format(ordinal_rexp, amend_rexp)

# TODO: rexp for a formal citation of the amendments
formal_amend_rexp = ''


def capture_informal_amendments(in_string):
    """Returns list of strings matching the informal amendments regex in given string

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


def find_amendments_in_line(in_string):
    """Returns list of strings matching the natural amendment rexp

    Each member is the full matched string
    :param in_string: line to search within
    :return: list of Strings
    """
    full_amend_pattern = re.compile(informal_amend_rexp)
    amend_matches = list(full_amend_pattern.finditer(in_string))
    if amend_matches:
        return list(map(lambda x: x.group(0), amend_matches))  # return only the full string of each match


def ordinal_to_number(ordinal_string):
    """Returns numerical value of given ordinal string

    :param ordinal_string:
    :return: the numerical value of the ordinal
    """
    return ordinal_variants[ordinal_string]


def generate_amendment_citations_from_string(in_string, offset, line_num, leg_count, file_id, ):
    """Returns an array of citation strings from a given string of natural references to amendments

    :param in_string: string that matches natural amendment format
    :param offset: byte offset in file in_string starts from
    :param line_num: line number in file
    :param leg_count: index of the current legislation citation created from this file
    :param file_id: id of the file being read
    :return: list of citation strings
    """
    matches = capture_informal_amendments(in_string)
    return list(map(lambda x: generate_amendment_citation(
        offset,
        offset + len(matches[0]),
        line_num,
        file_id + str(leg_count + matches.index(x)),
        ordinal_to_number(x),
        str.strip(matches[0])
    ), matches[1:]))


def generate_amendment_citation(
        start_index,
        end_index,
        line_num,
        cit_id,
        amend_num,
        text):
    """Return a citation string based on given data

    :param start_index: (int) Byte offset of text from beginning of file
    :param end_index: (int) end of text
    :param line_num: (int) line number from read file
    :param cit_id: (int) the id num of this citation
    :param amend_num: (int) the number of the amendment being referred to
    :param text: (str) the text holding the amendment reference
    :return: (str) the citation string in XML style
    """

    citation = '<citation ' \
               'id="{0}" ' \
               'entry_type="amendment" ' \
               'start="{1}" ' \
               'end="{2}" ' \
               'line="{3}" ' \
               'amendment="{4}>' \
               '{5}' \
               '</citation>' \
        .format(
            cit_id,
            start_index,
            end_index,
            line_num,
            amend_num,
            text
        )

    return citation


def find_legislations(txt, case8, file_id):
    legs = []
    with open(txt) as instream:

        offset = 0
        line_num = 1

        for line in instream:

            line_offset = len(line)
            amendment_matches = find_amendments_in_line(line)  # get list of matches

            if amendment_matches:
                # get the matches in order
                for matched_string in amendment_matches:
                    match_index = line.find(matched_string)
                    offset += match_index
                    line_offset -= len(matched_string)
                    line_offset -= match_index
                    # create a citation
                    amendment_cits = generate_amendment_citations_from_string(
                            matched_string,
                            offset,
                            line_num,
                            len(legs),
                            file_id[0:] + "_"
                    )
                    offset += len(matched_string)
                    for x in amendment_cits: print(x)
                    legs.extend(amendment_cits)

                    # substr the line from start point of match to end of line
                    # this is so we don't capture only the first ref to repeated amendments
                    line = line[match_index+len(matched_string):]

            line_num = line_num + 1
            offset += line_offset
    # print(legs)
    return legs
