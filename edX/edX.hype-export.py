#!/usr/bin/python

# 	edX.hype-export.py
#		
#		For MIT's edX system
#
#		Installation, usage, and additional info: 
#			https://tumult.com/hype/export-scripts/
#
#		MIT License
#		Copyright (c) 2018 Tumult Inc.
#

import argparse
import json
import sys
import distutils.util
import os

# update info
current_script_version = 2
username = os.path.split(os.path.expanduser('~'))[-1]
version_info_url = "https://static.tumult.com/hype/export-scripts/edX/latest_script_version.txt" # only returns a version number
download_url = "https://tumult.com/hype/export-scripts/edX/" # gives a user info to download and install
minimum_update_check_duration_in_seconds = 60 * 60 * 24 # once a day
defaults_bundle_identifier = "com.tumult.Hype4.hype-export.edX"


# html insertions
insert_at_head_start = ""

insert_at_head_end = ""

insert_at_body_start = """
	<script>

	window.HYPE_eventListeners = ("HYPE_eventListeners" in window === false) ? Array() : window.HYPE_eventListeners;
	window.HYPE_eventListeners.push({"type":"HypeResourceLoad", "callback": (function (hypeDocument, element, event) {
		var originalURL = event.url;
		var resourceName = originalURL.substring(originalURL.lastIndexOf('/') + 1);
		var edXAssetURL = "${edx_asset_url}";
		var documentNamePrefix = "${document_name}"
		return (edXAssetURL + documentNamePrefix + "-" + resourceName);
	})});


	</script>
"""

insert_at_body_end = ""


