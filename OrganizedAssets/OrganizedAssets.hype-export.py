#!/usr/bin/python

# 	OrganizedAssets.hype-export.py
#		Export Script that exports assets in a manner similar to the old Edge Animate
#		Instead of a single .hyperesources folder, it will export with images/ media/ and js/
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
current_script_version = 1
username = os.path.split(os.path.expanduser('~'))[-1]
version_info_url = "https://static.tumult.com/hype/export-scripts/OrganizedAssets/latest_script_version.txt" # only returns a version number
download_url = "https://tumult.com/hype/export-scripts/OrganizedAssets/" # gives a user info to download and install
minimum_update_check_duration_in_seconds = 60 * 60 * 24 # once a day
defaults_bundle_identifier = "com.tumult.Hype2.hype-export.OrganizedAssets"


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
	if args.get_options:		
		def save_options():
			return {
				"allows_export" : True,
				"allows_preview" : True,
			}
	
		options = {
			"save_options" : save_options(),
		}
	
		exit_with_result(options)

	## --replace_url [url] --url_type [HypeURLType] --is_reference [True|False] --should_preload [None|True|False] --is_preview [True|False] --export_uid [identifier]
	elif args.replace_url != None:
		url_info = {}
		url_info['is_reference'] = bool(distutils.util.strtobool(args.is_reference))
		if args.should_preload != None:
			url_info['should_preload'] = bool(distutils.util.strtobool(args.should_preload))
		
		if int(args.url_type) == HypeURLType.ResourcesFolder:
			url_info['url'] = "."
			pass
		elif (int(args.url_type) == HypeURLType.HypeJS):
			url_info['url'] = "js/" + args.replace_url
		elif (int(args.url_type) == HypeURLType.Resource):
			#images
			if args.replace_url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.psd', '.pdf')):
				url_info['url'] = "images/" + args.replace_url
			#audio
			elif args.replace_url.lower().endswith(('.mp3', '.m4a', '.oga', '.mp2', '.wav', '.aiff', '.aif', '.wma', '.aac', '.flac')):
				url_info['url'] = "media/" + args.replace_url
			#video
			elif args.replace_url.lower().endswith(('.mp4', '.m4v', '.ogg', '.ogv', '.mov', '.avi', '.flv', '.wmv', '.webm', '.mkv', '.qt', '.m4p', '.mpeg')):
				url_info['url'] = "media/" + args.replace_url
			#js
			elif args.replace_url.lower().endswith(('.js', '.jsx', '.coffee', '.map', '.ts', '.htc')):
				url_info['url'] = "js/" + args.replace_url
			#everything else
			else:
				url_info['url'] = args.replace_url

		else:
			url_info['url'] = args.replace_url
				
		exit_with_result(url_info)


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


# UTILITIES

# communicate info back to Hype
# uses delimiter (20 equal signs) so any above printing doesn't interfere with json data
def exit_with_result(result):
	import sys
	print "===================="
	print json.dumps({"result" : result})
	sys.exit(0)

if __name__ == "__main__":
	main()
