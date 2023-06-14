# Machine Learning

This is machine learning project for Traffic Detection from Capstone Group C23-PC636 for Bangkit Capstone Project

## Requirements

1. python3 
2. ffmpeg ( for stream m3u8 file )
3. v4l2loopback ( for virtual device )
4. RabbitMQ ( for task distribution )


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the package needed to run this project.

```bash
pip install -r requirements.txt
```

Note : Build `lap` yourself if u got error when installing lap
1. Clone lap github `git clone https://github.com/gatagat/lap`
2. Build lap `python setup.py install` (may need to install cython,etc.)


## Usage

1. Start RabbitMQ or other message broker
2. Start celery worker `.celery.sh` (may need to install message broker like RabbitMQ or Redis)
3. Start web.py `python web.py`
 

## Contributing

Currently, we only accept contribution from our own members.

## License

[MIT](https://choosealicense.com/licenses/mit/)