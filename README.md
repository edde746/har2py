# har2py

This is a fork of S1M0N38's har2py highly modified to meet my needs, mostly adding the request payload but also removing responses and cleaning up the code.

## Usage

1. Navigate the web with your browser while recording your activity. Then save the
data in HAR file. Here is an example with Chrome Devs Tools
![har.gif](https://github.com/S1M0N38/har2py/blob/main/har.gif?raw=true)

2. Go to the directory where is located the har file you want to convert and
type

```har2py my_har_file.har```

This will generate valid python code base on [requests](https://requests.readthedocs.io/en/master/)
library from *my_har_file.har*. The generated file will be called
*my_har_file.py* and be located in the same directory of the input file.

Additional arguemnts are describe in the help

```

> har2py -h

usage: har2py [-h] [-o OUTPUT] [-t TEMPLATE] [-f FILTERS] [-w] input

positional arguments:
  input                 har input file

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        py output file. If not the define use the same name of the har
                        file with py extension.
  -t TEMPLATE, --template TEMPLATE
                        jinja2 template used to generate py code. Default to requests.
                        (For now "requests" is the only available template)
  -w, --overwrite       overwrite py file if one previous py file with the same name
                        already exists.

```