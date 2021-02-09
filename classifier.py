# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os
import json
import sys
import PIL
import numpy as np
import tensorflow as tf


def load_labels(file_name):
    with open(file_name, "r") as f:
        return [line.strip() for line in f.readlines()]


def classify_imgs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--tests",
        default="detected_faces",
        help="folder of test imgs to be classified",
    )
    parser.add_argument(
        "-m",
        "--model_file",
        default="new_mobile_model.tflite",
        help=".tflite model to be executed",
    )
    parser.add_argument(
        "-l",
        "--label_file",
        default="class_labels.txt",
        help="name of file containing labels",
    )
    parser.add_argument("--input_mean", default=0.0, type=float, help="input_mean")
    parser.add_argument(
        "--input_std", default=255.0, type=float, help="input standard deviation"
    )
    parser.add_argument(
        "--num_threads", default=None, type=int, help="number of threads"
    )
    args = parser.parse_args()

    results = {}
    IMGS_DIR = os.listdir(args.tests)

    for file in IMGS_DIR:

        interpreter = tf.lite.Interpreter(
            model_path=args.model_file, num_threads=args.num_threads
        )
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # check the type of the input tensor
        floating_model = input_details[0]["dtype"] == np.float32

        # NxHxWxC, H:1, W:2
        height = input_details[0]["shape"][1]
        width = input_details[0]["shape"][2]
        img = PIL.Image.open(str(args.tests) + "/" + str(file)).resize((width, height))

        # add N dim
        input_data = np.expand_dims(img, axis=0)

        if floating_model:
            input_data = (np.float32(input_data) - args.input_mean) / args.input_std

        interpreter.set_tensor(input_details[0]["index"], input_data)

        interpreter.invoke()

        output_data = interpreter.get_tensor(output_details[0]["index"])
        confidences = np.squeeze(output_data)

        labels = load_labels(args.label_file)
        confidences = list(confidences)

        if floating_model:
            outcome_confidence = float(max(confidences))
            detection_outcome = {
                "match": labels[confidences.index(outcome_confidence)],
                "confidence": outcome_confidence,
            }

            results[file] = detection_outcome
        else:
            print("one of the confidences was not a floating_model")
            sys.exit(1)

    return results


def write_img_labels():
    DEST_FILE = "results.json"
    with open(DEST_FILE, "w") as outfile:
        json.dump(classify_imgs(), outfile)