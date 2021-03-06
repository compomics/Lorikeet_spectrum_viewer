import sys
import os
import numpy as np


htmlpage = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
 <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    
    <title>Lorikeet Spectrum Viewer</title>
    
    <!--[if IE]><script language="javascript" type="text/javascript" src="../js/excanvas.min.js"></script><![endif]-->
    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>
    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.4/jquery-ui.min.js"></script>
    <script type="text/javascript" src="../js/jquery.flot.js"></script>
    <script type="text/javascript" src="../js/jquery.flot.selection.js"></script>
    
    <script type="text/javascript" src="../js/specview.js"></script>
    <script type="text/javascript" src="../js/peptide.js"></script>
    <script type="text/javascript" src="../js/aminoacid.js"></script>
    <script type="text/javascript" src="../js/ion.js"></script>
    
    <link REL="stylesheet" TYPE="text/css" HREF="../css/lorikeet.css">
    
</head>

<body>

<h1>Lorikeet Plugin Example</h1>

<!-- PLACE HOLDER DIV FOR THE SPECTRUM -->
<div id="lorikeet1"></div>

<script type="text/javascript">

$(document).ready(function () {

	/* render the spectrum with the given options */
	$("#lorikeet1").specview({sequence: sequence1, 
								charge: charge,
								massError: 0.02,
								precursorMz: precursorMz,
								precursorMz: 1012.1,
								variableMods: varMods, 
								//ctermMod: ctermMod,
								peaks: peaks
								});	
});

'''

#command line arguments:
#- modifications file
#- spectrum file
- #spectrum title
- #sequence


#read modifications
mods = {}
with open(sys.argv[1])  as f:
	for row in f:
		l = row.rstrip().split('=')[1].split(',')
		mods[l[0].lower()] = float(l[1])

#fast search of spectrum title in spectrum file
#!!!! you might have to play with the grep string....
command = 'grep -B 1 -A 5000 "%s" %s > tmpout' % (sys.argv[3],sys.argv[2])
os.system(command)

# get peaks
msms_map1 = None
msms = []
peaks = []
f = open("tmpout")
skip = False
while (1):
	rows = f.readlines(50000)
	if not rows: break
	for row in rows:
		if skip:
			if row[:10] == "BEGIN IONS":
				skip = False
			else:
				continue
		row = row.rstrip()
		if row == "": continue
		if row[:5] == "TITLE":
			title = row[6:]
		elif row[0].isdigit():
			tmp = row.split()
			msms.append(float(tmp[0]))
			peaks.append(float(tmp[1]))
		elif row[:10] == "BEGIN IONS":
			msms = []
			peaks = []
		elif row[:6] == "CHARGE":
			charge = row[7:9].replace("+","")
		elif row[:7] == "PEPMASS":
			parent_mz = row[8:].split()[0]
		elif row[:8] == "END IONS":
			buf = "[" 
			for m,p in zip(msms,peaks):
				 buf += "[%f,%f]," % (m,p)
			buf = buf[:-1]+']'
			msms_map1 = buf
			break
	break

#prepare sequence for plotting
seq = sys.argv[4]
ntermmod = 0
if seq.startswith('('):
	tmp = seq.split(')')
	ntermmod = mods[tmp[0].replace('(','')]
	seq = tmp[1]
mod = -1
modpos = -1	
modamino = ''
modmz = -1
for m in mods:
	if m in seq:
		mod = m
		modmz = mods[m]
		tmp = seq.split(m)
		modpos = len(tmp[0])+1
		modamino = tmp[1][0]
		seq = tmp[0] + tmp[1]
			
with open(sys.argv[4]+'.html','w') as f:
	f.write(htmlpage+'\n')
	f.write('var sequence1 = "%s";\n'%seq)
	f.write('var peaks = %s;\n'%msms_map1)
	f.write('var charge = %s;\n'%charge)
	f.write('var precursorMz = %s;\n'%parent_mz)
	f.write('var varMods = [];\n')
	if mod != -1:
		f.write("varMods[0] = {index: %i, modMass: %f, aminoAcid: '%s'}\n"%(modpos,modmz,modamino))
	f.write('</script></body></html>\n')

command = "mv %s.html UWPR-Lorikeet-4bd48a5/html/" % sys.argv[4]
os.system(command)
command = "firefox UWPR-Lorikeet-4bd48a5/html/%s.html" % sys.argv[4]
os.system(command)
