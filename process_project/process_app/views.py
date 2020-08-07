from django.shortcuts import render
import subprocess
import re

posts = [
    {
        'author': 'CoreyMS',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'August 27, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'August 28, 2018'
    }
]

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

# Create your views here.

def process_home(request):
    if request.method == 'POST':
        print(request.POST.get('Start'))
        print(request.POST.get('Stop'))
        print(request.POST.get('Reload'))
    """
    processes = [
        {
            'unit': 'abrt-journal-core',
            'load': 'loaded',
            'active': 'active',
            'status': 'running',
            'description': 'Creates ABRT problems from coredumpctl messages'
        },

    ]
    """
    processes = get_processes()

    context = {
        # 'posts': posts,
        'processes': processes
    }
    if (request.GET.get('name_button')):
        print('success')

    return render(request=request, template_name='process_app/process_template.html',context=context)

def process_about(request):
    return render(request=request, template_name='process_app/process_about.html')