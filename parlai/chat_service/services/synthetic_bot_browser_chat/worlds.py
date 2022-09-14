#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
# py parlai/chat_service/tasks/overworld_demo/run.py --debug --verbose

from parlai.core.worlds import World, validate
from parlai.chat_service.services.messenger.worlds import OnboardWorld
from parlai.core.agents import create_agent_from_shared
import json
from parlai.core.message import Message

# ---------- Chatbot demo ---------- #
class SyntheticBotOnboardWorld(OnboardWorld):
    """
    Example messenger onboarding world for Chatbot Model.
    """

    @staticmethod
    def generate_world(opt, agents):
        return SyntheticBotOnboardWorld(opt=opt, agent=agents[0])

    def parley(self):
        self.episodeDone = True


class SyntheticBotTaskWorld(World):
    """
    Example one person world that talks to a provided agent (bot).
    """

    MAX_AGENTS = 1
    MODEL_KEY = 'bb3_3B'

    def __init__(self, opt, agent, bot):
        self.agent = agent
        self.episodeDone = False
        self.model = bot
        self.first_time = True

    @staticmethod
    def generate_world(opt, agents):
        if opt['models'] is None:
            raise RuntimeError("Model must be specified")
        return SyntheticBotTaskWorld(
            opt,
            agents[0],
            create_agent_from_shared(
                opt['shared_bot_params'][SyntheticBotTaskWorld.MODEL_KEY]
            ),
        )

    @staticmethod
    def assign_roles(agents):
        agents[0].disp_id = 'ChatbotAgent'

    def parley(self):
        if self.first_time:
            self.agent.observe(
                {
                    'id': 'World',
                    'text': 'Welcome to the ParlAI Chatbot demo. '
                    'You are now paired with a bot - feel free to send a message.'
                    'Type [DONE] to finish the chat, or [RESET] to reset the dialogue history.',
                }
            )
            bot_context = self.get_context()
            context_act = Message(
                {'id': 'context', 'text': bot_context, 'episode_done': False}
            )
            self.model.observe(validate(context_act))
            self.first_time = False
        a = self.agent.act()
        if a is not None:
            if '[DONE]' in a['text']:
                self.episodeDone = True
            elif '[RESET]' in a['text']:
                self.model.reset()
                self.agent.observe({"text": "[History Cleared]", "episode_done": False})
            else:
                print("===act====")
                print(a)
                print("~~~~~~~~~~~")
                self.model.observe(a)
                response = self.model.act()
                print("===response====")
                print(response)
                print("~~~~~~~~~~~")
                self.agent.observe(response)

    def episode_done(self):
        return self.episodeDone

    def shutdown(self):
        self.agent.shutdown()

    def get_context(self):
        file_path = '/home/moe/Documents/GitHub/ParlAI/parlai/chat_service/services/synthetic_bot_browser_chat/memory_data/bot_context.json'
        with open(file_path) as f:
            data = json.load(f)
        context = []
        for persona in data['personas']:
            context.append(f'your persona: {persona}')
        for c in data['additional_context']:
            context.append(c)
        return '\n'.join(context)

# ---------- Overworld -------- #
class SyntheticBotOverworld(World):
    """
    World to handle moving agents to their proper places.
    """

    def __init__(self, opt, agent):
        self.agent = agent
        self.opt = opt
        self.first_time = True
        self.episodeDone = False

    @staticmethod
    def generate_world(opt, agents):
        return SyntheticBotOverworld(opt, agents[0])

    @staticmethod
    def assign_roles(agents):
        for a in agents:
            a.disp_id = 'Agent'

    def episode_done(self):
        return self.episodeDone

    def parley(self):
        if self.first_time:
            self.agent.observe(
                {
                    'id': 'Overworld',
                    'text': 'Welcome to the overworld for the ParlAI messenger '
                    'chatbot demo. Please type "begin" to start, or "exit" to exit',
                    'quick_replies': ['begin', 'exit'],
                }
            )
            self.first_time = False
        a = self.agent.act()
        if a is not None and a['text'].lower() == 'exit':
            self.episode_done = True
            return 'EXIT'
        if a is not None and a['text'].lower() == 'begin':
            self.episodeDone = True
            return 'default'
        elif a is not None:
            self.agent.observe(
                {
                    'id': 'Overworld',
                    'text': 'Invalid option. Please type "begin".',
                    'quick_replies': ['begin'],
                }
            )
