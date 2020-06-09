#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xa33229bf

# Compiled with Coconut version 1.4.3-post_dev28 [Ernest Scribbler]

# Coconut Header: -------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division
import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = _coconut_os_path.dirname(_coconut_os_path.abspath(__file__))
_coconut_cached_module = _coconut_sys.modules.get(str("__coconut__"))
if _coconut_cached_module is not None and _coconut_os_path.dirname(_coconut_cached_module.__file__) != _coconut_file_path:
    del _coconut_sys.modules[str("__coconut__")]
_coconut_sys.path.insert(0, _coconut_file_path)
from __coconut__ import *
from __coconut__ import _coconut, _coconut_MatchError, _coconut_igetitem, _coconut_base_compose, _coconut_forward_compose, _coconut_back_compose, _coconut_forward_star_compose, _coconut_back_star_compose, _coconut_forward_dubstar_compose, _coconut_back_dubstar_compose, _coconut_pipe, _coconut_back_pipe, _coconut_star_pipe, _coconut_back_star_pipe, _coconut_dubstar_pipe, _coconut_back_dubstar_pipe, _coconut_bool_and, _coconut_bool_or, _coconut_none_coalesce, _coconut_minus, _coconut_map, _coconut_partial, _coconut_get_function_match_error, _coconut_base_pattern_func, _coconut_addpattern, _coconut_sentinel, _coconut_assert, _coconut_mark_as_match
if _coconut_sys.version_info >= (3,):
    _coconut_sys.path.pop(0)

# Compiled Coconut: -----------------------------------------------------------

from pprint import pprint
from collections import deque

from bbopt import BlackBoxOptimizer
from bbopt.constants import default_alg

from iternash.util import Str
from iternash.util import printret
from iternash.util import printerr
from iternash.util import clean_env


no_default = object()
_sentinel = object()

