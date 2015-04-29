#!/usr/bin/env python

import pb
import json

from os import path
from sys import exit
from argparse import ArgumentParser


def header():
    print '\n'
    print '-' * 80


if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument('-p', '--playbook', default=None, required=True)

    args = p.parse_args()

    header()

    print 'Doing first run (idempotent)...'
    playbook = pb.run_playbook(subset='all', pb_to_run=args.playbook)

    for h in sorted(playbook.stats.processed.keys()):
        t = playbook.stats.summarize(h)
        if t['changed'] != 0:
            print '\n\n* Got changes on first run. This was expected.'

    header()

    print 'Doing second run (idempotent)...'
    playbook = pb.run_playbook(subset='all', pb_to_run=args.playbook)

    for h in sorted(playbook.stats.processed.keys()):
        t = playbook.stats.summarize(h)
        if t['changed'] != 0:
            print "\n\n"
            if path.exists('runner_stats.json'):
                with open('runner_stats.json') as f:
                    runner_stats = json.loads(f.read())
                raise Exception("Playbook '%s' is NOT idempotent. Following tasks result in change: \n%s"
                                % (args.playbook, "\n".join([x.get('task_name') for x in runner_stats])))
            raise Exception('Playbook is not idempotent. Still has changes.')
        else:
            print 'Congratulations! Your playbook is idempotent!'

    print '-' * 80
