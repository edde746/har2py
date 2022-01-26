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


def main(
    har_file: str,
    py_file: str,
    overwrite: bool = False,
    template_dir: str = pathlib.Path(__file__).parents[0],
    template_name: str = 'requests.jinja2'
):
    har_file = pathlib.Path(har_file)
    if py_file:
        py_file = pathlib.Path(py_file)
    else:
        py_file = har_file.with_suffix('.py')

    if not har_file.is_file():
        raise FileNotFoundError

    if har_file.suffix != '.har':
        raise IOError(
            'input file has not ".har" extension. Please use an ".har" file'
        )

    if py_file.suffix != '.py':
        raise IOError(
            'output file has not ".py" extension. Please use an ".py" file'
        )

    if not overwrite and py_file.is_file():
        raise FileExistsError(f'{py_file} already exists.')

    with open(har_file, encoding='utf8', errors='ignore') as f:
        har = json.load(f)
    logging.debug(f'load {har_file}')

    har = preprocessing(har)
    py = rendering(har, template_dir=template_dir, template_name=template_name)

    with open(py_file, 'w') as f:
        f.write(py)
    logging.debug(f'saving {py_file}')


def preprocessing(har: dict):
    requests = [e['request'] for e in har['log']['entries']]
    print(requests)
    return {
        'requests': [
            {
                'url': request['url'].split('?')[0],
                'method': request['method'].lower(),
                'headers': [(h['name'], h['value']) for h in request['headers']],
                'cookies': [(h['name'], h['value']) for h in request['cookies']],
                'params': [(p['name'], p['value']) for p in request['queryString']],
                'payload': request['postData']['text'] if 'postData' in request else False,
            } for request in requests
        ]
    }

def rendering(har: dict, template_dir: str = pathlib.Path(__file__).parents[0], template_name: str = 'requests.jinja2'):
    # check for the correctness of the har structure
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template(template_name)
    logging.debug(f'render har with "{template.name}" template')

    print(har['requests'])
    py = template.render(
        requests=har['requests'],
    )

    # test if the generated code is python valid code
    try:
        ast.parse(py)
    except SyntaxError:
        raise SyntaxError(
            'cannot parse har into valid python code. '
            'Please check the correctness of the jinja2 template'
        )

    logging.debug('successfully generate valid python code')

    return py
