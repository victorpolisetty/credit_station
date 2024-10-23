# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2024 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This package contains round behaviours of CreditScoreAggregationAbciApp."""

from abc import ABC
from typing import Generator, Set, Type, cast

from packages.victorpolisetty.skills.credit_score_aggregation_abci.models import Params, SharedState
from packages.victorpolisetty.skills.credit_score_aggregation_abci.payloads import (
    HelloPayload,
    CollectAlpacaHistoricalDataPayload,
)
from packages.victorpolisetty.skills.credit_score_aggregation_abci.rounds import (
    CreditScoreAggregationAbciApp,
    HelloRound,
    CollectAlpacaHistoricalDataRound,
    SynchronizedData,
)
from packages.valory.skills.abstract_round_abci.base import AbstractRound
from packages.valory.skills.abstract_round_abci.behaviours import (
    AbstractRoundBehaviour,
    BaseBehaviour,
)


class HelloBaseBehaviour(BaseBehaviour, ABC):  # pylint: disable=too-many-ancestors
    """Base behaviour for the hello_abci skill."""

    @property
    def synchronized_data(self) -> SynchronizedData:
        """Return the synchronized data."""
        return cast(SynchronizedData, super().synchronized_data)

    @property
    def params(self) -> Params:
        """Return the params."""
        return cast(Params, super().params)

    @property
    def local_state(self) -> SharedState:
        """Return the state."""
        return cast(SharedState, self.context.state)


class HelloBehaviour(HelloBaseBehaviour):  # pylint: disable=too-many-ancestors
    """HelloBehaviour"""

    matching_round: Type[AbstractRound] = HelloRound

    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""

        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            sender = self.context.agent_address
            payload_content = "Hello world!"
            self.context.logger.info(payload_content)
            payload = HelloPayload(sender=sender, content=payload_content)

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()


class CollectAlpacaHistoricalDataBehaviour(HelloBaseBehaviour):  # pylint: disable=too-many-ancestors
    """Behaviour to request URLs from search engine"""

    matching_round: Type[AbstractRound] = CollectAlpacaHistoricalDataRound

    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""

        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            sender = self.context.agent_address
            shout_data = self.synchronized_data.hello_data
            payload_content = "Shouting: " + shout_data
            self.context.logger.info(payload_content)
            payload = CollectAlpacaHistoricalDataPayload(sender=sender, content=payload_content)

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()
        self.set_done()


class CreditScoreAggregationRoundBehaviour(AbstractRoundBehaviour):
    """CreditScoreAggregationBehaviour"""

    initial_behaviour_cls = HelloBehaviour
    abci_app_cls = CreditScoreAggregationAbciApp  # type: ignore
    behaviours: Set[Type[BaseBehaviour]] = [  # type: ignore
        HelloBehaviour,
        CollectAlpacaHistoricalDataBehaviour
    ]