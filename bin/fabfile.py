#!/usr/bin/env python

import os
import tempfile
import time
import hashlib

from fabric.api import *

_DELIMITER = '|'

def push_users(statedir=None):
    if not 'nimbus_userlist' in env:
        env['nimbus_userlist'] = _get_userlist()
    userlist_text = env['nimbus_userlist']

    if not 'nimbus_userlist_md5' in env:
        env['nimbus_userlist_md5'] = hashlib.md5(env['nimbus_userlist']).hexdigest()
    userlist_md5 = env['nimbus_userlist_md5']

    assert userlist_text
    assert userlist_md5

    if statedir:
        assert os.path.exists(statedir)
        statefile = os.path.join(statedir, 'lastupdate_'+env.host)
        try:
            f = None
            try:
                f = open(statefile)
                lastupdate_md5 = f.read().strip()
            finally:
                if f:
                    f.close()
        except:
            lastupdate_md5 = None

        if lastupdate_md5 == userlist_md5:
            print "Not updating because MD5 is the same"
            return

    remote_temp = None
    fd, path = tempfile.mkstemp()
    try:
        f = os.fdopen(fd, 'w')
        f.write(userlist_text)
        f.close()
        
        assert userlist_md5 == local('md5sum ' + path).split()[0]
        
        remote_temp = '~/.nimbus_users_tmp_' + str(int(time.time()))
        put(path, remote_temp)
        assert userlist_md5 == run('md5sum ' + remote_temp).split()[0]

        run('~/2.5/bin/nimbus-import-users -d --batch -D "%s" %s ' % (_DELIMITER, remote_temp))

        if statedir:
            try:
                f = None
                try:
                    f = open(statefile, 'w')
                    f.write(userlist_md5)
                finally:
                    if f:
                        f.close()
            except:
                print "Failed to write state file! "+ statefile

    finally:
        os.unlink(path)

        if remote_temp:
            run('rm -f '+remote_temp)

def _get_userlist():
    return local('nimbus-list-users -D "%s" --batch %%' % _DELIMITER)
