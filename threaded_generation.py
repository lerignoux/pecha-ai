import logging
import threading
from multiprocessing.pool import ThreadPool

from presentation_generation.pptx import Pptx
from image_generation.stability import Stability, GenerationException


log = logging.getLogger(__name__)


class threadedGeneration:

    default_images = [
        ("cake", "generated/__default__/cake.jpg"),
        ("fairy", "generated/__default__/fairy.jpg"),
        ("fish", "generated/__default__/fish.jpg"),
    ]

    ais = {
        'none': None,
        'stability': Stability
    }

    def __init__(self, config, pool_size=50):
         # we dont want users to be able to overload the system ;)
        self.config = config
        self.pool = ThreadPool(processes=pool_size)

    def get_config(self, ai):
        return self.config.get(ai, {})

    def generate_image(self, title, input_text, ai, config):
        ai = self.ais[ai](title, config)
        input_text = input_text.strip(" ,\r")
        image = ai.generate(input_text, input_text)
        if len(image) == 0:
            raise Exception(f"Failed generating image from input {input_text}.")
        elif len(image) > 1:
            log.warning(f"multiple images generated for input {input_test}, only first image will be used.")
        return (title, image[0])

    def generate_images(self, title, inputs, ai='stability'):
        if ai == 'none':
            return self.default_images

        config = self.get_config(ai)
        generation_threads = [None for i in inputs]
        images = [None for i in inputs]

        for i, input_text in enumerate(inputs):
            async_result = self.pool.apply_async(self.generate_image, (title, input_text, ai, config))
            generation_threads[i] = async_result

        for i, async_result in enumerate(generation_threads):
            images[i] = async_result.get()

        log.debug(f"Images generated: {images}")
        return images

    def generate_pecha(self, title, images, slide_duration):
        filename = Pptx(title, slide_duration=slide_duration).generate(title, images)
        log.debug(f"Generated presentation {filename}")
        return filename
