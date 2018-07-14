# -*- coding: utf-8 -*-
import scrapy


class CmsSpider(scrapy.Spider):
    name = 'cms'
    start_urls = ['http://www.cms.ba.gov.br/despesa.aspx/']

    @staticmethod
    def clean_list(list):
        # remove trash of list
        del list[:2]
        del list[-1]

        return list

    @staticmethod
    def clean_line(line):
        return line[1::2]

    def parse(self, response):

        divs = response.xpath('//*[@id="ContentPlaceHolder1_UpdatePanel1"]/div')

        clean_divs = self.clean_list(divs)

        for div in clean_divs:
            temp_info = div.xpath('./text()').extract()

            info = self.clean_line(temp_info)

            yield {
                'registro': info
            }
