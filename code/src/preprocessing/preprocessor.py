import os
import click
import logging
import joblib
import pathlib
import utils.logger as logger
import utils.general as general
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.base import BaseEstimator
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.compose import ColumnTransformer

LOG = None


def setup_logging():
    log_handler = logger.Logger()
    log_handler.setup()


def create_pipeline(config_data):
    sms_col = config_data["sms_col"]
    text_preproc = Pipeline([("Vect", CountVectorizer(stop_words='english'))])
    return text_preproc


def load_pipeline(config_data):
    registry_path = config_data["registry_path"]
    registry_df = general.read_csv(registry_path)
    best_preproc_runid = registry_df.iloc[-1]["preproc_runid"]
    preproc_artifact_path = os.path.join(config_data["preproc_prefix"],
                                         best_preproc_runid,
                                         "pipeline.pkl")
    return general.read_pkl(preproc_artifact_path)
    

def load_dataset(config_data):
    data_path = config_data["data_path"]
    header = config_data["header"]
    df = general.read_csv(data_path, sep="\t", names=header)
    LOG.info("Loaded %s rows from raw data", len(df))
    return df
        

@click.command()
@click.option("-r", "--runid", default="", help="Optional run id to pass")
@click.option("-c", "--config", required=True, help="Path to the config file")
@click.option("-t", "--train", is_flag=True, help="Train or Infer")
def run(runid, config, train):
    global LOG
    setup_logging()
    LOG = logging.getLogger(__name__)
    LOG.info("%s Starting Preprocessing %s", "*"*10, "*"*10)

    config_data = general.read_yaml(config)
    LOG.info(config_data)
    run_id = general.generate_runid() if runid == "" else runid
    LOG.info("Run_id in use: %s", run_id)

    df = load_dataset(config_data)
    output_prefix = os.path.join(config_data["preproc_prefix"], run_id)
    LOG.info("Output prefix in use: %s", output_prefix)
    write_list = []
    
    sms_col = config_data["sms_col"]
    if train:
        X = df[sms_col]
        LOG.info("Using train mode: Pipelines will be fitted and saved") 
        pipeline = create_pipeline(config_data)
        transformed = pipeline.fit_transform(X)
        new_feats = pipeline.named_steps["Vect"].get_feature_names()
        transformed_df = pd.DataFrame(transformed.toarray(),
                            columns=new_feats)
        transformed_df = pd.concat([transformed_df,
                                    df[[config_data["target_col"]]]], axis=1)
        write_list.append((pipeline,
                           os.path.join(output_prefix, "pipeline.pkl"),
                           "pickle"))
    else:
        LOG.info("Using predict mode: Fitted pipelines will be loaded") 
        pipeline = load_pipeline(config_data)
        X = df[sms_col]
        transformed = pipeline.transform(X)
        new_feats = pipeline.named_steps["Vect"].get_feature_names()
        transformed_df = pd.DataFrame(transformed.toarray(),
                            columns=new_feats)

    LOG.info("Shape of output: %s", transformed_df.shape)
    write_list.append((transformed_df,
                       os.path.join(output_prefix, "preprocessed.csv"),
                       "csv"))

    pathlib.Path(output_prefix).mkdir(parents=True, exist_ok=True)
    general.generic_write(write_list)
    LOG.info("%s Finished Preprocessing %s", "*"*10, "*"*10)
