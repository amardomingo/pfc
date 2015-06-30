import scrapy
from vademecum.items import VademecumItem

import re
import bs4
import json

class vademecumSpider(scrapy.Spider):
    
  # Test spider to get the vademecum.IO
  name = "vademecum"
  allowed_domains = ["http://www.dit.upm.es/"]
  url_base = "http://www.dit.upm.es/~pepe/libros/vademecum/topics/{}.html"
  
  start_urls = [url_base.format(str(i)) for i in xrange(4, 394)]

  def parse(self, response):
      
    doc = VademecumItem()
    doc["resource"] = response.url
    
    header = response.xpath(
          "//p[@class=\"MsoHeader\"]/ancestor::div/*[2]/descendant::*/*/text()")
          .extract()
    header = ''.join(header).strip()
    match = re.search("(\d+)\.\s*(.+)\s\[(.+)\]\s?\((.+)\)",
                      header, flags=re.U)
    if match and match.lastindex == 4:
      doc["title"] = match.group(2)
      doc["alternative"] = match.group(3)
      doc["concept"] = match.group(4)

    return doc