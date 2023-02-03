import os
import logging
import click
import pandas as pd
import utils.logger as logger
import utils.general as general
from datetime import datetime
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


LOG = None


def setup_logging():
    log_handler = logger.Logger()
    log_handler.setup()


def load_dataset(config_data, preproc_runid):
    data_path = os.path.join(config_data["preproc_prefix"], 
                            preproc_runid,
                            "preprocessed.csv")
    df = general.read_csv(data_path, sep=",", names=None)
    LOG.info("Loaded %s rows from preprocessed data", len(df))
    return df


def get_feats_and_labels(config_data, df):
    target_col = config_data["target_col"]
    target_mapping = config_data["target_mapping"]
    df[target_col] = df[target_col].map(target_mapping)
    X = df[[col for col in list(df.columns) if col != target_col]]
    y = df[target_col]
    return X, y


def create_model(config_data):
    naive_bayes = MultinomialNB()
    return naive_bayes


def get_metrics(y, predictions):
    metrics = {
        "acc": accuracy_score(y, predictions),
        "prec":precision_score(y, predictions),
        "recall": recall_score(y, predictions),
        "f1": f1_score(y, predictions)
    }
    print(metrics)
    return pd.DataFrame([metrics])


def update_registry(config_data, preproc_runid, train_runid):
    registry_path = config_data["registry_path"]
    entry_df = pd.DataFrame([{
        "moment": str(datetime.now()),
        "preproc_runid": preproc_runid,
        "trian_runid": train_runid,
    }])
    try:
        registry_df = general.read_csv(registry_path)
    except Exception:
        registry_df = pd.DataFrame(columns=entry_df.columns)

    updated_registry = pd.concat([registry_df, entry_df], ignore_index=True)
    return updated_registry


@click.command()
@click.option("-r", "--runid", default="", help="Optional run id.")
@click.option("-p", "--preproc-runid", default="", help="Preprocessing run id.")
@click.option("-c", "--config", required=True, help="Path to the config file.")
def run(runid, preproc_runid, config):
    global LOG
    setup_logging()
    LOG = logging.getLogger(__name__)
    LOG.info("%s Starting Preprocessing %s", "*"*10, "*"*10)

    config_data = general.read_yaml(config)
    LOG.info(config_data)
    seed = config_data.get("seed", 0)
    run_id = general.generate_runid() if runid == "" else runid
    output_prefix = os.path.join(config_data["train_prefix"], run_id)
    LOG.info("Output prefix in use: %s", output_prefix)
    LOG.info("Run_id in use: %s", run_id)
    LOG.info("Preprocessing run_id in use: %s", preproc_runid)

    df = load_dataset(config_data, preproc_runid)
    
    X, y = get_feats_and_labels(config_data, df)

    # train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, 
                                                        y, 
                                                        random_state=seed)

    LOG.info("X_train: %s, X_test: %s", len(X_train), len(X_test))
    LOG.info("Using train mode: Pipelines will be fitted and saved") 
    
    write_list = []
    model = create_model(config_data)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test) 
    metrics_df = get_metrics(y_test, predictions)
    registry_df = update_registry(config_data, preproc_runid, run_id)
    
    write_list.append((model,
                       os.path.join(output_prefix, "model.pkl"),
                       "pickle"))

    write_list.append((metrics_df,
                        os.path.join(output_prefix, "metrics.csv"),
                        "csv"))
    
    write_list.append((registry_df,
                        config_data["registry_path"],
                        "csv"))
       
    general.generic_write(write_list)
    LOG.info("%s Finished Preprocessing %s", "*"*10, "*"*10)
