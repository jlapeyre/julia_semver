# julia_semver

This package allows you to work with [Julia version specifiers](https://pkgdocs.julialang.org/v1/compatibility/)
in Python.
It provides three functions

- `version` - accepts a Julia version string and returns an instance of `semantic_version.Version`.
- `semver_spec` - accepts a Julia version specifier string and returns an instance of `semantic_version.NpmSpec`.
- `match` - `match(spec, vers)` returns true if vesion `vers` satisfies specifier `spec`.

The tools in [`semantic_version`](https://pypi.org/project/semantic-version/)
can then be used to work with versions and version specifiers.

#### Motivation

The package `semantic_version` can represent Julia versions and version specifiers. But, it does not
support the Julia syntax for constructing these representations from strings. This package provides
functions for these constructions that implement the Julia syntax exactly.

## Install

```sh
pip install julia_semver
```

## Details

- All of the [Julia version specifier format](https://pkgdocs.julialang.org/v1/compatibility/)
(as of julia v1.8) is supported.

- The syntax of the version strings and version specifier strings is exactly the same as that described in Julia docs
  and implemented in Julia.


## Semantics of matching and comparison

The functions and methods in `semantic_version` for comparing and matching differ in some respects from those of Julia.
In particular, in Julia, the prerelease is ignored when matching a version to a version specifier. The function
`julia_semver.match` tries to preserve the Julia semantics:

```python
semver_spec("1").match(version("1.1.2-DEV")) # False
julia_semver.match("1", "1.1.2-DEV") # True
julia_semver.match("1", "1.1.2-DEV", strict=True) # False
```

## Examples

See the [test suite](./src/julia_semver/tests/test_semver.py) for more examples.

```python
from julia_semver import semver_spec, version

version('1.8') in semver_spec('^1.7.2')
version('0.8') not in semver_spec('^0.7.2')
```

<!--  LocalWords:  julia semver NpmSpec
 -->
