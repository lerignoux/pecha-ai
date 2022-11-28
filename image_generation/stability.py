import logging
import requests
import getpass, os
import io
import os
import re
import warnings

from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation


log = logging.getLogger(__name__)


class GenerationException(Exception):
    pass


class Stability():
    """
    Image generation using Stability-SDK: https://github.com/Stability-AI/stability-sdk
    See more use cases examples: https://colab.research.google.com/github/stability-ai/stability-sdk/blob/main/nbs/demo_colab.ipynb#scrollTo=SCPVcZxjqV-u
    """
    def __init__(self, project_name="test", config=None):
        self.project_name = project_name
        self.api_key = config['api_key']
        os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'

        self.stability_api = client.StabilityInference(
            key=self.api_key,
            verbose=True
        )

    def generate(self, name, input):
        clean_name = re.sub('[^A-Za-z0-9]+', '_', name)
        clean_name = re.sub('_+', '_', clean_name)
        results = []
        answers = self.stability_api.generate(
            prompt=input,
            steps=50, # defaults to 50 if not specified
            width=960,
            height=576
        )

        # iterating over the generator produces the api response
        i = 0
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn("Your request activated the API's safety filters and could not be processed.Please modify the prompt and try again.")
                    raise GenerationException("Your request activated the API's safety filters and could not be processed.Please modify the prompt and try again.")

                if artifact.type == generation.ARTIFACT_IMAGE:
                    filename = f"generated/{self.project_name}/{clean_name}.jpg"
                    filename_raw = f"generated/{self.project_name}/debug/{clean_name}_raw.jpg"
                    try:
                        os.makedirs(os.path.dirname(filename))
                        os.makedirs(os.path.dirname(filename_raw))
                    except FileExistsError:
                        pass
                    img = Image.open(io.BytesIO(artifact.binary))
                    img = img.resize((1280, 1280))
                    try:
                        os.remove(filename_raw)
                    except OSError:
                        pass
                    img.save(filename_raw)
                    img = img.crop((0, 280, 1280, 1000))
                    try:
                        os.remove(filename)
                    except OSError:
                        pass
                    try:
                        img.save(filename)
                    except ValueError as e:
                        log.exception(f"Failed to save image {filename}: {e}")
                    results.append(filename)

        return results
