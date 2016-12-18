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
* Create ~/multidiary/data if nonexisting
* Run `docker run --name multidiary-mysql -e MYSQL_ROOT_PASSWORD=pw -d -p 3306:3306 -v ~/multidiary/data:/var/lib/mysql mysql:5.7.16`
* Check, if you can connect to db at localhost:3306
* Create tables using provided scripts
* Import example data using .csv files from exported_eng_data

## Running Flask server

```
cd ~/multidiary
python3 multidiary
```
