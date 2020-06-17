"""
This file is used to control all dependencies with Tribler.

Other files should never have a direct import from Tribler, as this reduces the maintainability of this code.
If Tribler alters its call methods, this should be the only file which needs to be updated in PlebNet.
"""

import os
import subprocess
import threading

import requests

from requests.exceptions import ConnectionError
from src.run_tribler import start_tribler_core
from tribler_core.utilities.osutils import get_root_state_directory

from plebnet.utilities import logger
from plebnet.settings import plebnet_settings

setup = plebnet_settings.get_instance()


def running():
    """
    Checks if Tribler is running.
    :return: True if tribler.service is active.
    """

    output = subprocess.run(['systemctl', 'is-active', 'tribler.service'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    process_running = (output == 'active\n')

    print("process_running was: " + str(process_running))

    return process_running


def start():
    """
    Starts Tribler by using the twistd plugin.
    :return: boolean representing the success of starting Tribler
    """
    env = os.environ.copy()
    # env['PYTHONPATH'] = os.path.join(setup.plebnet_home(), 'plebnet') + ":"
    # #env['PYTHONPATH'] += os.path.join(setup.plebnet_home(), 'plebnet/twisted/plugins') + ":"
    # env['PYTHONPATH'] += os.path.join(setup.plebnet_home(), 'tribler/src/pyipv8') + ":"
    # env['PYTHONPATH'] += os.path.join(setup.plebnet_home(), 'tribler/src/anydex') + ":"
    # env['PYTHONPATH'] += os.path.join(setup.plebnet_home(), 'tribler/src/tribler-common') + ":"
    # env['PYTHONPATH'] += os.path.join(setup.plebnet_home(), 'tribler/src/tribler-core')
    
    #print(env['PYTHONPATH'])

    command = ['systemctl', 'start', 'tribler.service']

    # if setup.wallets_testnet():
    #     command.append('--testnet')
    #
    # if setup.tribler_exitnode():
    #     command.append('--exitnode')

    try:
        exitcode = subprocess.call(command, cwd=os.path.join(setup.plebnet_home(), 'plebnet'), env=env)

        print("Exitcode was: " + str(exitcode))

        if exitcode != 0:
            logger.error('Failed to start Tribler', "tribler_controller")
            return False
        logger.success('Tribler is started', "tribler_controller")
        logger.log('testnet: ' + str(setup.wallets_testnet()))
        return True
    except subprocess.CalledProcessError as e:
        logger.error(e.output, "tribler_controller")
        return False


def get_uploaded():
    try:
        tu = requests.get('http://localhost:8085/trustchain/statistics').json()['statistics']['total_up']
        tu = int(tu)/1024.0/1024.0
        return tu
    except ConnectionError:
        return "Unable to retrieve amount of uploaded data"


def get_helped_by():
    try:
        return requests.get('http://localhost:8085/trustchain/statistics').json()['statistics']['peers_that_helped_pk']
    except ConnectionError:
        return "Unable to retrieve amount of peers that helped this agent"


def get_helped():
    try:
        return requests.get('http://localhost:8085/trustchain/statistics').json()['statistics']['peers_that_pk_helped']
    except ConnectionError:
        return "Unable to retrieve amount of peers helped by this agent"


def get_downloaded():
    try:
        td = requests.get('http://localhost:8085/trustchain/statistics').json()['statistics']['total_down']
        td = int(td)/1024.0/1024.0
        return td
    except ConnectionError:
        return "Unable to retrieve amount of downloaded data"
