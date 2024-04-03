# API Documentation

[Manage your AI Copilot users](https://help.getconduit.app/en/article/manage-your-ai-copilot-users-1y4wpc4/)

[Create an AI Сopilot for your app](https://help.getconduit.app/en/article/create-an-ai-sopilot-for-your-app-16uf54b/)

# Requirements 

Project requires Python>=3.11 and [Poetry](https://python-poetry.org/) for package dependencies.

```shell
poetry install
```

# Configuration

Open file `conduit/settings.py` and change `LINK_TOKEN` variable.  
You can acquire `LINK_TOKEN` [here](https://app.getconduit.app/auth/link_app_token/).   

# Running

Execute following command and open http://127.0.0.1:8000.
```shell
python manage.py runserver
```
