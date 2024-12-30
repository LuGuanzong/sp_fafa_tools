from app.control.download_img_from_xiapibuy import DownloadImgFromXiapi


def download_product_imgs() -> None:
    """
    从虾皮下载产品图
    :return:
    """
    dlf1688 = DownloadImgFromXiapi()
    dlf1688.download_imgs()


if __name__ == '__main__':
    download_product_imgs()