#!/usr/bin/python
from aiohttp import web
import aiohttp_jinja2
import jinja2
import subprocess
import re
import os

def get_processes():
    # run command systemctl on linux and get output of all loaded services
    p = subprocess.Popen("systemctl list-units --type=service", stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    output = output.decode('utf-8')

    # pattern to look for name of services and their status and description
    pattern = "(\S.*).service *(\S+) *(\S+) *(\S+) *(.*) "

    # example output :
    # lout = [('abrt-journal-core', 'loaded', 'active', 'running', 'Creates ABRT problems from coredumpctl messages'), ('abrt-oops', 'loaded', 'active', 'running', 'ABRT kernel log watcher')]
    lout = re.findall(pattern=pattern,string=output)

    # create list of dictionaries
    s_key = ['PROCESS', 'LOAD', 'ACTIVE', 'STATUS', 'DESCRIPTION']
    list_of_dict_out = []

    for l in lout:
        d = dict(zip(s_key,l))
        list_of_dict_out.append(d)
    return list_of_dict_out

@aiohttp_jinja2.template('webpage.html')
async def handle (request):
    processes = get_processes()
    context = {
        'processes': processes
    }

    return context

app = web.Application()
app.add_routes([
    web.get('/', handle)
])


aiohttp_jinja2.setup(
    app=app, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), 'templates'))
)

if __name__=='__main__':
    web.run_app(app=app)


