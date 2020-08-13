from typing import Any, Dict, Optional

from ConfigSpace.configuration_space import ConfigurationSpace
from ConfigSpace.hyperparameters import (
    CategoricalHyperparameter,
    UniformFloatHyperparameter,
    UniformIntegerHyperparameter
)

import numpy as np

import torch.optim.lr_scheduler
from torch.optim.lr_scheduler import _LRScheduler

from autoPyTorch.pipeline.components.setup.lr_scheduler.base_scheduler import BaseLRComponent


class ReduceLROnPlateau(BaseLRComponent):
    """
    Reduce learning rate when a metric has stopped improving. Models often benefit from
    reducing the learning rate by a factor of 2-10 once learning stagnates. This scheduler
    reads a metrics quantity and if no improvement is seen for a ‘patience’ number of epochs,
    the learning rate is reduced.

    Args:
        mode (str): One of min, max. In min mode, lr will be reduced when the quantity
            monitored has stopped decreasing; in max mode it will be reduced when
            the quantity monitored has stopped increasing
        factor (float): Factor by which the learning rate will be reduced. new_lr = lr * factor.
        patience (int): Number of epochs with no improvement after which learning
            rate will be reduced.
        random_state (Optional[np.random.RandomState]): random state
    """
    def __init__(
        self,
        mode: str,
        factor: float,
        patience: int,
        random_state: Optional[np.random.RandomState] = None
    ):

        super().__init__()
        self.mode = mode
        self.factor = factor
        self.patience = patience
        self.random_state = random_state
        self.scheduler = None  # type: Optional[_LRScheduler]

    def fit(self, X: np.ndarray, y: np.ndarray, **fit_params: Any
            ) -> BaseLRComponent:
        """
        Sets the scheduler component choice as CosineAnnealingWarmRestarts

        Args:
            X (np.ndarray): input features
            y (npndarray): target features

        Returns:
            A instance of self
        """

        # Make sure there is an optimizer
        if 'optimizer' not in fit_params:
            raise ValueError('Cannot use scheduler without an optimizer to wrap')

        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer=fit_params['optimizer'],
            mode=self.mode,
            factor=float(self.factor),
            patience=int(self.patience),
        )
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        return X

    @staticmethod
    def get_properties(dataset_properties: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        return {
            'shortname': 'CosineAnnealingWarmRestarts',
            'name': 'Cosine Annealing WarmRestarts',
        }

    @staticmethod
    def get_hyperparameter_search_space(dataset_properties: Optional[Dict] = None
                                        ) -> ConfigurationSpace:
        mode = CategoricalHyperparameter('mode', ['min', 'max'])
        patience = UniformIntegerHyperparameter(
            "patience", 5, 20, default_value=10)
        factor = UniformFloatHyperparameter(
            "factor", 0.01, 0.9, default_value=0.1)
        cs = ConfigurationSpace()
        cs.add_hyperparameters([mode, patience, factor])
        return cs
