ICE is an Integrated Customization Environment for Information Extraction developed by Yifan He and Ralph Grishman at NYU. More information can be found at the website http://nlp.cs.nyu.edu/ice/.

This folder contains the contents of ICE after I trained it on a corpus of 4000 legal documents. The folder can also be found at
```
/misc/proteus106/wlu/ice-bin
```
The corpus can be found at 
```
/misc/proteus106/wlu/legal_corpus/4000/texts/
```
To run the system, download the contents to a CIMS server. When running it for the first time, direct to ice-bin/ and run the following command copy the cache of the processed corpus from /misc/proteus106/wlu/ice-bin/cache
```
cp /misc/proteus106/wlu/ice-bin/cache cache
```
Then, execute the following command to run the system
```
./runice.sh
```
Since ICE is GUI-based, you will need an X server to run it remotely.

ICE also contains the Java Extraction Toolkit (JET), which is a set of language analysis tools developed by Ralph Grishman. More information on JET can be found at http://cs.nyu.edu/grishman/jet/guide/Jet.html.
