Steps to run it:
1. add your openai key to .env example file and rename it to .env
2. copy your pdf resume to the [resumes](resumes) folder
3. adjust [config.yaml](config.yaml) to your needs, if you have only openai key, use mini for parsing resume and job description and use gpt-4o for tailoring.
4. build docker image and run container: 
``` bash
docker-compose up --build -d
docker-compose exec resume-builder bash
```
5. run the script in the container and follow the instructions:
``` bash
python main.py
```