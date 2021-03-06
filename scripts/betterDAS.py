#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import time
import logging
import argparse
import itertools
import fnmatch

logging.basicConfig(level=logging.INFO, stream=sys.stderr)

# DBS modules
try:
    from dbs.apis.dbsClient import DbsApi
    dbsLoaded = True
except:
    dbsLoaded = False

def dataset_client(args):

    if not dbsLoaded:
        logging.error('You must source a crab environment to use DBS API.\nsource /cvmfs/cms.cern.ch/crab3/crab.sh')
        return

    url = 'https://cmsweb.cern.ch/dbs/prod/{0}/DBSReader'.format(args.instance)
    dbsclient = DbsApi(url)

    sortType = {
        'name': 'dataset',
        'time': 'last_modification_date',
    }

    if args.datasets:
        datasets = []
        for dataset in args.datasets:
            datasets += dbsclient.listDatasets(dataset=dataset,detail=True)
        for d in sorted(datasets, key=lambda k: k[sortType[args.sortOrder]]):
            print(d['dataset'])

    if args.primaryDatasets or args.acquisitionEras or args.processNames or args.dataTiers:
        pds = args.primaryDatasets if args.primaryDatasets else ['']
        aes = args.acquisitionEras if args.acquisitionEras else ['']
        dts = args.dataTiers if args.dataTiers else ['']
        datasets = []
        for pd, ae, dt in itertools.product(pds, aes, dts):
            kwargs = {}
            if pd: kwargs['primary_ds_name'] = pd
            if ae: kwargs['acquisition_era_name'] = ae
            if dt: kwargs['data_tier_name'] = dt
            kwargs['detail'] = True
            datasets += dbsclient.listDatasets(**kwargs)
        for d in sorted(datasets, key=lambda k: k[sortType[args.sortOrder]]):
            if args.processNames:
                if not any([fnmatch.fnmatch(d['processed_ds_name'],pn) for pn in args.processNames]): continue
            print(d['dataset'])
    
def file_client(args):

    if not dbsLoaded:
        logging.error('You must source a crab environment to use DBS API.\nsource /cvmfs/cms.cern.ch/crab3/crab.sh')
        return

    url = 'https://cmsweb.cern.ch/dbs/prod/{0}/DBSReader'.format(args.instance)
    dbsclient = DbsApi(url)

    if args.datasets:
        files = []
        for dataset in args.datasets:
            files += dbsclient.listFiles(dataset=dataset)
        for f in sorted(files, key=lambda k: k['logical_file_name']):
            print(f['logical_file_name'])

def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Get information from DBS')

    subparsers = parser.add_subparsers(help='Return type')

    # return a list of datasets
    parser_dataset = subparsers.add_parser('dataset', help='Return a list of datasets.')

    # full dataset path
    dataset_dataset = parser_dataset.add_argument_group(description='Full dataset name. Dataset form: /[primaryDataset]/[processName]/[dataTier]')
    dataset_dataset.add_argument('--datasets', type=str, nargs="*", help='Dataset names')
    # partial paths
    dataset_components = parser_dataset.add_argument_group(description='Dataset components')
    dataset_components.add_argument('--primaryDatasets', type=str, nargs="*", default=[], help='Primary dataset names')
    dataset_components.add_argument('--acquisitionEras', type=str, nargs="*", default=[], help='Acquisition era for datasets')
    dataset_components.add_argument('--processNames', type=str, nargs="*", default=[], help='Process name')
    dataset_components.add_argument('--dataTiers', type=str, nargs="*", default=[], help='Data tiers for dataset')

    # isntance
    dataset_instance = parser_dataset.add_argument('--instance', type=str, nargs='?', choices=['global','phys01','phys02','phys03','caf'], default='global', help='Use non-default DBS instance')

    parser_dataset.set_defaults(submit=dataset_client)

    # sort order
    parser_dataset.add_argument('--sortOrder', type=str, nargs='?', default='name', choices=['name','time'], help='Define output sort order')

    # return a list of files
    parser_file = subparsers.add_parser('files', help='Return a list of files.')

    file_dataset = parser_file.add_argument('--datasets', type=str, nargs="*", help='Dataset names')

    # isntance
    file_instance = parser_file.add_argument('--instance', type=str, nargs='?', choices=['global','phys01','phys02','phys03','caf'], default='global', help='Use non-default DBS instance')

    parser_file.set_defaults(submit=file_client)

    return parser.parse_args(argv)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    args.submit(args)

if __name__ == "__main__":
    status = main()
    sys.exit(status)
