#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

Lots of automated infrastructure tasks to manage EC2+S3 infra.

Most of the remote paths are defined under *env* global variable.
Most of the local paths are defined under *local_env* global variable.
Override env and local_env attributes to reflect your path choices.

Probably you are looking after *bootstrap* or *deploy* tasks. Check them first.


List of major tasks provided in this fabric script:

    bootstrap (The All-In-One starter task.
               Takes a new raw EC2 instance and make it a full workable server.

               Install all system-wide packages (currently only yum supported),
               install Chef,
               uploads our local Chef subfolder,
               start provisioning the server with uploaded Chef subfolder,
               creates a virtualenv and clone the git src repo into it,
               do the first Deploy)

    deploy (fetches code from git src repo,
            install pip requirements,
            upload static assets to S3,
            syncbd and migrate the DB (south migrations),
            restart gunicorn,
            install newest cronjob list)

    stop (stop gunicorn. Takes website out of service)
    start (Undo stop task. Start gunicorn)

    status (health status check on all major services, i.e.:
            Nginx,
            Memcached,
            Postgresql,
            Gunicorn,
            Supervisor)

    db_backup (do a db_backup and stores it remotely)
    fetch_backups (fetch the backups stored remotely to some local folder)
    cleanup_old_backups (cleanup remote folder to store just N latest backups)


ToDo: To create a Rollback task (panic button)

