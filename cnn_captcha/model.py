from torch import nn
from .model_config import Config


class CaptchaModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d((4, 6)),
        )

        self.classifiers = nn.ModuleList(
            [
                nn.Sequential(
                    nn.Flatten(),
                    nn.Linear(128 * 4 * 6, 256),
                    nn.BatchNorm1d(256),
                    nn.ReLU(),
                    nn.Dropout(0.5),
                    nn.Linear(256, Config.num_classes),
                )
                for _ in range(Config.max_length)
            ]
        )

    def forward(self, x):
        features = self.cnn(x)
        return [cls(features) for cls in self.classifiers]
