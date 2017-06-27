import re, json
from codecs import open


class Citation:
    def __init__(self, citation, cite_id, party1, party2, name, start, end, line_num):
        self.citation = citation
        self.cite_id = cite_id
        self.party1 = party1
        self.party2 = party2
        self.name = name
        self.start = start
        self.end = end
        self.line_num = line_num


def get_cite_obj(line):
    citation = re.search("(?<=\>)[^\<]+", line).group(0).replace("&amp;", "&").replace("&quot;", "\"").encode('utf-8')
    cite_id = "case" + re.search("(?<=citation_global_level_id=\")[^\"]+", line).group(0).split(".")[0]
    try:
        party1 = re.search("(?<=party1=\")[^\"]+", line).group(0)
        party2 = re.search("(?<=party2=\")[^\"]+", line).group(0)
    except AttributeError:
        party1 = "null"
        party2 = "null"
    try:
        name = re.search("(?<=name=\")[^\"]+", line).group(0)
    except AttributeError:
        name = "null"
    start = int(re.search("(?<=start=\")[^\"]+", line).group(0))
    end = int(re.search("(?<=end=\")[^\"]+", line).group(0))
    line_num = int(re.search("(?<=line=\")[^\"]+", line).group(0)) - 1
    return Citation(citation, cite_id, party1, party2, name, start, end, line_num)


def read_annotations(text_id):
    list_annotation = []
    with open("NYU_IE1/" + text_id + ".NYU_IE1", "r", encoding="utf8") as annotations:
        # annotations = input.read()
        for line in annotations:
            if line.startswith("<CITATION"):
                list_annotation.append(get_cite_obj(line))
    return list_annotation


def process_text(text_id, if_index):
    list_annotation = read_annotations(text_id)
    with open("texts/" + text_id + ".txt", "r", encoding="utf8") as input:
        text = input.read()
    mismatch = []
    index = 0
    with open("converted/" + text_id + ".converted", "w", encoding="utf8") as output:
        output.write('<DOC>\n<BODY>\n<TEXT>\n')
        last_end = 0
        for ann in list_annotation:
            output.write(text[last_end: ann.start])
            matched = text[ann.start: ann.end].replace("\n", "").encode('utf-8')
            if not ann.citation.replace(" ", "") == matched.replace(" ", ""):
                mismatch.append((ann, matched))
                output.write(matched.decode("utf-8"))
            else:
                if if_index:
                    output.write("LEGALCITATION{}".format(index))
                else:
                    output.write("LEGALCITATION")
            last_end = ann.end
            index += 1
        output.write(text[last_end:])
        output.write('</TEXT>\n</BODY>\n</DOC>')
    return mismatch, index


def main():
    if_index = False

    with open("text_ids.txt", "r") as file_text_id:
        list_text_id = [line.rstrip("\n") for line in file_text_id]
    # list_text_id = ["99101"]

    count = 0
    progress = -1
    total_line = len(list_text_id)
    max_index = 0
    with open("mismatches.txt", "w") as output:
        for text_id in list_text_id:
            count += 1
            if count * 100 / total_line > progress:
                progress = count * 100 / total_line
                print "\r[%-50s] %d%%" % ("=" * (progress / 2), progress),

            mismatch, index = process_text(text_id, if_index)

            if index > max_index:
                max_index = index

            for item in mismatch:
                ann, matched = item
                output.write("Document id: {}\n".format(text_id))
                output.write("Start: {}; End: {}; \nCitation: {}\nMatched: {}".format(
                    ann.start, ann.end, ann.citation, matched))
                output.write("\n\n")

        output.write("max index = {}\n".format(max_index))
    # for text_id in list_text_id:
    #     mismatch = process_text(text_id)


if __name__ == "__main__":
    main()