"""
from fabric.api import task, run, local, cd, sudo, lcd, put, get
from fabric.context_managers import settings
from fabric.contrib.files import append, exists

import os
import sys
from datetime import datetime


DEPLOY_LOCK_FILE = '/tmp/deploy_running.{0}'.format(os.environ['USER'])


@task
def get_deploy_lock():
    if exists(DEPLOY_LOCK_FILE):
        return False
    run('touch {0}'.format(DEPLOY_LOCK_FILE))
    return True


@task
def release_deploy_lock():
    run('rm -f {0}'.format(DEPLOY_LOCK_FILE))


@task
def test_local():
    """ Tests local connection """
    local('uname -a')


@task
def test_remote():
    """ Tests remote connection """
    run('uname -a')


@task
def psaux(grep=None):
    cmd = 'ps aux'
    if grep:
        cmd += ' | grep %s' % grep
    run(cmd)


def build_local_vars():
    """
    Build the object containing all special local variables
    """
    class Local:
        pass
    local_env = Local()
    local_env.deploy_root = os.path.dirname(__file__)
    local_env.project_root = os.path.join(local_env.deploy_root, '..')
    local_env.src_root = os.path.join(local_env.project_root, 'src')
    local_env.secret_file = os.path.join(local_env.src_root,
                                         'settings',
                                         'secret.py')
    local_env.etc_root = os.path.join(local_env.deploy_root, 'etc')
    local_env.chef_root = os.path.join(local_env.deploy_root, 'chef')
    local_env.db_backup_root = os.path.join(local_env.project_root, 'backups')
    local_env.db_backup_cleanup_script = os.path.join(local_env.deploy_root,
                                                      'pg_scripts',
                                                      'pg_cleanup_backups.py')

    return local_env


def build_remote_vars():
    """
    Build the object containing all special remote variables
    """
    from fabric.api import  env

    def load_node_json():
        import simplejson
        f = open('node.json')
        return simplejson.load(f)

    node_json = load_node_json()
    env.user = node_json.get('user', 'ec2-user')
    env.project_env = node_json.get('environment', 'PROD')

    env.hosts = ['ec2-54-232-126-197.sa-east-1.compute.amazonaws.com']
    #key_filename references a local filename, but it is necessary to ssh
    env.key_filename = '~/.ssh/ces27-key.pem'
    #env.forward_agent = True
    env.src_repo = 'git://github.com/rafaelmachado/ces27.git'

    env.home_root = '/home/{0}/'.format(env.user)
    env.profile_file = '{0}.profile'.format(env.home_root)
    env.profile_secret_file = '{0}.secret'.format(env.home_root)

    env.venv_root = '{0}.env/'.format(env.home_root)
    env.project_root = '{0}project/'.format(env.venv_root)
    env.deploy_root = '{0}deploy/'.format(env.project_root)
    env.secret_file = '{0}src/settings/secret.py'.format(env.project_root)
    env.etc_root = '/home/{0}/etc/'.format(env.user)  # non-sudo etc folder
    env.supervisord_file = '{0}supervisord.conf'.format(env.etc_root)
    env.src_root = '{0}src/'.format(env.project_root)
    env.public_static_root = '{0}public/static/'.format(env.project_root)

    env.db_backup_root = node_json.get('db_backup_folder',
                                         '/var/backups/db/')
    env.db_backup_cleanup_script = '{0}pg_scripts/pg_cleanup_backups.py'.\
            format(env.deploy_root)
    env.db_conf_file = '/var/lib/pgsql/data/postgresql.conf'

    return env


def _build_solr_env():
    class Solr(object):
        def is_installed(self):
            return exists(self.startjar)
    solr = Solr()
    solr.version = "3.6.1"
    solr.name = "apache-solr-{0}".format(solr.version)
    solr.tarname = "{0}.tgz".format(solr.name)
    solr.link = "http://www.mirrorservice.org/sites/ftp.apache.org/" + \
            "lucene/solr/{0}/{1}".format(solr.version, solr.tarname)
    solr.root = "/home/{0}/solr/".format(env.user)
    solr.start_root = "{0}{1}/example/".format(solr.root, solr.name)
    solr.startjar = "{0}start.jar".format(solr.start_root)
    solr.schema = "{0}solr/conf/schema.xml".format(solr.start_root)
    return solr


local_env = build_local_vars()
env = build_remote_vars()
solr = _build_solr_env()


@task
def bootstrap():
    """
    Bootstrap a new Instance.
        Install essential system-wide packages
        Use the provision system (Chef) to install server services
        Prepare the virtual environment for first use
        Deploy
        Setup Solr (optional)

    """
    build_essential()
    provision()
    build_venv()
    deploy()
    setup_solr()


@task
def build_essential():
    """
    Build and install essential pacakges for a new existing Instance
        Development Tools and Libs (gcc, python, etc)
        Imaging Libs
        Chef (needs Ruby)

    Also, prepares essential environment profile links

    """
    sudo('yum upgrade -y')
    sudo('yum groupinstall -y "Development Tools"')
    sudo('yum groupinstall -y "Development Libraries"')
    sudo('yum install -y openssl mod_ssl openssl-devel')
    sudo('yum install -y zlib zlib-devel\
         libjpeg libjpeg-devel libjpeg-static\
         freetype freetype-devel')

    sudo('yum install -y ruby ruby-devel rubygems\
         ruby-docs ruby-ri ruby-irb ruby-rdoc')
    sudo('gem install chef --no-ri --no-rdoc')

    run('touch {0}'.format(env.profile_file))
    if exists('~/.bash_profile'):
        run("echo 'source {0}' >> ~/.bash_profile".format(env.profile_file))


@task
def provision():
    chef_name = 'chef-{0}'.format(datetime.utcnow().
                                  strftime('%Y-%m-%d-%H-%M-%S'))
    chef_archive = _build_tmp_compressed_cookbooks(chef_name)
    _unzip_tmp_compressed_cookbooks_on_server(chef_archive)
    _chef_provision(chef_name)
    _delete_tmp_compressed_cookbooks(chef_name)


@task
def build_venv():
    """
    Install virtualenv
    Create a virtual environment (~/.env)
    Get source code and non-public files (files not in the src code repo)
    Do the first deploy
    Config supervisor
    Start supervisor

    """
    #install virtualenv
    sudo('pip install -U pip')
    sudo('pip install -U virtualenv')

    #create virtual environment w/ virtualenv
    if not exists(env.venv_root):
        run('virtualenv --distribute \
            --no-site-packages {0}'.format(env.venv_root))

    #clone the github repo
    with cd(env.venv_root):
        if not exists('project'):
            run('git clone {0} project'.format(env.src_repo))

    #install requirements
    _install_requirements('{0}requirements/prod.txt'.format(env.project_root),
                          update=True)

    send_secret_files()
    update_profile()

    #syncdb; migrate
    manage('syncdb --migrate --noinput')
    #supervisor configuration
    update_supervisor()


@task
def deploy():
    """
    Fetchs new code from source repo,
    install new requirements,
    deploy static assets to s3,
    make db changes,
    restart gunicorn to apply changes,

    ToDo: Improve the migrate DB phase.
    A backup before this step should make a *rollback* task possible.

    """
    soft_deploy(src=True, static=True, req=True, secret=True)


@task
def soft_deploy(src=True, static=True, req=False, secret=False):
    if not get_deploy_lock():
        print 'It appears another deploy is currently running. Try again later'
        return
    try:
        _soft_deploy(src=src, static=static, req=req, secret=secret)
    except Exception as e:
        print e
        print 'Some error found. Quitting now.'
        release_deploy_lock()
        sys.exit(1)
    release_deploy_lock()


def _soft_deploy(src=True, static=True, req=False, secret=False):
    """
    Same logic as deploy, but it only does (by default):
        - *src* code update and server restart
        - *static* files concat/compress/upload to S3

    Other possible options are:
        - *req*: install/update requirements
        - *secret*: send secret files to the server
    """

    if src:
        # pull the code from github.
        #don't send secret files again (only necessary at the bootstrap)
        update_src_code(secret=secret)

    if req:
        _install_requirements('{0}requirements/prod.txt'.\
                              format(env.project_root))

    if static:
        deploy_static_assets()

    if src:
        supervisorctl('stop', 'gunicorn')
        manage('syncdb --migrate --noinput')
        supervisorctl('start', 'gunicorn')


@task
def setup_solr():
    """ Setup haystack backend to Solr (if necessary) """

    # checks if solr is necessary on this build
    with open(os.path.join(local_env.project_root,
                           'requirements/prod.txt')) as f:
        content = f.read()
        if 'pysolr' not in content:  # Assume Solr is not necessary
            return

    if solr.is_installed():
        return

    print 'SOLR setup init'
    # fetch and install solr
    with cd('/tmp'):
        if not exists(solr.tarname):
            run('wget {0}'.format(solr.link))
            run('mkdir -p {1}; tar -xvzf {0} -C {1}'.format(solr.tarname,
                                                            solr.root))

    # build solr schema
    manage("build_solr_schema", redirect_to='/tmp/schema.xml')
    run('mv /tmp/schema.xml {0}'.format(solr.schema))

    # enable solr on supervisor
    update_supervisor()

    # update cron jobs (periodic update_index)
    update_cronjob()

    print 'SOLR setup complete.' + \
            'Run *fab manage:rebuild_index* if your indexes are stale.' + \
            'Note: It may take a while to rebuild all the indexes again.'


@task
def update_solr_schema():
    if not solr.is_installed():
        return
    manage("build_solr_schema", redirect_to='/tmp/schema.xml')
    run('mv /tmp/schema.xml {0}'.format(solr.schema))
    supervisorctl('restart', 'solr')


@task
def rebuild_solr_index():
    manage('rebuild_index --traceback --remove --noinput')


@task
def stop():
    """ Stop server """
    supervisorctl('stop', 'gunicorn')


@task
def start():
    """ Start server """
    supervisorctl('start', 'gunicorn')


@task
def status():
    """ Complete Status Check of the server """
    supervisorctl('status', 'gunicorn')
    service('status', 'nginx')
    service('status', 'postgresql')
    service('status', 'memcached')
    supervisorctl('status', 'solr')
    sudo('status supervisor')


@task
def manage(command, redirect_to=''):
    cmd = '{0}bin/python manage.py {1}'.format(env.venv_root, command) + \
            ' --settings=settings.prod'
    if redirect_to:
        cmd += ' > {0}'.format(redirect_to)
    with cd('{0}'.format(env.src_root)):
        run(cmd)


@task
def db_backup():
    """
    Make a potgresql DB backup using plain pg_dumpall.
    """
    sudo('su --session-command="pg_dumpall | \
         gzip > {0}db_$(date +\"\%b-\%d-\%Y_\%H-\%M\").gz" \
         postgres;'.format(env.db_backup_root))


@task
def fetch_backups(post_fetch_cleanup=False):
    """
    Fetches db backup files on the remote server
    to the local db backup folder

    By default do a db backup files cleanup
    (local and remote) after fetching files.
    This behaviour can be overriden by passing
    post_fetch_cleanup as False.

    TODO: Improve current fetch_backups to do not overdownload
    already existent files. Maybe use rsync over plain get.

    """
    if not os.path.exists(local_env.db_backup_root):
        local('mkdir -p {0}'.format(local_env.db_backup_root))

    #copy backups to tmp dir, set permissions, get and remove tmp dir
    temp_db_backups_root = '/tmp/db_backups/'
    sudo('rm -Rf {0} && cp -r {1} {0} && chmod -R a+rx {0}'.\
         format(temp_db_backups_root,
                env.db_backup_root.rstrip('/')))
    get('{0}*'.format(temp_db_backups_root),
        local_path=local_env.db_backup_root)
    sudo('rm -Rf {0}'.format(temp_db_backups_root))

    if post_fetch_cleanup:
        cleanup_old_backups()


@task
def cleanup_old_backups(max_backups=5, clean_local=False):
    """
    Process files on the remote server and clean up
    to retain a max of max_backups files

    Process files on the local machine and clean up
    to retain a max of max_backups files,
    if clean_local is True

    """
    sudo('python {0} {1} {2}'. format(env.db_backup_cleanup_script,
                                      env.db_backup_root,
                                      max_backups))

    if clean_local:
        local('python {0} {1} {2}'.format(local_env.db_backup_cleanup_script,
                                          local_env.db_backup_root,
                                          max_backups))


@task
def restore_db(db_backup_file):
    if not os.path.exists(db_backup_file):
        print '%s file does not exist' % db_backup_file
        return

    remote_tmp = '/tmp/_db_backup_file'

    put(db_backup_file, remote_tmp)
    dropdb_cmd = "dropdb {1}".format("db-user", "db")
    createdb_cmd = "createdb -O {0} -w {1}".format("db-user", "db")

    def _sudo_su_session_cmd(cmd, user='postgres'):
        run('sudo su --session-command="{0}" {1};'.format(cmd, user))

    # recreate (drop+create) db
    _sudo_su_session_cmd("{0}; {1};".format(dropdb_cmd, createdb_cmd))
    # applies db_backup_file
    _sudo_su_session_cmd("gunzip -c {0} | psql db;".format(remote_tmp))

    print 'Restore complete. You may also need to rebuild search indexes.'


@task
def enable_db_log_all():
    """ Logs all postgresql statements """
    c = 'perl -pi -e '
    c += '"s/log_min_duration_statement = .*/log_min_duration_statement = 0/" '
    sudo('{0} {1}'.format(c, env.db_conf_file))
    service('reload', 'postgresql')


@task
def disable_db_log_all():
    """ Disables above task """
    c = 'perl -pi -e '
    c += '"s/log_min_duration_statement = .*/log_min_duration_statement = -1/"'
    sudo('{0} {1}'.format(c, env.db_conf_file))
    service('reload', 'postgresql')


@task
def poll_memcached():
    run('echo stats | nc 127.0.0.1 11211')


@task
def supervisorctl(action, program=''):
    with cd(env.venv_root):
        sudo('bin/supervisorctl -c {0} {1} {2}'.format(
            env.supervisord_file, action, program))


@task
def service(action, program):
    sudo('service {0} {1}'.format(program, action))


@task
def deploy_static_assets():
    manage('collectstatic --noinput')
    manage('compress')

    upload_script = '/'.join([t.rstrip('/') for t in (env.deploy_root,
                                                      'aws',
                                                      'upload_static_s3.py')])
    #static_folder = os.path.abspath(static_folder)
    run('python {0} {1}'.format(upload_script, env.public_static_root))


def _install_requirements(requirements_file, update=False):
    additional_args = ['', '-U'][update]
    with cd(env.src_root):
        run('pip install {0} -r {1}'.format(additional_args,
                                            requirements_file))


@task
def update_supervisor():
    """
    Config and start supervisor

    Updates supervisor with the append_filename template supervisor conf file
    append_filename path is resolved relative to local_env.etc_root

    context is an additional context dictionary to populate the template

    """
    context = {'env': env, 'solr': solr}

    #supervisor configuration
    file_name = 'supervisord.conf'
    with open(os.path.join(local_env.etc_root, file_name)) as fd:
        config = fd.read().format(**context)
    run('mkdir -p {0} && rm -f {1}'.format(env.etc_root,
                                           env.supervisord_file))
    append(env.supervisord_file, config)

    #supervisor is gonna be managed by upstart (/etc/init/)
    file_name = 'supervisor_upstart.conf'
    with open(os.path.join(local_env.etc_root, file_name)) as f:
        config = f.read().format(**context)
        append('/tmp/{0}'.format(file_name), config)
    sudo('mv /tmp/{0} /etc/init/supervisor.conf'.format(file_name))

    #supervisor restart
    if 'run' in sudo('status supervisor'):
        sudo('stop supervisor')
    sudo('start supervisor')


@task
def update_cronjob(context=None):
    """
    Overrides server cronjobs w/ local file
        ./etc/main.cron

    appends is a list of cron template files (relative to local_env.etc_root)
    with contents to add to the main.cron file.
    appends can also be a single file name (string).

    context is an additional context dictionary to populate the template

    """
    context = {'env': env, 'solr': solr}

    file_name = 'main.cron'
    with open(os.path.join(local_env.etc_root, file_name)) as fd:
        config = fd.read().format(**context)
    with open('/tmp/{0}'.format(file_name), 'w') as f:
        f.write(config)

    put('/tmp/{0}'.format(file_name), '/tmp/{0}'.format(file_name))
    sudo('mv /tmp/{0} /etc/{0}'.format(file_name))

    with cd('/etc'):
        sudo('crontab main.cron')


@task
def update_profile():
    """
    Updates the ~/.profile file which is sourced by ~/.bash_profile.
    Everything inside of ~ /.profile is guaranteed to be available on the
    unix shell session and python work session.

    Also, immeditely updates the current session by doing a source on
    the fresh profile file.

    """
    def _set_export_secret_file(filepath):
        run('python {0} > {1}'.format(filepath, env.profile_secret_file))

    # updates default profile path and variables
    with open(os.path.join(local_env.etc_root, 'profile.bash')) as f:
        contents = f.read().format(**{'env': env})
        run('rm -f {0}; touch {0}'.format(env.profile_file))
        append(env.profile_file, contents)
        _set_export_secret_file(env.secret_file)

    run('source {0}'.format(env.profile_file))


#def _set_search_path_permissions():
    #"""
    #Search index path should be writable from any user/group
    #"""
    #search_index_path = '{0}apps/search/whoosh-index/'.format(env.src_root)
    #sudo('chmod -R 777 {0}'.format(search_index_path))


