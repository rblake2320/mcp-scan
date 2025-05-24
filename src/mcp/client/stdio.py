from . import StdioServerParameters, DummyClient


def stdio_client(params: StdioServerParameters) -> DummyClient:
    return DummyClient(params)
