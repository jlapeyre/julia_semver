# julia_semver

This package allows you to work with [Julia version specifiers](https://pkgdocs.julialang.org/v1/compatibility/).
It provides two functions

- `version` - accepts a Julia version string and returns an instance of `semantic_version.Version`.
- `semver_spec` accepts a Julia version specifier string and returns an instance of `semantic_version.NpmSpec`.

The tools in [`semantic_version`](https://pypi.org/project/semantic-version/)
can then be used to work with versions and version specifiers.

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


## Example

```python
from julia_semver import semver_spec, version

version('1.8') in semver_spec('1.7.2')
version('0.8') not in semver_spec('0.7.2')
```

<!--  LocalWords:  julia semver NpmSpec
 -->
