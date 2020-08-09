#!/usr/bin/python3
from aiohttp import web
import jinja2, aiohttp_jinja2
import re
import logging
import os, subprocess, sys
import sqlite3 as sql

# logging config:

logger = logging.getLogger(__name__)
log_format = logging.Formatter('%(asctime)s - %(levelname)s:%(module)s|%(lineno)d \ \ \ %(funcName)s:%(message)s')

logger.setLevel(logging.DEBUG)
log_debug = logging.FileHandler('debug.log')
log_debug.setFormatter(log_format)
logger.addHandler(log_debug)

# Separate file for errors

log_errors = logging.FileHandler('errors.log')
log_errors.setLevel(logging.WARNING)
log_errors.setFormatter(log_format)
logger.addHandler(log_errors)

# create DB table
DBNAME = 'process.db'


def create_db():
    sql_command = '''
        CREATE TABLE IF NOT EXISTS SRV (
            "process_name" TEXT NOT NULL UNIQUE,
            "loaded" TEXT NOT NULL,
            "active" TEXT NOT NULL,
            "status" TEXT NOT NULL,
            "description" TEXT,
            PRIMARY KEY("process_name")
        );'''
    db_connector = sql.connect(DBNAME)
    db_connector.execute(sql_command)
    db_connector.commit()
    db_connector.close()


def save_to_file(processes):
    sql_command = '''
        INSERT INTO SRV (
            process_name, loaded, active, status, description
            ) VALUES (?, ?, ?, ?, ?)
    '''
    try:
        db = sql.connect(DBNAME)
        cur = db.cursor()
        for proc in processes:
            cur.execute(sql_command, (proc['PROCESS'], proc['LOAD'], proc['ACTIVE'], proc['STATUS'], proc['DESCRIPTION']))
        db.commit()
        db.close()
        logger.info('Processes were written successfully to DB')
    except sql.OperationalError as o:
        logger.error('Cant write to DB. Error - ' + str(o))
    except:
        logger.error('cant write process info to db')


def get_processes():
    # run command systemctl on linux and get output of all loaded services
    p = subprocess.Popen("systemctl list-units --type=service", stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    output = output.decode('utf-8')

    # pattern to look for name of services and their status and description
    pattern = "(\S.*).service *(\S+) *(\S+) *(\S+) *(.*) "

    # example output : lout = [('abrt-journal-core', 'loaded', 'active', 'running', 'Creates ABRT problems from
    # coredumpctl messages'), ('abrt-oops', 'loaded', 'active', 'running', 'ABRT kernel log watcher')]
    lout = re.findall(pattern=pattern, string=output)

    # create list of dictionaries
    s_key = ['PROCESS', 'LOAD', 'ACTIVE', 'STATUS', 'DESCRIPTION']
    list_of_dict_out = []

    for l in lout:
        d = dict(zip(s_key, l))
        list_of_dict_out.append(d)

    return list_of_dict_out


create_db()


@aiohttp_jinja2.template('webpage.html')
async def handle(request):
    data = await request.post()
    print(data)

    processes = get_processes()
    save_to_file(processes)
    context = {'processes': processes}
    return context


app = web.Application()
app.add_routes([
    web.get('/', handle)
])

aiohttp_jinja2.setup(
    app=app, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), 'templates'))
)

proc_port = 8000
assert sys.version_info >= (3, 7), "Script requires Python 3.7+."

logger.debug('App is started successfully on port ' + str(proc_port))
web.run_app(app=app, port=proc_port)

logger.debug('App stopped working successfully')
