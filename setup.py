#!/usr/bin/env/python
# Program: Setup Event Collector MVision ePO
# Author: Cristian Rebollo Castillo

import configparser
import argparse
import textwrap
import os
from base64 import b64encode

# Function to show help on console
def help():

    helpy = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description= textwrap.dedent("""
            This script is intended to configure Mvision ePO Collector. 
            
            The SCOPE that can be used are the following:
            
                - epo.admin 
                - epo.adit.r 
                - epo.qery.g 
                - epo.resp.ru 
                - epo.pevt.r 
                - epo.ubp.r 
                - epo.sdlr.r 
                - epo.dir.a 
                - epo.evt.r 
                - epo.dxlc.r 
                - epo.eagt.r 
                - epo.eagt.tr 
                - epo.dash.r 
                - ens.comn.r 
                - ens.comn.vs 
                - ens.fw.r 
                - ens.fw.vc 
                - ens.fw.vr 
                - ens.fw.vp 
                - ens.fw.vs 
                - ens.wp.tr 
                - ens.wp.r 
                - ens.wp.vs 
                - ens.atp.vs 
                - ens.atp.r 
                - ens.am.r 
                - ens.am.tr 
                - ens.am.vs 
                - ens.am.ve 
                - ens.vrs.r 
                - ens.vrs.tr 
                - mvs.endp.r 
                - epo.reg_token
            
            Usage example multi-scope: epo.admin epo.adit.r epo.qery.g etc ...""")
    )
    helpy.parse_args()

# Function to configure conf file
def setup():

    while True:

        os.system('clear')
        print(textwrap.dedent('''\
                    #----------------------------------------------------------------------------------#
                    #                        Setup McAfee Mvision ePO Collector                        #
                    #----------------------------------------------------------------------------------#
                    #                                                                                  #
                    # For view Mvision Client ID, signin on https://auth.ui.mcafee.com/support.html    #
                    # Available Scopes with help [-h]                                                  #
                    # If you want edit event directory or scope, edit settings.cfg                     #
                    #----------------------------------------------------------------------------------#
                    ''')
              )

        client = input("+ Client name: ").upper()
        client_id = input("+ Client ID: ")
        epo_user  = input("+ Username: ")
        epo_pass  = input("+ Password: ")
        epo_scope = "epo.adit.r epo.qery.g epo.pevt.r epo.dir.a epo.evt.r epo.dash.r ens.comn.vs ens.fw.vs ens.wp.vs ens.atp.vs ens.am.vs ens.am.ve openid" #input("+ Scope: ")
        dir_events  = input("+ Events directory (absolute path): ")

        validate = ""

        if not dir_events.endswith("/"):
            dir_events = dir_events + "/"

        if not (client and client_id and epo_user and epo_pass and epo_scope and dir_events):
            print("\n------------------------------------------------------------------------------------")
            print("ERROR - You did not enter any data")
            print("------------------------------------------------------------------------------------")
            input("\nPress Enter to continue...")

        else:
            while validate != "y" and validate != "n":
                validate = input("\n[!] Is it correct? [y/n]: ")

            if validate == "y":
                break

    return client, client_id, epo_user, epo_pass, epo_scope, dir_events

def parser():

    if not os.path.isdir('./conf'):
        os.system('mkdir conf')

    cfgfile = open("./conf/{}.cfg".format(data[0]), "w")

    config = configparser.ConfigParser()
    config.add_section('MVISION_DATA')
    config.set('MVISION_DATA', 'client', data[0])
    config.set('MVISION_DATA', 'client_id', b64encode(data[1].encode()).decode())
    config.set('MVISION_DATA', 'epo_user', b64encode(data[2].encode()).decode())
    config.set('MVISION_DATA', 'epo_pass', b64encode(data[3].encode()).decode())
    config.set('MVISION_DATA', 'epo_scope', data[4])
    config.set('MVISION_DATA', 'dir_events', data[5])
    config.set('MVISION_DATA', 'state', "0")
    config.set('MVISION_DATA', 'last_since', "0")

    config.write(cfgfile)
    cfgfile.close()

if __name__ == "__main__":

    try:
        help()
        data = setup()
        parser()
    except KeyboardInterrupt:
        exit()
