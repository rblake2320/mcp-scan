import json

# ``aiohttp`` is an optional dependency. Import it lazily so that modules that
# don't require network functionality can still be used even if the package
# isn't installed (for example, when running unit tests in a minimal
# environment).
try:
    import aiohttp
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    aiohttp = None  # type: ignore
import shlex

try:
    from rapidfuzz.distance import Levenshtein  # type: ignore
    _levenshtein = Levenshtein.distance
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    def _levenshtein(a: str, b: str) -> int:
        """Simple Levenshtein distance implementation used as a fallback."""
        if a == b:
            return 0
        if len(a) == 0:
            return len(b)
        if len(b) == 0:
            return len(a)

        prev_row = list(range(len(b) + 1))
        for i, ca in enumerate(a, 1):
            row = [i]
            for j, cb in enumerate(b, 1):
                insert_cost = row[j - 1] + 1
                delete_cost = prev_row[j] + 1
                replace_cost = prev_row[j - 1] + (ca != cb)
                row.append(min(insert_cost, delete_cost, replace_cost))
            prev_row = row
        return prev_row[-1]
else:
    def _levenshtein(a: str, b: str) -> int:
        return Levenshtein.distance(a, b)


def calculate_distance(responses: list[str], reference: str):
    """Return ``responses`` sorted by distance from ``reference``."""

    return sorted([(w, _levenshtein(w, reference)) for w in responses], key=lambda x: x[1])


def rebalance_command_args(command: str, args: list[str] | None):
    """Combine a command string and additional arguments.

    The command string is parsed using :func:`shlex.split` so that quoted
    arguments are handled in a POSIX compatible manner.
    """

    parts = shlex.split(command)
    if not parts:
        return command, args or []

    command = parts[0]
    args = parts[1:] + (args or [])
    return command, args


async def upload_whitelist_entry(name: str, hash: str, base_url: str):
    """Upload a single whitelist entry to the given ``base_url``.

    Requires :mod:`aiohttp`. If the dependency is missing a ``RuntimeError`` is
    raised.
    """

    if aiohttp is None:
        raise RuntimeError("aiohttp is required for upload_whitelist_entry")

    url = base_url + "/api/v1/public/mcp-whitelist"
    headers = {"Content-Type": "application/json"}
    data = {
        "name": name,
        "hash": hash,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=json.dumps(data)) as response:
            if response.status != 200:
                raise Exception(
                    f"Failed to upload whitelist entry: {response.status} - {response.text}"
                )
