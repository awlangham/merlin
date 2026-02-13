async def get_transient(self, start_ts: int, end_ts: int):
    pipe = await self.node.data_read(self.stream_name + '/transients', start=start_ts, end=end_ts)
    sarray = await pipe.read_all(flatten=True)
    return sarray


async def get_transients(self, intervals: list[list[int]]) -> list:
    """
    Return a list of the transients corresponding
    to the specified intervals in the provided stream.
    """

    transients = []
    for interval in intervals:
        pipe = await self.node.data_read(self.stream_name + '/transients', start=interval[0], end=interval[1])
        sarray = await pipe.read_all(flatten=True)
        transients.append(sarray.T)
    return transients
