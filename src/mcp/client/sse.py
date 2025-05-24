from . import stdio_client, StdioServerParameters

def sse_client(*args, **kwargs):
    # Delegate to stdio_client for simplicity in tests
    return stdio_client(StdioServerParameters("", []))
