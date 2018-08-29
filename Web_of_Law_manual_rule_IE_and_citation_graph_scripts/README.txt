The programs described here were authored by Adam Meyers, Halley
Young, Vlad Tyshkevich, John Ortega and Rayat M Rahman.

This code is licensed under an Apache 2.0 license
(https://www.apache.org/licenses/LICENSE-2.0). The current version is
a development version, not not really ready for release. We are
developing this software as part of the Web of Law Project at NYU.

I. Files

1. Documentation

1.1 README.txt  --- This file

2. Python Code:

2.0.1 Required Package -- You must install Court Listener's REPORTERS
package (which seems to require Python 3.5 or higher). 

2.1 Utility python files (files with commands useful to multiple programs)

2.1.1 wol_utilities.py

2.1.2 roman.py  -- probably should be incorporated into wol_utilities.py

2.2 Reference Files (files containing information for lookup)

2.2.1 citation_tables.py  (this is the file that imports the REPORTERS package)
2.2.2 discourse_words.txt
2.2.3 POS.dict
2.2.4 relational.dict
2.2.5 time_names.dict
2.2.6 court_listener_directory_name_dict.py
2.2.7 district_courts.csv
2.2.8 STATES.dict

2.3 Preprocessing code (See 2.6.1 for corresponding run files).
2.3.1 encoding_fix.py
2.3.2 make_txt_file_from_json2.py
2.3.3 pre_process_annotation.py (pre-processing for annotation with Mae)

2.4 Rule-based Entity and Relation Tagging (See 2.6.2 for corresponding run files)
2.4.1 find_case_citations5.py --> run_citations_and_simple_relations_directory.py and 
      run_citations_and_simple_relations_file.py
2.4.2 find_quotes.py
2.4.3 find_legislations.py --> run_legislations.py and run_legislations_on_dir.py

2.5 Constructing Citation Graph (See 2.6.3 for corresponding run files)
2.5.1 get_elements.py
2.5.2 makecsv3.py
2.5.3 coreference3.py

2.6 Run Files

These are all set up to run the above programs in one of two ways:

A. File + arguments (if made executable and python3 variable is set properly)
B. python3 File + arguments (otherwise)

2.6.1 Preprocessing: Taking initial files from Court Listener and creating Web of Law input file formats

2.6.1.1 run_encoding_fix_on_directory.py
	2 arguments: 
	  	     Input Directory containing corrupted json files
		     Output Directory to put corrected json files
        Example run from command line: 
		run_encoding_fix_on_directory.py test/original_files test/fixed_files

2.6.1.2 run_make_txt_file_from_json2_one_directory.py
        1 argument:  DIRECTORY containing (corrected) json files
	Output = files in the same directory of file types .txt and .html-list
	        The .txt files are the input to future IE programs. This is based on
		    the best text field as per instructions from M. Lissner of Court Listener
		The .html-list is offset XML pointing to the txt file, based on that
		    same json text field. This can be combined with or compared to other 
		    annotation created from the .txt file, including but not limited to
		    annotation that our system creates.	
       	Example run from command line:
		run_make_txt_file_from_json2_one_directory.py test/fixed_files

2.6.1.3 run_make_txt_file_from_json2_one_file.py

        1 argument: a json file
	Ouput = corresponding .txt and .html-list files
	     The description is the same as 2.6.1, except only
	     these are created for one file is created instead
	     of the whole directory of files.
        Example run from command line:
		run_make_txt_file_from_json2_one_file.py test/fixed_files/108713.json

2.6.2 Initial Entity and Relation Files: Identifying Entities and
Relations using manual rules. These are limited to surface patterns
using combinations of dictionaries, regular expressions and other
similar methods. Relations are limited to those in close proximity,
linked either by: strict adjacency or part/whole (prenominal
modification, apposition, substrings, ...).

2.6.2.1 run_citations_and_simple_relations_directory.py
	1 argument: Directory containing files output from programs in 2.6.1.2
	Output: .case9 files are added to that same directory
	Example run from command line:
		run_citations_and_simple_relations_directory.py test/fixed_files

2.6.2.2 run_citations_and_simple_relations_file.py
	1 argument: filename from 2.6.1.3, but no file extension
	Output: corresponding .case9 file
	Example run from command line:
		run_citations_and_simple_relations_file.py test/fixed_files/108713

2.6.2.3 run_find_quotes.py
	1 argument: a directory
	Output: makes one .quotes file for each .txt file in the directory
	Example run from command line: 
		run_find_quotes test/fixed_files

2.6.2.4 run_legislations.py
	1 Argument filename from 2.6.1.3, but no file extension
	Output: corresponding .legislation9 file
	Example run from command line:
		run_legislations.py test/fixed_files/108713

2.6.2.5 run_legislations_on_dir.py
	1 argument: Directory containing files output from programs in 2.6.1.2
	Output: .legislation9 files are added to that same directory
	Example run from command line:
		run_legislations_on_dir.py test/fixed_files

2.6.3 Citation Graph Files: These programs uses the json files and the
various files created from previous stages to generate a citation
graph and which updates existing citations to include unique
identifiers and references to original files (making it possible to
look up files from citations).

2.6.3.1 run_citation_graph_on_directory_list.py
      2 arguments:
      	* A file listing directories to be used as input files, each 
	  directory should contain files processed in 2.6.2.
	* The prefix of the name of output files generated by this program
     Output:
	PREFIX_initial_table_file.tsv
		-- Lists each case file, along with information about 
		   citations pointing to that file
	PREFIX_global_table_file.tsv
		-- Lists each case citation cited anywhere in the
                   input, along with a global identifier and other
                   info, regardless of whether the citation points
                   back to any of the input files. Global IDs are 
		   floating point numbers. Global IDs with the same
		   floor refer to the same case, e.g., 
		   100.001 and 100.002 are coreferential (loosely 
		   speaking).
	PREFIX.citation_graph
		-- Lists each unique whole number (the floor of 
		   the global id), along with a list of global IDs
		   for the citations mentioned in that document (including
		   citations to the document itself).
	One .NYU_IE1 file for each case8 file in the input directories. 
	    	-- These files are elaborations of the .case8 files 
		   to include unique identifiers and pointers to files
		   corresponding ot the citations (when they exist).
        Example run from command line:
	run_citation_graph_on_directory_list.py directory_list test_output
	    Note that directory_list is a text file 
	    containing a single directory: test/fixed_files

2.6.4 Files for pre-processing of files for manual annotation. The
      purpose of this file is to create input to Mae, so annotation
      can be manually corrected.  Additional code may be needed to
      complete the annotation process. Changes to the task, changes to
      the annotation procedure, among other factors may cause the
      processing to change.  In addition, post-processors may be
      necessary to create the equivalent of the input files. This
      program is in a testing stage. It has not been run on the entire
      scotus corpus, just on a few test files. To run on the current
      test directory, the command is:

      run_pre_processing.py test/fixed_files


**************************************************************************
Note about the full Scotus Run

Similar runs were done on all 64K SCOTUS (Supreme Court) files and it
took approximately 1/2 a day to run.

The output files are:
     -- scotus.citation_graph
     -- scotus_global_table.tsv
     -- scotus_initial_table.tsv
     -- and the various files provided on the web of law website

We eventually plan to run the system on the entire Court Listener
   corpus -- The remaining tar.gz files are at NYU (for students in
   the Web of Law Project) in
   /home/meyers/Legal_Texts/corpus/originals/version2/

The current run does not include legislation in the citation graph,
but future versions should do so.

***************************************************************************

III. Notes about Citations to Legal Decisions

There are several types of citations to cases that we currently cover.
The most common types are listed, along with some of their
coreferential properties.

    A) Standard citations, listing the court reporter, the volume number
    and page number.  These are mostly unambiguous.  However, we have a
    found some cases where multiple cases are on the same page. This is
    typically because the court denied the request for a hearing or
    something like that. So in these cases, a number of unimportant cases
    can be listed as being coreferential with each other.
    
    B) Citations of the form X v Y, where two parties are in opposition
    with each other. These can be ambiguous simply because people can have
    the same last names. We use several factors to disambiguate, chief
    among them being: coreference with standard citations and the file
    names assigned by court listener to distinct files.  For cases, not
    associated with particular filenames, we may be incorrectly merging
    files together or splitting them apart. We have not evaluated these
    yet.
    
    C) Files with other names. Typically, these include names that have
    certain key phrases in them, e.g., "Ex parte" or "X Y Z cases".
    However, some names can be quite generic, e.g., "The" (capitalized)
    followed by some capitalized words. Consequently, we may currently be
    overgenerating or undergenerating these case names. We have not
    evaluated this yet. These may also be ambiguous in a similar way to
    the X v Y variety.