def _build_tmp_compressed_cookbooks(chef_name):
    chef_archive = '{0}.tar.gz'.format(chef_name)
    local('cp -r {0} /tmp/{1}'.format(local_env.chef_root, chef_name))
    local("cp node.json /tmp/{0}/node.json".format(chef_name))

    solo_rb = ('file_cache_path "/tmp/chef-solo"',
               'cookbook_path "/tmp/{0}/cookbooks"'.format(chef_name))
    with lcd('/tmp'):
        for line in solo_rb:
            local("echo '{0}' >> {1}/solo.rb".format(line, chef_name))
        local('tar czf {0} {1}'.format(chef_archive, chef_name))

    return chef_archive


def _unzip_tmp_compressed_cookbooks_on_server(chef_archive):
    put('/tmp/{0}'.format(chef_archive), '/tmp/{0}'.format(chef_archive))
    with cd('/tmp'):
        run('tar xf {0}'.format(chef_archive))


def _chef_provision(chef_name):
    with cd('/tmp/{0}'.format(chef_name)):
        with settings(warn_only=True):
            sudo('chef-solo -c solo.rb -j node.json')


def _delete_tmp_compressed_cookbooks(chef_name):
    local('rm -rf /tmp/{0}*'.format(chef_name))
    run('rm -rf /tmp/{0}*'.format(chef_name))


