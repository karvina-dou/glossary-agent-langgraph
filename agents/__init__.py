from agents.kv_agent.agent import build_workflow as kv_build
from agents.reg_agent.agent import build_workflow as reg_build

workflow_map = {
    'kv': kv_build,
    'reg': reg_build
}
