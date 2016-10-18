# PASA_view
<b>Description:</b><br>
<p>
This program will display IR spectra, convert from wavelength to wavenumber domaing, allow for comparisons to the USGS IR spectral library, label spectra, and save figures and spectra.</p>

<b>Operation:</b><br>
<p>
<i>Open a PASA data file:</i>
<ul>
<li>file-> Open-> Open PASA Spectrum -> navigate to file</li>
<i>Open a reference file:</i>
<li>file-> Open-> Open Reference Spectrum -> navigate to file</li>
<i>Note:</i>
<li>currently .txt, .csv, and .asc files are supported</li>
<li>files may be comma, space, or tab delimited</li>
<li>files are assumed to be in wavelength domain</li>
</ul></p>

<p>
<i>Convert spectrum from wavelength to wavenumber domain:</i><br>
<ul>
<li>click "Wavenumber" or "Wavelength" button</li>
<li>If a user-defined axis range has been selected, you will need to enter new axis values:</li>
<ul><li>1.6 µm = 6250 cm<sup>-1</sup></li>
<li>3.6 µm = 2780 cm<sup>-1</sup></li>
</ul></ul></p>

<p>
<i>Smooth Spectrum:</i><br>
<ul>
<li>applies a <a href="http://docs.scipy.org/doc/scipy-dev/reference/generated/scipy.signal.savgol_filter.html#scipy.signal.savgol_filter">Savitsky-Golay Smoothing filter</a> to the data</li>
<li>click "Smooth" button</li>
<li>enter values in dialog box for each spectrum:</li>
<li>a value of 0 for both variables will not smooth the data</li>
<li>Window Length: length of filter window</li>
<ul>
<li>must be positive odd integer</li>
<li>suggested value: 51</li>
</ul>
<li>Polynomial Order: order of polynomial to used to fit samples</li>
<ul>
<li>must be less than window length</li>
<li>suggested value: 3</li>
</ul></ul></p>

<p>
<i>Offset Spectra</i>
<ul>
<li>offsets spectrum vertically, scales spectra by multiplicative constant</li>
<li>click "Offset" button</li>
<li>enter values in dialog box for each spectrum:</li>
<li>Offset: vertical offset</li>
<li>Scale: linear scaling</li>
</ul></p>

<p>
<i>Label Peaks</i>
<ul>
<li>click "Format Label" button to change label font</li>
<li>optional: zoom in to region of interest</li>
<li>click "Label Feature" button</li>
<li>click the region of interest</li>
<li>enter the accompanying text</li>
<li>repeat for all desired areas</li>
<li>labels may be dragged to a more desirable location</li>
<li>click "Remove Labels" to remove all labels</li>
</ul></p>

<p>
<i>Define Axes</i>
<ul>
<li>click "Define Axes" button</li>
<li>enter values in dialog box for horizontal and vertical axes</li>
<ul>
<li>1.6 µm = 6250 cm<sup>-1</sup></li>
<li>3.6 µm = 2780 cm<sup>-1</sup></li>
</ul></ul></p>

<p>
<i>Legend Format</i>
<ul>
<li>click "Legend Format"</li>
<li>enter values in dialog box for spectrum name, spectrum linestyle, and legend font size</li>
<li>Linestyle uses matplotlib commands</li>
<ul>
<li>colors:</li>
<ul>
<li>k or 'black'</li>
<li>b or 'blue'</li>
<li>g or 'green'</li>
<li>r or 'red'</li>
<li>c or 'cyan'</li>
<li>m or 'magenta'</li>
<li>y or 'yellow'</li>
<li>w or 'white'</li>
</ul>
<li>linestyles:</li>
<ul>
<li>- or 'solid'</li>
<li>-- or 'dashed'</li>
<li>-. or 'dashdot'</li>
<li>: or 'dotted'</li>
<li>'None'</li>
</ul></ul></ul></p>

<p>
<i>Reset</i>
<ul>
<li>Click "Reset" to reset the plotting window and remove all stored data and variables.</li>
</ul></p>

<p>
<i>Save Figure</i>
<ul>
<li>click Save icon</li>
</ul></p>

<p>
<i>Save spectrum as ASCII file</i>
<ul>
<li>File->Export File</li>
<li>saves current spectrum (in wavelength or wavenumber domain, which ever is displayed)</li>
<li>data is stored in a two column, space-delimited format</li>
</ul></p>

<b>Future Plans:</b>
<ul>
<li>Allow user to add lines pointing to peak labels</li>
<li>Retrieve new label positions (after dragging) and overwrite values in label arrays</li>
<li>Break PASAview_main.py into modules</li>
</ul>

<b>Installation:</b>
<p>
<ul>
<li>Install Python using the <a href="http://continuum.io/downloads">Anaconda distribution</a>, which includes several useful scientific packages that will be necessary for the program to run.</li>
<li>Follow the installation instructions, select the default installation configuration.</li>
<li>Open the "Anaconda Command Prompt".</li>
<li>Type the following commands:</li></ul></p>
	conda install matplotlib
	conda install numpy
	conda install scipy

<p>
<ul>
<li>Download this github repository (<a href="https://github.com/kyleuckert/PASA_view/archive/master.zip">Download ZIP button</a>).</li>
<li>Start the program by double-clicking the PASAview_main.py file within the PASA_view folder. If this is the first time you are running a .py file, you may need to set .py to open using Python 2.7 by default:</li>
<ul>
<li>right click .py file, click "properties"</li>
<li>opens with -> change</li>
<li>browse to: Computer/C://Users/yourusername/Anaconda/python</li>
</ul></ul></p>