@task
def update_src_code(secret=False):
    with cd(env.project_root):
        run('git pull origin master')
    if secret:
        send_secret_files()


@task
def send_secret_files():
    #send extra files (not public on github)
    if os.path.exists(local_env.secret_file):
        put(local_env.secret_file, env.secret_file)
    else:
        print "[WARN] No local {0} secret file".format(local_env.secret_file)


@task
def fix_sftp_server():
    """
    Sometimes sftp server starts to close connections in some undefined way.
    If you start to see ssh.SSHException: Channel closed on your fabric cmds,
    run this task and try again
    """
    cmd = """
import os
config = ''
sshd_path = '/etc/ssh/sshd_config'
with open(sshd_path) as f:
    config = f.read()
config = config.replace('Subsystem sftp /usr/lib/openssh/sftp-server',
                        'Subsystem sftp internal-sftp')
with open(sshd_path, 'w') as f:
    f.write(config)
    """
    sudo('python<<EOF\n{0}\nEOF'.format(cmd))
    sudo('/etc/init.d/sshd restart')
    sudo('/etc/init.d/sshd restart')


@task
def swapon():
    """
    Turns on swapping on the aws instance (default is off)
    Actually this does not create a whole partition.
    We are goint to fake a swap partition with a 1024MB file,
    initially zero (/dev/zero)

    This approach is recommended for some emergencial high-memory usage tasks,
    like inserting a huge batch of elements into postgresql at once.

    Thanks to:
    serverfault.com/questions/218750/why-ec2-ubuntu-images-dont-have-swap

    """
    swapfile = '/var/swapfile'
    sudo('dd if=/dev/zero of={0} bs=1M count=1024'.format(swapfile))
    sudo('chmod 600 {0}'.format(swapfile))
    sudo('mkswap {0}'.format(swapfile))
    sudo('echo {0} none swap defaults 0 0 '.format(swapfile) + \
         ' | tee -a /etc/fstab')
    sudo('swapon -a')
    # print report
    run('cat /etc/fstab')
    run('df -h')


@task
def swapoff():
    """ Reverses back the above function (disables swapping) """
    swapfile = '/var/swapfile'
    sudo('swapoff -a')
    sudo('rm -f {0}'.format(swapfile))
