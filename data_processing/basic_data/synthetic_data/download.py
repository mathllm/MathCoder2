import os
import traceback

from tqdm import tqdm
from huggingface_hub import snapshot_download

# change to root directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../.."))


def download_model(huggingface_path, local_path):
    while True:
        try:
            snapshot_download(
                huggingface_path, 
                local_dir=local_path, 
                cache_dir=CACHE_DIR, 
                local_dir_use_symlinks=True
            )
            break
        except KeyboardInterrupt:
            break
        except:
            traceback.print_exc()
            continue


def download_data(huggingface_path, local_path, allow_patterns=None):
    while True:
        try:
            snapshot_download(
                huggingface_path, 
                local_dir=local_path, 
                cache_dir=CACHE_DIR, 
                repo_type='dataset',
                local_dir_use_symlinks=True,
                allow_patterns=allow_patterns
            )
            break
        except KeyboardInterrupt:
            break
        except:
            traceback.print_exc()
            continue


def main():
    download_data("ajibawa-2023/Maths-College", "data/Maths-College", allow_patterns=allow_patterns)
    download_data("ajibawa-2023/Education-College-Students", a"dta/Education-College-Students", allow_patterns=allow_patterns)
    allow_patterns = ["book_math*", "book_science*"]
    download_data("m-a-p/Matrix", "data/Matrix_math_science", allow_patterns=allow_patterns)


if __name__ == '__main__':
    main()