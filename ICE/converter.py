"""This script uses the annotations for citations in NYU_IE1 files to
replace each occurrence of a citation in the original legal document by the token 'LECI'.
Character offsets are preserved by padding spaces after the token to match the original length of the citation.
No changes are made when the string of the citation in the annotation does not match the one in the original document.
And all the mismatches are saved in a file called "mismatches.txt" along with the converted outputs.
"""

import re
import sys
from codecs import open


class Citation:
    def __init__(self, citation, start, end):
        """
        Parameters
        ----------
        citation : str
            The string of the citation in the text.
        start : int
            The starting position of the citation in the text.
        end : int
            The ending position of the citation in the text.
        """
        self.citation = citation
        self.start = start
        self.end = end


def get_cite_obj(line):
    """Create a Citation object using an annotation.
    Parameters
    ----------
    line : str
        The entry of the annotation for a citation.
    Returns
    -------
    Citation
        A Citation object created for the citation in the annotation.
    """
    citation = re.search('(?<=\>)[^\<]+', line).group(0).replace('&amp;', '&').replace('&quot;', '\"').encode('utf-8')
    start = int(re.search('(?<=start=\")[^\"]+', line).group(0))
    end = int(re.search('(?<=end=\")[^\"]+', line).group(0))
    return Citation(citation, start, end)


def read_annotations(text_id, paths):
    """Given an annotation file, create a list of Citation objects according to the annotations for citations.
    Parameters
    ----------
    text_id : str
        The name of the annotation file.
    Returns
    -------
    list of Citation
        A list of Citation objects created using the annotation file.
    """
    list_citation = []
    with open(paths['annotations'] + '/' + text_id + '.NYU_IE1', 'r', encoding='utf8') as annotations:
        for line in annotations:
            if line.startswith('<CITATION'):
                list_citation.append(get_cite_obj(line))
    return list_citation


def process_text(text_id, paths, add_tags):
    """Convert each occurrence of a citation in a file to the token 'LECI'.
    Parameters
    ----------
    text_id : str
        The name of the file.
    add_tags : bool
        A flag to indicate whether to add special tags required by JET to the output file.
    Returns
    -------
    list of tuple of str
        A list of the strings of the citations in the annotation that fail to match those in the text.
    """
    list_annotation = read_annotations(text_id, paths)
    with open(paths['texts'] + '/' + text_id + '.txt', 'r', encoding='utf8') as file_in:
        text = file_in.read()
    mismatch = []
    with open(paths['output'] + '/' + text_id + '.converted', 'w', encoding='utf8') as output:
        if add_tags:
            output.write('<DOC>\n<BODY>\n<TEXT>\n')
        last_end = 0
        for ann in list_annotation:
            output.write(text[last_end: ann.start])
            matched = text[ann.start: ann.end].replace('\n', '').encode('utf-8')
            if not ann.citation.replace(' ', '') == matched.replace(' ', ''):
                # If the string of the citation in the annotation fails to match that in the text,
                # the text is left unchanged.
                mismatch.append((ann, matched))
                output.write(matched.decode('utf-8'))
            else:
                # Pad spaces after the token to preserve character offsets
                output.write('LECI' + ' '*(len(matched) - 4))
            last_end = ann.end
        output.write(text[last_end:])
        if add_tags:
            output.write('</TEXT>\n</BODY>\n</DOC>')
    return mismatch


def parse_args():
    """Parse the input arguments
    Returns
    -------
    dict
        A dictionary containing all the paths needed by the script.
    bool
        A flag to indicate whether to add the special tags required by JET.
    """
    if len(sys.argv) < 5:
        print "Error: Not enough input arguments.\n" \
              "Usage:\n" \
              " Arg1: Path to the file that contains the filenames of the documents to be processed.\n" \
              " Arg2: Path to the directory that contains the files to be processed.\n" \
              " Arg3: Path to the directory that contains the NYU_IE1 annotation files.\n" \
              " Arg4: Path to the output directory.\n" \
              " Arg5 (optional): A flag to indicate whether to add the special tags required by JET.\n"
        exit(0)

    paths = dict()
    add_tags = False
    paths['text_ids'], paths['texts'], paths['annotations'], paths['output'] = sys.argv[1:5]
    if len(sys.argv) > 5:
        add_tags = True

    return paths, add_tags


def main():
    paths, add_tags = parse_args()

    with open(paths['text_ids'], 'r') as file_text_id:
        list_text_id = [line.rstrip('\n') for line in file_text_id]

    count = 0
    progress = -1
    total_line = len(list_text_id)
    with open(paths['output'] + '/' + 'mismatches.txt', 'w') as output:
        for text_id in list_text_id:
            count += 1
            if count * 100 / total_line > progress:
                progress = count * 100 / total_line
                print '\r[%-50s] %d%%' % ('=' * (progress / 2), progress),

            mismatch = process_text(text_id, paths, add_tags)

            for item in mismatch:
                ann, matched = item
                output.write('Document id: ' + text_id + '\n')
                output.write('Start: %d; End: %d; \nCitation: %s\nMatched: %s' % (
                    ann.start, ann.end, ann.citation, matched))
                output.write('\n\n')


if __name__ == '__main__':
    main()
