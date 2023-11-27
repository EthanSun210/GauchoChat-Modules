"""Module for creating conversation openings in the GauchoChat project.

This module is designed to generate conversation openers for the
GauchoChat AI system. Its primary function is to provide an interface
for other modules to initiate conversations with varied and imaginative
starting points.
"""

import random

from fastchat.conversation import Conversation, SeparatorStyle

from utils.config import GlobalConfig as GC
from utils.state_manager import get_history_from_state_manager
from utils.utils import my_debug_logger
from utils.vicuna import filter_main_dialogue_output
from utils.vicuna import make_request_to_vicuna_model


def generate_conversation_opener_generic(state_manager):
    """
    Generate a generic conversation opener based on the state manager history.

    This function is the primary interface used by other modules to initiate a
    conversation. It analyzes the current state and history to produce an
    appropriate conversation starter, ensuring a dynamic and contextually
    relevant beginning to each interaction.

    Args:
        state_manager (StateManager): An instance of StateManager that contains
                                      the current state and history of the
                                      conversation.

    Returns:
        str: A conversation opener generated based on the current context.

    Note:
        This function should be the only one called by external modules to
        generate conversation openers within this module.
    """
    history = get_history_from_state_manager(state_manager)
    external_knowledge = getattr(state_manager.user_attributes,
                                 "topical_knowledge", None)
    response = _get_opener_response(
        history, False,  # continued_generation,
        external_knowledge=external_knowledge, state_manager=state_manager)
    return response["dialogue_response"]


def _get_fallback_opener():
    """
    Retrieve a fallback conversation opener.

    This function is called when there is an exception in generating a
    conversation opener dynamically. It randomly selects from a
    predefined list of openers.

    Returns:
        str: A randomly chosen fallback conversation opener.
    """
    fallback_openers = [
        ("I'm a bot with imagination, so let's start with something fun! "
         "I'm curious, if you suddenly discovered how to teleport, "
         "where would you go?"),

        ("I'm a bot with imagination, so let's start with something fun! "
         "I'm curious, if you were given the opportunity to have dinner with"
         " any historical figure, who would you choose?"),

        ("I'm a bot with imagination, so let's start with something fun! "
         "I'm curious, if you could instantly learn any language, "
         "which one would you choose?"),

        ("I'm a bot with imagination, so let's start with something fun! "
         "I'm curious, if you could have a conversation with any animal, "
         "which animal would you choose?"),

        ("I'm a bot with imagination, so let's start with something fun! "
         "I'm curious, if you could have a time machine, would you rather "
         "go to the past or the future?"),
        # ... other predefined openers ...
    ]
    return random.choice(fallback_openers)


def _create_opener_conversation(history):
    """
    Create a conversation object for the opener.

    This function creates a conversation object for the opener, which is used
    to generate the prompt for the opener.

    Args:
        history (list): A list of dictionaries containing the history of the
                        conversation.

    Returns:
        Conversation: A Conversation object containing the history of the
                      conversation.
    """
    # Create conversation object
    conv = Conversation(
        system=GC.opener_prompt,
        roles=("Human", "Assistant"),
        messages=(),
        offset=2,
        sep_style=SeparatorStyle.SINGLE,
        sep="</s>",
    )

    # Add history
    for turn in history:
        if turn.get("user"):
            conv.append_message(conv.roles[0], turn["user"])
        if turn.get("bot"):
            conv.append_message(conv.roles[1], turn["bot"])
        else:
            conv.append_message(conv.roles[1], None)

    return conv


def _add_external_knowledge_to_conv(conv, external_knowledge):
    """
    Add external knowledge to the opener.

    This function adds external knowledge to the conversation, which is used to
    generate the prompt for the opener.

    Args:
        conv (Conversation): A Conversation object containing the history of
                             the conversation.
        external_knowledge (str): A string containing the external knowledge
                                  to be added to the opener.
    """
    if external_knowledge:
        conv.system += (
            "\nHere's some external knowledge you "
            "can use when making your response: "
            f"{external_knowledge}"
            "\n"
        )


def _get_prompt(conv, continued_generation):
    """
    Get the prompt for the opener from the conversation.

    This function gets the prompt from the conversation, which is used to
    request response from the language model.

    Args:
        conv (Conversation): A Conversation object containing the history of
                             the conversation.
        continued_generation (bool): A boolean indicating whether or not the
                                     conversation is continuing.

    Returns:
        str: A string containing the prompt for the opener.
    """
    prompt = conv.get_prompt()
    if continued_generation and prompt.endswith(conv.sep):
        prompt = prompt[:-len(conv.sep)]
    return prompt


def _filter_response(response, prompt, conv, continued_generation, **kwargs):
    """
    Filter the response from the model.

    This function filters the response from the model, and returns the
    filtered dialogue response.

    Args:
        response (str): A string containing the response from the model.
        prompt (str): A string containing the prompt for the opener.
        conv (Conversation): A Conversation object containing the history of
                             the conversation.
        continued_generation (bool): A boolean indicating whether or not the
                                     conversation is continuing.

    Returns:
        str: A string containing the filtered response from the model.
    """
    dialogue_response = filter_main_dialogue_output(
        response, prompt, conv,
        continued_generation, **kwargs)
    dialogue_response = dialogue_response.split("###")[0]
    return dialogue_response


def _get_opener_response(
    history,
    controller_address=GC.controller_address,
    worker_address=None,
    model_name=GC.model_name,
    max_new_tokens=64,
    continued_generation=False,
    external_knowledge=None,
    state_manager=None,
    **kwargs
):
    """
    Generate a dialogue response for the conversation opener.

    This function generates a response for the conversation opener based on the
    given history and other parameters. It creates a conversation, adds
    external knowledge if available, gets the prompt, makes a request to
    the model, and filters the response.

    Args:
        history (list): A list of dictionaries containing the history of the
                        conversation.
        controller_address (str): The address of the controller.
        worker_address (str, optional): The address of the worker.
        model_name (str): The name of the model to be used.
        max_new_tokens (int): The maximum number of new tokens to be generated.
        continued_generation (bool): Whether to continue the generation.
        external_knowledge (str, optional): External knowledge to be added to
                                             the opener.
        state_manager (StateManager, optional): An instance of StateManager
                                                that contains the current state
                                                and history of the
                                                conversation.
        **kwargs: Additional keyword arguments.

    Returns:
        dict: A dictionary containing the dialogue response.
    """
    try:
        # Make prompt
        conv = _create_opener_conversation(history)
        # Add external knowledge
        _add_external_knowledge_to_conv(conv, external_knowledge)
        # Get prompt
        prompt = _get_prompt(conv, continued_generation)
        stop_token = conv.sep+conv.roles[0]
        # Make request
        response = make_request_to_vicuna_model(
            prompt, stop_token, controller_address, worker_address,
            model_name, max_new_tokens)
        # Debug log
        my_debug_logger.debug(f"Opener response prompt: {prompt}")
        # Filter response
        dialogue_response = _filter_response(
            response, prompt, conv, continued_generation, **kwargs)
        return {"dialogue_response": dialogue_response}
    except Exception as e:
        my_debug_logger.error(f"Error in get_opener_response: {e}")
        return {"dialogue_response": _get_fallback_opener()}
