from agents.reg_agent import states
from agents.reg_agent.prompts import craft_prompt

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


# utility functions
def build_model(model_args):
    return ChatOpenAI(**model_args)


# nodes
def validate_node(state: states.ValidateState) -> states.ValidateState:
    system_prompt, user_prompt = craft_prompt(state)
    model = build_model(
        state['external_args']["model_args"]
    )
    response = model.invoke([SystemMessage(content=system_prompt),
                            HumanMessage(content=user_prompt)]).content

    return {'response': response}
