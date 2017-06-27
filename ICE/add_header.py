with open('text_ids.txt', 'r') as list_in:
    for line in list_in:
        name = line.rstrip('\r\n')
        with open('converted/' + name + '.converted', 'r') as file_in:
            body = file_in.read()
            with open('converted_header/' + name + '.converted', 'w') as file_out:
                file_out.write('<DOC>\n<BODY>\n<TEXT>\n')
                file_out.write(body)
                file_out.write('</TEXT>\n</BODY>\n</DOC>')

