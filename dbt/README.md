Welcome to your new dbt project!

This file is about running dbt locally with virtual env

## Before you start

*Requirements*

- Python 3.7+
- pip 19.1+


```bash

pip install virtualenv
python -m venv dbtVirtual
source ./dbtVirtual/bin/activate

#install requirements in your virtual environment

pip install -r requirements.txt

mkdir dbt-projects
cd dbt-projects
dbt init project-name

nano ~/.dbt/profiles.yml

```

## Update the profiles.yml

```yaml

#paste below at bottom of the yaml file and update project and dataset
project-name:
  outputs:
    dev:
      type: bigquery
      method: oauth
      project: bridge_data_analytics
      dataset: nakul # You can also use "schema" here
      threads: 10
      timeout_seconds: 300
      location: australia-southeast1 # Optional, one of US or EU
      priority: interactive
      retries: 3
  target: dev

```

### Using the starter project

```bash
cd project-name
```

Try running the following commands:
- dbt run
- dbt test


### Resources:
- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](http://slack.getdbt.com/) on Slack for live discussions and support
- Find [dbt events](https://events.getdbt.com) near you
- Check out [the blog](https://blog.getdbt.com/) for the latest news on dbt's development and best practices


### Using the spotlight project

Try running the following commands:
- dbt run -m example
- dbt test -m example
