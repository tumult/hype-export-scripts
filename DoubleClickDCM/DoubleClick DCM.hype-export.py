#!/usr/bin/python

import argparse
import json
import sys
import distutils.util
import os

# update info
current_script_version = 1
version_info_url = "http://static.tumult.com/hype/export-scripts/DoubleClickDCM/latest_script_version.txt" # only returns a version number
download_url = "http://tumult.com/hype/export-scripts/DoubleClickDCM/" # gives a user info to download and install
minimum_update_check_duration_in_seconds = 60 * 60 * 24 # once a day
defaults_bundle_identifier = "com.tumult.Hype2.hype-export.DoubleClickDCM"

# html insertions
insert_at_head_start = """
	<meta name="ad.size" content="width=${width},height=${height}">
	<script>
		window.clickTag = "${clickTag}";
	</script>
	<script src="https://s0.2mdn.net/ads/studio/Enabler.js"></script>
	${rushEventsForPreview}
"""

insert_at_head_end = """
	<script>
	
	(function () {
		
		var thisHypeDocument = null;
	
		function preInit() {
			if (Enabler.isInitialized()) {
				init();
			} else {
				Enabler.addEventListener(studio.events.StudioEvent.INIT, init);
			}
		}
	
		function init() {
			// Polite loading
			if (Enabler.isVisible()) {
				show();
			} else {
				Enabler.addEventListener(studio.events.StudioEvent.VISIBLE, show);
			}
		}
	
		function show() {
			if(thisHypeDocument != null) {
				thisHypeDocument.showSceneNamed(thisHypeDocument.sceneNames()[0]);
			}
		}
	
		function hypeDocumentLoadCallback(hypeDocument, element, event) {
			thisHypeDocument = hypeDocument;
			if(!Enabler.isInitialized() || !Enabler.isVisible()) {
				// don't load the Hype document until DoubleClick Enabler has loaded and is visible
				return false;
			} 
			return true;
		}

		if("HYPE_eventListeners" in window === false) {
			window.HYPE_eventListeners = Array();
		}
		window.HYPE_eventListeners.push({"type":"HypeDocumentLoad", "callback":hypeDocumentLoadCallback});
	
		window.addEventListener('load', preInit);

	})();
	
	function hypeAdExit() {
		window.open(window.clickTag, "_blank");
	}
	
	</script>
"""

insert_at_body_start = ""
insert_at_body_end = ""