We currently have grouped together citations that we believe are
coreferential by means of a numbering system. Each distinct citation
has a different three decimal place number associated
it. Coreferential items begin with the same whole number, e.g., 55.001
and 55.002 would label coreferential citations.  Our use of
"corefence" is somewhat loose.  It includes: different citations by
virtue of minor spelling differences; citations that refer to
different stages of the same case (hopefully including the final
verdict or the binding opinion); and cases that have been grouped
together -- while originally separate cases, they were later merged
into one case and a decision was given to the whole set.

IV. Notes about citations to legislation

Several patterns are used to capture legislation and the result is a
somewhat diverse collection. It is also possible that some of the
captured citations actually refer back to documents that do not have
the status of a law, but are some type of publication.

Patterns/Legislation types include:

    A. The US constitution or Amendments thereof, e.g., "Eighteenth
       Amendment"
    B. Acts, Rules or Treaties (and sections thereof), e.g., "§ 35 of
       the Porto Rican act of April 12, 1900, 31 Stat. 85"
    C. Government regulations, e.g., "65 I.C.C. 36" (regulation of the 
       Interstate Commerse Commission)
    D. Other Statutes, e.g., "Mississippi Laws 1930"

V. Notes about Manual Annotation

1) There will be a separate directory having to do with manual
annotation, including a README.

2) Note that due to idiosyncrasies of the MAE program, and possibly of
XML in general, the quotations posed a problem. By beginning and
ending with quotation marks, quoted text complicates recognition of
xml attributes. Given a feature value pair: feature=""abcdefg hijk"",
it is necessary to choose the correct instance of a quotation marks
(") as delimiters. To simplify this problem, the pre-processor
substitutes the inside quotation mark (") with the following character
(«). Post-processing should be prepared to handle this character
correctly (e.g., subsituting a "; or substituting a &quot; as
appropriate).

