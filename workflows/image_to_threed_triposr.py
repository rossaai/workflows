from typing import List
from rossa import (
    Image,
    BaseWorkflow,
    ControlsField,
    ControlValue,
    ReferenceImageControl,
    ThreeDResponse,
    next_control,
    ContentType,
    ControlOption,
    ControlContent,
    ImageControlContent,
)

# Adapted from: https://github.com/camenduru/TripoSR-replicate/blob/main/cog.yaml
image = (
    Image.from_registry("nvidia/cuda:12.1.1-devel-ubuntu22.04", add_python="3.10")
    .apt_install(
        "gcc",
        "g++",
        "aria2",
        "git",
        "git-lfs",
        "wget",
        "libgl1",
        "libglib2.0-0",
        "ffmpeg",
        "cmake",
        "libgtk2.0-0",
        "libopenmpi-dev",
    )
    .workdir("/root")
    .run_commands(
        "git clone https://github.com/VAST-AI-Research/TripoSR",
    )
    .workdir("/root/TripoSR")
    .run_commands(
        "pip install torch==2.1.0+cu121 torchvision==0.16.0+cu121 torchaudio==2.1.0+cu121 torchtext==0.16.0 torchdata==0.7.0 --extra-index-url https://download.pytorch.org/whl/cu121 -U",
    )
    .run_commands(
        "pip install https://github.com/camenduru/wheels/releases/download/colab/torchmcubes-0.1.0-cp310-cp310-linux_x86_64.whl",
    )
    .run_commands(
        "pip install trimesh omegaconf einops rembg huggingface_hub transformers"
    )
)


with image.imports():
    import numpy as np
    import rembg
    import torch
    from PIL import Image as PILImage
    import time

    from TripoSR.tsr.system import TSR
    from TripoSR.tsr.utils import (
        remove_background,
        resize_foreground,
        to_gradio_3d_orientation,
    )

    def preprocess_image(
        input_image: PILImage,
        do_remove_background: bool,
        foreground_ratio: float,
        rembg_session,
    ):
        def fill_background(image):
            image = np.array(image).astype(np.float32) / 255.0
            image = image[:, :, :3] * image[:, :, 3:4] + (1 - image[:, :, 3:4]) * 0.5
            image = Image.fromarray((image * 255.0).astype(np.uint8))
            return image

        if do_remove_background:
            image = input_image.convert("RGB")
            image = remove_background(image, rembg_session)
            image = resize_foreground(image, foreground_ratio)
            image = fill_background(image)
        else:
            image = input_image
            if image.mode == "RGBA":
                image = fill_background(image)
        return image


class ReferenceImageControl(ControlOption):
    title: str = "Reference"
    description: str = (
        "Guides the image generation process. Lower values blend the colors more, while higher values reduce the influence of the reference image."
    )
    supported_contents: List[ControlContent] = [ImageControlContent()]


class Workflow(BaseWorkflow):
    image = image
    title = "3D Model Generator"
    version = "TripoSR V1"
    description = "Transform your images into 3D models"

    def download(self):
        TSR.from_pretrained(
            "stabilityai/TripoSR",
            config_name="config.yaml",
            weight_name="model.ckpt",
        )

        rembg.new_session()

    def load(self):
        if torch.cuda.is_available():
            device = "cuda:0"
        else:
            device = "cpu"

        start = time.time()
        model = TSR.from_pretrained(
            "stabilityai/TripoSR",
            config_name="config.yaml",
            weight_name="model.ckpt",
        )

        # adjust the chunk size to balance between speed and memory usage
        model.renderer.set_chunk_size(8192)
        model.to(device)

        print(f"Model loaded in {time.time() - start} seconds")

        rembg_session = rembg.new_session()

        self.model = model
        self.device = device
        self.rembg_session = rembg_session

        print("Model loaded in", time.time() - start, "seconds")

    def run(
        self,
        controls: List[ControlValue] = ControlsField(options=[ReferenceImageControl()]),
        resolution: int = 256,
        remove_background: bool = True,
        foreground_ratio: float = 0.85,
        format: str = "glb",
    ):
        image = next_control(controls, ReferenceImageControl())

        image = image.to_pil_image(ContentType.IMAGE)

        image = preprocess_image(
            image, remove_background, foreground_ratio, self.rembg_session
        )

        with torch.no_grad():
            scene_codes = self.model(image, device=self.device)

        mesh = self.model.extract_mesh(scene_codes, resolution=resolution)[0]

        mesh = to_gradio_3d_orientation(mesh)

        mesh_glb = mesh.export(file_type=format)

        # save mesh to file with same format
        yield ThreeDResponse(content=mesh_glb)
