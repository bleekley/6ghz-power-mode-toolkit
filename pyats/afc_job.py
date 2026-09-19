import os
from genie.harness.main import gRun

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    gRun(trigger_datafile=os.path.join(here, 'afc_monitor.yaml'),
         mapping_datafile=os.path.join(here, 'mapping.yaml'),
         subsection_datafile=os.path.join(here, 'subsections.yaml'),
         trigger_uids=['AfcReadiness'])
