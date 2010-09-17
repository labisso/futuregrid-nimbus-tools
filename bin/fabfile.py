#!/usr/bin/env python

import os
import tempfile
import time

from fabric.api import *

_DELIMITER = '|'

def push_users():
    if not 'nimbus_userlist' in env:
        env['nimbus_userlist'] = _get_userlist()
    userlist_text = env['nimbus_userlist']
    assert userlist_text

    remote_temp = None
    fd, path = tempfile.mkstemp()
    try:
        f = os.fdopen(fd, 'w')
        f.write(userlist_text)
	f.close()

        remote_temp = '~/.nimbus_users_tmp_' + str(int(time.time()))
        put(path, remote_temp)

        run('~/2.5/bin/nimbus-import-users -d --batch -D "%s" %s ' % (_DELIMITER, remote_temp))

    finally:
        os.unlink(path)

        if remote_temp:
            run('rm -f '+remote_temp)

def _get_userlist():
    return local('nimbus-list-users -D "%s" --batch %%' % _DELIMITER)
