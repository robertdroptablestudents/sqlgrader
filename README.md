# SQLGrader

Providing automated grading and test environment management for relational databases ([Postgres](https://www.postgresql.org/), [MSSQL](https://www.microsoft.com/sql-server/), and [MySQL](https://www.mysql.com/)). Uses Python ([Django](https://www.djangoproject.com/), [Flask](https://flask.palletsprojects.com/)) and [Docker-in-Docker](https://docs.docker.com/) to provide a GUI on top of coordination of grading environments according to your schema specifications.

![GitHub](https://img.shields.io/github/license/robertdroptablestudents/sqlgrader?style=flat-square)

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/robertdroptablestudents/sqlgrader/droplet%20refresh?style=flat-square) => main branch deployed live at [http://sqlgrader.drewsk.tech/](http://sqlgrader.drewsk.tech/)



## Quick Start

SQLGrader is available as a container image for ARM64 and AMD64 architectures. Pull the image and run to give SQLGrader a spin:

```bash
docker pull ghcr.io/robertdroptablestudents/sqlgrader:latest
docker run -p 80:80 --name sqlgrader --privileged -d ghcr.io/robertdroptablestudents/sqlgrader:latest
```

*Note: the webUI may take a few minutes to build and run after starting the container*

## Documentation

Project documentation is available at [https://robertdroptablestudents.github.io/](https://robertdroptablestudents.github.io/)

![Architecture overview](https://robertdroptablestudents.github.io/assets/diagrams/arch.png)



## Contributing

Contributions are welcome!
1. This project has a [Code of Conduct](code_of_conduct.md)
2. Documentation on development for SQLGrader is available at [https://robertdroptablestudents.github.io/docs/development](https://robertdroptablestudents.github.io/docs/development)
