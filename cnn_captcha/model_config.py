import torch


class Config:
    # 数据集路径
    vlm_captchas_path = "datasets/vlm_captchas"
    vlm_labels_path = "datasets/vlm_labels.json"
    human_captchas_path = "datasets/human_captchas"
    human_labels_path = "datasets/human_labels.json"
    test_captchas_path = "datasets/test_captchas"
    test_labels_path = "datasets/test_labels.json"

    # 训练参数
    batch_size = 64
    lr = 0.001
    num_epochs_pretrain = 50
    num_epochs_finetune = 100
    num_classes = 36
    max_length = 4

    # 模型保存路径
    pretrain_model_path = "pretrain_model.pth"
    final_model_path = "final_model.pth"

    # 设备配置
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# 字符映射表
char2idx = {
    char: idx for idx, char in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
}
idx2char = {idx: char for char, idx in char2idx.items()}
