import os
import re
import shutil
import pandas as pd
import px4tools

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


def register_log(filepath):
    """
    Registers the log in 'filepath'
    """
    print("Attempting to register log", filepath)

    try:
        meta = pd.read_csv(
            os.path.join(LOGS_DIR, 'metadata.csv'),
            index_col='id'
        )
        print("Opened metadata.csv")
        print(meta)
    except FileNotFoundError:
        meta = pd.DataFrame(
            {
                'timestamp': pd.Series(dtype='datetime64[ns]'),
                'drone': pd.Series(dtype='str'),
                'FCU': pd.Series(dtype='str'),
                'id_orig': pd.Series(dtype='int'),
            },
            index=pd.Index([], name='id')
        )
        # meta.index.rename('id')
        print("Creating metadata.csv")
        print(meta)
    id = len(meta.index)
    
    # Extracts information from log name
    filename = os.path.basename(filepath)
    m = re.search('log_(\d+)_(\d+)-(\d+)-(\d+)-(\d+)-(\d+)-(\d+).ulg', filename)
    if not m:
        raise ValueError("Invalid file name. Logs are named as 'log_id_year_month_day_hour_minute_second.ulg'")
    id_orig = int(m.group(1))
    year = int(m.group(2))
    month = int(m.group(3))
    day = int(m.group(4))
    hour = int(m.group(5))
    minute = int(m.group(6))
    second = int(m.group(7))
    
    # Initializes Series object
    new_row = pd.Series(dtype='object', name=id)
    new_row['timestamp'] = pd.Timestamp(year, month, day, hour, minute, second)
    print("Log collected in", new_row['timestamp'])
    new_row['id_orig'] = id_orig
    print("Original id was", new_row['id_orig'])

    # Registers the topics
    log = px4tools.read_ulog(filepath)
    print("Adding bool columns")
    for k in log.keys():
        # print("\t", k)
        new_row[k] = True
        if k not in meta:
            print("\t", k)
            meta[k] = pd.Series([False]*len(meta.index), dtype='bool')
    for k in meta:
        if k[:2]=='t_' and k not in new_row:
            new_row[k] = False
    
    print("Adding row to metadata.csv")
    meta = meta.append(new_row)
    meta.to_csv(os.path.join(LOGS_DIR, 'metadata.csv'))
    print(meta)

    print("Moving log to logs folder, renamed to", f'log_{id:04d}.ulg')
    shutil.move(filepath, os.path.join(LOGS_DIR, f'log_{id:04d}.ulg')) 

def register_all(unprocessed_dir):
    for f in os.listdir(unprocessed_dir):
        if f != ".gitkeep":
            register_log(os.path.join(unprocessed_dir, f))

# def main():
#     process_all(os.path.join(PROJECT_DIR, 'unprocessed'))


if __name__ == '__main__':
    # filepath = r'D:\Documentos\Skyrats\SkyanalysisTools\unprocessed\log_0_2021-1-24-16-42-42.ulg'
    # filepath = r'D:\Documentos\Skyrats\SkyanalysisTools\unprocessed\log_21_2021-8-12-18-27-34.ulg'
    # register_log(filepath)
    register_all(os.path.join(PROJECT_DIR, 'unprocessed'))
