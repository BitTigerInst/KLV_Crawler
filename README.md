
# KLV Crawler
This crawler can crawl tens of thousands of apps information from the Xiaomi App Store, and save them into the MongoDB. It is based on Python + Scrapy. 

## Getting Started

### Prerequisties:

You'll need to install:
 * Python (2.7.10)
 * scrapy(python lib)
 * pymongo(python lib)
 * MongoDB (3.0.0+)

### Installing

#### Python(Mac OSX)
```bash
sudo pip install scrapy
sudo pip install pymongo
```

#### MongoDB(CentOS7)
```bash
yum -y install mongodb-org mongodb-org-server
systemctl start mongod
````
## Usage

### Download
```bash
git clone https://github.com/BitTigerInst/KLV_Crawler.git
```

### Run
```bash
cd KLV_Crawler
scrapy crawl cnproxy
scrapy crawl vkea_xiaomi
```
## Team Members
||
|:--:|
|![Vkea95](https://avatars1.githubusercontent.com/u/10228267?v=3&u=c33fe84168e0cbbd75fc84d69029abb90a873ee1&s=140)|
|[Vkea95](https://github.com/vkea95)|

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Project Information