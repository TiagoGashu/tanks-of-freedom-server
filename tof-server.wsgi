activate_this = '/var/www/tof-server/flask/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

#activator = 'some/path/to/activate_this.py'
#with open(activator) as f:
#    exec(f.read(), {'__file__': activator})

from tof_server import app as application