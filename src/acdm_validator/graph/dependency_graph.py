"""Dependency graph construction and deterministic topological ordering."""

from collections import Counter

from acdm_validator.contracts import EntityContract


class DependencyGraph:
    def __init__(self, contracts: list[EntityContract]):
        names = [contract.entity_name for contract in contracts if contract.entity_name]
        duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
        self.duplicates = duplicates
        self.contracts = {
            contract.entity_name: contract for contract in contracts if contract.entity_name
        }
        self.missing: dict[str, tuple[str, ...]] = {}
        for name, contract in self.contracts.items():
            absent = tuple(dep for dep in contract.depends_on if dep not in self.contracts)
            if absent:
                self.missing[name] = absent
        self.cycles = self._find_cycles()

    def dependencies(self, entity: str) -> list[EntityContract]:
        contract = self.contracts[entity]
        return [self.contracts[name] for name in contract.depends_on if name in self.contracts]

    def topological_order(self) -> list[EntityContract]:
        """Return dependencies before their consumers; append cyclic nodes deterministically."""
        ordered: list[EntityContract] = []
        permanent: set[str] = set()
        active: set[str] = set()

        def visit(name: str) -> None:
            if name in permanent or name in active:
                return
            active.add(name)
            for dependency in self.contracts[name].depends_on:
                if dependency in self.contracts:
                    visit(dependency)
            active.remove(name)
            permanent.add(name)
            ordered.append(self.contracts[name])

        for entity_name in sorted(self.contracts):
            visit(entity_name)
        return ordered

    def _find_cycles(self) -> list[tuple[str, ...]]:
        cycles: set[tuple[str, ...]] = set()
        visited: set[str] = set()
        stack: list[str] = []

        def canonical(cycle: list[str]) -> tuple[str, ...]:
            body = cycle[:-1]
            rotations = [tuple(body[index:] + body[:index]) for index in range(len(body))]
            return min(rotations)

        def walk(name: str) -> None:
            if name in stack:
                start = stack.index(name)
                cycles.add(canonical(stack[start:] + [name]))
                return
            if name in visited:
                return
            stack.append(name)
            for dependency in self.contracts[name].depends_on:
                if dependency in self.contracts:
                    walk(dependency)
            stack.pop()
            visited.add(name)

        for entity_name in sorted(self.contracts):
            walk(entity_name)
        return sorted(cycles)
