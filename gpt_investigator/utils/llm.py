# libraries
from __future__ import annotations

import json
import logging
from typing import Optional, Any, Dict

from .costs import estimate_llm_cost


def get_llm(llm_provider, **kwargs):
    match llm_provider:
        case "openai":
            from ..llm_provider import OpenAIProvider
            llm_provider = OpenAIProvider
        case "azureopenai":
            from ..llm_provider import AzureOpenAIProvider
            llm_provider = AzureOpenAIProvider
        case "google":
            from ..llm_provider import GoogleProvider
            llm_provider = GoogleProvider
        case "ollama":
            from ..llm_provider import OllamaProvider
            llm_provider = OllamaProvider
        case "groq":
            from ..llm_provider import GroqProvider
            llm_provider = GroqProvider
        case "together":
            from ..llm_provider import TogetherProvider
            llm_provider = TogetherProvider
        case "huggingface":
            from ..llm_provider import HugginFaceProvider
            llm_provider = HugginFaceProvider
        case "mistral":
            from ..llm_provider import MistralProvider
            llm_provider = MistralProvider
        case "anthropic":
            from ..llm_provider import AnthropicProvider
            llm_provider = AnthropicProvider
        # Generic case for all other providers supported by Langchain
        case _:
            from gpt_investigator.llm_provider import GenericLLMProvider
            return GenericLLMProvider.from_provider(llm_provider, **kwargs)

    return llm_provider(**kwargs)


async def create_chat_completion(
        messages: list,  # type: ignore
        model: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        llm_provider: Optional[str] = None,
        stream: Optional[bool] = False,
        websocket: Any | None = None,
        llm_kwargs: Dict[str, Any] | None = None,
        cost_callback: callable = None
) -> str:
    """Create a chat completion using the OpenAI API
    Args:
        messages (list[dict[str, str]]): The messages to send to the chat completion
        model (str, optional): The model to use. Defaults to None.
        temperature (float, optional): The temperature to use. Defaults to 0.9.
        max_tokens (int, optional): The max tokens to use. Defaults to None.
        stream (bool, optional): Whether to stream the response. Defaults to False.
        llm_provider (str, optional): The LLM Provider to use.
        webocket (WebSocket): The websocket used in the currect request,
        cost_callback: Callback function for updating cost
    Returns:
        str: The response from the chat completion
    """

    # validate input
    if model is None:
        raise ValueError("Model cannot be None")
    if max_tokens is not None and max_tokens > 8001:
        raise ValueError(
            f"Max tokens cannot be more than 8001, but got {max_tokens}")

    # Get the provider from supported providers
    provider = get_llm(llm_provider, model=model, temperature=temperature, max_tokens=max_tokens, **llm_kwargs)

    response = ""
    # create response
    for _ in range(10):  # maximum of 10 attempts
        response = await provider.get_chat_response(
            messages, stream, websocket
        )

        if cost_callback:
            llm_costs = estimate_llm_cost(str(messages), response)
            cost_callback(llm_costs)

        return response

    logging.error(f"Failed to get response from {llm_provider} API")
    raise RuntimeError(f"Failed to get response from {llm_provider} API")
