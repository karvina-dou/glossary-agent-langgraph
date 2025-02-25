import os
import json
import yaml
import argparse
from tqdm import tqdm
from datetime import datetime
from data.dataloader import DataEngine
from agents import workflow_map


def parsing(response, del_keys):
    # output cleaning
    for del_k in del_keys:
        response[del_k] = ''  # safety
        del response[del_k]

    return response


def parse_args():
    parser = argparse.ArgumentParser('Inference code for KV langgraph pipeline')
    parser.add_argument('--cfg', help='path to yaml file for config')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    assert os.path.isfile(args.cfg)
    config = yaml.safe_load(open(args.cfg, 'r'))

    save_dir = f'./responses/{config['workflow'].upper()}_{datetime.now().strftime('%Y%m%d-%H%M%S')}'
    os.makedirs(save_dir, exist_ok=True)

    workflow = workflow_map[config['workflow']]()
    engine = DataEngine(config['data_path'], config['max_concurrency'], config['preprocess_fn'])

    for file_id, file, generator in tqdm(engine()):
        response_dict = {}
        for batch_id, batch in generator():
            # add external args
            _ = [
                b.update(
                    {'external_args': {'model_args': config['model_args'],
                                       'glossary_path': engine.glossary_path}, }
                )
                for b in batch
            ]
            # inference
            responses = workflow.batch(
                batch, config={"max_concurrency": config['max_concurrency']}
            )

            # output parsing
            _ = [
                response_dict.update(
                    {batch_id * config['max_concurrency'] + idx: parsing(response, config['del_keys'])}
                )
                for idx, response in enumerate(responses)
            ]
        with open(os.path.join(save_dir, f'response_{str(file_id).zfill(3)}.json'), 'w') as js:
            json.dump(response_dict, js, indent=4)

        if file_id + 1 == config['max_case']:
            print(f'Reached max # of cases: {file_id}')
            break
