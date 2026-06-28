"""Public exception hierarchy."""


class ACDMValidatorError(Exception):
    """Base exception for ACDM Validator."""


class ContractLoadError(ACDMValidatorError):
    """Raised when a contract file cannot be read as a YAML mapping."""


class DependencyGraphError(ACDMValidatorError):
    """Raised when the dependency graph cannot be constructed."""
