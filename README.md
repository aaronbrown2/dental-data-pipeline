This iteration of the project implements encryption of radiograph uploads. The project can easily be built in docker with the following command:

    "docker-compose up --build"

This will create a docker image that serves the application at https://localhost:8000. Just go to that link, create an account, click on radiographs then click upload radiograph. You can then choose any JPEG/PNG/TIFF file to upload and the application will automatically create a new folder in the project directory called "uploads." It will then encrypt the image and generate a unique filename for it. You can then click on the image in the application and it will decrypt the file and serve up the original image.

A crypto key is already provided through environment variables in docker-compose.yml.
If you run the app outside Docker, you’ll need to generate your own key.