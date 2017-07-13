<p>This is the README file for Ice, a rapid information extraction customizer.</p>

<p>Ice is licensed under the Apache 2.0 license.</p>

<h1>Running Ice</h1>

<p>The easiest way to use Ice is to use the binary distribution.</p>

<p>To use the binary distribution, download the binary distribution and unzip the package. In <em>runice.sh</em>, point both $ICE_HOME
and $ICE_LIB_HOME to directory of the binary distribution. Both variables are set to . by default.</p>

<p>Then, from the working directory, run</p>

<pre><code>./runice.sh
</code></pre>

<h1>Running Ice Tagger</h1>

<p>Ice bundles a relation tagger based on Jet, which tags mentions of relations in text files, using
the models that you build with Ice. Note that before the Ice tagger can find the relations,
you have to use <em>Export</em> in Ice to export them to the underlying Jet tagger.</p>

<p>To run the tagger, from the working directory, run</p>

<pre><code>./runtagger.sh propertyFile txtFileList apfFileList
</code></pre>

<p>where <em>propertyFile</em> is the Jet properties file. We suggest that you use <em>tagprops</em> that is delivered
 with this package. If you are familiar with Jet and Ice, you can use your own properties file too.
 <em>txtFileList</em> are the list of text input files, and <em>apfFileList</em> is the list of output files in Ace apf
 format. Both file lists assume the "one-file-name-per-line" format and should have the same length. The
 output file corresponds to the input file at the same line number.</p>

<h1>Building and Running Ice from Source</h1>

<p>We assume that you have git and maven installed on your system.</p>

<h2>Build</h2>

<p>Please run:</p>

<pre><code>mvn package
</code></pre>

<p>If everything works, you should find
ICE-0.2.0-jar-with-dependencies.jar (the fatjar), and ICE-0.2.0.jar in
target/</p>

<h2>Preparing models</h2>

<p>Ice relies on Jet and its models. We provide the Jet binary and necessary models in the
binary distribution. However, if you are building from source, you might also want to
obtain Jet from: <a href="http://cs.nyu.edu/grishman/jet/jet.html">http://cs.nyu.edu/grishman/jet/jet.html</a></p>

<p>The current version of Ice assumes that it is run from a "working directory", where three 
Jet property files are located: <em>props</em>, <em>parseprops</em>, and <em>onomaprops</em>. These three files 
tell Ice where models for Jet are located. These files are released together with the 
Java source code in the <code>src/props</code> directory.</p>

<p>In theory, Jet model files can sit anywhere. However, to use the property files directly, 
you can copy <code>data/</code> and <code>acedata/</code> directories from Jet into the working directory.</p>

<p>In addition, Ice itself uses two configuration files: <em>ice.yml</em> and <em>iceprops</em>, which should be 
put in the working directory as well. </p>

<p>After these steps, the working directory we have prepared will look like this:</p>

<pre><code>working_dir/
    props - Jet property file 1
    parseprops - Jet property file 2
    onomaprops - Jet property file 3
    ice.yml - Ice configuration file 1
    iceprops - Ice configuration file 2
    data/ - model files, including parseModel.gz
    acedata/ - model files
</code></pre>

<p>With these files, we should be ready to go. </p>

<h2>Starting the GUI</h2>

<p>The easiest way to run Ice is to run from the working directory we prepared in the previous section.</p>

<p>Copy <em>src/scripts/runice.sh</em> to the working directory. In <em>runice.sh</em>, point $ICE_HOME to 
the directory containing ICE-0.2.0-jar-with-dependencies.jar (target/), and
$ICE_LIB_HOME to the directory containing Jet-1.8.0.11-ICE-jar-with-dependencies.jar (lib/).</p>

<p>Then, from the working directory, run</p>

<pre><code>./runice.sh
</code></pre>

<h1>User Manual</h1>

<p>Please refer to <a href="docs/iceman.md">iceman</a> for usage.</p>
