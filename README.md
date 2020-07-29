## Script for parsing book site.

 Script for parsing [book site tululu.org](http://tululu.org/l55)

## Getting Started
* cd to the directory where requirements.txt is located.
* activate your virtualenv.
* install dependencies:
```bat
 pip install -r requirements.txt
``` 

 To pars all pages:
```bat
python parse_tululu_category.py
```

 Script can take special commands (optional):
```bat
--start_page
``` 
 Indicates page since which parse started. 
 Default pars started from first page.
 
```bat
--end_page
``` 
 Indicates page which parse will be end. Default pars ended by lats page.

```bat
--dist_folder
```
 Indicates folder for parsed files.By default, the files is created in the dist_folder.

```bat
--skip_imgs
```
 Flag, if exist all images wouldn't download.
 
```bat
--skip_txt
``` 
 Flag, if exist all txt wouldn't download.
  
```bat
--json_path
```
 Indicates folder for json file which would created by the script.
 By default, the file is created in the dist_folder.
 
 ## Motivation
 
 The code is written for educational purposes - this is a lesson in Python and web development on the site [Devman](https://dvmn.org).
  