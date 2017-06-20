I. Introduction

This directory is devoted to developing an annotation task. There are
several stages to this process and it is possible to augment any of the
stages as we go forward. The result can be more than one overlapping
annotation task and any number of systems for doing the tasks automatically.

Our "first" stage is the pre-processing.  It is possible that further
development of systems in later stages can be joined to this stage to
create better preprocessing.  For simplicity in this description, I
will pretend that this doesn't happen. Preprocessing includes both
preparation of the text and any type of system that can automatically
annotate. For purposes of preprocessing, a system is successful if
using the automatically created annotation saves time and/or improves
the quality of the second stage.

The "second" stage is manual annotation. We use the output of the
pre-processing stages to provide our input to our manual annotation
program or programs. To do annotation well we need a good annotation
guideline. Typically, we do some pre-processing, write an initial
guideline and have at least two people annotate the same text. We then
compare the results. If the manual annotators annotated the text in
almost the same way, the specifications are pretty good. If the
inter-annotator agreement score is low, then the specifications should
be adjusted to improve agreement and more text should be
annotated. Typically, annotation is done in rounds. First a little bit
of text is multiply annotated and then adjudicated. The differences
are discussed, the specs are updated. In each subsequent round, a
larger and larger amount of text is annotated. At each adjudication,
the specs are adjusted. After several rounds, we attempt to annotate
enough documents to enable automatic processing of the text. There are
also ways of annotating while running a system. These methods are
called "active learning".  Our initial annotation will have as its
goal to simply define a good IE task.

The "third" stage is to create an automatic annotation
system. Supervised machine learning requires the most annotated
data. As noted above, techniques such as active learning requires
somewhat less (combining the second and third stage). In addition,
manual rule systems do not require any training data, per se, although
it is normal not to use your test data to develop your rules. Finally,
there are some unsupervised (and semi-supervised) techniques, which
essentially combine manual rules and statistical methods.

II. Files

The following files are included in this directory:

README.txt -- this README file

ATTRIBUTION.dtd -- a dtd file to be used for annotation along with
Amber Stubb's Mae program
(https://github.com/amber-stubbs/mae-annotation). This assumes the
current output of run_pre_processing.py

sample_files -- a directory of: input to annotation preprocessor,
output of annotation preprocessor and one sample annotated file. Here
is a description of the file types:

.txt, .quotes, .case8 -- input to annotation preprocessor (as
      	       	      descripted in README for
      	       	      Web_of_Law_manual_rule_IE_and_citation_graph_scripts

.terms -- possible input for future versions of preprocessor

_annotate.xml -- output of preprocessor and input for Mae

AM_108713_annotate.xml -- one sample file in which I annotated 2
instances of an ATTRIBUTION relation, one of which used only existing
entities (linking a NAME with quoted text) and one relation that
required additional entity annotation, linking an instance of
legislation with a "message".

III. Annotation guidelines and future annotation

The output contains the output of many the WOL manual rules and could,
in theory be made to include more of the output. I am going to propose
a very simple, but useful initial annotation task. However, please
feel free to consider other annotation tasks, possibly modifying the
.dtd file in the process (please name your new .dtd file something
different). This initial annotation task does not use all of the
features that were added.

A. The attribution task. Individual sections of text (messages) are
attributed in legal documents to sources. These sources can be people,
organizations or documents. Mae, which was developed for TimeML,
assumes that all relations are "from" one entity "to" another. We are
adopting this way of representing relations, simply because that
allows us to use this entry program (as opposed to writing our
own). For our purposes, then, an ATTRIBUTE relation is a relation from
a source to a message.

The source usually will be something we have already automatically
annotated, but occasionally will be something we haven't. For this
reason, we may have to mark additional entities, in order to link them
as sources. For example, we can mark citations to additional
documents. The automatic annotation only chooses case
citations. However, "legislation" (laws, parts of laws, ammendments,
regulations, etc.) is also an option under the "citation" entity, as
is "other_written_document" and "other". If none of the entities
provided (citation, NAME, PROFESSION, ORGANIZATION, FAMILY,
LEGAL_ROLE) clearly fits a particular source, one can always mark it
as COMMUNICATOR, which is intended to be the generic type of source.

The message can be an existing instance of quoted text or it can be
some other text, which can be tagged as a MESSAGE, with several
sub-types. One notable subtype, mixed_quote, is intended to be a
string which contains some quoted substrings. These seem to occur a
lot in legal text.

B. Other Annotation tasks: please feel free to attempt to define
another annotation task (or another part of the same annotation
task). Our goal is to select relations that are likely to help
represent the connections between texts, connections between subject
matter and citations, reasons that a particular person or case is
being cited, and other things that might be helpful in searching
and/or understanding legal documents.  For example, coreference tasks
may be extremely helpful. Some additional pre-processing may be
needed, e.g., using the coreference between citations provided in the
.NYU_IE1 files (this includes cross-document coreference).


