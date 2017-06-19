import re
from wol_utilities import *
from xml.sax.saxutils import escape
from xml.sax.saxutils import unescape

quote_id = 0

def make_one_line(string):
  return(re.sub(os.linesep,' ',string))

def make_quote_output_string(start,end,string):
  global quote_id
  quote_id += 1
  out_string = "<quote"
  for attribute, value in [['local_id',quote_id],['start',start],['end',end],['string',make_one_line(wol_escape(string))]]:
    out_string += ' '+attribute+'="'+str(value)+'"'
  out_string+=('></quote>')
  return(out_string)

def find_quotes(txt_file,quotes_file):
  file_position = 0
  start_quote = False
  end_quote = False
  start = 0
  quote_pattern = re.compile('"')
  output = []
  with open(txt_file) as instream, open(quotes_file,'w') as outstream:
    big_string = instream.read()
    match = quote_pattern.search(big_string,file_position)
    while match:
      if start_quote and match:
        end = match.end()
        output.append([start,end,big_string[start:end]])
        start_quote = False
      elif match:
        start_quote = True
        start = match.start()
      file_position = match.end()
      match = quote_pattern.search(big_string,file_position)
    for start,end,string in output:
      out_string = make_quote_output_string(start,end,string)
      outstream.write(out_string+os.linesep)
    
                       
      
      
