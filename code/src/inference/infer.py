import os
import logging
import click
import pandas as pd
import utils.logger as logger
import utils.general as general
import preprocessing.preprocessor as preprocessor
import training.train as train 


LOG = None


def setup_logging():
    log_handler = logger.Logger()
    log_handler.setup()


def get_inv_mapping(mapping):
    inv_mapping = {}
    for k, v in mapping.items():
        inv_mapping[v] = k
    return inv_mapping


@click.command()
@click.option("-c", "--config", required=True, help="Path to the config file.")
@click.option("-s", "--sms", required=True, help="SMS to classify.")
def run(config, sms):
    global LOG
    setup_logging()
    LOG = logging.getLogger(__name__)
    LOG.info("%s Starting Inference %s", "*"*10, "*"*10)

    config_data = general.read_yaml(config)
    LOG.info(config_data)
    inv_mapping = get_inv_mapping(config_data["target_mapping"])
    seed = config_data.get("seed", 0)
    X = pd.Series([sms], dtype=str)

    preproc_pipeline = preprocessor.load_pipeline(config_data)
    model = train.load_model(config_data)

    transformed_df = preprocessor.transform(X, preproc_pipeline, train=False)
    predictions = model.predict(transformed_df)
    predictions = list(map(lambda x: inv_mapping[x], predictions))
    LOG.info("Predictions: %s", predictions)
    
    LOG.info("%s Finished Inference %s", "*"*10, "*"*10)
