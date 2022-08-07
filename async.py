import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import time


start_time = time.time()
car_logos = {}
brand_names = []

async def get_info(rows):
    about_brand = {}
    for i in range(0, len(rows)):
        rows[i] = rows[i].text.replace(':', '')
        if rows[i].split()[0] in ['Founded', 'Founder', 'Owner',  'Owners', 'Predecessor', 'Official Site', 'Country', 'Markets', 'Name', 'Type', 'Slogan','History', 'Headquarters', 'Parent']:
            about_brand[rows[i].split()[0]] = ' '.join(rows[i].split()[1:])
        if ' '.join(rows[i].split()[0:2]) == 'Official Site':
            about_brand[' '.join(rows[i].split()[0:2])] = rows[i].split()[2]
        else:
            pass
    return about_brand

async def get_content(session, brand):
    brand_url = f'https://www.carlogos.org{brand}'
    async with session.get(brand_url) as response2:
        soup2 = BeautifulSoup(await response2.text(), 'html.parser')
        info = soup2.find('div', class_='content')

        if soup2.find('div', class_='content') is None:
            overview = soup2.find('div', class_='overview')
            logo = soup2.find('p', class_='shadow')
            rows = overview.find_all('p')
            name = soup2.find('div', class_='title')
            car_logos[name.find('h1').text.replace('Logo', '')] = await get_info(rows)
            car_logos[name.find('h1').text.replace('Logo', '')]['Link to present logo'] = logo.find('img')['src']
        else:
            content = info.find('table')
            rows = content.find_all('tr')[1:]
            car_logos[content.find('th').text.split()[0]] = await get_info(rows)
            logo_link = info.find('img')['src']
            if logo_link.startswith('https:') == True:
                car_logos[content.find('th').text.split()[0]]['Link to present logo'] = logo_link
            else:
                car_logos[content.find('th').text.split()[0]]['Link to present logo'] = 'https:' + logo_link

async def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
    async with aiohttp.ClientSession(trust_env=True) as session:
        for i in range(1, 9):
            url = 'https://www.carlogos.org/car-brands/'
            if i == 1:
                url = url
            else:
                url = url + f'page-{i}.html'
            response = await session.get(url=url, headers=headers)
            soup = BeautifulSoup(await response.text(), 'html.parser')
            logo_list = soup.find('ul', class_='logo-list')
            brand_list = logo_list.find_all('li')
            for i in range(len(brand_list)):
                brand_names.append((brand_list[i].find('a')).get('href'))
            tasks = []
            for brand in brand_names:
                    task = asyncio.create_task(get_content(session, brand))
                    tasks.append(task)
            await asyncio.gather(*tasks)

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
end_time = time.time() - start_time
print(f"\nExecution time: {end_time} seconds")

with open("carlogos_file.json", "w", encoding='utf-16') as file:
    json.dump(car_logos, file, indent=4, ensure_ascii=False)