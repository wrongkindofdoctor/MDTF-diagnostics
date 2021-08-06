#!/usr/bin/env python3
""" run the MDTF-diagnostics docker container on the parallelWorks platform """
import os
import docker

USER = "Jessica.Liptak@"
MDTF_ROOT = os.path.join("/pw","storage","mdtf")
print(MDTF_ROOT)
volume_list = {os.path.join(MDTF_ROOT,"inputdata"): {'bind': '/proj/inputdata', 'mode': 'ro'}, \
   os.path.join(MDTF_ROOT,"wkdir"): {'bind': '/proj/wkdir', 'mode': 'rw'}, \
   os.path.join(MDTF_ROOT,"MDTF-diagnostics/diagnostics"): {'bind': '/proj/MDTF-diagnostics/diagnostics', 'mode': 'ro'}, \
   os.path.join(MDTF_ROOT,"MDTF-diagnostics/src"): {'bind': '/proj/MDTF-diagnostics/src', 'mode': 'ro'}, \
   os.path.join(MDTF_ROOT,"MDTF-diagnostics/mdtf_framework.py"): {'bind': '/proj/MDTF-diagnostics/mdtf_framework.py', 'mode': 'ro'}, \
   os.path.join(MDTF_ROOT,"MDTF-diagnostics/mdtf"): {'bind': '/proj/MDTF-diagnostics/mdtf', 'mode': 'ro'}, \
   }

client = docker.from_env()

mdtf_container = client.containers.run('wrongkindofdoctor/mdtf.alpha-01:latest', \
   ['mdtf -f ' + MDTF_ROOT + '/MDTF-diagnostics/src/default_tests.jsonc -v'], \
    volumes=volume_list, \
    detach=True, \
    entrypoint="/proj/MDTF-diagnostics/mdtf")

# print log information
logs = mdtf_container.logs(stream=True)
for line in logs:
    print(line)

