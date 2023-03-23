import aiohttp

from core import schemas


async def check_api_token(api_token):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://suppliers-api.wildberries.ru/public/api/v1/info',
                               headers={'Authorization': api_token}) as resp:
            return resp.status != 401


async def get_my_cards(api_token):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://suppliers-api.wildberries.ru/public/api/v1/info',
                               headers={'Authorization': api_token}) as resp:
            response = await resp.json()
            return response


async def is_my_card(api_token, article):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://suppliers-api.wildberries.ru/public/api/v1/info',
                               headers={'Authorization': api_token}) as resp:
            response = await resp.json()
            for card in response:
                if article == card["nmId"]:
                    return True
            return False


async def get_card(card_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://card.wb.ru/cards/detail?nm={card_id}') as resp:
            response = await resp.json(content_type="text/plain")
            if not response["data"]["products"]:
                return None
            else:
                return schemas.CardOut(**response["data"]["products"][0])


async def check_article(card_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://card.wb.ru/cards/detail?nm={card_id}') as resp:
            response = await resp.json(content_type="text/plain")
            if not response["data"]["products"]:
                return None
            else:
                return response["data"]["products"][0]


async def change_price_by_pre_price(change_data: schemas.ChangePriceByPrePrice):
    async with aiohttp.ClientSession() as session:
        async with session.post('https://suppliers-api.wildberries.ru/public/api/v1/prices',
                                headers={'Authorization': change_data.api_key},
                                json=[{
                                    "nmId": change_data.article,
                                    "price": change_data.price
                                }]) as resp:
            response = await resp.json(content_type="text/plain")
            if "errors" in response:
                return "Error"


async def change_price_by_sale(change_data: schemas.ChangePriceBySale):
    async with aiohttp.ClientSession() as session:
        async with session.post('https://suppliers-api.wildberries.ru/public/api/v1/updateDiscounts',
                                headers={'Authorization': change_data.api_key},
                                json=[{
                                    "nm": change_data.article,
                                    "discount": change_data.discount
                                }]) as resp:
            response = await resp.json(content_type="text/plain")
            if "errors" in response:
                return "Error"


async def change_price_all(api_key, articles):
    async with aiohttp.ClientSession() as session:
        async with session.post('https://suppliers-api.wildberries.ru/public/api/v1/prices',
                                headers={'Authorization': api_key},
                                json=articles) as resp:
            response = await resp.json(content_type="text/plain")

            if "errors" in response:
                return "Error"
