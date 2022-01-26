import argparse,jinja2,ast,json,logging,pathlib

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input',
        action='store',
        help='har input file',
    )
    parser.add_argument(
        '-o', '--output',
        action='store',
        default='',
        type=str,
        help=(
            'py output file. If not the define use the same name '
            'of the har file with py extension.'
        ),
    )
    parser.add_argument(
        '-t', '--template',
        action='store',
        default='requests',
        type=str,
        help=(
            'jinja2 template used to generate py code. '
            'Default to requests. '
            '(For now "requests" is the only available template)'
        ),
    )
    parser.add_argument(
        '-w', '--overwrite',
        action='store_true',
        help=(
            'overwrite py file if one previous py file with the same name '
            'already exists.'
        ),
    )

    args = parser.parse_args()
    main(args.input, args.output, overwrite=args.overwrite, template_name=args.template + '.jinja2')


def main(har_file, py_file, overwrite = False, template_dir= pathlib.Path(__file__).parents[0], template_name = 'requests.jinja2'):
    har_file = pathlib.Path(har_file)
    py_file = pathlib.Path(py_file) if py_file else har_file.with_suffix('.py')

    if not har_file.is_file():
        raise FileNotFoundError

    if har_file.suffix != '.har':
        raise IOError('Input file has not ".har" extension. Please use an ".har" file')

    if py_file.suffix != '.py':
        raise IOError('Output file has not ".py" extension. Please use an ".py" file')

    if not overwrite and py_file.is_file():
        raise FileExistsError(f'{py_file} already exists.')

    # Load HAR
    with open(har_file, encoding='utf8', errors='ignore') as f:
        har = json.load(f)
    logging.debug(f'load {har_file}')

    py = rendering(preprocessing(har), template_dir=template_dir, template_name=template_name)

    with open(py_file, 'w') as f:
        f.write(py)
    logging.debug(f'Saved {py_file}')


def preprocessing(har: dict):
    requests = [e['request'] for e in har['log']['entries']]
    return {
        'requests': [
            {
                'url': request['url'].split('?')[0],
                'method': request['method'].lower(),
                'headers': [(h['name'], h['value']) for h in request['headers']],
                'cookies': [(h['name'], h['value']) for h in request['cookies']],
                'params': [(p['name'], p['value']) for p in request['queryString']],
                'payload': request['postData']['text'] if 'postData' in request else False,
                #'jsonPayload': 'application/json' in request['postData']['mimeType'] if 'postData' in request else False
            } for request in requests
        ]
    }

def rendering(har: dict, template_dir: str = pathlib.Path(__file__).parents[0], template_name: str = 'requests.jinja2'):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template(template_name)
    logging.debug(f'Using template: "{template.name}"')

    py = template.render(requests=har['requests'])

    try:
        ast.parse(py)
    except SyntaxError:
        raise SyntaxError('Failed to generate code, ensure that template is valid')

    logging.debug('Successfully generate valid python code')

    return py

if __name__ == "__main__":
    cli()