class HypeURLType:
	Unknown = 0
	HypeJS = 1
	Resource = 2
	Link = 3
	ResourcesFolder = 4

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--get_options', action='store_true')

	parser.add_argument('--replace_url')
	parser.add_argument('--url_type')
	parser.add_argument('--is_reference', default="False")

	parser.add_argument('--modify_staging_path')
	parser.add_argument('--destination_path')
	parser.add_argument('--html_filename')
	parser.add_argument('--main_container_width')
	parser.add_argument('--main_container_height')
	parser.add_argument('--is_preview', default="False")

	parser.add_argument('--check_for_updates', action='store_true')

	#custom defined arguments
	parser.add_argument('--clickTag', default="")
	
	args, unknown = parser.parse_known_args()
	

	## --get_options
	##		return arguments to be presented in the Hype UI as a dictionary:
	##		'export_options' is a dictionary of key/value pairs that make modifications to Hype's export/preview system. Some useful ones:
	##			'exportShouldInlineHypeJS' : boolean
	##			'exportShouldInlineDocumentLoader' : boolean
	##			'exportShouldUseExternalRuntime' : boolean
	##			'exportExternalRuntimeURL' : string
	##			'exportShouldSaveHTMLFile' : boolean
	##			'indexTitle' : string
	##			'exportShouldBustBrowserCaching' : boolean
	##			'exportShouldIncludeTextContents' : boolean
	##			'exportShouldIncludePIE' : boolean
	##			'exportSupportInternetExplorer6789' : boolean
	##			'initialSceneIndex' : integer
	##		'save_options' is a dictionary of key/value pairs that for determining when/how to export. valid keys:
	##			'file_extension' : the final extension when exported (ex. "zip")
	##			'allows_export' : should show up in the File > Export as HTML5 menu and Advanced Export
	##			'allows_preview' : should show up in the Preview menu, if so --is_preview True is passed into the --modify_staging_path call
	##		'document_arguments' should be an array of keys, these will be passed to subsequent calls via --key value
	##		'extra_actions' should be an array of dictionaries
	##			'label': string that is the user presented name
	##			'function': javascript function to call if this action is triggered, just the name of it
	##			'arguments': array of dictionaries that represent arguments passed into the function
	##				'label': string that is presented to Hype UI
	##				'type': string that is either "String" (will be quoted and escaped) or "Expression" (passed directly to function argument as-is)
	if args.get_options:		
		def export_options():
			return {
				"exportShouldInlineHypeJS" : True,
				"exportShouldInlineDocumentLoader" : True,
				"exportShouldUseExternalRuntime" : False,
				#"exportExternalRuntimeURL" : "",
				"exportShouldSaveHTMLFile" : True,
				"exportShouldNameAsIndexDotHTML" : True,
				#"indexTitle" : "",
				"exportShouldBustBrowserCaching" : False,
				"exportShouldIncludeTextContents" : False,
				"exportShouldIncludePIE" : False,
				"exportSupportInternetExplorer6789" : False,
				#"initialSceneIndex" : 0,
			}

		def save_options():
			return {
				"file_extension" : "zip",
				"allows_export" : True,
				"allows_preview" : True,
			}

		def document_arguments():
			return ["clickTag"];
	
		def extra_actions():
			return [
				{"label" : "Exit via clickTag", "function" : "hypeAdExit"},
			]
		
		options = {
			"export_options" : export_options(),
			"save_options" : save_options(),
			"document_arguments" : document_arguments(),
			"extra_actions" : extra_actions(),
		}
	
		print json.dumps({"result" : options})
		sys.exit(0)


	## --replace_url [url] --url_type [HypeURLType] --is_reference [True|False]
	##		return a dictionary with "url" and "is_reference" keys
	##		if HypeURLType.ResourcesFolder, you can set the url to "." so there is no .hyperesources folder and everything
	##		is placed nex to the .html file
	elif args.replace_url != None:
		url_info = {}
		url_info['is_reference'] = bool(distutils.util.strtobool(args.is_reference))
		
		if int(args.url_type) == HypeURLType.ResourcesFolder:
			url_info['url'] = "."
		else:
			url_info['url'] = args.replace_url
		
		print json.dumps({"result" : url_info})
		sys.exit(0)


	## --modify_staging_path [filepath] --destination_path [filepath] --html_filename [filename.html] --main_container_width [number] --main_container_height [number] --is_preview [True|False]
	##		return True if you moved successfully to the destination_path, otherwise don't return anything and Hype will make the move
	##		make any changes you'd like before the save is complete
	##		for example, if you are a zip, you need to zip and write to the destination_path
	##		or you may want to inject items into the HTML file
	##		if it is a preview, you shouldn't do things like zip it up, as Hype needs to know where the index.html file is
	elif args.modify_staging_path != None:
		import os
		import string
		
		is_preview = bool(distutils.util.strtobool(args.is_preview))
		
		# add in width/height into insert_at_head_start variable
		global insert_at_head_start
		template = string.Template(insert_at_head_start)
		if is_preview:
			rushEventsForPreview = '<script data-exports-type="dclk-quick-preview">studio.Enabler.setRushSimulatedLocalEvents(true);</script>';
		else:
			rushEventsForPreview = '';
		
		insert_at_head_start = template.substitute({'width' : args.main_container_width, 'height' : args.main_container_height, "clickTag" : args.clickTag, "rushEventsForPreview" : rushEventsForPreview })
		
		index_path = os.path.join(args.modify_staging_path, args.html_filename)
		perform_html_additions(index_path)

		import shutil
		shutil.rmtree(args.destination_path, ignore_errors=True)
		
		if is_preview == True:
			shutil.move(args.modify_staging_path, args.destination_path)
			print json.dumps({"result" : True})
		else:
			zip(args.modify_staging_path, args.destination_path)
			print json.dumps({"result" : True})
		sys.exit(0)

	## --check_for_updates
	##		return a dictionary with "url", "from_version", and "to_version" keys if there is an update, otherwise don't return anything and exit
	##		it is your responsibility to decide how often to check
	elif args.check_for_updates:
		import subprocess
		import urllib2
		
		last_check_timestamp = None
		try:
			last_check_timestamp = subprocess.check_output(["defaults", "read", defaults_bundle_identifier, "last_check_timestamp"]).strip()
		except:
			pass

		try:
			timestamp_now = subprocess.check_output(["date", "+%s"]).strip()
			if (last_check_timestamp == None) or ((int(timestamp_now) - int(last_check_timestamp)) > minimum_update_check_duration_in_seconds):
				subprocess.check_output(["defaults", "write", defaults_bundle_identifier, "last_check_timestamp", timestamp_now])
				latest_script_version = int(urllib2.urlopen(version_info_url).read().strip())
				if latest_script_version > current_script_version:
					print json.dumps({"result" : {"url" : download_url, "from_version" : str(current_script_version), "to_version" : str(latest_script_version)}})
		except:
			pass

		sys.exit(0)


# HTML FILE MODIFICATION

def perform_html_additions(index_path):
	index_contents = None
	with open(index_path, 'r') as target_file:
		index_contents = target_file.read()
		
	if index_contents == None:
		return
		
	import re
	if insert_at_head_start != None:
		head_start = re.search("<head.*?>", index_contents, re.IGNORECASE).end()
		index_contents = index_contents[:head_start] + insert_at_head_start + index_contents[head_start:]
	if insert_at_head_end != None:
		head_end = re.search("</head", index_contents, re.IGNORECASE).start()
		index_contents = index_contents[:head_end] + insert_at_head_end + index_contents[head_end:]
	if insert_at_body_start != None:
		body_start = re.search("<body.*?>", index_contents, re.IGNORECASE).end()
		index_contents = index_contents[:body_start] + insert_at_body_start + index_contents[body_start:]
	if insert_at_body_end != None:
		body_end = re.search("</body", index_contents, re.IGNORECASE).start()
		index_contents = index_contents[:body_end] + insert_at_body_end + index_contents[body_end:]

	with open(index_path, 'w') as target_file:
		target_file.write(index_contents)


# UTILITIES

# from http://stackoverflow.com/questions/14568647/create-zip-in-python
def zip(src, dst):
	import os
	import zipfile
	zf = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
	abs_src = os.path.abspath(src)
	for dirname, subdirs, files in os.walk(src):
		for filename in files:
			absname = os.path.abspath(os.path.join(dirname, filename))
			arcname = absname[len(abs_src) + 1:]
			zf.write(absname, arcname)
	zf.close()


if __name__ == "__main__":
	main()
