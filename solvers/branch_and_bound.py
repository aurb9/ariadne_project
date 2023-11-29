from pyariadne import ValidatedOptimiserInterface, ValidatedKleenean, ValidatedFeasibilityProblem, ValidatedNumberVector


class BranchAndBound:  # (ValidatedOptimiserInterface):
    def __init__(self, opt: ValidatedOptimiserInterface) -> None:
        # TODO: shouldn't it return a BranchAndBound...Optimiser (e.g., BranchAndBoundInteriorPointOptimiser)?
        self.opt = opt

    def feasible(self, p: ValidatedFeasibilityProblem) -> ValidatedKleenean:
        pass

    def _branch(self) -> None:
        pass

    def _bound(self) -> None:
        pass

    def _optimise(self) -> None:
        pass

    def minimise(self, p: ValidatedFeasibilityProblem) -> ValidatedNumberVector:
        pass
