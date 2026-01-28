def generate(mcp_config):
    return [{"type": c, "data": mcp_config["data"]} for c in mcp_config["charts"]]
