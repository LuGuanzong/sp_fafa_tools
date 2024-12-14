from app.control.download_img_from_1688 import DownloadImgFrom1688


def download_product_imgs() -> None:
    """
    从1688下载产品图
    :return:
    """
    dlf1688 = DownloadImgFrom1688()
    dlf1688.download_imgs()


if __name__ == '__main__':
    download_product_imgs()