class Agent(_coconut.object):
    """Agent class.

    Parameters:
    - _name_ is the key to assign this agent's action in the environment, or None
        for no name.
    - _actor_ is a function from the environment to the agent's action.
    - _default_ is the agent's initial action.
    - _period_ is the period at which to call the agent (default is 1).
    - _extra_defaults_ are extra variables that need to be given defaults.
    - _copy_func_ determines the function used to copy the agent's action (default is identity).
    - _debug_ controls whether the agent should print what it's doing.
    """

    def __init__(self, name, actor, default=no_default, period=1, extra_defaults={}, copy_func=None, debug=False):
        self.name = name
        self.actor = actor
        self.default = default
        self.period = period
        self.extra_defaults = extra_defaults
        self.copy_func = copy_func
        self.debug = debug

    def clone(self, name=None, actor=None, default=_sentinel, period=None, extra_defaults=None, copy_func=_sentinel, debug=None):
        """Create a copy of the agent (optionally) with new parameters."""
        if default is _sentinel:
            default = self.default
        if copy_func is _sentinel:
            copy_func = self.copy_func
        return Agent((self.name if name is None else name), (self.actor if actor is None else actor), default, (self.period if period is None else period), (lambda _coconut_none_coalesce_item: self.extra_defaults if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(extra_defaults), copy_func, (self.debug if debug is None else debug))

    def __call__(self, env):
        """Call the agent's actor function."""
        try:
            result = self.actor(env)
            if self.debug:
                print("{_coconut_format_0}({_coconut_format_1}) = {_coconut_format_2}".format(_coconut_format_0=(self), _coconut_format_1=(env), _coconut_format_2=(result)))
            return result
        except:
            printerr("Error calculating action for {_coconut_format_0}({_coconut_format_1}):".format(_coconut_format_0=(self), _coconut_format_1=(env)))
            raise

    def __repr__(self):
        return "Agent({_coconut_format_0})".format(_coconut_format_0=(self.name))

    def has_default(self):
        """Whether the agent has a default."""
        return self.default is not no_default


def agent(name_or_agent_func=None, **kwargs):
    """Decorator for easily constructing agents.

    If a string is passed to the decorator it will use that as the name,
    otherwise the name is inferred from the name of the function.

    Examples:

        @agent()  # or just @agent
        def x(env) =
            ...

        @agent("x")
        def x_agent(env) =
            ...

        @agent(name="x", default=...)
        def x_agent(env) =
            ...
    """
    if name_or_agent_func is None:
        return _coconut.functools.partial(agent, **kwargs)
    elif isinstance(name_or_agent_func, Str):
        return _coconut.functools.partial(Agent, name_or_agent_func, **kwargs)
    elif "name" in kwargs:
        return Agent(kwargs.pop("name"), name_or_agent_func, **kwargs)
    else:
        return Agent(name_or_agent_func.__name__, name_or_agent_func, **kwargs)


DEFAULT_EXPR_ALIASES = {"\n": ""}

def expr_agent(name, expr, vars={}, aliases=DEFAULT_EXPR_ALIASES, eval=eval, **kwargs):
    """Construct an agent that computes its action by evaluating an expression.

    Parameters:
    - _name_ is the name the agent's action will be assigned in the environment.
    - _expr_ is an expression to be evaluated in the environment to determine the
        agent's action.
    - _vars_ are the globals to be used for evaluating the agent's action.
    - _aliases_ are simple replacements to be made to the expr before evaluating it
        (the default is {"\\n": "", "^": "**"}).
    - _eval_ is the eval function to use (defaults to Python eval, but can be set to
        coconut.convenience.coconut_eval instead to use Coconut eval).
    - _kwargs_ are passed to `Agent`.
    """
    for k, v in aliases.items():
        expr = expr.replace(k, v)
    return Agent(name, _coconut.functools.partial(eval, expr, vars), **kwargs)


def human_agent(name, pprint=True, vars={}, aliases=DEFAULT_EXPR_ALIASES, eval=eval, **kwargs):
    """Construct an agent that prompts a human for an expression as in expr_agent.

    Parameters are as per expr_agent plus _pprint_ which determines whether to
    pretty print the environment for the human."""
    def human_actor(env):
        if pprint:
            pprint(clean_env(env))
        expr = input("{_coconut_format_0} = ".format(_coconut_format_0=(name)))
        return expr_agent(expr, vars, aliases, eval)(env)
    return Agent(name, human_actor, **kwargs)


def bbopt_agent(name, tunable_actor, util_func, file, alg=default_alg, **kwargs):
    """Construct an agent that selects its action using a black box optimizer.

    Parameters:
    - _name_ is the name the agent's action will be assigned in the environment.
    - _tunable_actor_ is a function from (bb, env) to an action (see the BBopt docs
        for how to use the bb object to define tunable parameters).
    - _util_func_ is the a function from the env resulting from the agent's action
        to the utility it should get for that action.
    - _file_ should be set to __file__.
    - _alg_ determines the black box optimization algorithm to use (the default
        is tree_structured_parzen_estimator).
    - _kwargs_ are passed to `Agent`.
    """
    def bbopt_actor(env):
        _coconut_match_to = env
        _coconut_match_check = False
        if _coconut.isinstance(_coconut_match_to, _coconut.abc.Mapping):
            _coconut_match_temp_0 = _coconut_match_to.get((name + "_bb"), _coconut_sentinel)
            if _coconut_match_temp_0 is not _coconut_sentinel:
                bb = _coconut_match_temp_0
                _coconut_match_check = True
        if _coconut_match_check:
            bb.maximize(util_func(env))
        else:
            bb = BlackBoxOptimizer(file=file, tag=env["game"].name + "_" + name)
            env[name + "_bb"] = bb
        bb.run(alg=alg if not env["game"].final_step else None)
        return tunable_actor(bb, env)
    return Agent(name, bbopt_actor, **kwargs)


def debug_agent(debug_str, name=None, **kwargs):
    """Construct an agent that prints a formatted debug string.

    Example:
        debug_agent("x = {x}")
            is roughly equivalent to
        Agent(None, env -> print("x = {x}".format(**env)))
    """
    return Agent(name, lambda env: (printret)(debug_str.format(**env)), **kwargs)


def debug_all_agent(pretty=True, **kwargs):
    """Construct an agent that prints the entire env, prettily if _pretty_."""
    print_func = pprint if pretty else print
    return Agent(None, lambda env: print_func(clean_env(env)), **kwargs)


def init_agent(name, constant):
    """Construct an agent that just initializes name to the given constant."""
    return Agent(name, lambda env: constant, default=constant, period=float("inf"))


def hist_agent(hist_name, var_name, maxhist=None, initializer=(), **kwargs):
    """Construct an agent that records a history.

    Parameters:
    - _hist_name_ is the name of this agent.
    - _var_name_ is the name of the agent to record.
    - _maxhist_ is the maximum history to store.
    - _initializer_ is an iterable to fill the initial history with.
    - _kwargs_ are passed to Agent.
    """
    def hist_actor(env):
        env[hist_name].append(env[var_name])
        return env[hist_name]
    init_hist = [] if maxhist is None else deque(maxlen=maxhist)
    for x in initializer:
        init_hist.append(x)
    return Agent(hist_name, hist_actor, default=init_hist, **kwargs)
