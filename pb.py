#!/usr/bin/env python

import os
import ansible.playbook

from ansible import utils
from ansible import callbacks
from ansible import inventory
from ansible.callbacks import display
from ansible.color import ANSIBLE_COLOR, stringc


def colorize(lead, num, color):
    """
    Print 'lead' = 'num' in 'color'
    :param lead:
    :param num:
    :param color:
    """
    if num != 0 and ANSIBLE_COLOR and color is not None:
        return '%s%s%-15s' % (stringc(lead, color), stringc('=', color),
                              stringc(str(num), color))
    else:
        return '%s=%-4s' % (lead, str(num))


def hostcolor(host, stats, color=True):
    """
    Print the status colors
    :param host: The hostname
    :param stats: The stats from the ansible run
    :param color: Boolean for if colors should be shown
    """
    if ANSIBLE_COLOR and color:
        if stats['failures'] != 0 or stats['unreachable'] != 0:
            return '%-37s' % stringc(host, 'red')
        elif stats['changed'] != 0:
            return '%-37s' % stringc(host, 'yellow')
        else:
            return '%-37s' % stringc(host, 'green')
    return '%-26s' % host


def main():
    """
    A fake main method
    """
    server_object = vendor.provision()
    run_playbook(server_object.name, '/PATH/TO/PLAYBOOK/sample.yml')


def run_playbook(subset=None, pb_to_run=None, forks=5, retry=True):
    """
    This is just a simple method to run playbooks
    :param subset: The subset of hosts
    :param pb_to_run: The full path to the playbook to run
    :param forks: The number of forks
    :param retry: Should we attempt a retry?
    """
    # Initiate the inventory
    im = inventory.Inventory('/etc/ansible/hosts')
    im.subset(subset)

    # Get the playbook
    im.set_playbook_basedir(os.path.dirname(pb_to_run))
    hosts = im.list_hosts(subset)
    failed_hosts = list()

    # Fail for no hosts
    if len(hosts) == 0:
        raise Exception('Unable to automatically do %s run.' % pb_to_run)

    # Make sure we aggregate the stats
    stats = callbacks.AggregateStats()

    # Initiate an instance of the playbook class
    pb = ansible.playbook.PlayBook(
        inventory=im,
        playbook=pb_to_run,
        callbacks=callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY),
        runner_callbacks=callbacks.PlaybookRunnerCallbacks(stats,
                                                           verbose=utils.VERBOSITY),
        stats=stats,
        forks=forks
    )

    # Run the playbook
    print 'Beginning %s run against hosts...' % pb_to_run
    pb.run()
    print 'Playbook run completed...\n'

    # Sort the hosts
    hosts = sorted(pb.stats.processed.keys())
    for h in hosts:
        t = pb.stats.summarize(h)
        if t['unreachable'] > 0 or t['failures'] > 0:
            raise Exception('%s - %s has failed.' % (h, pb_to_run))
        display('%s : %s %s %s %s' % (
            hostcolor(h, t, False),
            colorize('ok', t['ok'], 'green'),
            colorize('changed', t['changed'], 'yellow'),
            colorize('unreachable', t['unreachable'], 'red'),
            colorize('failed', t['failures'], 'red')),
            screen_only=True
        )
        if t['unreachable'] > 0 or t['failures'] > 0:
            if retry:
                print ('%s - %s has failed. One retry will be attempted'
                       % (h, pb_to_run))
            else:
                raise Exception('%s - %s has failed.' % (h, pb_to_run))
            failed_hosts.append(h)
    # Only return on failed hosts
    if len(failed_hosts) > 0 and retry:
        failed_hosts = ':'.join(failed_hosts)
        run_playbook(subset=failed_hosts, pb_to_run=pb_to_run, retry=False)

    # Return the playbook object
    return pb


if __name__ == "__main__":
    main()

