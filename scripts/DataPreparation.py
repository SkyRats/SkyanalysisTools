import os
import io
import shutil
import pandas as pd
from tabulate import tabulate

PROJECT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
TMP_DIR = os.path.join(PROJECT_DIR, 'tmp')
LOGS_DIR = os.path.join(PROJECT_DIR, 'logs')

def check_dir(dir):
    """
    Verifies if a directory exists and, if not, it is created

    Parameters
    ----------
    dir: str
        Target directory
    """

    e = os.path.exists(dir)
    if not e:
        print("Creating directory", dir)
        os.makedirs(dir)
    return e

def process_ulg(filepath):
    """Converts a .ulg file into CSV files and split them into the corresponding folders

    Parameters
    ----------
    filepath: str
        Absolute filepath to the ULOG file to be processed
    """

    print("Processing", filepath)
    # Check is csv temporary folder exists and is empty
    csv_dir = os.path.join(TMP_DIR, 'csv')
    e = check_dir(csv_dir)
    if e and not os.listdir(csv_dir):
        print("Directory", csv_dir, "not empty, deleting all contents")
        for f in os.listdir(csv_dir):
            os.remove(os.path.join(csv_dir, f))

    # Convert ulg to csv
    print("Converting ulg to csv")
    os.system(f"ulog2csv -o {csv_dir} {filepath}")

    #Adiciona a tabela        
    pd.read_csv('/home/skyrats/SkyanalysisTools/Tabela.csv')


    # Moving csv to folders 
    print("Moving files to appropriate folders")
    filename = os.path.basename(filepath)[:-4]
    for csv in os.listdir(csv_dir):
        log_dir = os.path.join(LOGS_DIR, csv[len(filename)+1:-4])
        check_dir(log_dir)
        # TODO: No momento o programa não confere se o arquivo já existe. O que fazer?
        shutil.move(os.path.join(csv_dir, csv), os.path.join(log_dir, f'{filename}.csv')) 

            
    # Move ulg to folder
    ulg_dir = os.path.join(LOGS_DIR, 'ulg')
    check_dir(ulg_dir)
    shutil.move(filepath, os.path.join(ulg_dir, f'{filename}.ulg'))
    print("Done!")

def process_all(unprocessed_dir):
    """ Passes 'unprocessed_dir' as parameter to function 'process_ulg' 

    Parameters
    ----------
    unprocessed_dir: str
        Auxiliar folder created in order to support converting
    """
    for f in os.listdir(unprocessed_dir):
        if f != ".gitkeep":
            process_ulg(os.path.join(unprocessed_dir, f))

def main():
    process_all(os.path.join(PROJECT_DIR, 'unprocessed'))


