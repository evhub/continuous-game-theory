#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x701cdb2b

# Compiled with Coconut version 1.4.0-post_dev40 [Ernest Scribbler]

# Coconut Header: -------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division
import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = _coconut_os_path.dirname(_coconut_os_path.abspath(__file__))
_coconut_cached_module = _coconut_sys.modules.get(str("__coconut__"))
if _coconut_cached_module is not None and _coconut_os_path.dirname(_coconut_cached_module.__file__) != _coconut_file_path:
    del _coconut_sys.modules[str("__coconut__")]
_coconut_sys.path.insert(0, _coconut_file_path)
from __coconut__ import *
from __coconut__ import _coconut, _coconut_MatchError, _coconut_igetitem, _coconut_base_compose, _coconut_forward_compose, _coconut_back_compose, _coconut_forward_star_compose, _coconut_back_star_compose, _coconut_forward_dubstar_compose, _coconut_back_dubstar_compose, _coconut_pipe, _coconut_back_pipe, _coconut_star_pipe, _coconut_back_star_pipe, _coconut_dubstar_pipe, _coconut_back_dubstar_pipe, _coconut_bool_and, _coconut_bool_or, _coconut_none_coalesce, _coconut_minus, _coconut_map, _coconut_partial, _coconut_get_function_match_error, _coconut_base_pattern_func, _coconut_addpattern, _coconut_sentinel, _coconut_assert
if _coconut_sys.version_info >= (3,):
    _coconut_sys.path.pop(0)

# Compiled Coconut: -----------------------------------------------------------

from copy import deepcopy

from tqdm import tqdm

from iternash.agent import Agent


class Game(_coconut.object):
    def __init__(self, *args, **kwargs):
        self.env = {"final_step": False}
        self.agents = {}
        self.handlers = []
        self.setup(*args, **kwargs)

    def setup(*_coconut_match_to_args, **_coconut_match_to_kwargs):
        """Add new agents/variables."""
        _coconut_match_check = False
        _coconut_FunctionMatchError = _coconut_get_function_match_error()
        if _coconut.sum((_coconut.len(_coconut_match_to_args) > 0, "self" in _coconut_match_to_kwargs)) == 1:
            _coconut_match_temp_0 = _coconut_match_to_args[0] if _coconut.len(_coconut_match_to_args) > 0 else _coconut_match_to_kwargs.pop("self")
            agents = _coconut_match_to_args[1:]
            _coconut_match_temp_1 = _coconut_match_to_kwargs.pop("sequential_init") if "sequential_init" in _coconut_match_to_kwargs else True
            self = _coconut_match_temp_0
            sequential_init = _coconut_match_temp_1
            named_agents = _coconut_match_to_kwargs
            _coconut_match_check = True
        if not _coconut_match_check:
            _coconut_match_val_repr = _coconut.repr(_coconut_match_to_args)
            _coconut_match_err = _coconut_FunctionMatchError("pattern-matching failed for " "'match def setup(self, *agents, sequential_init=True, **named_agents):'" " in " + (_coconut_match_val_repr if _coconut.len(_coconut_match_val_repr) <= 500 else _coconut_match_val_repr[:500] + "..."))
            _coconut_match_err.pattern = 'match def setup(self, *agents, sequential_init=True, **named_agents):'
            _coconut_match_err.value = _coconut_match_to_args
            raise _coconut_match_err

        self.i = 0
        for a in _coconut.itertools.chain.from_iterable((_coconut_func() for _coconut_func in (lambda: agents, lambda: named_agents.items()))):
            _coconut_match_to = a
            _coconut_match_check = False
            if (_coconut.isinstance(_coconut_match_to, _coconut.abc.Sequence)) and (_coconut.len(_coconut_match_to) == 2) and (_coconut.isinstance(_coconut_match_to[0], str)):
                name = _coconut_match_to[0]
                actor = _coconut_match_to[1]
                _coconut_match_check = True
            if _coconut_match_check:
                if not callable(actor):
                    self.env[name] = actor
                    continue
                a = Agent(name, actor)
            if a.has_default():
                self.env[a.name] = a.default
            self.agents[a.name] = a
        self.step(sequential_update=sequential_init)

    def attach(self, handler, period=100):
        """Attach a handler to be called at interval period."""
        self.handlers.append((handler, period))

    def call_handlers(self):
        """Call all attached handlers."""
        for handler, period in self.handlers:
            if self.i % period == 0:
                handler(self.env)

    def step(self, sequential_update=True):
        """Iterate one step."""
        if sequential_update:
            for a in self.agents.values():
                self.env[a.name] = a(self.env)
        else:
            self.env = dict(((a.name), (a(self.env))) for a in self.agents.values())
        self.i += 1
        self.call_handlers()
        return self.env

    def final_step(self, sequential_update=True):
        """Perform a final step with BBopt parameters set to serving."""
        self.env["final_step"] = True
        try:
            return self.step(sequential_update=sequential_update).copy()
        finally:
            self.env["final_step"] = False

    def run(self, max_steps=1000, sequential_update=True):
        """Iterate until equilibrium or max_steps is reached."""
        for _ in tqdm(range(max_steps)):
            prev_env = deepcopy(self.env)
            self.step(sequential_update=sequential_update)
            if self.env == prev_env:
                break
        return self.final_step()

    def clone(self, *args, **kwargs):
        """Create a new copy of the environment with new agents."""
        new_game = deepcopy(self)
        new_game.setup(*args, **kwargs)
        return new_game
