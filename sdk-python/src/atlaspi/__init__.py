"""atlaspi — Python client for the AtlasPI Historical Geography API.

Free, public, no-auth REST API with 862 historical entities from 4500 BCE to 2024.

Quick start:

    from atlaspi import AtlasPI
    client = AtlasPI()
    snapshot = client.snapshot(year=1250)
    similar = client.entities.similar(entity_id=1)

Async:

    from atlaspi import AsyncAtlasPI
    async with AsyncAtlasPI() as client:
        snapshot = await client.snapshot(year=1500)

Docs: https://atlaspi.cra-srl.com/docs
Source: https://github.com/Soil911/AtlasPI
"""

from atlaspi.client import AtlasPI, AsyncAtlasPI, AtlasPIError

__version__ = "0.1.0"

__all__ = ["AtlasPI", "AsyncAtlasPI", "AtlasPIError", "__version__"]
