import os
import re
import shutil
from mimetypes import guess_extension
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests


class DownloadImgFrom1688:
    """
    从1688对应的商品网页下载主图、sku图、详情图
    """

    def __init__(self, html=''):
        self.html_content = html  # 目标1688网页的html代码
        self.base_url = 'https://detail.1688.com'

        if not self.html_content:
            self.html_content = input('请输入目标产品1688网页的html代码：')

        self.soup = BeautifulSoup(self.html_content, 'html.parser')
        self.folder_name = '图片1688'

    def get_main_imgs(self) -> list:
        """
        :return: 主图图片链接列表
        """
        # 找到主图轮播图上一层的div1
        div1 = self.soup.find('div', class_='img-list-wrapper')

        # 如果没有找到div1，返回空列表
        if div1 is None:
            img_src_list = list()
        else:
            # 找到div1内所有class为detail-gallery-turn-wrapper的div中的img标签
            img_tags = div1.find_all('img', recursive=False)  # recursive=False确保只在直接子节点中查找
            # 提取每个img标签的src属性，并将其转换为绝对URL（如果需要）
            img_src_list = [urljoin(self.base_url, img['src']) for img in img_tags]

        return img_src_list

    def get_sku_imgs(self) -> list:
        """
        :return: sku图链接列表
        """
        sku_urls = list()

        sku_item_wrappers = self.soup.find_all('div', class_='sku-item-wrapper')

        for sku_item_wrapper in sku_item_wrappers:
            sku_item_image = sku_item_wrapper.find('div', class_='sku-item-image')

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
        if not os.path.exists(self.folder_name):
            # 创建文件夹
            os.makedirs(self.folder_name)

        print(f"--------识别到{prefix}链接一共有{len(image_urls)}条--------")

        # 下载每张图片
        for idx, image_url in enumerate(image_urls):
            file_name = f'{prefix}_{idx + 1}.jpg'

            # 发送HTTP GET请求获取图片
            response = requests.get(image_url, stream=True)

            # 检查请求是否成功
            if response.status_code == 200:
                # 尝试从Content-Type中猜测文件扩展名
                content_type = response.headers.get('Content-Type')
                file_extension = guess_extension(content_type) or '.jpg'  # 默认为.jpg

                # 构建完整的文件路径
                file_path = os.path.join(self.folder_name, f'{file_name}{file_extension}')

                # 以二进制模式打开文件并写入响应内容
                with open(file_path, 'wb') as image_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        image_file.write(chunk)

                print(f'Downloaded {file_path}')
            else:
                print(f'Failed to download {image_url} (status code: {response.status_code})')

    def download_imgs_from_1688(self):
        """
        下载主图、sku图、详情图
        :return:
        """
        # 如果文件夹已存在，则清空它
        if os.path.exists(self.folder_name):
            shutil.rmtree(self.folder_name)

        # 创建文件夹
        os.makedirs(self.folder_name)

        # 下载主图
        self.download_from_list(image_urls=self.get_main_imgs(), prefix='主图')
        # 下载sku图
        self.download_from_list(image_urls=self.get_sku_imgs(), prefix='sku')
        # 下载详情图
        self.download_from_list(image_urls=self.get_desc_imgs(), prefix='详情')
