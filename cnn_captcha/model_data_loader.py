import os
import json
from collections import defaultdict
import torch
from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image
from .model_config import Config, char2idx


class CaptchaDataset(Dataset):
    def __init__(
        self, captchas_path, labels_path, transform=None, return_filename=False
    ):
        with open(labels_path) as f:
            self.labels = json.load(f)
        self.image_files = list(self.labels.keys())
        self.captchas_path = captchas_path
        self.transform = transform
        self.return_filename = return_filename

        # 统计标签长度
        lengths = defaultdict(int)
        for label in self.labels.values():
            lengths[len(label)] += 1
        print(f"Label length distribution: {dict(lengths)}")

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img_name = self.image_files[idx]
        image = Image.open(os.path.join(self.captchas_path, img_name))
        label = self.labels[img_name]

        if self.transform:
            image = self.transform(image)

        # 将标签转换为四个分类任务的目标
        target = []
        for char in label[: Config.max_length]:
            target.append(char2idx[char.upper()])

        if self.return_filename:
            return image, torch.LongTensor(target), img_name
        return image, torch.LongTensor(target)


# 数据增强配置
train_transform = transforms.Compose(
    [
        transforms.Grayscale(),
        transforms.RandomRotation(5),
        transforms.RandomAffine(degrees=0, translate=(0.05, 0.05)),
        transforms.ToTensor(),
    ]
)

val_transform = transforms.Compose(
    [
        transforms.Grayscale(),
        transforms.ToTensor(),
    ]
)

test_transform = transforms.Compose(
    [
        transforms.Grayscale(),
        transforms.ToTensor(),
    ]
)
