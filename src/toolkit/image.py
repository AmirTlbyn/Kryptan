import uuid
from os import path, mkdir, remove
from typing import Optional


def delete_image(file_dir: str):

    file_dir = file_dir[1:]
    if path.exists(file_dir):
        remove(file_dir)
    else:
        raise Exception("The file does not exist")



def image_validator(file_dir, limit_size : Optional[float] = None):

    if (limit_size is not None) and ((path.getsize(file_dir)/1024) > limit_size):
        delete_file(file_dir)
        raise Exception("file size is too big.")
        
    
    # validated_formats = [
    #     ""
    # ]
    
    # chack format is valid or not



def upload_image(
    file,
    dir: str,
    prefix_dir : Optional[list] = None,
    previous_file : Optional[str] = None,
    limit_size : Optional[float] = None,
    ):
    
    # create directory
    file_dir = path.join("media", dir)

    if not path.exists("media"):
        mkdir("media")

    if not path.exists(file_dir):
        mkdir(file_dir)
    

    if prefix_dir is not None:
        for pd in prefix_dir:
            file_dir = path.join(file_dir, pd)
            if not path.exists(file_dir):
                mkdir(file_dir)

    # create prefix code
    prefix_code = uuid.uuid4().hex + uuid.uuid4().hex

    # rename file
    file_name = file.name.replace(' ', '_').replace("-","_")

    # create file directory
    exp_data = "{0}/{1}-{2}".format(
                                    file_dir,
                                    prefix_code,
                                    file_name)

    with open(
        exp_data,
        "wb") as exp_file:
        exp_file.write(file.read())
    exp_file.close()

    # check validate of image
    image_validator(file_dir=exp_data, limit_size=limit_size)

    # delete previous file 
    if (previous_file is not None) and (previous_file != ''):
        delete_image(file_dir=previous_file[1:])

    return "/" + exp_data

