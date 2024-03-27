class ChannelNotExist(Exception):
    """Raised when get_channel and fetch_channel both failed to resolve from a channel_id."""
    pass