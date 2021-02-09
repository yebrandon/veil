import face_recognition
import os
import PIL

DEST_DIR = os.getcwd() + "/detected_faces/"


def remove_files(target_dir):
    for file in os.listdir(target_dir):
        os.remove(target_dir + "/" + file)


def process_imgs():
    """
    Detect human faces in an image and save faces as seperate files
    """
    remove_files(DEST_DIR)

    img = face_recognition.load_image_file("capture.png")
    face_locations = face_recognition.face_locations(
        img, 1, "cnn"
    )  # Using cnn model for higher accuracy

    # Crop image to include only face and save
    for i in range(len(face_locations)):
        top, right, bottom, left = face_locations[i]
        face_image = img[top:bottom, left:right]
        pil_image = PIL.Image.fromarray(face_image)
        pil_image.save(DEST_DIR + "face_" + str(i) + ".jpg")
