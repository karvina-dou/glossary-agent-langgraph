import os
import json
import yaml
import argparse
from datetime import datetime
from data.dataloader import get_dataloader
from agents.kv_agent.agent import build_workflow


def parsing(response):
    # verbal output
    print(f"Input: {response['input_text']}")
    if response['detected_abbr'] == ['None']:
        print("  No abbreviations detected.")
        print(f"Output: {response['input_text']}\n")
    else:
        for processed_abbr in response['processed_abbr']:
            for k, v in processed_abbr.items():  # lazy
                print(f"  {k} → {v}")
        print(f"Output: {response["process_text"]}\n")

    # output cleaning
    for del_k in ['external_args', 'detected_abbr', 'current_abbr', "replacement"]:
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

    save_dir = f'./responses/KV_{datetime.now().strftime('%Y%m%d-%H%M%S')}'
    os.makedirs(save_dir, exist_ok=True)

    workflow = build_workflow()
    generator, glossary_path = get_dataloader(config['dataset'])

    for case_id, case in enumerate(generator):
        response_dict = {}
        for sentence_id, sentence in enumerate(case.split('.')):  # compatibility
            if not sentence:
                continue
            response_state = workflow.invoke({
                "input_text": case + '.',
                'external_args': {
                    'model_args': config['model_args'],
                    'glossary_path': glossary_path
                    }
                })
            response_state = parsing(response_state)
            response_dict[sentence_id] = response_state

        with open(os.path.join(save_dir, f'response_{str(case_id).zfill(3)}.json'), 'w') as js:
            json.dump(response_dict, js, indent=4)