class HypeURLType:
	Unknown = 0
	HypeJS = 1
	Resource = 2
	Link = 3
	ResourcesFolder = 4

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--hype_version')
	parser.add_argument('--hype_build')
	parser.add_argument('--export_uid')

	parser.add_argument('--get_options', action='store_true')

	parser.add_argument('--replace_url')
	parser.add_argument('--url_type')
	parser.add_argument('--is_reference', default="False")
	parser.add_argument('--should_preload')

	parser.add_argument('--modify_staging_path')
	parser.add_argument('--destination_path')
	parser.add_argument('--export_info_json_path')
	parser.add_argument('--is_preview', default="False")

	parser.add_argument('--check_for_updates', action='store_true')
	
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
			cdnPath = "${edx_asset_url}"
			
			return {
				"exportShouldInlineHypeJS" : True,
				"exportShouldInlineDocumentLoader" : False,
				"exportShouldUseExternalRuntime" : True,
				"exportExternalRuntimeURL" : cdnPath,
				"exportShouldSaveHTMLFile" : True,
				"exportShouldNameAsIndexDotHTML" : False,
				#"indexTitle" : "",
				"exportShouldBustBrowserCaching" : False,
				"exportShouldIncludeTextContents" : False,
				"exportShouldIncludePIE" : True,
				"exportSupportInternetExplorer6789" : True,
				"exportShouldSaveRestorableDocument" : False,
			}

		def save_options():
			return {
				"allows_export" : True,
				"allows_preview" : True,
			}
	
		def document_arguments():
			return ["Asset URL"];
				
		options = {
			"export_options" : export_options(),
			"save_options" : save_options(),
			"document_arguments" : document_arguments(),
			"min_hype_build_version" : "574", # build number (ex "574") and *not* marketing version (ex "3.6.0")
			#"max_hype_build_version" : "10000", # build number (ex "574") and *not* marketing version (ex "3.6.0")
		}
	
		exit_with_result(options)


	## --replace_url [url] --url_type [HypeURLType] --is_reference [True|False] --should_preload [None|True|False] --is_preview [True|False] --export_uid [identifier]
	##		return a dictionary with "url", "is_reference", and optional "should_preload" keys
	##		if HypeURLType.ResourcesFolder, you can set the url to "." so there is no .hyperesources folder and everything
	##		is placed next to the .html file
	##		should_preload may be None type in cases where it won't be used
	elif args.replace_url != None:
		url_info = {}
		url_info['is_reference'] = True
		if args.should_preload != None:
			url_info['should_preload'] = bool(distutils.util.strtobool(args.should_preload))
		
		if int(args.url_type) == HypeURLType.ResourcesFolder:
			url_info['url'] = "."
		elif int(args.url_type) == HypeURLType.HypeJS:
			url_info['url'] = "${edx_asset_url}" + args.replace_url
		else:
			url_info['url'] = args.replace_url
				
		exit_with_result(url_info)


	## --modify_staging_path [filepath] --destination_path [filepath] --export_info_json_path [filepath] --is_preview [True|False] --export_uid [identifier]
	##		return True if you moved successfully to the destination_path, otherwise don't return anything and Hype will make the move
	##		make any changes you'd like before the save is complete
	##		for example, if you are a zip, you need to zip and write to the destination_path
	##		or you may want to inject items into the HTML file
	##		if it is a preview, you shouldn't do things like zip it up, as Hype needs to know where the index.html file is
	##		export_info_json_path is a json object holding keys:
	##			html_filename: string that is the filename for the html file which you may want to inject changes into
	##			main_container_width: number representing the width of the document in pixels
	##			main_container_height: number representing the height of the document in pixels
	##			document_arguments: dictionary of key/value pairs based on what was passed in from the earlier --get_options call
	##			extra_actions: array of dictionaries for all usages of the extra actions. There is no guarantee these all originated from this script or version.
	##				function: string of function name (as passed in from --get_options)
	##				arguments: array of strings
	elif args.modify_staging_path != None:
		import os
		import string
		
		is_preview = bool(distutils.util.strtobool(args.is_preview))

		# read export_info.json file
		export_info_file = open(args.export_info_json_path)
		export_info = json.loads(export_info_file.read())
		export_info_file.close()

		if "Asset URL" in export_info["document_arguments"]:
			edx_asset_url = export_info["document_arguments"]["Asset URL"]
		else:
			edx_asset_url = ""

		document_name = os.path.splitext(export_info["html_filename"])[0]
	
		index_path = os.path.join(args.modify_staging_path, export_info["html_filename"])

		perform_html_additions(index_path)		
		perform_html_substitutions(index_path, {"edx_asset_url" : edx_asset_url, "document_name" : document_name })
		perform_custom_html_substution(index_path, "./%24%7Bedx_asset_url%7D", edx_asset_url)
		
		for filename in os.listdir(args.modify_staging_path):
			if filename == export_info["html_filename"]:
				continue
			elif filename.startswith("HYPE") and filename.endswith("js"):
				continue
			elif filename.endswith("hype_generated_script.js"):
				new_filename = filename.replace("${edx_asset_url}", "")
			else:
				new_filename = document_name + "-" + filename
			os.rename(os.path.join(args.modify_staging_path, filename), os.path.join(args.modify_staging_path, new_filename))

		import shutil
		shutil.rmtree(args.destination_path, ignore_errors=True)		
		shutil.move(args.modify_staging_path, args.destination_path)
		exit_with_result(True)


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
				request = urllib2.Request(version_info_url, headers={'User-Agent' : "Magic Browser"})
				latest_script_version = int(urllib2.urlopen(request).read().strip())
				if latest_script_version > current_script_version:
					exit_with_result({"url" : download_url, "from_version" : str(current_script_version), "to_version" : str(latest_script_version)})
		except:
			pass


# HTML FILE MODIFICATION

def perform_custom_html_substution(index_path, search_string, replace_string):
	import string

	index_contents = None
	with open(index_path, 'r') as target_file:
		index_contents = target_file.read()
		
	if index_contents == None:
		return
		
	template = string.Template(index_contents)
	index_contents = index_contents.replace(search_string, replace_string)

	with open(index_path, 'w') as target_file:
		target_file.write(index_contents)	


def perform_html_substitutions(index_path, substitions):
	import string

	index_contents = None
	with open(index_path, 'r') as target_file:
		index_contents = target_file.read()
		
	if index_contents == None:
		return
		
	template = string.Template(index_contents)
	index_contents = template.substitute(substitions)

	with open(index_path, 'w') as target_file:
		target_file.write(index_contents)
	

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

# communicate info back to Hype
# uses delimiter (20 equal signs) so any above printing doesn't interfere with json data
def exit_with_result(result):
	import sys
	print "===================="
	print json.dumps({"result" : result})
	sys.exit(0)

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
