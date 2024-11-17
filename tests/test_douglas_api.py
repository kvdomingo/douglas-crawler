import pytest

from douglas.internal.douglas_api import DouglasAPI

api = DouglasAPI()


@pytest.mark.asyncio(loop_scope="module")
async def test_avocado_mask_28ml_has_correct_ean():
    data = await api.product.get("077163")
    assert data.ean == "3605971937811"


@pytest.mark.asyncio(loop_scope="module")
async def test_avocado_mask_100ml_has_correct_ean():
    data = await api.product.get("077164")
    assert data.ean == "3605971937897"
