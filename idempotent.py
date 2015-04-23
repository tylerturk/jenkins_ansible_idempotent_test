#!/usr/bin/env python

import pb

from sys import exit


def header():
    print '\n'
    print '-' * 80


if __name__ == '__main__':
    header()

    print 'Doing first run (idempotent)...'
    playbook = pb.run_playbook(subset='all', pb_to_run='lineinfile.yml')

    for h in sorted(playbook.stats.processed.keys()):
        t = playbook.stats.summarize(h)
        if t['changed'] != 0:
            print '\n\n* Got changes on first run. This was expected.'

    header()

    print 'Doing second run (idempotent)...'
    playbook = pb.run_playbook(subset='all', pb_to_run='lineinfile.yml')

    for h in sorted(playbook.stats.processed.keys()):
        t = playbook.stats.summarize(h)
        if t['changed'] != 0:
            raise Exception('Playbook is not idempotent. Still has changes.')
        else:
            print 'Congratulations! Your playbook is idempotent!'

    header()

    print 'Doing first run (non-idempotent)...'
    playbook = pb.run_playbook(subset='all', pb_to_run='touch_file.yml')

    for h in sorted(playbook.stats.processed.keys()):
        t = playbook.stats.summarize(h)
        if t['changed'] != 0:
            print '\n\n* Got changes on first run. This was expected.'

    header()

    print 'Doing second run (non-idempotent)...'
    playbook = pb.run_playbook(subset='all', pb_to_run='touch_file.yml')

    for h in sorted(playbook.stats.processed.keys()):
        t = playbook.stats.summarize(h)
        if t['changed'] != 0:
            raise Exception('Playbook is not idempotent. Still has changes.')
        else:
            print 'Congratulations! Your playbook is non-idempotent!'

    print '-' * 80
