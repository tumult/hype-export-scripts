# Hype Export Scripts

* [Overview](#overview)
	* [Features](#features)
	* [Things you could do with Export Scripts](#things-you-could-do-with-export-scripts)
* [User Resources](#user-resources)
* [Installation and Naming](#installation-amp-naming)
* [API Basics](#api-basics)
* [API Reference](#api-reference)
	* [get\_options](#get_options)
	* [replace\_url](#replace_url)
	* [modify\_staging\_path](#modify_staging_path)
	* [check\_for\_updates](#check_for_updates)
* [Debugging](#debugging)
	* [Seeing arguments and capturing output](#seeing-arguments-and-capturing-output)
	* [Printing your own logs](#printing-your-own-logs)
* [Examples](#examples)
* [Tips](#tips)
* [Publishing](#publishing)

## Overview

Tumult Hype v3.6 introduced the feature of Export Scripts.  These are scripts called by Hype that can add an item in the **File > Export as HTML** menu and extend Hype's UI allowing automated modifications to the HTML5 content Hype produces.

Often Hype is part of a workflow where its output may need to be manipulated before being published.  For example, ad-tech networks such as DoubleClick need specific JavaScripts referenced, meta annotations in the HTML head, cannot include some specific Hype resources, and the final file needs to be zipped.  Developers can build an Export Script to accomplish these tasks. It can then be distributed to other users to automate these workflows.

### Features

* Add menu item entries to **File > Export as HTML**, **Advanced Export**, and optionally the **Preview** toolbar item.
* Set values for export options (like those revealed in Advanced Export and a few others)
* Alter resource URLs, where they are saved, if they are full URLs, and preloading settings
* Perform modifications to the entire export folder and HTML files on the way out
* Add variables within Hype's UI that will be passed to the script
* Add custom actions in Hype's UI that will run javascript functions with arguments

### Things you could do with Export Scripts

* Produce a zip file for ad networks
* Post-process images
* Upload to servers/services
* Insert default javascripts into the head HTML or make other HTML modifications
* Define asset folder structures (use img,css,js, etc. instead of .hyperesources)

## User Resources

* Get Export Scripts: [http://tumult.com/hype/export-scripts/](http://tumult.com/hype/export-scripts/)
* Documentation: [http://tumult.com/hype/documentation/3.0/#export-scripts](http://tumult.com/hype/documentation/3.0/#export-scripts)


## Installation and Naming

* Export Scripts must have an extension recognizable as a script (`.sh`, `.py`, `.rb`, etc.).
* Export Scripts must have `hype-export` within their filename to, for example: `DoubleClickStudio.hype-export.py`.
* Export Scripts must have permissions set as executable: `chmod 755 [filename]`
* Export Scripts are installed by the user in the Application Scripts folder for Hype. This folder is dependent on how the user obtained Hype:

```
    Tumult Store & Mac App Store: ~/Library/Application Scripts/com.tumult.Hype2/
    Setapp: ~/Library/Application Scripts/com.tumult.hype-setapp/
    Beta: ~/Library/Application Scripts/com.tumult.Beta.Hype2/
```

Hype's Export preference pane offers a button for the user to easily go to this folder.  If the script successfully meets the above points, it will show up in the list in this pane.


## API Basics

Export scripts are called with arguments to denote data that is requested from them. They are not kept alive and must return a JSON result. Because of this, Export Scripts may be called when Hype is launched, re-activated, and multiple times when previewing or exporting a document.

There are only four specific calls, denoted by the first argument passed in:

* `get_options` - sets export options, save panel options, and configures Hype UI
* `replace_url` - modify resource URLs
* `modify_staging_path` - make any changes to Hype's export
* `check_for_updates` - a chance to check if there's a newer version of your script

Some of these have additional arguments passed in (see documentation below), for example: 

```
./DoubleClick Studio.hype-export.py --replace_url greenGrow.png --url_type 2 --is_reference False --should_preload True --export_uid 46383A66-D54C-4287-B1AF-FDB36BB52BBB-19131-00002EDE358D277D --hype_version 3.6.0 --hype_build 571
```

The output must be printed to stdout in JSON format as a dictionary with a `"result"` key. Python example:

```
print json.dumps({"result" : resulting_data_object})
```

## API Reference

### get\_options

`--get_options`

**return** a JSON dictionary with the following keys to be presented in the Hype UI:

```
'export_options' : dictionary # key/value pairs that make modifications to Hype's export/preview system. Some useful ones:
	'exportShouldInlineHypeJS' : boolean
	'exportShouldInlineDocumentLoader' : boolean
	'exportShouldUseExternalRuntime' : boolean
	'exportExternalRuntimeURL' : string
	'exportShouldSaveHTMLFile' : boolean
	'indexTitle' : string
	'exportShouldBustBrowserCaching' : boolean
	'exportShouldIncludeTextContents' : boolean
	'exportShouldIncludePIE' : boolean
	'exportSupportInternetExplorer6789' : boolean
	'initialSceneIndex' : integer
'save_options' : dictionary # key/value pairs that for determining when/how to export. valid keys:
	'file_extension' : string # the final extension when exported (ex. "zip")
	'allows_export' : boolean # should show up in the File > Export as HTML5 menu and Advanced Export
	'allows_preview' : boolean # should show up in the Preview menu, if so --is_preview True is passed into the --modify_staging_path call
'document_arguments' : array # list of keys that will be passed to subsequent calls via --key value, shows up in document inspector
'extra_actions' : array # should be an array of dictionaries, shows up in actions
	'label' : string # user presented name
	'function' : string # javascript function to call if this action is triggered, just the name of it
	'arguments' : array # array of dictionaries that represent arguments passed into the function
		'label' : string  # presented to Hype UI
		'type' : string # that is either "String" (will be quoted and escaped) or "Expression" (passed directly to function argument as-is)
```


### replace\_url

`--replace_url [url] --url_type [HypeURLType] --is_reference [True|False] --should_preload [None|True|False] --is_preview [True|False] --export_uid [identifier]`

if `HypeURLType` is 4, (aka `ResourcesFolder`), you can set the url to `"."` so there is no .hyperesources folder and everything is placed next to the .html file.  Enumeration of types (in Python):

```
class HypeURLType:
	Unknown = 0
	HypeJS = 1
	Resource = 2
	Link = 3
	ResourcesFolder = 4
```

`should_preload` is an optional argument that may not be passed in if it does not apply to the resource type.

`is_preview` indicates whether this was activated from the preview toolbar item, or via the export menu.

`export_uid` is an identifier specific to the export that can be used to help keep state between calls, as `replace_url` may be called multiple times. This is the same identifier passed into `modify_staging_path`.


**return** a JSON dictionary with `'url'`, `'is_reference'`, and optional `'should_preload'` keys.


### modify\_staging\_path

`--modify_staging_path [filepath] --destination_path [filepath] --export_info_json_path [filepath] --is_preview [True|False] --export_uid [identifier]`


Make any changes you'd like before the save is complete.  For example, if you are a zip, you need to zip and write to the `destination_path`, or you may want to inject items into the HTML file.  If it is a preview (`is_preview`), you shouldn't do things like zip it up, as Hype needs to know where the index.html file is located.

`export_uid` is an identifier specific to the export and matches any earlier calls to `replace_url`.

`export_info_json_path` is a file path to a json object you can read holding keys:

```
'html_filename' : string #  that is the filename for the html file which you may want to inject changes into
'main_container_width' : number # representing the width of the document in pixels
'main_container_height' : number # representing the height of the document in pixels
'document_arguments' : dictionary # of key/value pairs based on what was passed in from the earlier --get_options call
'extra_actions' : array # of dictionaries for all usages of the extra actions. There is no guarantee these all originated from this script or version.
	'function' : string # function name (as passed in from --get_options)
	'arguments' : array # of strings
```
	
**return** True if you moved successfully to the destination\_path, otherwise don't return anything and Hype will make the move.

### check\_for\_updates

`--check_for_updates`

This is presently called whenever an export is initiated, but that is subject to change. It isn't recommended you test against a server on each call; it is your responsibility to decide how often to check.

**return** a JSON dictionary with "url", "from\_version", and "to\_version" keys if there is an update, otherwise don't return anything and exit.

## Debugging

### Seeing arguments and capturing output

In the course of developing an Export Script, you may be curious to get better visibility into what is being passed to your Script, and the output that Hype sees.  You can enable Hype to log via enabling this default:

`defaults write com.tumult.Hype2 enableExportScriptDebugLogging -bool YES`

*Or, if you are using a beta version of Hype, you must use this command:*

`defaults write com.tumult.Beta.Hype4 enableExportScriptDebugLogging -bool YES`

You can then view the output by running this command in the Terminal (Sierra):

`log stream --style syslog --predicate '(processImagePath contains[c] "hype") && (category != "security_exception")'`

### Printing your own logs

The output of Export Scripts must be in a specific JSON format on stdout, which means that you cannot write to stdout with standard print/echo messages without modifications.  One option is to use stderr instead of stdout.  The other is that Hype will only use the resulting JSON after this delimiter:

`====================`

Anything logged before will be ignored by Hype, and thus will show up.  So to this end, you could print/echo whatever you want, and then use a return command that always adds the delimiter. Here's a python example:

```
# communicate info back to Hype
# uses delimiter (20 equal signs) so any above printing doesn't interfere with json data
def exit_with_result(result):
	import sys
	print "===================="
	print json.dumps({"result" : result})
	sys.exit(0)
```


## Examples

There is a full example showing usage of all APIs and providing some utilitiy functions here:

[SampleExportScript.hype-export.py](https://github.com/tumult/hype-export-scripts/blob/master/SampleExportScript/SampleExportScript.hype-export.py)

It is the recommended starting point for any new scripts.


## Tips

* If you need to show a dialog or ask for user input, you can use the `osascript -e` command to run Apple Script with can use `display dialog` and prompt the user.

* Hype's Application Scripts folder is recursively scanned, so if you have any needed resources you can store those with the script in a folder.

* The script environment is different than running from the Terminal; for example the PATH may not include all your expected directories. A common issue would be if you are calling out to a tool installed via homebrew it may not be found.  In this case you should use the full path to the binary (`/usr/local/bin/the_tool`) or change the PATH variable to include your search directories.

## Publishing

You can distribute your own Export Scripts however you would like. Due to needing executable permissions, it is recommended that you encapsulate the script in a format that retains permissions, such as `.zip`, `.dmg`, or `.pkg`.  It is a good idea to include installation instructions, since it isn't straight forward and often a user's Library folder is hidden.

If you feel the Export Script would be generally useful to a wide audience of Hype users, you are welcome to share it on the [forums](https://forums.tumult.com) or email [Tumult](mailto:contact@tumult.com) to see if it should be included on the main [Hype Export Scripts](http://tumult.com/hype/export-scripts/) page.  You are also welcome to fork this repository and submit pull requests for new scripts or changes to existing ones.
