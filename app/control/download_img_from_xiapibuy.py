import os
import random
import re
import shutil
import time
from mimetypes import guess_extension
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests


class DownloadImgFromXiapi:
    """
    从虾皮中国可访问站点对应的商品网页下载主图、sku图
    """

    def __init__(self, html=''):
        self.html_content = html  # 目标虾皮网页的html代码
        if not self.html_content:
            # html源文件路径
            file_path = 'forUse'
            print(f'正在读取{file_path}文件里的html信息')
            with open(file_path, 'r', encoding='utf-8') as file:
                # 读取文件的全部内容
                self.html_content = file.read()

        print(f'html信息读取完毕')

        self.base_url = 'https://my.xiapibuy.com'
        self.soup = BeautifulSoup(self.html_content, 'html.parser')  # 解析过的目标虾皮网页的html代码
        self.folder_name = '图片虾皮'  # 放置下载好的图片的文件夹
        self.desktop_path = Path(Path.home(), 'Desktop')  # 获取当前用户的桌面路径
        self.save_path = self.desktop_path / self.folder_name  # 构建完整的文件保存路径

    def get_main_imgs(self) -> list:
        """
        :return: 主图图片链接列表
        """
        # 找到所有主图的元素
        img_list_wrapper = self.soup.find('source', class_='UkIsx8', type_='image/webp')

        if img_list_wrapper is None:
            img_src_list = list()
        else:
            # 提取每个img标签的src属性，并将其转换为绝对URL（如果需要）
            img_src_list = [urljoin(self.base_url, img['srcset']) for img in img_list_wrapper]

        return img_src_list

    def get_sku_imgs(self) -> list:
        """
        :return: sku图链接列表
        """
        sku_urls = list()

        sku_item_wrappers = self.soup.find_all('div', class_='sku-item-wrapper')

        for sku_item_wrapper in sku_item_wrappers:
            sku_item_image = sku_item_wrapper.find('div', class_='sku-item-image')

            if not sku_item_image:
                continue

            # 提取style属性中的background URL
            style = sku_item_image.get('style')

            # 使用正则表达式提取URL
            url_match = re.search(r'url\("([^"]+)"\)', style)
            if url_match:
                background_url = url_match.group(1)
                sku_urls.append(background_url)

        return sku_urls

    def get_desc_imgs(self) -> list:
        """
        获取class为content-detail的div里面的所有class为desc-img-loaded的子孙img的src，返回列表
        :return: 详情图链接列表
        """
        content_detail_div = self.soup.find('div', class_='content-detail')

        # 如果找到了content-detail div，则继续查找其内部所有class为desc-img-loaded的子孙img
        if content_detail_div:
            # 使用find_all查找所有class为desc-img-loaded的子孙img元素，并提取src属性
            img_src_list = [img['src'] for img in
                            content_detail_div.find_all('img', class_='desc-img-loaded', recursive=True)]

            # 返回src属性的列表
            return img_src_list
        else:
            # 如果没有找到content-detail div，则返回空列表
            return []

    def turn_webg_to_png(self):
        """
        把webg格式的图片转换为png
        :return:
        """
        pass

    def download_from_list(self, image_urls=None, prefix='图片') -> None:
        """
        下载列表里的图片
        :param prefix: 下载下来的图片前缀
        :param image_urls: 图片链接列表
        :return:
        """
        if image_urls is None:
            image_urls = list()

        # 如果文件夹已存在，则清空它
        if not os.path.exists(self.save_path):
            # 创建文件夹
            os.makedirs(self.save_path)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

        print('')
        print(f"--------识别到{prefix}链接一共有{len(image_urls)}条--------")

        # 下载每张图片
        for idx, image_url in enumerate(image_urls):
            file_name = f'{prefix}_{idx + 1}'

            # 发送HTTP GET请求获取图片
            response = requests.get(image_url, headers=headers, stream=True)

            # 随机延迟
            delay = random.uniform(1, 3)  # 1到3秒之间的随机延迟
            time.sleep(delay)

            # 检查请求是否成功
            if response.status_code == 200:
                # 尝试从Content-Type中猜测文件扩展名
                content_type = response.headers.get('Content-Type')
                file_extension = guess_extension(content_type) or '.jpg'  # 默认为.jpg

                # 构建完整的文件路径
                file_path = os.path.join(self.save_path, f'{file_name}{file_extension}')

                # 以二进制模式打开文件并写入响应内容
                with open(file_path, 'wb') as image_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        image_file.write(chunk)

                print(f'Downloaded {file_name}{file_extension}')
            else:
                print(f'Failed to download {image_url} (status code: {response.status_code})')
                print('response', response.json())

    def download_imgs(self):
        """
        下载主图、sku图、详情图
        :return:
        """
        # 如果文件夹已存在，则清空它
        if os.path.exists(self.save_path):
            shutil.rmtree(self.save_path)

        # 创建文件夹
        os.makedirs(self.save_path)

        # 下载主图
        self.download_from_list(image_urls=self.get_main_imgs(), prefix='主图')
        # 下载sku图
        self.download_from_list(image_urls=self.get_sku_imgs(), prefix='sku')
        # 下载详情图
        self.download_from_list(image_urls=self.get_desc_imgs(), prefix='详情')

        print(f'已完成下载，存储路径在 {self.save_path}')
