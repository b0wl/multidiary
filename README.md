# multidiary



# Linux installation

## Downloading repository

```
git clone https://github.com/b0wl/multidiary.git ~/multidiary
cd ~/multidiary
pip3 install -r requirements
```

## Running MySQL server

* [Install Docker](https://docs.docker.com/engine/installation/linux/ubuntulinux/)
* Create ~/multidiary/.data if nonexisting
* Run `docker run --name multidiary-mysql -e MYSQL_ROOT_PASSWORD=pw -d -p 3306:3306 -v ~/multidiary/.data:/var/lib/mysql mysql`
* Check, if you can connect to db at localhost:3306. _You may use `MySQL workbench`_
* Create and populate tables using provided scripts

## Running Flask server

```
cd ~/multidiary
python3 multidiary.py
```

# Windows installation

## Downloading repository

```
git clone https://github.com/b0wl/multidiary.git multidiary
cd multidiary
pip install -r requirements -r win_requirements
```

## MySQL server

Server may be run on Docker like in linux or without it.

* For Docker installation guide go [here](https://docs.docker.com/engine/installation/windows/).
 * On Windows 10 Professional, Enterprise or Education with Microsoft Hyper-V check [this](https://docs.docker.com/docker-for-windows/) guide.
 * On older Windows versions and Win10 Home check [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/)


* For non-Docker solution install standard MySQL server.
    * Download [MySQL Installer](http://dev.mysql.com/downloads/installer/)
    * Download and configure MySQL Server within MySQL Installer (for easier usage install MySQL Notifier to run/stop server)
        * set user to `root` and password to `pw`
        * set address and port to `localhost:3306`

## Running Flask server

* Make sure to change `SQLALCHEMY_DATABASE_URI` in `config.py` to `'mysql+pymysql://root:pw@0.0.0.0:3306/Mikroblog'`
* If you are running server without Docker, also change address from `0.0.0.0` to `localhost`.
```
cd multidiary
python multidiary.py
```