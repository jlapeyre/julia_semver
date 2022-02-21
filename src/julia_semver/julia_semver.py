import re
import semantic_version

# We need to use semantic_version.NpmSpec because it can represent a union of specifications.
# In a Julia semver spec, a comma-separated list of specs means the union of the specs.
# In NpmSpec a union is represented by separating a list of specs by " || ".

# These follow very closely Pkg/Versions.jl.
# In particular, they are meant to match exactly the same strings mentioned there.
_re_version = "v?([0-9]+?)(?:\\.([0-9]+?))?(?:\\.([0-9]+?))?"
re_semver_interval = re.compile(f'^([~^]?)?{_re_version}$')
re_inequality_interval = re.compile(
    f"^((?:≥\\s*)|(?:>=\\s*)|(?:=\\s*)|(?:<\\s*)|(?:=\\s*))v?{_re_version}$"
    )
re_hyphen_interval = re.compile(
    f"^[\\s]*{_re_version}[\\s]*?\\s-\\s[\\s]*?{_re_version}[\\s]*$"
    )


# Use space for NpmSpec. Comma for SimpleSpec
_RANGE_SEP = ' ' # or ','
# == for SimpleSpec. = for NpmSpec
_EXACT_VER = '='

def semver_interval(sstr):
    s = _RANGE_SEP
    mres = re_semver_interval.match(sstr)
    if mres is None:
        return None
    modif, major, in_minor, in_patch = mres.groups()
    if (in_minor is not None and in_patch is not None and
        major == '0' and in_minor == '0' and in_patch == '0'):
        raise ValueError("invalid version: \"0.0.0\"")
    minor = '0' if in_minor is None else in_minor
    patch = '0' if in_patch is None else in_patch
    lower = f"{major}.{minor}.{patch}"
    if major == '0':
        if in_minor is None:
            return "<1.0.0"
        if minor != '0':
            nminor = str(int(minor) + 1)
            return f">={lower}{s}<0.{nminor}.0"
        else:
            if in_patch is None: # 0.0
                return "<0.1.0"
            return f"{_EXACT_VER}0.0.{patch}"
    if modif == '' or modif == '^':
        nmajor = str(int(major) + 1)
        return f">={lower}{s}<{nmajor}.0.0"
    else: # tilde
        if in_minor is None and in_patch is None:
            nmajor = str(int(major) + 1)
            return f">={lower}{s}<{nmajor}.0.0"
        nminor = str(int(minor) + 1)
        return f">={lower}{s}<{major}.{nminor}.0"


def semver_inequality(sstr):
    s = _RANGE_SEP
    mres = re_inequality_interval.match(sstr)
    if mres is None:
        return None
    ineq, major, in_minor, in_patch = mres.groups()
    ineq = ineq.strip()
    if ineq == "=":
        ineq = _EXACT_VER # Use == here for SimpleSpec
    minor = '0' if in_minor is None else in_minor
    patch = '0' if in_patch is None else in_patch
    return f"{ineq}{major}.{minor}.{patch}"


def semver_hyphen(sstr):
    s = _RANGE_SEP
    mres = re_hyphen_interval.match(sstr)
    if mres is None:
        return None
    lmajor, in_lminor, in_lpatch, umajor, in_uminor, in_upatch = mres.groups()
    lminor = '0' if in_lminor is None else in_lminor
    lpatch = '0' if in_lpatch is None else in_lpatch
    uminor = '0' if in_uminor is None else in_uminor
    upatch = '0' if in_upatch is None else in_upatch
    if in_uminor is not None and in_upatch is not None:
        return f">={lmajor}.{lminor}.{lpatch}{s}<={umajor}.{uminor}.{upatch}"
    if in_uminor is None:
        numajor = str(int(umajor) + 1)
        return f">={lmajor}.{lminor}.{lpatch}{s}<{numajor}.{uminor}.{upatch}"
    if in_upatch is None:
        numinor = str(int(uminor) + 1)
        return f">={lmajor}.{lminor}.{lpatch}{s}<{umajor}.{numinor}.{upatch}"

# a single spec taken from a comma separated list
def one_semver_spec(sstr):
    sstr = sstr.strip()
    for f in (semver_interval, semver_inequality, semver_hyphen):
        res = f(sstr)
        if res is None:
            continue
        return res
    raise ValueError(f"'{sstr}' is not a valid Julia semver spec")


# Comma separated list of specs
def semver_spec(spec):
    """
    Return an object representing the Julia semver specification given by the string `spec`.

    `spec` must follow the Julia version specifier format defined in
    https://pkgdocs.julialang.org/v1/compatibility/#Version-specifier-format
    The entire specification format as of Julia v1.8 is supported. The object returned is
    an instance of `semantic_version.NpmSpec`. Julia versions may be expressed as
    instances of `semantic_version.Version`. One may then use methods and functions supported
    by `NpmSpec` and `Version` to filter, test for inclusion, etc.
    """
    specs = spec.split(",")
    spec_str = " || ".join([one_semver_spec(spec) for spec in specs])
    return semantic_version.NpmSpec(spec_str)


# Taken from base/version.jl
VERSION_REGEX = re.compile(r"""^
    v?                                      # prefix        (optional)
    (\d+)                                   # major         (required)
    (?:\.(\d+))?                            # minor         (optional)
    (?:\.(\d+))?                            # patch         (optional)
    (?:(-)|                                 # pre-release   (optional)
    ([a-z][0-9a-z-]*(?:\.[0-9a-z-]+)*|-(?:[0-9a-z-]+\.)*[0-9a-z-]+)?
    (?:(\+)|
    (?:\+((?:[0-9a-z-]+\.)*[0-9a-z-]+))?    # build         (optional)
    ))
$""", re.I | re.X)


def version(vstr):
    """
    Return an instance of `semantic_version.Version` constructed from
    the Julia version string `vstr`. The input string `vstr` is parsed
    exactly as it would by in Julia.
    """
    m = VERSION_REGEX.match(vstr)
    if m is None:
        raise ValueError(f"Invalid Julia version string: {vstr}")
    major, minor, patch, minus, prerl, plus, build = m.groups()
    major = int(major)
    minor = int(minor) if minor is not None else 0
    patch = int(patch) if patch is not None else 0
    if prerl is not None and prerl[0] == '-':
        prerl = prerl[1:]
    if prerl is not None:
        prerl = prerl.split('.')
    if build is not None:
        build = build.split('.')
    return semantic_version.Version(
        major=major, minor=minor, patch=patch, prerelease=prerl, build=build
    )


def match(spec, vers, strict=False):
    """
    Return `True` if the version `vers` satisfies the specification `spec`.

    Parameters:
    `spec` : str or an object created by `semver_spec`.
        The Julia version specification
    `vers` : str or an object created by `version`.
        The Julia version
     strict : bool
        If `True` then prerelease and build versions will not match.
        If `False`, then prelease and build are ignored when matching
    """
    if isinstance(spec, str):
        spec = semver_spec(spec)
    if isinstance(vers, str):
        vers = version(vers)
    if not strict:
        vers = vers.truncate(level='patch') # truncate at patch level
    return spec.match(vers)
