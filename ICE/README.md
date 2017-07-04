# Overview

ICE is an Integrated Customization Environment for Information Extraction developed by Yifan He and Ralph Grishman at NYU. More information can be found at the website http://nlp.cs.nyu.edu/ice/. You can also download the original software at their website.

# Set up ICE

## Install X Server
Since ICE is GUI-based, you will need an X server to run it remotely. Please google "xserver + your operating system" to find out how to set it up. You can test whether the setup is successful by running the following commands:
```
ssh -X username@address
xclock
```
If successful, you should see a display of a clock on your local machine. The `-X` flag can be replaced by `-Y`.

## Set up the original version

Download the original software from [here](https://github.com/ivanhe/ice/releases/download/v0.2.0beta/ice-bin.zip "ice-bin.zip") (I copied the link from ICE's website). Then unzip the file and under the directory `ice-bin/`, exsecute the following command to run the software:
```
./runice.sh
```

## Set up the pre-trained version

The [ice-bin](./ice-bin) folder here contains the contents of ICE after I trained it on a corpus of 4000 legal documents, except the cache for the preprocessed documents.

The folder can also be found on the CIMS server at `/misc/proteus106/wlu/ice-bin`.

The corpus can be found at `/misc/proteus106/wlu/legal_corpus/4000/texts/`.

To run the software, download the [ice-bin](./ice-bin) folder to a CIMS server. When running it for the first time, direct to `ice-bin/` and run the following command to add the cache of the preprocessed corpus:
```
cp -r /misc/proteus106/wlu/ice-bin/cache cache
```
Then, execute the following command to run the software:
```
./runice.sh
```

ICE also contains the Java Extraction Toolkit (JET), which is a set of language analysis tools developed by Ralph Grishman. More information on JET can be found at http://cs.nyu.edu/grishman/jet/guide/Jet.html.
