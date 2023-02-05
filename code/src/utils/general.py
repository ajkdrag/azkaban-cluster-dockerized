import io
import os
import yaml
import uuid
import joblib
import pandas as pd
import utils.s3_utils as s3_utils
from pathlib import Path


def generate_runid():
    return str(uuid.uuid4())


def read_yaml(yaml_path):
    if yaml_path.startswith("s3"):
        stream = s3_utils.stream_file(yaml_path)
        obj = yaml.safe_load(stream)
    else:
        with open(yaml_path) as stream:
            obj = yaml.safe_load(stream)
    return obj


def read_csv(csv_path, **kwargs):
    if csv_path.startswith("s3"):
        contents = io.BytesIO(s3_utils.stream_file(csv_path).read())
        df = pd.read_csv(contents, **kwargs)
    else:
        df = pd.read_csv(csv_path, **kwargs)
    return df


def read_pkl(pkl_path):
    if pkl_path.startswith("s3"):
        contents = io.BytesIO(s3_utils.stream_file(pkl_path).read())
        obj = joblib.load(contents)
    else:
        obj = joblib.load(pkl_path)
    return obj


def write_pkl(obj, filepath):
    localpath = Path(filepath).name if filepath.startswith("s3") else filepath
    Path(localpath).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, localpath)
    if filepath.startswith("s3"):
        s3_utils.upload_file(localpath, filepath)
        os.remove(localpath)


def write_csv(df, filepath):
    localpath = Path(filepath).name if filepath.startswith("s3") else filepath
    Path(localpath).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(localpath, index=False)
    if filepath.startswith("s3"):
        s3_utils.upload_file(localpath, filepath)
        os.remove(localpath)

def generic_write(write_list):
    write_dict = {
        "pickle": write_pkl,
        "csv": write_csv,
    }

    for stuff in write_list:
        obj, filepath, write_type = stuff
        write_dict[write_type](obj, filepath)
        

def generic_read(read_list):
    read_dict = {
        "pickle": read_pkl,
        "csv": read_csv,
        "yaml": read_yaml,
    }

    read_items = []
    for stuff in read_list:
        filepath, read_type = stuff
        reader = read_dict[read_type]
        read_items.append(reader(filepath))
    return read_items
