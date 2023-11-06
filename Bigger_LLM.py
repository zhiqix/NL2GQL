
import asyncio
from typing import NamedTuple, Union

import openai
from openai.error import APIConnectionError
from Config import *
import time

"""
Call the OpenAI's API
"""

class OPENAI():

    def __init__(self):
        self.__init_openai()
        self.llm = openai
        self.model = OPENAI_API_MODEL
        self.auto_max_tokens = False

    def __init_openai(self):
        openai.api_key = OPENAI_API_KEY
        if OPENAI_API_BASE:
            openai.api_base = OPENAI_API_BASE

    async def _achat_completion_stream(self, messages: list[dict]) -> str:
        response = await openai.ChatCompletion.acreate(**self._cons_kwargs(messages), stream=True)

        # create variables to collect the stream of chunks
        collected_chunks = []
        collected_messages = []
        # iterate through the stream of events
        async for chunk in response:
            collected_chunks.append(chunk)  # save the event response
            choices = chunk["choices"]
            if len(choices) > 0:
                chunk_message = chunk["choices"][0].get("delta", {})  # extract the message
                collected_messages.append(chunk_message)  # save the message
                if "content" in chunk_message:
                    print(chunk_message["content"], end="")
        print()

        full_reply_content = "".join([m.get("content", "") for m in collected_messages])
        usage = self._calc_usage(messages, full_reply_content)
        self._update_costs(usage)
        return full_reply_content

    def _cons_kwargs(self, messages: list[dict]) -> dict:
        kwargs = {
            "messages": messages,
            # "max_tokens": MAX_TOKENS,
            "n": 1,
            "stop": None,
            "temperature": 0.3,
            "timeout": 3,
        }
        kwargs_mode = {"model": self.model}
        kwargs.update(kwargs_mode)
        return kwargs



    def _chat_completion(self, messages: list[dict]) -> dict:
        rsp = self.llm.ChatCompletion.create(**self._cons_kwargs(messages))
        # self._update_costs(rsp)
        return rsp.choices[0].message.content


    def completion(self, messages: list[dict]) -> dict:
        # if isinstance(messages[0], Message):
        #     messages = self.messages_to_dict(messages)
        return self._chat_completion(messages)

    # async def acompletion(self, messages: list[dict]) -> dict:
    #     # if isinstance(messages[0], Message):
    #     #     messages = self.messages_to_dict(messages)
    #     return await self._achat_completion(messages)


    async def acompletion_text(self, messages: list[dict], stream=False) -> str:
        """when streaming, print each token in place."""
        if stream:
            return await self._achat_completion_stream(messages)
        rsp = await self._achat_completion(messages)
        return self.get_choice_text(rsp)





